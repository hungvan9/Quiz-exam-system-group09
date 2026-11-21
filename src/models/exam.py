"""Domain models for teacher-managed syllabus, questions and exams."""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional


@dataclass
class Answer:
    content: str
    is_correct: bool = False
    answer_id: Optional[int] = None


@dataclass
class Question:
    content: str
    question_type: str = "MULTIPLE_CHOICE"
    marks: Decimal = Decimal("1.00")
    answers: List[Answer] = field(default_factory=list)
    question_id: Optional[int] = None

    def validate(self) -> None:
        if not self.content or not self.content.strip():
            raise ValueError("Question content is required.")
        if self.question_type not in {"MULTIPLE_CHOICE", "WRITTEN"}:
            raise ValueError("Question type must be MULTIPLE_CHOICE or WRITTEN.")
        if Decimal(str(self.marks)) < 0:
            raise ValueError("Question marks cannot be negative.")
        if self.question_type == "MULTIPLE_CHOICE":
            if len(self.answers) < 2:
                raise ValueError("A multiple-choice question requires at least two answers.")
            if sum(1 for answer in self.answers if answer.is_correct) != 1:
                raise ValueError("A multiple-choice question must have exactly one correct answer.")
        elif self.answers:
            raise ValueError("Written questions must not contain multiple-choice answers.")


@dataclass
class Exam:
    title: str
    syllabus_id: int
    start_time: object
    end_time: object
    duration: int
    rules: str = ""
    status: str = "Draft"
    exam_id: Optional[int] = None
    questions: List[Question] = field(default_factory=list)

    def validate(self) -> None:
        if not self.title or not self.title.strip():
            raise ValueError("Exam title is required.")
        if int(self.duration) <= 0:
            raise ValueError("Exam duration must be greater than zero.")
        if self.end_time <= self.start_time:
            raise ValueError("Exam end time must be later than start time.")
        if self.status not in {"Draft", "Published", "Completed"}:
            raise ValueError("Invalid exam status.")


@dataclass
class Syllabus:
    title: str
    subject_id: int
    teacher_id: int
    description: str = ""
    status: str = "DRAFT"
    syllabus_id: Optional[int] = None
    chapters: list = field(default_factory=list)
