"""Comprehensive QA & Automated Grading Test Suite.

Owner: Nguyễn Đăng Khoa (Backend Grading & QA Lead).
"""
from datetime import datetime, timedelta
import pytest
from src.app import app
from src.business_layer.grading_service import GradingService
from src.data_layer.db_connection import DatabaseConnection


class FakeGradingDAO:
    """In-memory DAO stub for deterministic unit testing of GradingService."""

    def __init__(self, bundle):
        self.bundle = bundle
        self.saved_records = []

    def get_grading_bundle(self, attempt_id: int):
        if not self.bundle or self.bundle["attempt"]["attempt_id"] != attempt_id:
            return None
        return self.bundle

    def save_result(self, attempt_id: int, score: float, grade: str, status: str = "GRADED"):
        record = {
            "result_id": len(self.saved_records) + 1,
            "attempt_id": attempt_id,
            "score": score,
            "grade": grade,
            "status": status,
        }
        self.saved_records.append(record)
        return record


def _sample_bundle(selected_map):
    start = datetime(2026, 11, 21, 9, 0, 0)
    submit = start + timedelta(minutes=22)
    return {
        "attempt": {
            "attempt_id": 101,
            "student_id": 3,
            "exam_id": 1,
            "start_time": start,
            "submit_time": submit,
            "attempt_status": "SUBMITTED",
            "exam_title": "Software Engineering Midterm",
            "duration": 30,
            "total_marks": 4.0,
        },
        "questions": [
            {"question_id": 1, "exam_id": 1, "content": "Q1", "question_type": "MULTIPLE_CHOICE", "marks": 1.0},
            {"question_id": 2, "exam_id": 1, "content": "Q2", "question_type": "MULTIPLE_CHOICE", "marks": 1.0},
            {"question_id": 3, "exam_id": 1, "content": "Q3", "question_type": "MULTIPLE_CHOICE", "marks": 2.0},
        ],
        "answers": [
            {"answer_id": 11, "question_id": 1, "content": "Opt A", "is_correct": 1},
            {"answer_id": 12, "question_id": 1, "content": "Opt B", "is_correct": 0},
            {"answer_id": 21, "question_id": 2, "content": "Opt A", "is_correct": 0},
            {"answer_id": 22, "question_id": 2, "content": "Opt B", "is_correct": 1},
            {"answer_id": 31, "question_id": 3, "content": "Opt A", "is_correct": 0},
            {"answer_id": 32, "question_id": 3, "content": "Opt B", "is_correct": 1},
        ],
        "student_answers": [
            {"student_answer_id": idx, "attempt_id": 101, "question_id": qid, "selected_answer_id": aid, "answer_content": None}
            for idx, (qid, aid) in enumerate(selected_map.items(), start=1)
        ],
    }


# ==================== 1. UNIT TESTS: AUTOMATED GRADING ====================
def test_grade_attempt_all_correct():
    dao = FakeGradingDAO(_sample_bundle({1: 11, 2: 22, 3: 32}))
    service = GradingService(dao=dao)

    res = service.grade_attempt(101)

    assert res["score"] == 10.0
    assert res["grade"] == "A"
    assert res["correct_count"] == 3
    assert res["incorrect_count"] == 0
    assert res["blank_count"] == 0
    assert res["time_spent_minutes"] == 22
    assert len(dao.saved_records) == 1


def test_grade_attempt_partial_weighted_and_blank():
    # Q1 (1pt) correct, Q2 (1pt) wrong, Q3 (2pt) blank -> 1/4 = 2.5/10 (F)
    dao = FakeGradingDAO(_sample_bundle({1: 11, 2: 21}))
    service = GradingService(dao=dao)

    res = service.grade_attempt(101)

    assert res["score"] == 2.5
    assert res["grade"] == "F"
    assert res["correct_count"] == 1
    assert res["incorrect_count"] == 1
    assert res["blank_count"] == 1
    assert res["details"][0]["your_answer"] == "A"
    assert res["details"][0]["is_correct"] is True
    assert res["details"][1]["your_answer"] == "A"
    assert res["details"][1]["correct_answer"] == "B"
    assert res["details"][1]["is_correct"] is False
    assert res["details"][2]["your_answer"] == "-"
    assert res["details"][2]["is_blank"] is True


def test_grade_attempt_all_blank():
    dao = FakeGradingDAO(_sample_bundle({}))
    service = GradingService(dao=dao)

    res = service.grade_attempt(101)

    assert res["score"] == 0.0
    assert res["grade"] == "F"
    assert res["blank_count"] == 3


def test_grade_attempt_missing_id_raises_value_error():
    dao = FakeGradingDAO(None)
    service = GradingService(dao=dao)

    with pytest.raises(ValueError):
        service.grade_attempt(9999)


@pytest.mark.parametrize(
    "score,expected_grade",
    [
        (9.5, "A"),
        (8.5, "A"),
        (7.2, "B"),
        (7.0, "B"),
        (6.0, "C"),
        (5.5, "C"),
        (4.5, "D"),
        (4.0, "D"),
        (3.99, "F"),
        (0.0, "F"),
    ],
)
def test_letter_grade_scale_boundaries(score, expected_grade):
    assert GradingService.calculate_letter_grade(score) == expected_grade


# ==================== 2. QA SECURITY & RBAC ROUTE TESTS ====================
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_unauthenticated_access_redirects_to_login(client):
    for protected_url in [
        "/admin/dashboard",
        "/teacher/dashboard",
        "/student/dashboard",
        "/student/result/1",
    ]:
        resp = client.get(protected_url)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]


def test_rbac_prevents_cross_role_dashboard_access(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 3
        sess["role"] = "STUDENT"

    assert client.get("/admin/dashboard").status_code == 302
    assert client.get("/teacher/dashboard").status_code == 302


def test_grade_api_unauthorized_and_not_found(client):
    # Unauthenticated -> 401
    resp_unauth = client.post("/api/attempts/1/grade")
    assert resp_unauth.status_code == 401

    # Authenticated with non-existent attempt -> 404
    with client.session_transaction() as sess:
        sess["user_id"] = 3
        sess["role"] = "STUDENT"
    resp_404 = client.post("/api/attempts/999999/grade")
    assert resp_404.status_code == 404


# ==================== 3. INTEGRATION TEST WITH MYSQL ====================
def test_mysql_end_to_end_grading_persistence():
    try:
        conn = DatabaseConnection.get_connection()
    except Exception:
        pytest.skip("MySQL database not reachable in current environment")

    cursor = conn.cursor(dictionary=True)
    attempt_id = None
    try:
        cursor.execute("SELECT student_id FROM students LIMIT 1")
        student = cursor.fetchone()
        cursor.execute("SELECT exam_id FROM exams LIMIT 1")
        exam = cursor.fetchone()
        if not student or not exam:
            pytest.skip("Seed student or exam missing")

        cursor.execute(
            """
            INSERT INTO exam_attempts (student_id, exam_id, start_time, submit_time, status)
            VALUES (%s, %s, NOW() - INTERVAL 10 MINUTE, NOW(), 'SUBMITTED')
            """,
            (student["student_id"], exam["exam_id"]),
        )
        attempt_id = cursor.lastrowid
        conn.commit()

        service = GradingService()
        graded = service.grade_attempt(attempt_id)

        assert graded["attempt_id"] == attempt_id
        assert 0.0 <= graded["score"] <= 10.0
        assert graded["grade"] in {"A", "B", "C", "D", "F"}
    finally:
        if attempt_id is not None:
            cursor.execute("DELETE FROM exam_attempts WHERE attempt_id = %s", (attempt_id,))
            conn.commit()
        cursor.close()
        conn.close()