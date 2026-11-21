USE quiz_exam_db;
-- Demo accounts all use the SHA-256 hash of the password: password123
INSERT IGNORE INTO users (user_id, username, email, password, name, status, role) VALUES
(1,'admin','admin@group09.local','ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f','System Administrator','ACTIVE','ADMIN'),
(2,'teacher','teacher@group09.local','ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f','Demo Teacher','ACTIVE','TEACHER'),
(3,'student','student@group09.local','ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f','Demo Student','ACTIVE','STUDENT');
INSERT IGNORE INTO administrators (admin_id, admin_code) VALUES (1,'ADM0001');
INSERT IGNORE INTO teachers (teacher_id, teacher_code, specialization) VALUES (2,'GV0002','Software Engineering');
INSERT IGNORE INTO students (student_id, student_code) VALUES (3,'SV0003');
INSERT IGNORE INTO subjects (subject_id, subject_name, description) VALUES (1,'Software Engineering','Demo subject for Group 09');
INSERT IGNORE INTO syllabuses (syllabus_id, subject_id, teacher_id, title, description, status) VALUES
(1,1,2,'Introduction to Software Engineering','Sample syllabus','PUBLISHED');
INSERT IGNORE INTO syllabus_contents (content_id, syllabus_id, chapter_title, content, sort_order) VALUES
(1,1,'Chapter 1 - Introduction','Software process and lifecycle.',1),
(2,1,'Chapter 2 - Requirements','Functional and non-functional requirements.',2);
INSERT IGNORE INTO exams (exam_id, syllabus_id, created_by_teacher_id, title, start_time, end_time, duration, rules, status, total_marks) VALUES
(1,1,2,'Sample Draft Exam','2026-01-01 08:00:00','2030-01-01 17:00:00',30,'Read each question carefully.','Draft',10.00);
INSERT IGNORE INTO questions (question_id, exam_id, content, question_type, marks) VALUES
(1,1,'Which activity identifies stakeholder needs?','MULTIPLE_CHOICE',5.00),
(2,1,'Explain why software requirements should be validated.','WRITTEN',5.00);
INSERT IGNORE INTO answers (answer_id, question_id, content, is_correct) VALUES
(1,1,'Requirements elicitation',TRUE),(2,1,'Code compilation',FALSE),(3,1,'Deployment',FALSE),(4,1,'Hardware repair',FALSE);
