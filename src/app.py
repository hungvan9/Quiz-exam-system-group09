"""Main Flask entrypoint wiring Presentation, Business, and Data layers."""
import os
from datetime import timedelta
from typing import Any, Dict, List, cast
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from src.business_layer.auth_service import AuthService
from src.business_layer.exam_service import ExamService
from src.business_layer.grading_service import GradingService
from src.data_layer.db_connection import DatabaseConnection
from src.presentation_layer.admin_routes import admin_bp
from src.presentation_layer.teacher_routes import teacher_bp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "presentation_layer", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "presentation_layer", "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "quiz-exam-system-group09-secret")
app.permanent_session_lifetime = timedelta(days=30)

auth_service = AuthService()
exam_service = ExamService()
grading_service = GradingService()

app.register_blueprint(admin_bp)
app.register_blueprint(teacher_bp)


def _redirect_by_role(role: str):
    r = (role or "").upper()
    if r == "ADMIN":
        return redirect(url_for("admin_dashboard"))
    if r == "TEACHER":
        return redirect(url_for("teacher_dashboard"))
    return redirect(url_for("student_dashboard"))


@app.route("/")
def index():
    if "user_id" in session:
        return _redirect_by_role(session.get("role", ""))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    remember = request.form.get("remember") == "on"

    success, message, user = auth_service.login(username, password)
    if not success or not user:
        return render_template("login.html", error=message), 401

    session.permanent = remember
    session["user_id"] = user["user_id"]
    session["username"] = user["username"]
    session["name"] = user["name"]
    session["role"] = user["role"]
    return _redirect_by_role(user["role"])


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    success, message, _ = auth_service.register_student(name, username, email, password)
    if not success:
        return render_template("register.html", error=message), 400
    return render_template("login.html", success=message)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ==================== DASHBOARD PAGES ====================

@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("role") != "ADMIN":
        return redirect(url_for("login"))
    return render_template("admin.html")


@app.route("/teacher/dashboard")
def teacher_dashboard():
    if session.get("role") != "TEACHER":
        return redirect(url_for("login"))
    return render_template("teacher.html")


@app.route("/student/dashboard")
def student_dashboard():
    if session.get("role") != "STUDENT":
        return redirect(url_for("login"))
    active_tab = request.args.get("tab", "home")
    return render_template("student_dashboard.html", active_tab=active_tab)


# ==================== STUDENT EXAM & GRADING FLOW ====================

@app.route("/student/exams", methods=["GET"])
def student_available_exams():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    exams = exam_service.get_available_exams_for_student(session["user_id"])
    return jsonify({"success": True, "exams": exams}), 200


@app.route("/student/exam/<int:exam_id>")
def student_exam_page(exam_id: int):
    if session.get("role") != "STUDENT":
        return redirect(url_for("login"))
    return render_template("exam-interface.html", exam_id=exam_id)


@app.route("/api/student/exam/<int:exam_id>/start", methods=["POST"])
def api_student_start_exam(exam_id: int):
    if session.get("role") != "STUDENT":
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    try:
        data = exam_service.start_or_resume_exam(session["user_id"], exam_id)
        return jsonify({"success": True, **data}), 200
    except PermissionError as exc:
        return jsonify({"success": False, "message": str(exc)}), 403
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400


@app.route("/api/student/attempt/<int:attempt_id>/answer", methods=["POST"])
def api_student_save_answer(attempt_id: int):
    if session.get("role") != "STUDENT":
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    payload = request.get_json(silent=True) or {}
    question_id = payload.get("question_id")
    answer_id = payload.get("answer_id")
    if question_id is None:
        return jsonify({"success": False, "message": "question_id is required"}), 400
    try:
        saved = exam_service.save_answer(
            session["user_id"],
            attempt_id,
            int(question_id),
            int(answer_id) if answer_id is not None else None,
        )
        return jsonify({"success": True, "saved": saved}), 200
    except PermissionError as exc:
        return jsonify({"success": False, "message": str(exc)}), 403
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400


@app.route("/api/student/attempt/<int:attempt_id>/submit", methods=["POST"])
def api_student_submit_exam(attempt_id: int):
    if session.get("role") != "STUDENT":
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    try:
        result = grading_service.submit_and_grade_attempt(session["user_id"], attempt_id)
        return jsonify({
            "success": True,
            "result": result,
            "redirect_url": url_for("student_result_page", attempt_id=attempt_id),
        }), 200
    except PermissionError as exc:
        return jsonify({"success": False, "message": str(exc)}), 403
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400


@app.route("/student/result/<int:attempt_id>")
def student_result_page(attempt_id: int):
    if session.get("role") != "STUDENT":
        return redirect(url_for("login"))
    try:
        result = grading_service.get_result_detail(session["user_id"], attempt_id)
        return render_template("result.html", result=result)
    except (PermissionError, ValueError):
        return redirect(url_for("student_dashboard"))


@app.route("/api/student/profile-history", methods=["GET"])
def api_student_profile_history():
    if session.get("role") != "STUDENT":
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    student_id = session["user_id"]
    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT u.user_id, u.username, u.email, u.name, u.phone, u.address, u.status,
                   s.student_code
            FROM users u
            LEFT JOIN students s ON s.student_id = u.user_id
            WHERE u.user_id = %s
            """,
            (student_id,),
        )
        profile = cursor.fetchone()
        profile_data: Dict[str, Any] = dict(cast(Dict[str, Any], profile)) if profile else {}

        cursor.execute(
            """
            SELECT ea.attempt_id, ea.exam_id, ea.start_time, ea.submit_time, ea.status AS attempt_status,
                   e.title AS exam_title, e.duration, e.total_marks,
                   r.result_id, r.score, r.grade, r.status AS result_status
            FROM exam_attempts ea
            JOIN exams e ON e.exam_id = ea.exam_id
            LEFT JOIN results r ON r.attempt_id = ea.attempt_id
            WHERE ea.student_id = %s
            ORDER BY ea.attempt_id DESC
            """,
            (student_id,),
        )
        history_rows = cursor.fetchall() or []
        history: List[Dict[str, Any]] = []
        for row in history_rows:
            item: Dict[str, Any] = dict(cast(Dict[str, Any], row))
            start_dt: Any = item.get("start_time")
            if start_dt and hasattr(start_dt, "strftime"):
                item["start_time"] = start_dt.strftime("%d/%m/%Y %H:%M")
            submit_dt: Any = item.get("submit_time")
            if submit_dt and hasattr(submit_dt, "strftime"):
                item["submit_time"] = submit_dt.strftime("%d/%m/%Y %H:%M")
            if item.get("score") is not None:
                item["score"] = float(item["score"])
            history.append(item)

        return jsonify({"success": True, "profile": profile_data, "history": history}), 200
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)