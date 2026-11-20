class Subject:
    def __init__(self, subject_id=None, subject_name="", description=""):
        self.subject_id = subject_id
        self.subject_name = subject_name
        self.description = description


class Exam:
    def __init__(self, exam_id=None, subject_id=None, created_by_teacher_id=None,
                 title="", start_time=None, end_time=None, duration=60, rules=""):
        self.exam_id = exam_id
        self.subject_id = subject_id
        self.created_by_teacher_id = created_by_teacher_id
        self.title = title
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.rules = rules


class Question:
    def __init__(self, question_id=None, exam_id=None, content="",
                 question_type="MULTIPLE_CHOICE", marks=1.0):
        self.question_id = question_id
        self.exam_id = exam_id
        self.content = content
        self.question_type = question_type
        self.marks = marks
        self.answers = []


class Answer:
    def __init__(self, answer_id=None, question_id=None, content="", is_correct=False):
        self.answer_id = answer_id
        self.question_id = question_id
        self.content = content
        self.is_correct = is_correct


class ExamAttempt:
    def __init__(self, attempt_id=None, student_id=None, exam_id=None,
                 start_time=None, submit_time=None, status="IN_PROGRESS"):
        self.attempt_id = attempt_id
        self.student_id = student_id
        self.exam_id = exam_id
        self.start_time = start_time
        self.submit_time = submit_time
        self.status = status


class StudentAnswer:
    def __init__(self, student_answer_id=None, attempt_id=None, question_id=None,
                 selected_answer_id=None, answer_content="", submitted_at=None):
        self.student_answer_id = student_answer_id
        self.attempt_id = attempt_id
        self.question_id = question_id
        self.selected_answer_id = selected_answer_id
        self.answer_content = answer_content
        self.submitted_at = submitted_at


class Result:
    def __init__(self, result_id=None, attempt_id=None, score=0.0, grade="", status="COMPLETED"):
        self.result_id = result_id
        self.attempt_id = attempt_id
        self.score = score
        self.grade = grade
        self.status = status