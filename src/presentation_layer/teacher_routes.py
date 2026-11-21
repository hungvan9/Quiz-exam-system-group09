"""JSON endpoints for the authenticated Teacher module."""
from functools import wraps
from flask import Blueprint, jsonify, request, session
from src.business_layer.teacher_service import TeacherService, TeacherServiceError

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")
teacher_service = TeacherService()


def teacher_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if session.get("role") != "TEACHER":
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


@teacher_bp.get("/syllabuses")
@teacher_required
def list_syllabuses():
    return _run(lambda: teacher_service.list_syllabuses(session["user_id"], request.args.get("subject_id")))


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


@teacher_bp.post("/exams")
@teacher_required
def create_exam():
    return _run(lambda: teacher_service.create_exam(session["user_id"], request.get_json(silent=True) or {}), 201)


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
