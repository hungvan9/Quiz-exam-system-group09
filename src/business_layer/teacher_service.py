"""Teacher use cases: syllabus, question bank and exam authoring."""
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional
from src.data_layer import course_exam_dao as default_dao


class TeacherServiceError(Exception):
    def __init__(self, message: str, code: str = "TEACHER_ERROR", http_status: int = 400):
        super().__init__(message)
        self.message, self.code, self.http_status = message, code, http_status

    def to_dict(self):
        return {"success": False, "error": self.code, "message": self.message}


class TeacherService:
    def __init__(self, repository=None):
        self.repo = repository or default_dao

    @staticmethod
    def _positive_id(value, label):
        try: number = int(value)
        except (TypeError, ValueError): raise TeacherServiceError(f"{label} must be a positive integer.")
        if number <= 0: raise TeacherServiceError(f"{label} must be a positive integer.")
        return number

    @staticmethod
    def _text(value, label, max_length=None):
        if not isinstance(value, str) or not value.strip():
            raise TeacherServiceError(f"{label} is required.")
        value = value.strip()
        if max_length and len(value) > max_length:
            raise TeacherServiceError(f"{label} must not exceed {max_length} characters.")
        return value

    def list_syllabuses(self, teacher_id, subject_id=None):
        teacher_id = self._positive_id(teacher_id, "teacher_id")
        return self.repo.list_syllabuses(teacher_id, int(subject_id) if subject_id else None)

    def create_syllabus(self, teacher_id, data):
        teacher_id = self._positive_id(teacher_id, "teacher_id")
        title = self._text(data.get("title"), "Syllabus title", 150)
        subject_id = self._positive_id(data.get("subject_id"), "subject_id")
        chapters = data.get("chapters", [])
        if not isinstance(chapters, list): raise TeacherServiceError("chapters must be a list.")
        for chapter in chapters:
            if not isinstance(chapter, dict): raise TeacherServiceError("Each chapter must be an object.")
            chapter["chapter_title"] = self._text(chapter.get("chapter_title"), "Chapter title", 150)
        syllabus_id = self.repo.create_syllabus(teacher_id, subject_id, title, (data.get("description") or "").strip(), chapters)
        return self.repo.get_syllabus(syllabus_id, teacher_id)

    def update_syllabus(self, teacher_id, syllabus_id, data):
        teacher_id = self._positive_id(teacher_id, "teacher_id")
        syllabus_id = self._positive_id(syllabus_id, "syllabus_id")
        title = self._text(data.get("title"), "Syllabus title", 150)
        chapters = data.get("chapters")
        if chapters is not None:
            if not isinstance(chapters, list): raise TeacherServiceError("chapters must be a list.")
            for chapter in chapters:
                chapter["chapter_title"] = self._text(chapter.get("chapter_title"), "Chapter title", 150)
        if not self.repo.update_syllabus(syllabus_id, teacher_id, title, (data.get("description") or "").strip(), chapters):
            raise TeacherServiceError("Syllabus not found or not owned by this teacher.", "NOT_FOUND", 404)
        return self.repo.get_syllabus(syllabus_id, teacher_id)

    def change_syllabus_status(self, teacher_id, syllabus_id, status):
        status = str(status or "").upper()
        if status not in {"DRAFT", "PUBLISHED", "ARCHIVED"}: raise TeacherServiceError("Invalid syllabus status.")
        if not self.repo.set_syllabus_status(self._positive_id(syllabus_id, "syllabus_id"), self._positive_id(teacher_id, "teacher_id"), status):
            raise TeacherServiceError("Syllabus not found or not owned by this teacher.", "NOT_FOUND", 404)
        return {"success": True, "status": status}

    def delete_syllabus(self, teacher_id, syllabus_id):
        if not self.repo.delete_syllabus(self._positive_id(syllabus_id, "syllabus_id"), self._positive_id(teacher_id, "teacher_id")):
            raise TeacherServiceError("Syllabus not found or not owned by this teacher.", "NOT_FOUND", 404)
        return {"success": True}

    def list_exams(self, teacher_id, status=None):
        if status and status not in {"Draft", "Published", "Completed"}: raise TeacherServiceError("Invalid exam status.")
        return self.repo.list_exams(self._positive_id(teacher_id, "teacher_id"), status)

    def create_exam(self, teacher_id, data):
        teacher_id = self._positive_id(teacher_id, "teacher_id")
        title = self._text(data.get("title"), "Exam title", 150)
        syllabus_id = self._positive_id(data.get("syllabus_id"), "syllabus_id")
        try:
            start = datetime.fromisoformat(data.get("start_time")) if isinstance(data.get("start_time"), str) else data.get("start_time")
            end = datetime.fromisoformat(data.get("end_time")) if isinstance(data.get("end_time"), str) else data.get("end_time")
            duration = int(data.get("duration"))
        except (TypeError, ValueError): raise TeacherServiceError("Provide valid start_time, end_time and duration.")
        if not start or not end or end <= start: raise TeacherServiceError("Exam end_time must be later than start_time.")
        if duration <= 0: raise TeacherServiceError("Exam duration must be greater than zero.")
        exam_id = self.repo.create_exam(teacher_id, syllabus_id, title, start, end, duration, (data.get("rules") or "").strip())
        return self.repo.get_exam_by_id(exam_id)

    def add_question(self, teacher_id, exam_id, data):
        teacher_id = self._positive_id(teacher_id, "teacher_id")
        exam_id = self._positive_id(exam_id, "exam_id")
        content = self._text(data.get("content"), "Question content")
        qtype = str(data.get("question_type", "MULTIPLE_CHOICE")).upper()
        if qtype not in {"MULTIPLE_CHOICE", "WRITTEN"}: raise TeacherServiceError("Unsupported question type.")
        try: marks = Decimal(str(data.get("marks", 1)))
        except InvalidOperation: raise TeacherServiceError("Question marks must be numeric.")
        if marks < 0: raise TeacherServiceError("Question marks cannot be negative.")
        answers = data.get("answers", [])
        if qtype == "MULTIPLE_CHOICE":
            if not isinstance(answers, list) or len(answers) < 2: raise TeacherServiceError("Multiple-choice questions need at least two answers.")
            for answer in answers: answer["content"] = self._text(answer.get("content"), "Answer content")
            if sum(bool(a.get("is_correct")) for a in answers) != 1: raise TeacherServiceError("Exactly one answer must be marked correct.")
        else:
            if answers: raise TeacherServiceError("Written questions cannot have answer options.")
        question_id = self.repo.add_question(exam_id, teacher_id, content, qtype, marks, answers)
        return {"question_id": question_id, "exam_id": exam_id, "content": content, "question_type": qtype, "marks": str(marks), "answers": answers}

    def list_question_banks(self, teacher_id, subject_id=None):
        return self.repo.list_question_banks(self._positive_id(teacher_id, "teacher_id"), int(subject_id) if subject_id else None)

    def create_question_bank(self, teacher_id, data):
        teacher_id = self._positive_id(teacher_id, "teacher_id")
        name = self._text(data.get("question_set_name"), "Question bank name", 150)
        subject_id = self._positive_id(data.get("subject_id"), "subject_id")
        qtype = str(data.get("question_type", "MULTIPLE_CHOICE")).upper()
        if qtype not in {"MULTIPLE_CHOICE", "WRITTEN"}:
            raise TeacherServiceError("Unsupported question type.")
        bank_id = self.repo.create_question_bank(teacher_id, subject_id, name, qtype, data.get("difficulty_level", "MEDIUM"), data.get("explanation", ""))
        return {"question_set_id": bank_id, "question_set_name": name, "subject_id": subject_id, "question_type": qtype}

    def list_bank_questions(self, teacher_id, question_set_id):
        return self.repo.list_bank_questions(self._positive_id(teacher_id, "teacher_id"), self._positive_id(question_set_id, "question_set_id"))

    def add_question_to_bank(self, teacher_id, question_set_id, data):
        teacher_id = self._positive_id(teacher_id, "teacher_id")
        question_set_id = self._positive_id(question_set_id, "question_set_id")
        content = self._text(data.get("content"), "Question content")
        qtype = str(data.get("question_type", "MULTIPLE_CHOICE")).upper()
        if qtype not in {"MULTIPLE_CHOICE", "WRITTEN"}:
            raise TeacherServiceError("Unsupported question type.")
        try:
            marks = Decimal(str(data.get("marks", 1)))
        except InvalidOperation:
            raise TeacherServiceError("Question marks must be numeric.")
        if marks < 0:
            raise TeacherServiceError("Question marks cannot be negative.")
        answers = data.get("answers", [])
        if qtype == "MULTIPLE_CHOICE":
            if not isinstance(answers, list) or len(answers) < 2:
                raise TeacherServiceError("Multiple-choice questions need at least two answers.")
            for answer in answers:
                answer["content"] = self._text(answer.get("content"), "Answer content")
            if sum(bool(a.get("is_correct")) for a in answers) != 1:
                raise TeacherServiceError("Exactly one answer must be marked correct.")
        elif answers:
            raise TeacherServiceError("Written questions cannot have answer options.")
        question_id = self.repo.add_question_to_bank(teacher_id, question_set_id, content, qtype, marks, answers)
        return {"question_id": question_id, "question_set_id": question_set_id, "content": content, "question_type": qtype, "marks": str(marks), "answers": answers}

    def publish_exam(self, teacher_id, exam_id):
        if not self.repo.publish_exam(self._positive_id(exam_id, "exam_id"), self._positive_id(teacher_id, "teacher_id")):
            raise TeacherServiceError("Draft exam not found or not owned by this teacher.", "NOT_FOUND", 404)
        return {"success": True, "status": "Published"}

    def delete_exam(self, teacher_id, exam_id):
        if not self.repo.delete_exam(self._positive_id(exam_id, "exam_id"), self._positive_id(teacher_id, "teacher_id")):
            raise TeacherServiceError("Draft exam not found or not owned by this teacher.", "NOT_FOUND", 404)
        return {"success": True}
