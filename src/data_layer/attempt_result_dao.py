"""DAO for student exam attempts and saved answers.

Owner: Nguyễn Thành Vinh (ExamAttempts / StudentAnswers portion).
Only SQL persistence lives here; business rules are implemented by ExamService.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Dict, Optional
from src.data_layer.db_connection import DatabaseConnection


def _connection():
    return DatabaseConnection.get_connection()


@contextmanager
def _cursor(dictionary: bool = True):
    connection = _connection()
    cursor = connection.cursor(dictionary=dictionary)
    try:
        yield connection, cursor
    except Exception:
        try:
            connection.rollback()
        finally:
            raise
    finally:
        try:
            cursor.close()
        finally:
            connection.close()


def _row(cursor) -> Optional[Dict[str, Any]]:
    row = cursor.fetchone()
    return dict(row) if row is not None else None


def get_student_id_by_user_id(user_id: int) -> Optional[int]:
    with _cursor() as (_, cursor):
        cursor.execute("SELECT student_id FROM students WHERE student_id = %s", (user_id,))
        row = _row(cursor)
        return int(row["student_id"]) if row else None


def create_attempt(student_id: int, exam_id: int, start_time=None) -> Dict[str, Any]:
    with _cursor() as (connection, cursor):
        cursor.execute(
            """INSERT INTO exam_attempts (student_id, exam_id, start_time, status)
               VALUES (%s, %s, %s, 'IN_PROGRESS')""",
            (student_id, exam_id, start_time),
        )
        attempt_id = cursor.lastrowid
        connection.commit()
        cursor.execute(
            """SELECT attempt_id, student_id, exam_id, start_time, submit_time, status
               FROM exam_attempts WHERE attempt_id = %s""",
            (attempt_id,),
        )
        return _row(cursor) or {
            "attempt_id": attempt_id, "student_id": student_id, "exam_id": exam_id,
            "start_time": start_time, "submit_time": None, "status": "IN_PROGRESS",
        }


def get_in_progress_attempt(student_id: int, exam_id: int) -> Optional[Dict[str, Any]]:
    with _cursor() as (_, cursor):
        cursor.execute(
            """SELECT attempt_id, student_id, exam_id, start_time, submit_time, status
               FROM exam_attempts
               WHERE student_id = %s AND exam_id = %s AND status = 'IN_PROGRESS'
               ORDER BY attempt_id DESC LIMIT 1""",
            (student_id, exam_id),
        )
        return _row(cursor)


def get_attempt_by_id(attempt_id: int) -> Optional[Dict[str, Any]]:
    with _cursor() as (_, cursor):
        cursor.execute(
            """SELECT attempt_id, student_id, exam_id, start_time, submit_time, status
               FROM exam_attempts WHERE attempt_id = %s""",
            (attempt_id,),
        )
        return _row(cursor)


def update_attempt_status(attempt_id: int, status: str, submit_time=None) -> Optional[Dict[str, Any]]:
    allowed = {"IN_PROGRESS", "SUBMITTED", "EXPIRED"}
    normalized = str(status).upper()
    if normalized not in allowed:
        raise ValueError(f"Unsupported attempt status: {status}")
    with _cursor() as (connection, cursor):
        cursor.execute(
            """UPDATE exam_attempts SET status = %s, submit_time = %s
               WHERE attempt_id = %s""",
            (normalized, submit_time, attempt_id),
        )
        connection.commit()
        cursor.execute(
            """SELECT attempt_id, student_id, exam_id, start_time, submit_time, status
               FROM exam_attempts WHERE attempt_id = %s""",
            (attempt_id,),
        )
        return _row(cursor)


def is_question_in_attempt(attempt_id: int, question_id: int) -> bool:
    with _cursor() as (_, cursor):
        cursor.execute(
            """SELECT 1 FROM exam_attempts ea
               JOIN questions q ON q.exam_id = ea.exam_id
               WHERE ea.attempt_id = %s AND q.question_id = %s LIMIT 1""",
            (attempt_id, question_id),
        )
        return cursor.fetchone() is not None


def is_answer_for_question(answer_id: int, question_id: int) -> bool:
    with _cursor() as (_, cursor):
        cursor.execute(
            "SELECT 1 FROM answers WHERE answer_id = %s AND question_id = %s LIMIT 1",
            (answer_id, question_id),
        )
        return cursor.fetchone() is not None


def save_student_answer(
    attempt_id: int,
    question_id: int,
    selected_answer_id: Optional[int] = None,
    answer_content: Optional[str] = None,
    submitted_at=None,
) -> Dict[str, Any]:
    """Insert or update the student's answer for one question (AJAX upsert)."""
    with _cursor() as (connection, cursor):
        cursor.execute(
            """SELECT student_answer_id FROM student_answers
               WHERE attempt_id = %s AND question_id = %s LIMIT 1""",
            (attempt_id, question_id),
        )
        existing = _row(cursor)
        if existing:
            cursor.execute(
                """UPDATE student_answers
                   SET selected_answer_id = %s, answer_content = %s, submitted_at = %s
                   WHERE student_answer_id = %s""",
                (selected_answer_id, answer_content, submitted_at, existing["student_answer_id"]),
            )
            answer_id = existing["student_answer_id"]
        else:
            cursor.execute(
                """INSERT INTO student_answers
                   (attempt_id, question_id, selected_answer_id, answer_content, submitted_at)
                   VALUES (%s, %s, %s, %s, %s)""",
                (attempt_id, question_id, selected_answer_id, answer_content, submitted_at),
            )
            answer_id = cursor.lastrowid
        connection.commit()
        cursor.execute(
            """SELECT student_answer_id, attempt_id, question_id,
                      selected_answer_id, answer_content, submitted_at
               FROM student_answers WHERE student_answer_id = %s""",
            (answer_id,),
        )
        return _row(cursor) or {
            "student_answer_id": answer_id, "attempt_id": attempt_id,
            "question_id": question_id, "selected_answer_id": selected_answer_id,
            "answer_content": answer_content, "submitted_at": submitted_at,
        }


def get_answers_by_attempt(attempt_id: int):
    with _cursor() as (_, cursor):
        cursor.execute(
            """SELECT student_answer_id, attempt_id, question_id,
                      selected_answer_id, answer_content, submitted_at
               FROM student_answers WHERE attempt_id = %s
               ORDER BY student_answer_id""",
            (attempt_id,),
        )
        return [dict(row) for row in cursor.fetchall()]