"""MySQL data access for teacher syllabus, question bank and exam management."""
from contextlib import contextmanager
from typing import Optional
from .db_connection import DatabaseConnection


@contextmanager
def _db():
    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        yield conn, cursor
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def _one(cursor):
    row = cursor.fetchone()
    return dict(row) if row else None


def _many(cursor):
    return [dict(row) for row in cursor.fetchall()]


def list_syllabuses(teacher_id: int, subject_id: Optional[int] = None):
    with _db() as (_, cur):
        sql = """SELECT s.*, sub.subject_name FROM syllabuses s
                 JOIN subjects sub ON sub.subject_id=s.subject_id WHERE s.teacher_id=%s"""
        params = [teacher_id]
        if subject_id is not None:
            sql += " AND s.subject_id=%s"; params.append(subject_id)
        sql += " ORDER BY s.updated_at DESC"
        cur.execute(sql, tuple(params)); return _many(cur)


def get_syllabus(syllabus_id: int, teacher_id: Optional[int] = None):
    with _db() as (_, cur):
        sql = "SELECT * FROM syllabuses WHERE syllabus_id=%s"; params = [syllabus_id]
        if teacher_id is not None:
            sql += " AND teacher_id=%s"; params.append(teacher_id)
        cur.execute(sql, tuple(params)); row = _one(cur)
        if row:
            cur.execute("SELECT * FROM syllabus_contents WHERE syllabus_id=%s ORDER BY sort_order, content_id", (syllabus_id,))
            row["chapters"] = _many(cur)
        return row


def create_syllabus(teacher_id: int, subject_id: int, title: str, description: str = "", chapters=None):
    with _db() as (conn, cur):
        cur.execute("INSERT INTO syllabuses (subject_id,teacher_id,title,description) VALUES (%s,%s,%s,%s)", (subject_id, teacher_id, title, description))
        syllabus_id = cur.lastrowid
        for index, chapter in enumerate(chapters or [], 1):
            cur.execute("INSERT INTO syllabus_contents (syllabus_id,chapter_title,content,sort_order) VALUES (%s,%s,%s,%s)", (syllabus_id, chapter["chapter_title"], chapter.get("content", ""), chapter.get("sort_order", index)))
        conn.commit(); return syllabus_id


def update_syllabus(syllabus_id: int, teacher_id: int, title: str, description: str, chapters=None):
    with _db() as (conn, cur):
        cur.execute("UPDATE syllabuses SET title=%s,description=%s WHERE syllabus_id=%s AND teacher_id=%s", (title, description, syllabus_id, teacher_id))
        if cur.rowcount == 0:
            cur.execute("SELECT 1 FROM syllabuses WHERE syllabus_id=%s AND teacher_id=%s", (syllabus_id, teacher_id))
            if not cur.fetchone(): return False
        if chapters is not None:
            cur.execute("DELETE FROM syllabus_contents WHERE syllabus_id=%s", (syllabus_id,))
            for index, chapter in enumerate(chapters, 1):
                cur.execute("INSERT INTO syllabus_contents (syllabus_id,chapter_title,content,sort_order) VALUES (%s,%s,%s,%s)", (syllabus_id, chapter["chapter_title"], chapter.get("content", ""), chapter.get("sort_order", index)))
        conn.commit(); return True


def set_syllabus_status(syllabus_id: int, teacher_id: int, status: str):
    with _db() as (conn, cur):
        cur.execute("UPDATE syllabuses SET status=%s WHERE syllabus_id=%s AND teacher_id=%s", (status, syllabus_id, teacher_id))
        conn.commit(); return cur.rowcount > 0


def delete_syllabus(syllabus_id: int, teacher_id: int):
    with _db() as (conn, cur):
        cur.execute("DELETE FROM syllabuses WHERE syllabus_id=%s AND teacher_id=%s", (syllabus_id, teacher_id))
        conn.commit(); return cur.rowcount > 0


def list_exams(teacher_id: int, status: Optional[str] = None):
    with _db() as (_, cur):
        sql = """SELECT e.*, s.title AS syllabus_title FROM exams e
                 JOIN syllabuses s ON s.syllabus_id=e.syllabus_id WHERE e.created_by_teacher_id=%s"""
        params = [teacher_id]
        if status:
            sql += " AND e.status=%s"; params.append(status)
        sql += " ORDER BY e.created_at DESC"; cur.execute(sql, tuple(params)); return _many(cur)


def get_exam_by_id(exam_id: int):
    with _db() as (_, cur):
        cur.execute("SELECT * FROM exams WHERE exam_id=%s", (exam_id,)); exam = _one(cur)
        if exam:
            cur.execute("SELECT * FROM questions WHERE exam_id=%s ORDER BY question_id", (exam_id,)); questions = _many(cur)
            for q in questions:
                cur.execute("SELECT answer_id,question_id,content,is_correct FROM answers WHERE question_id=%s ORDER BY answer_id", (q["question_id"],)); q["answers"] = _many(cur)
            exam["questions"] = questions
        return exam


def create_exam(teacher_id: int, syllabus_id: int, title: str, start_time, end_time, duration: int, rules: str = ""):
    with _db() as (conn, cur):
        cur.execute("SELECT syllabus_id FROM syllabuses WHERE syllabus_id=%s AND teacher_id=%s", (syllabus_id, teacher_id))
        if not cur.fetchone(): raise ValueError("Syllabus not found or not owned by this teacher.")
        cur.execute("INSERT INTO exams (syllabus_id,created_by_teacher_id,title,start_time,end_time,duration,rules,status) VALUES (%s,%s,%s,%s,%s,%s,%s,'Draft')", (syllabus_id, teacher_id, title, start_time, end_time, duration, rules))
        exam_id = cur.lastrowid; conn.commit(); return exam_id


def update_exam(exam_id: int, teacher_id: int, **fields):
    allowed = {"title", "syllabus_id", "start_time", "end_time", "duration", "rules"}
    values = {key: value for key, value in fields.items() if key in allowed}
    if not values: return False
    with _db() as (conn, cur):
        cur.execute("SELECT status FROM exams WHERE exam_id=%s AND created_by_teacher_id=%s", (exam_id, teacher_id))
        row = _one(cur)
        if not row or row["status"] != "Draft": return False
        if "syllabus_id" in values:
            cur.execute("SELECT 1 FROM syllabuses WHERE syllabus_id=%s AND teacher_id=%s", (values["syllabus_id"], teacher_id))
            if not cur.fetchone(): raise ValueError("Syllabus not found or not owned by this teacher.")
        sql = "UPDATE exams SET " + ",".join(f"{key}=%s" for key in values) + " WHERE exam_id=%s AND created_by_teacher_id=%s"
        cur.execute(sql, tuple(values.values()) + (exam_id, teacher_id)); conn.commit(); return cur.rowcount > 0


def add_question(exam_id: int, teacher_id: int, content: str, question_type: str, marks, answers=None):
    with _db() as (conn, cur):
        cur.execute("SELECT exam_id FROM exams WHERE exam_id=%s AND created_by_teacher_id=%s AND status='Draft'", (exam_id, teacher_id))
        if not cur.fetchone(): raise ValueError("Draft exam not found or not owned by this teacher.")
        cur.execute("INSERT INTO questions (exam_id,content,question_type,marks) VALUES (%s,%s,%s,%s)", (exam_id, content, question_type, marks))
        question_id = cur.lastrowid
        for answer in answers or []:
            cur.execute("INSERT INTO answers (question_id,content,is_correct) VALUES (%s,%s,%s)", (question_id, answer["content"], bool(answer.get("is_correct", False))))
        conn.commit(); return question_id


def update_question(question_id: int, teacher_id: int, content: str, question_type: str, marks, answers=None):
    with _db() as (conn, cur):
        cur.execute("SELECT q.question_id FROM questions q JOIN exams e ON e.exam_id=q.exam_id WHERE q.question_id=%s AND e.created_by_teacher_id=%s AND e.status='Draft'", (question_id, teacher_id))
        if not cur.fetchone(): return False
        cur.execute("UPDATE questions SET content=%s,question_type=%s,marks=%s WHERE question_id=%s", (content, question_type, marks, question_id))
        if answers is not None:
            cur.execute("DELETE FROM answers WHERE question_id=%s", (question_id,))
            for answer in answers:
                cur.execute("INSERT INTO answers (question_id,content,is_correct) VALUES (%s,%s,%s)", (question_id, answer["content"], bool(answer.get("is_correct", False))))
        conn.commit(); return True


def delete_question(question_id: int, teacher_id: int):
    with _db() as (conn, cur):
        cur.execute("DELETE q FROM questions q JOIN exams e ON e.exam_id=q.exam_id WHERE q.question_id=%s AND e.created_by_teacher_id=%s AND e.status='Draft'", (question_id, teacher_id))
        conn.commit(); return cur.rowcount > 0


def publish_exam(exam_id: int, teacher_id: int):
    with _db() as (conn, cur):
        cur.execute("SELECT e.exam_id,e.start_time,e.end_time,e.duration,COUNT(q.question_id) AS question_count,COALESCE(SUM(q.marks),0) AS total_marks FROM exams e LEFT JOIN questions q ON q.exam_id=e.exam_id WHERE e.exam_id=%s AND e.created_by_teacher_id=%s AND e.status='Draft' GROUP BY e.exam_id", (exam_id, teacher_id))
        exam = _one(cur)
        if not exam: return False
        if exam["end_time"] <= exam["start_time"] or exam["duration"] <= 0 or exam["question_count"] < 1:
            raise ValueError("Exam needs a valid schedule, positive duration and at least one question.")
        cur.execute("UPDATE exams SET status='Published',total_marks=%s WHERE exam_id=%s", (exam["total_marks"], exam_id)); conn.commit(); return True


def delete_exam(exam_id: int, teacher_id: int):
    with _db() as (conn, cur):
        cur.execute("DELETE FROM exams WHERE exam_id=%s AND created_by_teacher_id=%s AND status='Draft'", (exam_id, teacher_id))
        conn.commit(); return cur.rowcount > 0

# Contract consumed by ExamService (student online-exam workflow).
def list_published_exams():
    with _db() as (_, cur):
        cur.execute("SELECT * FROM exams WHERE status='Published' ORDER BY start_time"); return _many(cur)


def get_questions_by_exam(exam_id: int):
    exam = get_exam_by_id(exam_id)
    return (exam or {}).get("questions", [])


def create_question_bank(teacher_id: int, subject_id: int, name: str, question_type: str = "MULTIPLE_CHOICE", difficulty_level: str = "MEDIUM", explanation: str = ""):
    with _db() as (conn, cur):
        cur.execute("INSERT INTO question_banks (subject_id,teacher_id,question_set_name,question_type,difficulty_level,explanation) VALUES (%s,%s,%s,%s,%s,%s)", (subject_id, teacher_id, name, question_type, difficulty_level, explanation))
        bank_id = cur.lastrowid; conn.commit(); return bank_id


def list_question_banks(teacher_id: int, subject_id: Optional[int] = None):
    with _db() as (_, cur):
        sql = "SELECT qb.*,s.subject_name FROM question_banks qb JOIN subjects s ON s.subject_id=qb.subject_id WHERE qb.teacher_id=%s"
        params = [teacher_id]
        if subject_id is not None:
            sql += " AND qb.subject_id=%s"; params.append(subject_id)
        sql += " ORDER BY qb.updated_at DESC"; cur.execute(sql, tuple(params)); return _many(cur)


def add_question_to_bank(teacher_id: int, question_set_id: int, content: str, question_type: str, marks, answers=None):
    with _db() as (conn, cur):
        cur.execute("SELECT question_set_id FROM question_banks WHERE question_set_id=%s AND teacher_id=%s", (question_set_id, teacher_id))
        if not cur.fetchone(): raise ValueError("Question bank not found or not owned by this teacher.")
        cur.execute("INSERT INTO questions (exam_id,question_set_id,content,question_type,marks) VALUES (NULL,%s,%s,%s,%s)", (question_set_id, content, question_type, marks))
        question_id = cur.lastrowid
        for answer in answers or []:
            cur.execute("INSERT INTO answers (question_id,content,is_correct) VALUES (%s,%s,%s)", (question_id, answer["content"], bool(answer.get("is_correct", False))))
        conn.commit(); return question_id


def list_bank_questions(teacher_id: int, question_set_id: int):
    with _db() as (_, cur):
        cur.execute("SELECT q.* FROM questions q JOIN question_banks qb ON qb.question_set_id=q.question_set_id WHERE qb.teacher_id=%s AND qb.question_set_id=%s ORDER BY q.question_id", (teacher_id, question_set_id))
        questions = _many(cur)
        for question in questions:
            cur.execute("SELECT answer_id,content,is_correct FROM answers WHERE question_id=%s ORDER BY answer_id", (question["question_id"],))
            question["answers"] = _many(cur)
        return questions
