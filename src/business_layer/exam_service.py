"""Business rules for the student's online examination workflow.

Owner: Nguyễn Thành Vinh.

Three-layer contract
--------------------
This service contains no SQL and no Flask request/session code. The route layer
passes the authenticated ``session['user_id']`` to this service. The service
uses an exam repository (implemented by Long in course_exam_dao.py) and the
Attempt DAO implemented in attempt_result_dao.py.

Expected exam_repository methods:
    get_exam_by_id(exam_id) -> dict | None
    list_published_exams() -> list[dict]
    get_questions_by_exam(exam_id) -> list[dict]

The exam dictionary follows the ERD / CONTRIBUTING contract and contains:
    exam_id, title, status ('Published'), start_time, end_time, duration, rules
Question dictionaries contain question_id, content, question_type, marks and
an optional ``answers`` list (answer_id, content, is_correct). Correct-answer
flags are removed before returning questions to the student.

Expected attempt_repository methods are the public functions in
src.data_layer.attempt_result_dao. Dependencies are injected so this module can
be unit-tested before Hưng's MySQL connection and Long's DAO are merged.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Callable, Dict, Iterable, List, Optional

try:  # Package import when the application is launched from the repository root.
    from ..data_layer import attempt_result_dao
except ImportError:  # pragma: no cover - supports legacy direct imports
    import attempt_result_dao  # type: ignore


IN_PROGRESS = "IN_PROGRESS"
SUBMITTED = "SUBMITTED"
EXPIRED = "EXPIRED"
PUBLISHED = "Published"


class ExamServiceError(Exception):
    """A user-safe business error that the Flask route can map to JSON."""

    def __init__(self, message: str, code: str = "EXAM_ERROR", http_status: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.http_status = http_status

    def to_dict(self) -> Dict[str, Any]:
        return {"success": False, "error": self.code, "message": self.message}


class ExamService:
    """Implements available-exam, start, resume, autosave and submit rules."""

    def __init__(
        self,
        exam_repository: Any,
        attempt_repository: Any = None,
        clock: Optional[Callable[[], datetime]] = None,
    ) -> None:
        if exam_repository is None:
            raise ValueError("exam_repository is required")
        self.exams = exam_repository
        self.attempts = attempt_repository or attempt_result_dao
        self.clock = clock or datetime.now

    def list_available_exams(self, user_id: int) -> List[Dict[str, Any]]:
        """Return published exams whose scheduled window is currently open."""
        self._validate_user_id(user_id)
        list_method = getattr(self.exams, "list_published_exams", None)
        if not callable(list_method):
            raise ExamServiceError(
                "Exam repository must implement list_published_exams().",
                "EXAM_REPOSITORY_CONTRACT", 500,
            )
        now = self._now()
        exams = list_method() or []
        available = []
        for exam in exams:
            if not self._is_published(exam):
                continue
            start = self._normalize_datetime(exam.get("start_time"))
            end = self._normalize_datetime(exam.get("end_time"))
            if now > end:
                continue
            item = self._public_exam_fields(exam)
            item["availability"] = "UPCOMING" if now < start else "AVAILABLE"
            available.append(item)
        return available

    def start_exam(self, user_id: int, exam_id: int) -> Dict[str, Any]:
        """Start an attempt or resume the student's existing active attempt."""
        self._validate_user_id(user_id)
        self._validate_id(exam_id, "exam_id")
        student_id = self._student_id(user_id)
        exam = self._get_exam(exam_id)
        now = self._now()
        self._require_published(exam)
        self._require_schedule_open(exam, now)
        self._require_positive_duration(exam)

        active = self.attempts.get_in_progress_attempt(student_id, exam_id)
        if active:
            if self._deadline(exam, active) <= now:
                active = self.attempts.update_attempt_status(
                    active["attempt_id"], EXPIRED, submit_time=now
                )
                raise ExamServiceError(
                    "The time for this exam has expired.", "EXAM_TIME_EXPIRED", 409
                )
            return self._build_attempt_payload(exam, active, now)

        attempt = self.attempts.create_attempt(student_id, exam_id, start_time=now)
        return self._build_attempt_payload(exam, attempt, now)

    def get_attempt(self, user_id: int, attempt_id: int) -> Dict[str, Any]:
        """Reload an attempt (e.g. after refresh/re-login) and its saved answers."""
        self._validate_user_id(user_id)
        self._validate_id(attempt_id, "attempt_id")
        student_id = self._student_id(user_id)
        attempt = self.attempts.get_attempt_by_id(attempt_id)
        self._require_attempt_owner(attempt, student_id)
        exam = self._get_exam(int(attempt["exam_id"]))
        now = self._now()
        if str(attempt.get("status", "")).upper() == IN_PROGRESS:
            if self._deadline(exam, attempt) <= now:
                attempt = self.attempts.update_attempt_status(
                    attempt_id, EXPIRED, submit_time=now
                ) or {**attempt, "status": EXPIRED, "submit_time": now}
        return self._build_attempt_payload(exam, attempt, now)

    def save_answer(
        self,
        user_id: int,
        attempt_id: int,
        question_id: int,
        selected_answer_id: Optional[int] = None,
        answer_content: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Save/replace one answer, designed to be called by the AJAX endpoint."""
        self._validate_user_id(user_id)
        self._validate_id(attempt_id, "attempt_id")
        self._validate_id(question_id, "question_id")
        student_id = self._student_id(user_id)
        attempt = self.attempts.get_attempt_by_id(attempt_id)
        self._require_attempt_owner(attempt, student_id)
        self._require_attempt_in_progress(attempt)
        exam = self._get_exam(int(attempt["exam_id"]))
        now = self._now()
        if self._deadline(exam, attempt) <= now:
            self.attempts.update_attempt_status(attempt_id, EXPIRED, submit_time=now)
            raise ExamServiceError(
                "Time is up. The exam was automatically submitted.",
                "EXAM_TIME_EXPIRED", 409,
            )

        if not self.attempts.is_question_in_attempt(attempt_id, question_id):
            raise ExamServiceError(
                "This question does not belong to the current exam.",
                "QUESTION_NOT_IN_EXAM", 404,
            )

        question = self._get_question(exam, question_id)
        question_type = str(question.get("question_type", "MULTIPLE_CHOICE")).upper()
        if selected_answer_id is not None:
            self._validate_id(selected_answer_id, "selected_answer_id")
            if question_type in {"WRITTEN", "ESSAY", "SHORT_ANSWER"}:
                raise ExamServiceError(
                    "Written questions cannot use a multiple-choice answer option.",
                    "INVALID_ANSWER_TYPE", 400,
                )
            if not self.attempts.is_answer_for_question(selected_answer_id, question_id):
                raise ExamServiceError(
                    "The selected answer does not belong to this question.",
                    "ANSWER_NOT_IN_QUESTION", 400,
                )
        elif answer_content is not None and question_type not in {
            "WRITTEN", "ESSAY", "SHORT_ANSWER"
        }:
            raise ExamServiceError(
                "Text answers are only accepted for written questions.",
                "INVALID_ANSWER_TYPE", 400,
            )

        saved = self.attempts.save_student_answer(
            attempt_id=attempt_id,
            question_id=question_id,
            selected_answer_id=selected_answer_id,
            answer_content=answer_content,
            submitted_at=now,
        )
        return {"success": True, "saved_at": now.isoformat(), "answer": self._to_api_value(saved)}

    def submit_exam(
        self,
        user_id: int,
        attempt_id: int,
        automatic: bool = False,
    ) -> Dict[str, Any]:
        """Submit manually or close as EXPIRED when the timer reaches zero.

        Grading is intentionally not performed here; it belongs to Khoa's
        grading_service.py and consumes the closed Exam_Attempts row.
        """
        self._validate_user_id(user_id)
        self._validate_id(attempt_id, "attempt_id")
        student_id = self._student_id(user_id)
        attempt = self.attempts.get_attempt_by_id(attempt_id)
        self._require_attempt_owner(attempt, student_id)

        status = str(attempt.get("status", "")).upper()
        if status != IN_PROGRESS:
            return {
                "success": True,
                "already_submitted": True,
                "attempt": attempt,
                "status": status,
            }

        exam = self._get_exam(int(attempt["exam_id"]))
        now = self._now()
        expired = automatic or self._deadline(exam, attempt) <= now
        final_status = EXPIRED if expired else SUBMITTED
        updated = self.attempts.update_attempt_status(
            attempt_id, final_status, submit_time=now
        ) or {**attempt, "status": final_status, "submit_time": now}
        return {
            "success": True,
            "already_submitted": False,
            "status": final_status,
            "attempt": updated,
            "submitted_at": now.isoformat(),
        }

    # ---------- Private validation / mapping helpers ----------

    def _now(self) -> datetime:
        value = self.clock()
        if not isinstance(value, datetime):
            raise TypeError("clock must return datetime")
        return self._normalize_datetime(value)

    @staticmethod
    def _normalize_datetime(value: Any) -> datetime:
        if isinstance(value, str):
            text = value.strip().replace("Z", "+00:00")
            try:
                value = datetime.fromisoformat(text)
            except ValueError as exc:
                raise ExamServiceError("Invalid date/time value from repository.", "INVALID_DATETIME", 500) from exc
        if not isinstance(value, datetime):
            raise ExamServiceError("Required date/time is missing from repository.", "INVALID_DATETIME", 500)
        # MySQL DATETIME is timezone-naive in the provided ERD. Keep comparison
        # consistent with the server's local clock rather than mixing aware/naive values.
        return value.replace(tzinfo=None) if value.tzinfo is not None else value

    @staticmethod
    def _validate_user_id(user_id: int) -> None:
        ExamService._validate_id(user_id, "user_id")

    @staticmethod
    def _validate_id(value: Any, label: str) -> None:
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ExamServiceError(f"{label} must be a positive integer.", "INVALID_ID", 400)

    @staticmethod
    def _is_published(exam: Dict[str, Any]) -> bool:
        return str(exam.get("status", "")).strip().casefold() == PUBLISHED.casefold()

    def _require_published(self, exam: Dict[str, Any]) -> None:
        if not self._is_published(exam):
            raise ExamServiceError(
                "This exam has not been published by the teacher.", "EXAM_NOT_PUBLISHED", 403
            )

    def _within_schedule(self, exam: Dict[str, Any], now: datetime) -> bool:
        start = self._normalize_datetime(exam.get("start_time"))
        end = self._normalize_datetime(exam.get("end_time"))
        return start <= now <= end

    def _require_schedule_open(self, exam: Dict[str, Any], now: datetime) -> None:
        start = self._normalize_datetime(exam.get("start_time"))
        end = self._normalize_datetime(exam.get("end_time"))
        if now < start:
            raise ExamServiceError("This exam has not started yet.", "EXAM_NOT_STARTED", 409)
        if now > end:
            raise ExamServiceError("The exam schedule has ended.", "EXAM_SCHEDULE_ENDED", 409)

    @staticmethod
    def _require_positive_duration(exam: Dict[str, Any]) -> None:
        try:
            duration = int(exam.get("duration"))
        except (TypeError, ValueError):
            duration = 0
        if duration <= 0:
            raise ExamServiceError("The exam duration is not configured.", "INVALID_EXAM_DURATION", 500)

    def _student_id(self, user_id: int) -> int:
        student_id = self.attempts.get_student_id_by_user_id(user_id)
        if student_id is None:
            raise ExamServiceError(
                "The current account is not linked to a student profile.",
                "STUDENT_PROFILE_NOT_FOUND", 403,
            )
        return int(student_id)

    def _get_exam(self, exam_id: int) -> Dict[str, Any]:
        method = getattr(self.exams, "get_exam_by_id", None)
        if not callable(method):
            raise ExamServiceError(
                "Exam repository must implement get_exam_by_id(exam_id).",
                "EXAM_REPOSITORY_CONTRACT", 500,
            )
        exam = method(exam_id)
        if not exam:
            raise ExamServiceError("Exam was not found.", "EXAM_NOT_FOUND", 404)
        return exam

    @staticmethod
    def _require_attempt_owner(attempt: Optional[Dict[str, Any]], student_id: int) -> None:
        if not attempt:
            raise ExamServiceError("Exam attempt was not found.", "ATTEMPT_NOT_FOUND", 404)
        if int(attempt.get("student_id", -1)) != student_id:
            raise ExamServiceError(
                "You are not allowed to access another student's attempt.",
                "ATTEMPT_FORBIDDEN", 403,
            )

    @staticmethod
    def _require_attempt_in_progress(attempt: Dict[str, Any]) -> None:
        if str(attempt.get("status", "")).upper() != IN_PROGRESS:
            raise ExamServiceError(
                "This exam attempt has already been submitted.", "ATTEMPT_CLOSED", 409
            )

    def _deadline(self, exam: Dict[str, Any], attempt: Dict[str, Any]) -> datetime:
        start = self._normalize_datetime(attempt.get("start_time"))
        duration = int(exam["duration"])
        duration_deadline = start + timedelta(minutes=duration)
        scheduled_end = self._normalize_datetime(exam.get("end_time"))
        return min(duration_deadline, scheduled_end)

    def _get_questions(self, exam_id: int) -> List[Dict[str, Any]]:
        method = getattr(self.exams, "get_questions_by_exam", None)
        if not callable(method):
            raise ExamServiceError(
                "Exam repository must implement get_questions_by_exam(exam_id).",
                "EXAM_REPOSITORY_CONTRACT", 500,
            )
        return list(method(exam_id) or [])

    def _get_question(self, exam: Dict[str, Any], question_id: int) -> Dict[str, Any]:
        for question in self._get_questions(int(exam["exam_id"])):
            if int(question.get("question_id", -1)) == question_id:
                return question
        raise ExamServiceError("Question was not found in this exam.", "QUESTION_NOT_IN_EXAM", 404)

    def _build_attempt_payload(
        self,
        exam: Dict[str, Any],
        attempt: Dict[str, Any],
        now: datetime,
    ) -> Dict[str, Any]:
        status = str(attempt.get("status", "")).upper()
        if status == IN_PROGRESS and self._deadline(exam, attempt) <= now:
            attempt = self.attempts.update_attempt_status(
                int(attempt["attempt_id"]), EXPIRED, submit_time=now
            ) or {**attempt, "status": EXPIRED, "submit_time": now}
            status = EXPIRED

        questions = self._get_questions(int(exam["exam_id"]))
        public_questions = [self._hide_correct_answers(question) for question in questions]
        answers = self.attempts.get_answers_by_attempt(int(attempt["attempt_id"]))
        remaining = 0
        if status == IN_PROGRESS:
            remaining = max(0, int((self._deadline(exam, attempt) - now).total_seconds()))

        return {
            "success": True,
            "exam": self._public_exam_fields(exam),
            "attempt": self._to_api_value(deepcopy(attempt)),
            "questions": self._to_api_value(public_questions),
            "saved_answers": self._to_api_value(answers),
            "remaining_seconds": remaining,
            "status": status,
        }

    @staticmethod
    def _hide_correct_answers(question: Dict[str, Any]) -> Dict[str, Any]:
        safe_question = deepcopy(question)
        safe_question.pop("correct_answer", None)
        safe_question.pop("correct_answer_id", None)
        safe_question.pop("answer_key", None)
        answers = safe_question.get("answers")
        if isinstance(answers, list):
            safe_question["answers"] = [
                {key: value for key, value in answer.items() if key not in {"is_correct", "correct"}}
                if isinstance(answer, dict) else answer
                for answer in answers
            ]
        return safe_question

    @staticmethod
    def _public_exam_fields(exam: Dict[str, Any]) -> Dict[str, Any]:
        allowed = ("exam_id", "title", "start_time", "end_time", "duration", "rules", "status")
        return ExamService._to_api_value({key: exam[key] for key in allowed if key in exam})

    @staticmethod
    def _to_api_value(value: Any) -> Any:
        """Convert DB-native values (datetime/Decimal) to JSON-safe primitives."""
        if isinstance(value, datetime):
            return value.isoformat(sep=" ")
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, dict):
            return {key: ExamService._to_api_value(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [ExamService._to_api_value(item) for item in value]
        return value


# Small functional wrappers make route integration straightforward without
# requiring each route to know the service class internals.
def create_exam_service(exam_repository: Any, attempt_repository: Any = None, clock: Any = None) -> ExamService:
    return ExamService(exam_repository, attempt_repository=attempt_repository, clock=clock)
