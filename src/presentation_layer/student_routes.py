"""Student exam HTTP routes.

The blueprint is deliberately independent from app.py (owned by the Tech Lead).
The application factory should call configure_exam_routes(exam_repository) and
register student_exam_bp. Authentication is read from Flask session only.
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request, session

from ..business_layer.exam_service import ExamService, ExamServiceError

student_exam_bp = Blueprint("student_exam", __name__, url_prefix="/student/exams")
_exam_service = None


def configure_exam_routes(exam_repository, attempt_repository=None, clock=None):
    """Inject Long's exam repository and Vinh's attempt DAO."""
    global _exam_service
    _exam_service = ExamService(
        exam_repository,
        attempt_repository=attempt_repository,
        clock=clock,
    )
    return student_exam_bp


def _service():
    if _exam_service is None:
        raise ExamServiceError(
            "Student exam service has not been configured by the application.",
            "EXAM_SERVICE_NOT_CONFIGURED", 500,
        )
    return _exam_service


def _student_user():
    user_id = session.get("user_id")
    role = str(session.get("role", "")).upper()
    if not user_id:
        return None, (jsonify({"success": False, "error": "AUTH_REQUIRED",
                               "message": "Please log in first."}), 401)
    if role and role != "STUDENT":
        return None, (jsonify({"success": False, "error": "FORBIDDEN",
                               "message": "Only student accounts can take exams."}), 403)
    return int(user_id), None


def _error_response(error):
    if isinstance(error, ExamServiceError):
        return jsonify(error.to_dict()), error.http_status
    return jsonify({"success": False, "error": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred."}), 500


@student_exam_bp.get("")
@student_exam_bp.get("/")
def list_available_exams():
    user_id, error = _student_user()
    if error:
        return error
    try:
        return jsonify({"success": True,
                        "exams": _service().list_available_exams(user_id)})
    except Exception as exc:
        return _error_response(exc)


@student_exam_bp.post("/<int:exam_id>/start")
def start_exam(exam_id):
    user_id, error = _student_user()
    if error:
        return error
    try:
        return jsonify(_service().start_exam(user_id, exam_id)), 201
    except Exception as exc:
        return _error_response(exc)


@student_exam_bp.get("/attempts/<int:attempt_id>")
def get_attempt(attempt_id):
    user_id, error = _student_user()
    if error:
        return error
    try:
        return jsonify(_service().get_attempt(user_id, attempt_id))
    except Exception as exc:
        return _error_response(exc)


@student_exam_bp.put("/attempts/<int:attempt_id>/answers")
def save_answer(attempt_id):
    user_id, error = _student_user()
    if error:
        return error
    payload = request.get_json(silent=True) or {}
    question_id = payload.get("question_id")
    if question_id is None:
        return jsonify({"success": False, "error": "MISSING_QUESTION_ID",
                        "message": "question_id is required."}), 400
    try:
        result = _service().save_answer(
            user_id=user_id,
            attempt_id=attempt_id,
            question_id=question_id,
            selected_answer_id=payload.get("selected_answer_id"),
            answer_content=payload.get("answer_content"),
        )
        return jsonify(result)
    except Exception as exc:
        return _error_response(exc)


@student_exam_bp.post("/attempts/<int:attempt_id>/submit")
def submit_exam(attempt_id):
    user_id, error = _student_user()
    if error:
        return error
    payload = request.get_json(silent=True) or {}
    try:
        return jsonify(_service().submit_exam(
            user_id, attempt_id, automatic=bool(payload.get("automatic", False))
        ))
    except Exception as exc:
        return _error_response(exc)
