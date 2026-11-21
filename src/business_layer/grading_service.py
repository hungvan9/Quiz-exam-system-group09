"""Business logic for automated exam grading and result breakdown.

Owner: Nguyễn Đăng Khoa (Backend Grading & QA Lead).
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from src.data_layer import result_dao


OPTION_LABELS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class GradingService:
    """Service responsible for scoring submitted attempts and building result reports."""

    def __init__(self, dao: Any = result_dao):
        self.dao = dao

    @staticmethod
    def calculate_letter_grade(score_on_10: float) -> str:
        """Convert a 10-point score into a standard university letter grade."""
        if score_on_10 >= 8.5:
            return "A"
        if score_on_10 >= 7.0:
            return "B"
        if score_on_10 >= 5.5:
            return "C"
        if score_on_10 >= 4.0:
            return "D"
        return "F"

    def grade_attempt(self, attempt_id: int) -> Dict[str, Any]:
        """Auto-grade an exam attempt, persist to `results`, and return detailed breakdown."""
        bundle = self.dao.get_grading_bundle(attempt_id)
        if not bundle:
            raise ValueError(f"Exam attempt #{attempt_id} does not exist.")

        attempt = bundle["attempt"]
        questions = bundle["questions"]
        answers = bundle["answers"]
        student_answers = bundle["student_answers"]

        options_by_q: Dict[int, List[Dict[str, Any]]] = {}
        for ans in answers:
            qid = int(ans["question_id"])
            options_by_q.setdefault(qid, []).append(ans)

        student_ans_by_q: Dict[int, Dict[str, Any]] = {
            int(sa["question_id"]): sa for sa in student_answers
        }

        correct_count = 0
        incorrect_count = 0
        blank_count = 0
        earned_marks = 0.0
        max_possible_marks = 0.0
        has_written = False
        details: List[Dict[str, Any]] = []

        for idx, q in enumerate(questions, start=1):
            qid = int(q["question_id"])
            q_marks = float(q.get("marks") or 0.0)
            q_type = str(q.get("question_type") or "MULTIPLE_CHOICE").upper()
            max_possible_marks += q_marks

            q_options = options_by_q.get(qid, [])
            labeled_options = []
            correct_label = "-"
            correct_text = ""
            correct_answer_id: Optional[int] = None

            for opt_idx, opt in enumerate(q_options):
                label = OPTION_LABELS[opt_idx] if opt_idx < len(OPTION_LABELS) else str(opt_idx + 1)
                labeled_options.append((label, opt))
                if bool(opt.get("is_correct")):
                    correct_label = label
                    correct_text = str(opt.get("content") or "")
                    correct_answer_id = int(opt["answer_id"])

            sa = student_ans_by_q.get(qid)
            selected_id = sa.get("selected_answer_id") if sa else None
            written_text = (sa.get("answer_content") or "").strip() if sa else ""

            your_label = "-"
            your_text = ""
            is_correct = False
            is_blank = False
            marks_earned_q = 0.0

            if q_type == "WRITTEN":
                has_written = True
                if not written_text:
                    blank_count += 1
                    is_blank = True
                else:
                    your_label = "Written"
                    your_text = written_text
            else:
                if selected_id is None:
                    blank_count += 1
                    is_blank = True
                else:
                    selected_id_int = int(selected_id)
                    for label, opt in labeled_options:
                        if int(opt["answer_id"]) == selected_id_int:
                            your_label = label
                            your_text = str(opt.get("content") or "")
                            break

                    if correct_answer_id is not None and selected_id_int == correct_answer_id:
                        correct_count += 1
                        is_correct = True
                        marks_earned_q = q_marks
                        earned_marks += q_marks
                    else:
                        incorrect_count += 1

            details.append(
                {
                    "question_no": idx,
                    "question_id": qid,
                    "question_content": q.get("content", ""),
                    "your_answer": your_label,
                    "your_answer_text": your_text,
                    "correct_answer": correct_label,
                    "correct_answer_text": correct_text,
                    "is_correct": is_correct,
                    "is_blank": is_blank,
                    "marks_earned": round(marks_earned_q, 2),
                    "max_marks": round(q_marks, 2),
                }
            )

        if max_possible_marks > 0:
            score_on_10 = round((earned_marks / max_possible_marks) * 10.0, 2)
        else:
            score_on_10 = 0.0

        grade = self.calculate_letter_grade(score_on_10)
        result_status = "PENDING" if has_written else "GRADED"

        saved = self.dao.save_result(
            attempt_id=attempt_id,
            score=score_on_10,
            grade=grade,
            status=result_status,
        )

        duration = int(attempt.get("duration") or 0)
        start_time = attempt.get("start_time")
        submit_time = attempt.get("submit_time")
        time_spent_minutes = 0
        if isinstance(start_time, datetime) and isinstance(submit_time, datetime):
            diff_minutes = int(round((submit_time - start_time).total_seconds() / 60.0))
            time_spent_minutes = max(1, min(diff_minutes, duration)) if duration > 0 else max(1, diff_minutes)

        start_time_str = (
            start_time.strftime("%d/%m/%Y %H:%M")
            if isinstance(start_time, datetime)
            else str(start_time or "")
        )

        return {
            "result_id": saved.get("result_id"),
            "attempt_id": attempt_id,
            "exam_id": attempt.get("exam_id"),
            "exam_title": attempt.get("exam_title", "Exam"),
            "duration": duration,
            "time_spent_minutes": time_spent_minutes,
            "start_time_str": start_time_str,
            "score": score_on_10,
            "grade": grade,
            "status": result_status,
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "blank_count": blank_count,
            "total_questions": len(questions),
            "details": details,
        }

    def get_or_grade_result(self, attempt_id: int) -> Optional[Dict[str, Any]]:
        """Return full graded result breakdown for an attempt, or None if attempt does not exist."""
        try:
            return self.grade_attempt(attempt_id)
        except ValueError:
            return None