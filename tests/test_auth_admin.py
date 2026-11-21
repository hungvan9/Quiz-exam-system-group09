"""Cross-tests for Phan Văn Hưng's authentication and administration module."""
from unittest.mock import MagicMock

from src.business_layer.auth_service import AuthService, AdminService
from src.models.user import User


def test_password_hash_is_sha256_and_deterministic():
    assert AuthService.hash_password("abc123") == "6ca13d52ca70c883e0f0bb101e425a89e8624de51db2d2392593af6a84118090"
    assert AuthService.hash_password("abc123") != "abc123"


def test_login_success_for_active_user():
    dao = MagicMock()
    dao.find_by_username_or_email.return_value = User(
        user_id=7, username="teacher", email="t@example.test",
        password=AuthService.hash_password("secret"), name="Teacher",
        status="ACTIVE", role="TEACHER",
    )
    ok, message, user = AuthService(dao).login("teacher", "secret")
    assert ok is True
    assert user.user_id == 7
    assert user.role == "TEACHER"


def test_login_rejects_wrong_password():
    dao = MagicMock()
    dao.find_by_username_or_email.return_value = User(
        user_id=7, password=AuthService.hash_password("correct"), status="ACTIVE"
    )
    ok, _, user = AuthService(dao).login("teacher", "wrong")
    assert ok is False and user is None


def test_login_rejects_locked_account():
    dao = MagicMock()
    dao.find_by_username_or_email.return_value = User(
        user_id=7, password=AuthService.hash_password("secret"), status="LOCKED"
    )
    ok, message, user = AuthService(dao).login("teacher", "secret")
    assert ok is False and user is None
    assert "locked" in message.lower()


def test_registration_rejects_admin_role_escalation():
    dao = MagicMock()
    dao.find_by_username_or_email.return_value = None
    ok, message = AuthService(dao).register("New User", "n@example.test", "newuser", "secret", "ADMIN")
    assert ok is True
    created = dao.create_user.call_args.args[0]
    assert created.role == "STUDENT"


def test_admin_rejects_invalid_account_status():
    dao = MagicMock()
    ok, message = AdminService(dao).toggle_user_lock(10, "DELETED")
    assert ok is False
    dao.update_status.assert_not_called()


def test_admin_locks_existing_user():
    dao = MagicMock()
    dao.update_status.return_value = True
    ok, _ = AdminService(dao).toggle_user_lock(10, "LOCKED")
    assert ok is True
    dao.update_status.assert_called_once_with(10, "LOCKED")


def test_admin_delete_missing_user_reports_failure():
    dao = MagicMock()
    dao.delete_user.return_value = False
    ok, _ = AdminService(dao).remove_user(99)
    assert ok is False
