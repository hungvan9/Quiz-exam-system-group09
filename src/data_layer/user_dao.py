from typing import List, Optional
from src.data_layer.db_connection import DatabaseConnection
from src.models.user import User


class UserDAO:
    def find_by_username_or_email(self, identifier: str) -> Optional[User]:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM users WHERE username = %s OR email = %s LIMIT 1"
            cursor.execute(query, (identifier, identifier))
            row = cursor.fetchone()
            if not row:
                return None
            return User(
                user_id=row["user_id"],
                username=row["username"],
                email=row["email"],
                password=row["password"],
                name=row["name"],
                phone=row["phone"] or "",
                address=row["address"] or "",
                status=row["status"],
                role=row["role"],
            )
        finally:
            cursor.close()
            conn.close()

    def create_user(self, user: User) -> int:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO users (username, email, password, name, phone, address, status, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (
                    user.username,
                    user.email,
                    user.password,
                    user.name,
                    user.phone,
                    user.address,
                    user.status,
                    user.role,
                ),
            )
            user_id = cursor.lastrowid

            if user.role == "STUDENT":
                cursor.execute(
                    "INSERT INTO students (student_id, student_code) VALUES (%s, %s)",
                    (user_id, f"SV{user_id:04d}"),
                )
            elif user.role == "TEACHER":
                cursor.execute(
                    "INSERT INTO teachers (teacher_id, teacher_code, specialization) VALUES (%s, %s, %s)",
                    (user_id, f"GV{user_id:04d}", "General"),
                )
            elif user.role == "ADMIN":
                cursor.execute(
                    "INSERT INTO administrators (admin_id, admin_code) VALUES (%s, %s)",
                    (user_id, f"ADM{user_id:04d}"),
                )

            conn.commit()
            return user_id
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def search_users(self, keyword: str = "", role: str = "", status: str = "") -> List[User]:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = "SELECT * FROM users WHERE 1=1"
            params = []
            if keyword:
                sql += " AND (name LIKE %s OR email LIKE %s OR username LIKE %s)"
                like_kw = f"%{keyword}%"
                params.extend([like_kw, like_kw, like_kw])
            if role:
                sql += " AND role = %s"
                params.append(role)
            if status:
                sql += " AND status = %s"
                params.append(status)
            sql += " ORDER BY user_id ASC"

            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()
            return [
                User(
                    user_id=r["user_id"],
                    username=r["username"],
                    email=r["email"],
                    password=r["password"],
                    name=r["name"],
                    phone=r["phone"] or "",
                    address=r["address"] or "",
                    status=r["status"],
                    role=r["role"],
                )
                for r in rows
            ]
        finally:
            cursor.close()
            conn.close()

    def update_status(self, user_id: int, status: str) -> bool:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET status = %s WHERE user_id = %s", (status, user_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    def delete_user(self, user_id: int) -> bool:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    def update_password(self, email: str, hashed_password: str) -> bool:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()