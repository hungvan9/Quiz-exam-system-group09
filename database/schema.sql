-- Quiz Examination System - Group 09
-- MySQL 8.0+. Tables follow docs/Requirement_and_Design_Document_Group09.pdf.
CREATE DATABASE IF NOT EXISTS quiz_exam_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE quiz_exam_db;

CREATE TABLE IF NOT EXISTS users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  email VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL COMMENT 'Password hash; never store plaintext',
  name VARCHAR(100) NOT NULL,
  phone VARCHAR(20) NULL,
  address VARCHAR(255) NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
  role VARCHAR(20) NOT NULL,
  CONSTRAINT chk_users_role CHECK (role IN ('STUDENT','TEACHER','ADMIN')),
  CONSTRAINT chk_users_status CHECK (status IN ('ACTIVE','LOCKED'))
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS students (
  student_id INT PRIMARY KEY,
  student_code VARCHAR(30) NOT NULL UNIQUE,
  CONSTRAINT fk_students_user FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS teachers (
  teacher_id INT PRIMARY KEY,
  teacher_code VARCHAR(30) NOT NULL UNIQUE,
  specialization VARCHAR(100) NULL,
  CONSTRAINT fk_teachers_user FOREIGN KEY (teacher_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS administrators (
  admin_id INT PRIMARY KEY,
  admin_code VARCHAR(30) NOT NULL UNIQUE,
  CONSTRAINT fk_admins_user FOREIGN KEY (admin_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS subjects (
  subject_id INT AUTO_INCREMENT PRIMARY KEY,
  subject_name VARCHAR(100) NOT NULL,
  description TEXT NULL
) ENGINE=InnoDB;

-- Syllabus and chapters are represented as a syllabus header and ordered content rows.
CREATE TABLE IF NOT EXISTS syllabuses (
  syllabus_id INT AUTO_INCREMENT PRIMARY KEY,
  subject_id INT NOT NULL,
  teacher_id INT NOT NULL,
  title VARCHAR(150) NOT NULL,
  description TEXT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
  document_url VARCHAR(500) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_syllabus_subject FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
  CONSTRAINT fk_syllabus_teacher FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
  CONSTRAINT chk_syllabus_status CHECK (status IN ('DRAFT','PUBLISHED','ARCHIVED')),
  INDEX idx_syllabus_teacher (teacher_id, subject_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS syllabus_contents (
  content_id INT AUTO_INCREMENT PRIMARY KEY,
  syllabus_id INT NOT NULL,
  chapter_title VARCHAR(150) NOT NULL,
  content TEXT NULL,
  sort_order INT NOT NULL DEFAULT 1,
  CONSTRAINT fk_syllabus_contents_syllabus FOREIGN KEY (syllabus_id) REFERENCES syllabuses(syllabus_id) ON DELETE CASCADE,
  INDEX idx_syllabus_content_order (syllabus_id, sort_order)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS exams (
  exam_id INT AUTO_INCREMENT PRIMARY KEY,
  syllabus_id INT NOT NULL,
  created_by_teacher_id INT NOT NULL,
  updated_by_admin_id INT NULL,
  title VARCHAR(150) NOT NULL,
  start_time DATETIME NOT NULL,
  end_time DATETIME NOT NULL,
  duration INT NOT NULL,
  rules TEXT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'Draft',
  total_marks DECIMAL(6,2) NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_exams_syllabus FOREIGN KEY (syllabus_id) REFERENCES syllabuses(syllabus_id),
  CONSTRAINT fk_exams_teacher FOREIGN KEY (created_by_teacher_id) REFERENCES teachers(teacher_id),
  CONSTRAINT fk_exams_admin FOREIGN KEY (updated_by_admin_id) REFERENCES administrators(admin_id) ON DELETE SET NULL,
  CONSTRAINT chk_exam_duration CHECK (duration > 0),
  CONSTRAINT chk_exam_schedule CHECK (end_time > start_time),
  CONSTRAINT chk_exam_status CHECK (status IN ('Draft','Published','Completed')),
  INDEX idx_exam_status_schedule (status, start_time, end_time),
  INDEX idx_exam_teacher (created_by_teacher_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS question_banks (
  question_set_id INT AUTO_INCREMENT PRIMARY KEY,
  subject_id INT NOT NULL,
  teacher_id INT NOT NULL,
  question_set_name VARCHAR(150) NOT NULL,
  question_type VARCHAR(30) NOT NULL DEFAULT 'MULTIPLE_CHOICE',
  difficulty_level VARCHAR(20) NULL,
  explanation TEXT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_question_bank_subject FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
  CONSTRAINT fk_question_bank_teacher FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS questions (
  question_id INT AUTO_INCREMENT PRIMARY KEY,
  exam_id INT NULL,
  question_set_id INT NULL,
  content TEXT NOT NULL,
  question_type VARCHAR(30) NOT NULL DEFAULT 'MULTIPLE_CHOICE',
  marks DECIMAL(6,2) NOT NULL DEFAULT 1.00,
  CONSTRAINT fk_questions_exam FOREIGN KEY (exam_id) REFERENCES exams(exam_id) ON DELETE CASCADE,
  CONSTRAINT fk_questions_bank FOREIGN KEY (question_set_id) REFERENCES question_banks(question_set_id) ON DELETE SET NULL,
  CONSTRAINT chk_question_type CHECK (question_type IN ('MULTIPLE_CHOICE','WRITTEN')),
  CONSTRAINT chk_question_marks CHECK (marks >= 0),
  INDEX idx_question_exam (exam_id),
  INDEX idx_question_bank (question_set_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS answers (
  answer_id INT AUTO_INCREMENT PRIMARY KEY,
  question_id INT NOT NULL,
  content TEXT NOT NULL,
  is_correct BOOLEAN NOT NULL DEFAULT FALSE,
  CONSTRAINT fk_answers_question FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE,
  INDEX idx_answer_question (question_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS exam_attempts (
  attempt_id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  exam_id INT NOT NULL,
  start_time DATETIME NOT NULL,
  submit_time DATETIME NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'IN_PROGRESS',
  CONSTRAINT fk_attempt_student FOREIGN KEY (student_id) REFERENCES students(student_id),
  CONSTRAINT fk_attempt_exam FOREIGN KEY (exam_id) REFERENCES exams(exam_id),
  CONSTRAINT chk_attempt_status CHECK (status IN ('IN_PROGRESS','SUBMITTED','EXPIRED')),
  INDEX idx_attempt_student_exam (student_id, exam_id, status)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS student_answers (
  student_answer_id INT AUTO_INCREMENT PRIMARY KEY,
  attempt_id INT NOT NULL,
  question_id INT NOT NULL,
  selected_answer_id INT NULL,
  answer_content TEXT NULL,
  submitted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_student_answer_attempt FOREIGN KEY (attempt_id) REFERENCES exam_attempts(attempt_id) ON DELETE CASCADE,
  CONSTRAINT fk_student_answer_question FOREIGN KEY (question_id) REFERENCES questions(question_id),
  CONSTRAINT fk_student_answer_option FOREIGN KEY (selected_answer_id) REFERENCES answers(answer_id) ON DELETE SET NULL,
  UNIQUE KEY uq_attempt_question (attempt_id, question_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS results (
  result_id INT AUTO_INCREMENT PRIMARY KEY,
  attempt_id INT NOT NULL UNIQUE,
  score DECIMAL(6,2) NOT NULL DEFAULT 0,
  grade VARCHAR(10) NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
  CONSTRAINT fk_result_attempt FOREIGN KEY (attempt_id) REFERENCES exam_attempts(attempt_id) ON DELETE CASCADE
) ENGINE=InnoDB;
