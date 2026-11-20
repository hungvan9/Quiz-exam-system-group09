from datetime import datetime, timedelta
from unittest.mock import MagicMock
import pytest


class ExamProcessContract:
    """Kiểm thử nghiệp vụ luồng làm bài thi trực tuyến (Use Case 4.3.3)."""

    def __init__(self, attempt_dao):
        self.attempt_dao = attempt_dao

    def start_exam(self, student_id: int, exam: dict):
        if exam.get("status") != "PUBLISHED":
            raise ValueError("Exam is not available.")
        return self.attempt_dao.create_attempt(student_id=student_id, exam_id=exam["exam_id"])

    def auto_save_answer(self, attempt: dict, question_id: int, selected_answer_id: int):
        if attempt.get("status") != "IN_PROGRESS":
            raise ValueError("Cannot save answer for a submitted or expired attempt.")
        return self.attempt_dao.upsert_student_answer(
            attempt_id=attempt["attempt_id"],
            question_id=question_id,
            selected_answer_id=selected_answer_id,
        )

    def submit_exam(self, attempt: dict, duration_minutes: int, current_time: datetime):
        deadline = attempt["start_time"] + timedelta(minutes=duration_minutes)
        final_status = "EXPIRED" if current_time > deadline else "SUBMITTED"
        self.attempt_dao.complete_attempt(attempt["attempt_id"], current_time, final_status)
        return final_status


def test_start_published_exam_success():
    mock_dao = MagicMock()
    mock_dao.create_attempt.return_value = {"attempt_id": 101, "status": "IN_PROGRESS"}
    service = ExamProcessContract(mock_dao)

    attempt = service.start_exam(student_id=3, exam={"exam_id": 1, "status": "PUBLISHED"})
    assert attempt["attempt_id"] == 101
    assert attempt["status"] == "IN_PROGRESS"


def test_start_draft_exam_raises_error():
    mock_dao = MagicMock()
    service = ExamProcessContract(mock_dao)

    with pytest.raises(ValueError, match="Exam is not available."):
        service.start_exam(student_id=3, exam={"exam_id": 1, "status": "DRAFT"})


def test_auto_save_answer_during_active_exam():
    mock_dao = MagicMock()
    mock_dao.upsert_student_answer.return_value = True
    service = ExamProcessContract(mock_dao)

    saved = service.auto_save_answer(
        attempt={"attempt_id": 101, "status": "IN_PROGRESS"},
        question_id=1,
        selected_answer_id=2,
    )
    assert saved is True
    mock_dao.upsert_student_answer.assert_called_once_with(
        attempt_id=101, question_id=1, selected_answer_id=2
    )


def test_auto_save_after_submit_fails():
    mock_dao = MagicMock()
    service = ExamProcessContract(mock_dao)

    with pytest.raises(ValueError, match="Cannot save answer"):
        service.auto_save_answer(
            attempt={"attempt_id": 101, "status": "SUBMITTED"},
            question_id=1,
            selected_answer_id=2,
        )


def test_submit_exam_within_time_limit():
    mock_dao = MagicMock()
    service = ExamProcessContract(mock_dao)
    start = datetime(2026, 11, 20, 10, 0, 0)
    submit_at = datetime(2026, 11, 20, 10, 12, 0)

    status = service.submit_exam(
        attempt={"attempt_id": 101, "start_time": start, "status": "IN_PROGRESS"},
        duration_minutes=15,
        current_time=submit_at,
    )
    assert status == "SUBMITTED"


def test_auto_submit_when_time_expires():
    mock_dao = MagicMock()
    service = ExamProcessContract(mock_dao)
    start = datetime(2026, 11, 20, 10, 0, 0)
    expired_time = datetime(2026, 11, 20, 10, 16, 0)

    status = service.submit_exam(
        attempt={"attempt_id": 101, "start_time": start, "status": "IN_PROGRESS"},
        duration_minutes=15,
        current_time=expired_time,
    )
    assert status == "EXPIRED"