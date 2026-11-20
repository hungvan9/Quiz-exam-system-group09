from typing import Optional


class User:
    def __init__(
        self,
        user_id: Optional[int] = None,
        username: str = "",
        email: str = "",
        password: str = "",
        name: str = "",
        phone: str = "",
        address: str = "",
        status: str = "ACTIVE",
        role: str = "STUDENT",
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.name = name
        self.phone = phone
        self.address = address
        self.status = status
        self.role = role

    def edit_profile(self, name: str, phone: str, address: str) -> None:
        self.name = name
        self.phone = phone
        self.address = address

    def is_active(self) -> bool:
        return self.status == "ACTIVE"


class Student(User):
    def __init__(self, student_code: str = "", **kwargs):
        super().__init__(role="STUDENT", **kwargs)
        self.student_id = self.user_id
        self.student_code = student_code


class Teacher(User):
    def __init__(self, teacher_code: str = "", specialization: str = "", **kwargs):
        super().__init__(role="TEACHER", **kwargs)
        self.teacher_id = self.user_id
        self.teacher_code = teacher_code
        self.specialization = specialization


class Administrator(User):
    def __init__(self, admin_code: str = "", **kwargs):
        super().__init__(role="ADMIN", **kwargs)
        self.admin_id = self.user_id
        self.admin_code = admin_code