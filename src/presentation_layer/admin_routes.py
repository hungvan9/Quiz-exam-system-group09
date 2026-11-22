"""Admin routes and dashboard actions."""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from src.business_layer.auth_service import AdminService

admin_bp = Blueprint("admin", __name__)
admin_service = AdminService()


def _require_admin() -> bool:
    return str(session.get("role") or "").upper() == "ADMIN"


def admin_panel():
    if not _require_admin():
        return redirect(url_for("login"))

    keyword_user = request.args.get("q_user", "").strip()
    role_filter = request.args.get("role", "").strip()
    keyword_subject = request.args.get("q_subject", "").strip()

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


def update_user_status(user_id: int):
    if not _require_admin():
        return redirect(url_for("login"))
    target_status = request.form.get("status", "").strip().upper()
    success, message = admin_service.toggle_user_lock(user_id, target_status)
    flash(message, "success" if success else "error")
    return redirect(url_for("admin_dashboard"))


def delete_user(user_id: int):
    if not _require_admin():
        return redirect(url_for("login"))
    success, message = admin_service.remove_user(user_id)
    flash(message, "success" if success else "error")
    return redirect(url_for("admin_dashboard"))


def add_subject():
    if not _require_admin():
        return redirect(url_for("login"))
    subject_name = request.form.get("subject_name", "")
    description = request.form.get("description", "")
    success, message = admin_service.add_subject(subject_name, description)
    flash(message, "success" if success else "error")
    return redirect(url_for("admin_dashboard"))


def delete_subject(subject_id: int):
    if not _require_admin():
        return redirect(url_for("login"))
    success, message = admin_service.remove_subject(subject_id)
    flash(message, "success" if success else "error")
    return redirect(url_for("admin_dashboard"))


@admin_bp.record_once
def _register_admin_endpoints(state):
    app = state.app
    app.add_url_rule("/admin/dashboard", endpoint="admin_dashboard", view_func=admin_panel, methods=["GET"])
    app.add_url_rule("/admin/users/<int:user_id>/status", endpoint="update_user_status", view_func=update_user_status, methods=["POST"])
    app.add_url_rule("/admin/users/<int:user_id>/delete", endpoint="delete_user", view_func=delete_user, methods=["POST"])
    app.add_url_rule("/admin/subjects/add", endpoint="add_subject", view_func=add_subject, methods=["POST"])
    app.add_url_rule("/admin/subjects/<int:subject_id>/delete", endpoint="delete_subject", view_func=delete_subject, methods=["POST"])
