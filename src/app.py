import os
from functools import wraps
from flask import Flask, flash, redirect, render_template, request, session, url_for
from src.business_layer.auth_service import AdminService, AuthService
from src.data_layer import course_exam_dao
from src.presentation_layer.student_routes import configure_exam_routes
from src.presentation_layer.teacher_routes import teacher_bp

base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, "presentation_layer", "templates")
static_dir = os.path.join(base_dir, "presentation_layer", "static")

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "group09_quiz_exam_secret_key")

auth_service = AuthService()
admin_service = AdminService()

app.register_blueprint(teacher_bp)
app.register_blueprint(configure_exam_routes(course_exam_dao))


def role_required(required_role: str):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get("role") != required_role:
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return decorated
    return decorator


# ==================== AUTH ROUTES ====================
@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        success, message, user = auth_service.login(username, password)
        if success and user:
            session["user_id"] = user.user_id
            session["username"] = user.username
            session["name"] = user.name
            session["role"] = user.role
            flash(message, "success")

            if user.role == "ADMIN":
                return redirect(url_for("admin_dashboard"))
            if user.role == "TEACHER":
                return redirect(url_for("teacher_dashboard"))
            return redirect(url_for("student_dashboard"))
        error = message
    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    success_msg = None
    if request.method == "POST":
        name = request.form.get("name", "")
        email = request.form.get("email", "")
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        re_password = request.form.get("re_password", "")
        role = request.form.get("role", "STUDENT")

        if re_password and password != re_password:
            error = "Passwords do not match."
        else:
            ok, msg = auth_service.register(name, email, username, password, role)
            if ok:
                success_msg = msg
            else:
                error = msg
    return render_template("register.html", error=error, success_msg=success_msg)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ==================== ADMIN ROUTES ====================
@app.route("/admin/dashboard")
@role_required("ADMIN")
def admin_dashboard():
    keyword_user = request.args.get("q_user", "")
    role_filter = request.args.get("role", "")
    keyword_subject = request.args.get("q_subject", "")

    stats = admin_service.get_overview_stats()
    users = admin_service.list_users(keyword=keyword_user, role=role_filter)
    subjects = admin_service.list_subjects(keyword=keyword_subject)

    return render_template(
        "admin.html",
        stats=stats,
        users=users,
        subjects=subjects,
        keyword_user=keyword_user,
        role_filter=role_filter,
        keyword_subject=keyword_subject,
    )


@app.route("/admin/users/<int:user_id>/status", methods=["POST"])
@role_required("ADMIN")
def update_user_status(user_id: int):
    target_status = request.form.get("status", "ACTIVE")
    ok, msg = admin_service.toggle_user_lock(user_id, target_status)
    flash(msg, "success" if ok else "error")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/users/<int:user_id>/delete", methods=["POST"])
@role_required("ADMIN")
def delete_user(user_id: int):
    ok, msg = admin_service.remove_user(user_id)
    flash(msg, "success" if ok else "error")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/subjects/add", methods=["POST"])
@role_required("ADMIN")
def add_subject():
    name = request.form.get("subject_name", "")
    desc = request.form.get("description", "")
    ok, msg = admin_service.add_subject(name, desc)
    flash(msg, "success" if ok else "error")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/subjects/<int:subject_id>/delete", methods=["POST"])
@role_required("ADMIN")
def delete_subject(subject_id: int):
    ok, msg = admin_service.remove_subject(subject_id)
    flash(msg, "success" if ok else "error")
    return redirect(url_for("admin_dashboard"))


# ==================== TEACHER & STUDENT PAGE ROUTES ====================
@app.route("/teacher/dashboard")
@role_required("TEACHER")
def teacher_dashboard():
    return render_template("teacher.html")


@app.route("/student/dashboard")
@role_required("STUDENT")
def student_dashboard():
    return render_template("student_dashboard.html")


@app.route("/student/exam/<int:exam_id>")
@role_required("STUDENT")
def student_exam_page(exam_id: int):
    return render_template("exam-interface.html", exam_id=exam_id)


@app.route("/student/result/<int:attempt_id>")
@role_required("STUDENT")
def student_result_page(attempt_id: int):
    return render_template("result.html", attempt_id=attempt_id)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)