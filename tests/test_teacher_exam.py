"""Cross-tests for Võ Bảo Long's teacher module.

The repository snapshot supplied for integration has teacher_service.py and
course_exam_dao.py as empty placeholders. These tests intentionally skip until
Long's implementation is merged; they must not pretend an absent module passed.
"""
import pytest

from src.business_layer import teacher_service
from src.data_layer import course_exam_dao


def _implemented_public_functions(module):
    return [
        value for name, value in vars(module).items()
        if not name.startswith("_") and callable(value)
    ]


def test_teacher_service_is_implemented():
    functions = _implemented_public_functions(teacher_service)
    if not functions:
        pytest.skip(
            "Waiting for Long to merge src/business_layer/teacher_service.py; "
            "cannot cross-test Syllabus, Question Bank and Exam creation yet."
        )
    assert functions, "Teacher service should expose its public business functions."


def test_course_exam_dao_is_implemented():
    functions = _implemented_public_functions(course_exam_dao)
    if not functions:
        pytest.skip(
            "Waiting for Long to merge src/data_layer/course_exam_dao.py; "
            "DAO integration tests require the teacher module contract."
        )
    assert functions, "Course/exam DAO should expose its public query functions."
