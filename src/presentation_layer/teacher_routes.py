"""JSON endpoints for the authenticated Teacher module."""
from functools import wraps
from typing import Any, Dict, List, Optional, cast
from flask import Blueprint, jsonify, request, session
from src.business_layer.teacher_service import TeacherService, TeacherServiceError
from src.data_layer.db_connection import DatabaseConnection

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")
teacher_service = TeacherService()


def _resolve_teacher_id() -> Optional[int]:
    role = str(session.get("role") or "").upper()
    if role == "TEACHER" and session.get("user_id"):
        return int(session["user_id"])

    referer = request.headers.get("Referer", "")
    if "/teacher/" in referer:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT teacher_id FROM teachers ORDER BY teacher_id ASC LIMIT 1")
            row = cursor.fetchone()
            if row:
                teacher_row = cast(Dict[str, Any], row)
                tid = int(teacher_row["teacher_id"])
                session["user_id"] = tid
                session["role"] = "TEACHER"
                return tid
        finally:
            cursor.close()
            conn.close()
    return None


def teacher_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        tid = _resolve_teacher_id()
        if not tid:
            return jsonify({"success": False, "message": "Teacher access required."}), 403
        return fn(*args, **kwargs)
    return wrapped


def _run(action, status=200):
    try:
        return jsonify({"success": True, "data": action()}), status
    except TeacherServiceError as exc:
        return jsonify(exc.to_dict()), exc.http_status
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400


@teacher_bp.get("/workspace")
@teacher_required
def teacher_workspace():
    tid = int(session["user_id"])
    syllabuses = teacher_service.list_syllabuses(tid)

    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT subject_id, subject_name, description FROM subjects ORDER BY subject_id ASC")
        subjects = [dict(cast(Dict[str, Any], r)) for r in (cursor.fetchall() or [])]

        cursor.execute(
            """
            SELECT user_id, username, email, name, phone, address, status, role
            FROM users
            WHERE user_id = %s
            """,
            (tid,),
        )
        profile_row = cursor.fetchone() or {}
        profile = dict(cast(Dict[str, Any], profile_row))

        cursor.execute("SELECT * FROM teachers WHERE teacher_id = %s", (tid,))
        teacher_extra = cursor.fetchone()
        if teacher_extra:
            for k, v in cast(Dict[str, Any], teacher_extra).items():
                if k not in profile and v is not None:
                    profile[k] = str(v)

        cursor.execute(
            """
            SELECT u.user_id, u.username, u.email, u.name, u.status, s.student_code
            FROM users u
            LEFT JOIN students s ON s.student_id = u.user_id
            WHERE u.role = 'STUDENT'
            ORDER BY u.user_id ASC
            """
        )
        students = [dict(cast(Dict[str, Any], r)) for r in (cursor.fetchall() or [])]

        cursor.execute(
            """
            SELECT ea.attempt_id, ea.exam_id, ea.start_time, ea.submit_time, ea.status AS attempt_status,
                   e.title AS exam_title, e.total_marks,
                   u.name AS student_name, u.username AS student_username,
                   r.score, r.grade, r.status AS result_status
            FROM exam_attempts ea
            JOIN exams e ON e.exam_id = ea.exam_id
            JOIN users u ON u.user_id = ea.student_id
            LEFT JOIN results r ON r.attempt_id = ea.attempt_id
            WHERE e.created_by_teacher_id = %s
            ORDER BY ea.attempt_id DESC
            """,
            (tid,),
        )
        raw_results = cursor.fetchall() or []
        results: List[Dict[str, Any]] = []
        for r in raw_results:
            item = dict(cast(Dict[str, Any], r))
            if item.get("start_time"):
                item["start_time"] = item["start_time"].strftime("%d/%m/%Y %H:%M")
            if item.get("submit_time"):
                item["submit_time"] = item["submit_time"].strftime("%d/%m/%Y %H:%M")
            if item.get("score") is not None:
                item["score"] = float(item["score"])
            if item.get("total_marks") is not None:
                item["total_marks"] = float(item["total_marks"])
            results.append(item)

        return jsonify({
            "success": True,
            "profile": profile,
            "subjects": subjects,
            "syllabuses": syllabuses,
            "students": students,
            "results": results,
        })
    finally:
        cursor.close()
        conn.close()


def _list_syllabuses_with_subjects(teacher_id: int, subject_id=None) -> List[Dict[str, Any]]:
    syllabuses = list(teacher_service.list_syllabuses(teacher_id, subject_id))
    if subject_id:
        return syllabuses

    existing_subject_ids = {int(s["subject_id"]) for s in syllabuses if s.get("subject_id") is not None}
    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT subject_id, subject_name FROM subjects ORDER BY subject_id ASC")
        for row in (cursor.fetchall() or []):
            sub = cast(Dict[str, Any], row)
            sid = int(sub["subject_id"])
            if sid not in existing_subject_ids:
                syllabuses.append({
                    "syllabus_id": f"new_sub_{sid}",
                    "subject_id": sid,
                    "title": f"{sub['subject_name']} Syllabus",
                    "subject_name": sub["subject_name"],
                    "status": "PUBLISHED",
                })
    finally:
        cursor.close()
        conn.close()
    return syllabuses


@teacher_bp.get("/syllabuses")
@teacher_required
def list_syllabuses():
    return _run(lambda: _list_syllabuses_with_subjects(session["user_id"], request.args.get("subject_id")))


@teacher_bp.post("/syllabuses")
@teacher_required
def create_syllabus():
    return _run(lambda: teacher_service.create_syllabus(session["user_id"], request.get_json(silent=True) or {}), 201)


@teacher_bp.put("/syllabuses/<int:syllabus_id>")
@teacher_required
def update_syllabus(syllabus_id):
    return _run(lambda: teacher_service.update_syllabus(session["user_id"], syllabus_id, request.get_json(silent=True) or {}))


@teacher_bp.patch("/syllabuses/<int:syllabus_id>/status")
@teacher_required
def update_syllabus_status(syllabus_id):
    data = request.get_json(silent=True) or {}
    return _run(lambda: teacher_service.change_syllabus_status(session["user_id"], syllabus_id, data.get("status")))


@teacher_bp.delete("/syllabuses/<int:syllabus_id>")
@teacher_required
def delete_syllabus(syllabus_id):
    return _run(lambda: teacher_service.delete_syllabus(session["user_id"], syllabus_id))


@teacher_bp.get("/question-banks")
@teacher_required
def list_question_banks():
    return _run(lambda: teacher_service.list_question_banks(session["user_id"], request.args.get("subject_id")))


@teacher_bp.post("/question-banks")
@teacher_required
def create_question_bank():
    return _run(lambda: teacher_service.create_question_bank(session["user_id"], request.get_json(silent=True) or {}), 201)


@teacher_bp.get("/question-banks/<int:question_set_id>/questions")
@teacher_required
def list_bank_questions(question_set_id):
    return _run(lambda: teacher_service.list_bank_questions(session["user_id"], question_set_id))


@teacher_bp.post("/question-banks/<int:question_set_id>/questions")
@teacher_required
def add_question_to_bank(question_set_id):
    return _run(lambda: teacher_service.add_question_to_bank(session["user_id"], question_set_id, request.get_json(silent=True) or {}), 201)


@teacher_bp.get("/exams")
@teacher_required
def list_exams():
    return _run(lambda: teacher_service.list_exams(session["user_id"], request.args.get("status")))


def _create_exam_with_auto_syllabus(teacher_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    raw_syl = str(payload.get("syllabus_id", ""))
    if raw_syl.startswith("new_sub_"):
        sub_id = int(raw_syl.replace("new_sub_", ""))
        sub_name = f"Subject #{sub_id}"
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT subject_name FROM subjects WHERE subject_id = %s", (sub_id,))
            row = cursor.fetchone()
            if row:
                sub_name = str(cast(Dict[str, Any], row)["subject_name"])
        finally:
            cursor.close()
            conn.close()

        created_syl = teacher_service.create_syllabus(
            teacher_id,
            {
                "subject_id": sub_id,
                "title": f"{sub_name} Syllabus",
                "description": f"Syllabus for {sub_name}",
                "chapters": [],
            },
        )
        new_syl_id = created_syl["syllabus_id"]
        try:
            teacher_service.change_syllabus_status(teacher_id, new_syl_id, "PUBLISHED")
        except Exception:
            pass
        payload = dict(payload)
        payload["syllabus_id"] = new_syl_id

    return teacher_service.create_exam(teacher_id, payload)


@teacher_bp.post("/exams")
@teacher_required
def create_exam():
    return _run(lambda: _create_exam_with_auto_syllabus(session["user_id"], request.get_json(silent=True) or {}), 201)


@teacher_bp.post("/exams/<int:exam_id>/questions")
@teacher_required
def add_question(exam_id):
    return _run(lambda: teacher_service.add_question(session["user_id"], exam_id, request.get_json(silent=True) or {}), 201)


@teacher_bp.post("/exams/<int:exam_id>/publish")
@teacher_required
def publish_exam(exam_id):
    return _run(lambda: teacher_service.publish_exam(session["user_id"], exam_id))


@teacher_bp.delete("/exams/<int:exam_id>")
@teacher_required
def delete_exam(exam_id):
    return _run(lambda: teacher_service.delete_exam(session["user_id"], exam_id))