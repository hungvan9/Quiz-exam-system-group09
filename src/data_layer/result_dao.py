"""DAO for exam grading data retrieval and results persistence.

Owner: Nguyễn Đăng Khoa (Backend Grading & QA Lead).
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Dict, List, Optional
from src.data_layer.db_connection import DatabaseConnection


@contextmanager
def _cursor(dictionary: bool = True):
    connection = DatabaseConnection.get_connection()
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


def get_grading_bundle(attempt_id: int) -> Optional[Dict[str, Any]]:
    """Fetch attempt, exam metadata, questions, options, and student answers."""
    with _cursor() as (_, cursor):
        cursor.execute(
            """
            SELECT ea.attempt_id, ea.student_id, ea.exam_id,
                   ea.start_time, ea.submit_time, ea.status AS attempt_status,
                   e.title AS exam_title, e.duration, e.total_marks
            FROM exam_attempts ea
            JOIN exams e ON e.exam_id = ea.exam_id
            WHERE ea.attempt_id = %s
            """,
            (attempt_id,),
        )
        attempt = cursor.fetchone()
        if not attempt:
            return None

        exam_id = attempt["exam_id"]

        cursor.execute(
            """
            SELECT question_id, exam_id, content, question_type, marks
            FROM questions
            WHERE exam_id = %s
            ORDER BY question_id ASC
            """,
            (exam_id,),
        )
        questions = [dict(row) for row in cursor.fetchall()]

        question_ids = [q["question_id"] for q in questions]
        answers: List[Dict[str, Any]] = []
        if question_ids:
            placeholders = ", ".join(["%s"] * len(question_ids))
            cursor.execute(
                f"""
                SELECT answer_id, question_id, content, is_correct
                FROM answers
                WHERE question_id IN ({placeholders})
                ORDER BY question_id ASC, answer_id ASC
                """,
                tuple(question_ids),
            )
            answers = [dict(row) for row in cursor.fetchall()]

        cursor.execute(
            """
            SELECT student_answer_id, attempt_id, question_id,
                   selected_answer_id, answer_content, submitted_at
            FROM student_answers
            WHERE attempt_id = %s
            ORDER BY student_answer_id ASC
            """,
            (attempt_id,),
        )
        student_answers = [dict(row) for row in cursor.fetchall()]

        return {
            "attempt": dict(attempt),
            "questions": questions,
            "answers": answers,
            "student_answers": student_answers,
        }


def save_result(
    attempt_id: int,
    score: float,
    grade: str,
    status: str = "GRADED",
) -> Dict[str, Any]:
    """Insert or update a grading result row and mark attempt as SUBMITTED if still open."""
    with _cursor() as (connection, cursor):
        cursor.execute(
            """
            UPDATE exam_attempts
            SET status = 'SUBMITTED',
                submit_time = COALESCE(submit_time, NOW())
            WHERE attempt_id = %s AND status = 'IN_PROGRESS'
            """,
            (attempt_id,),
        )

        cursor.execute(
            """
            INSERT INTO results (attempt_id, score, grade, status)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                score = VALUES(score),
                grade = VALUES(grade),
                status = VALUES(status)
            """,
            (attempt_id, score, grade, status),
        )
        connection.commit()

        cursor.execute(
            """
            SELECT result_id, attempt_id, score, grade, status
            FROM results
            WHERE attempt_id = %s
            """,
            (attempt_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else {
            "attempt_id": attempt_id,
            "score": score,
            "grade": grade,
            "status": status,
        }


def get_result_by_attempt(attempt_id: int) -> Optional[Dict[str, Any]]:
    """Fetch persisted result record for a given attempt."""
    with _cursor() as (_, cursor):
        cursor.execute(
            """
            SELECT result_id, attempt_id, score, grade, status
            FROM results
            WHERE attempt_id = %s
            """,
            (attempt_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None