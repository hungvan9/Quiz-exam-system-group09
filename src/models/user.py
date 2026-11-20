class User:
    def __init__(self, user_id=None, username="", password="", name="",
                 phone="", address="", status="ACTIVE", role="STUDENT"):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.name = name
        self.phone = phone
        self.address = address
        self.status = status
        self.role = role

    def login(self):
        return self.status == "ACTIVE"

    def logout(self):
        return True

    def edit_profile(self, name, phone, address):
        self.name = name
        self.phone = phone
        self.address = address


class Student(User):
    def __init__(self, user_id=None, username="", password="", name="",
                 phone="", address="", status="ACTIVE", student_code=""):
        super().__init__(user_id, username, password, name, phone, address, status, role="STUDENT")
        self.student_id = user_id
        self.student_code = student_code


class Teacher(User):
    def __init__(self, user_id=None, username="", password="", name="",
                 phone="", address="", status="ACTIVE", teacher_code="", specialization=""):
        super().__init__(user_id, username, password, name, phone, address, status, role="TEACHER")
        self.teacher_id = user_id
        self.teacher_code = teacher_code
        self.specialization = specialization


class Administrator(User):
    def __init__(self, user_id=None, username="", password="", name="",
                 phone="", address="", status="ACTIVE", admin_code=""):
        super().__init__(user_id, username, password, name, phone, address, status, role="ADMIN")
        self.admin_id = user_id
        self.admin_code = admin_code