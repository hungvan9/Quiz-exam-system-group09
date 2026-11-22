import unittest
from unittest.mock import MagicMock, patch

from src.business_layer.auth_service import AuthService


class TestAuthCases(unittest.TestCase):
    def setUp(self):
        self.patcher = patch("src.data_layer.user_dao.DatabaseConnection.get_connection")
        self.mock_get_conn = self.patcher.start()
        self.mock_cursor = MagicMock()
        self.mock_get_conn.return_value.cursor.return_value = self.mock_cursor
        self.auth_service = AuthService()

    def tearDown(self):
        self.patcher.stop()

    def _sample_user_row(self):
        return {
            "user_id": 10,
            "username": "student01",
            "email": "student01@gmail.com",
            "password": AuthService.hash_password("123456"),
            "name": "Student 01",
            "phone": "0901234567",
            "address": "Ho Chi Minh City",
            "status": "ACTIVE",
            "role": "STUDENT",
        }

    def test_tc01_login_valid_credentials(self):
        """TC01: Login with valid username and password."""
        self.mock_cursor.fetchone.return_value = self._sample_user_row()

        success, message, user = self.auth_service.login("student01", "123456")

        self.assertTrue(success)
        self.assertEqual(message, "User logs in successfully")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "student01")

    def test_tc02_login_wrong_password(self):
        """TC02: Login with valid username and wrong password."""
        self.mock_cursor.fetchone.return_value = self._sample_user_row()

        success, message, user = self.auth_service.login("student01", "wrongpass")

        self.assertFalse(success)
        self.assertEqual(message, "Invalid username or password.")
        self.assertIsNone(user)

    def test_tc03_register_account_success(self):
        """TC03: Register a new student account with valid inputs."""
        self.mock_cursor.fetchone.return_value = None
        self.mock_cursor.lastrowid = 10

        success, message = self.auth_service.register(
            name="John",
            email="john@gmail.com",
            username="student01",
            password="123456",
        )

        self.assertTrue(success)
        self.assertEqual(message, "Registration is completed successfully")


if __name__ == "__main__":
    unittest.main()
