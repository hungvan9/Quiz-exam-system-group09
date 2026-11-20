import hashlib
from typing import Dict, List, Optional, Tuple
from src.data_layer.db_connection import DatabaseConnection
from src.data_layer.user_dao import UserDAO
from src.models.user import User


class AuthService:
    def __init__(self, user_dao: Optional[UserDAO] = None):
        self.user_dao = user_dao or UserDAO()

    @staticmethod
    def hash_password(raw_password: str) -> str:
        return hashlib.sha256(raw_password.encode("utf-8")).hexdigest()

    def login(self, username_or_email: str, password: str) -> Tuple[bool, str, Optional[User]]:
        if not username_or_email or not password:
            return False, "Invalid username or password.", None

        user = self.user_dao.find_by_username_or_email(username_or_email.strip())
        if not user or user.password != self.hash_password(password):
            return False, "Invalid username or password.", None

        if not user.is_active():
            return False, "Account is locked. Please contact administrator.", None

        return True, "User logs in successfully", user

    def register(
        self, name: str, email: str, username: str, password: str, role: str = "STUDENT"
    ) -> Tuple[bool, str]:
        if not all([name.strip(), email.strip(), username.strip(), password]):
            return False, "All fields are required."

        if self.user_dao.find_by_username_or_email(username.strip()):
            return False, "Username already exists."

        if self.user_dao.find_by_username_or_email(email.strip()):
            return False, "Email already exists."

        normalized_role = role.strip().upper()
        if normalized_role not in ("STUDENT", "TEACHER"):
            normalized_role = "STUDENT"

        new_user = User(
            username=username.strip(),
            email=email.strip(),
            password=self.hash_password(password),
            name=name.strip(),
            status="ACTIVE",
            role=normalized_role,
        )
        self.user_dao.create_user(new_user)
        return True, "Registration is completed successfully"


class AdminService:
    def __init__(self, user_dao: Optional[UserDAO] = None):
        self.user_dao = user_dao or UserDAO()

    def get_overview_stats(self) -> Dict[str, int]:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            stats = {"students": 0, "teachers": 0, "subjects": 0, "exams": 0}
            cursor.execute("SELECT COUNT(*) AS cnt FROM users WHERE role = 'STUDENT'")
            stats["students"] = cursor.fetchone()["cnt"]
            cursor.execute("SELECT COUNT(*) AS cnt FROM users WHERE role = 'TEACHER'")
            stats["teachers"] = cursor.fetchone()["cnt"]
            cursor.execute("SELECT COUNT(*) AS cnt FROM subjects")
            stats["subjects"] = cursor.fetchone()["cnt"]
            cursor.execute("SELECT COUNT(*) AS cnt FROM exams")
            stats["exams"] = cursor.fetchone()["cnt"]
            return stats
        finally:
            cursor.close()
            conn.close()

    def list_users(self, keyword: str = "", role: str = "", status: str = "") -> List[User]:
        return self.user_dao.search_users(keyword=keyword, role=role, status=status)

    def toggle_user_lock(self, user_id: int, target_status: str) -> Tuple[bool, str]:
        if target_status not in ("ACTIVE", "LOCKED"):
            return False, "Invalid account status."
        if not self.user_dao.update_status(user_id, target_status):
            return False, "User not found."
        return True, f"Account status updated to {target_status}."

    def remove_user(self, user_id: int) -> Tuple[bool, str]:
        if not self.user_dao.delete_user(user_id):
            return False, "User not found."
        return True, "User deleted successfully."

    def list_subjects(self, keyword: str = "") -> List[Dict]:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            if keyword:
                cursor.execute(
                    "SELECT * FROM subjects WHERE subject_name LIKE %s OR description LIKE %s ORDER BY subject_id ASC",
                    (f"%{keyword}%", f"%{keyword}%"),
                )
            else:
                cursor.execute("SELECT * FROM subjects ORDER BY subject_id ASC")
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def add_subject(self, subject_name: str, description: str) -> Tuple[bool, str]:
        if not subject_name.strip():
            return False, "Subject name is required."
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO subjects (subject_name, description) VALUES (%s, %s)",
                (subject_name.strip(), description.strip()),
            )
            conn.commit()
            return True, "Subject added successfully."
        finally:
            cursor.close()
            conn.close()

    def remove_subject(self, subject_id: int) -> Tuple[bool, str]:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM subjects WHERE subject_id = %s", (subject_id,))
            conn.commit()
            if cursor.rowcount == 0:
                return False, "Subject not found."
            return True, "Subject deleted successfully."
        finally:
            cursor.close()
            conn.close()