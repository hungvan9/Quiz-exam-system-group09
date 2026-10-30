# Requirement Specification and Design Document

## 1. Functional Requirements

The Quiz Examination System requires the following basic features, divided by user roles:

**1.1. Common Functions (Authentication & Profile):**
*   **Register:** New users can register for a student account in the system.
*   **Login & Logout:** All users (Students, Teachers, and Administrators) must log into the system to access their specific features and can log out when finished.
*   **Edit details:** Users can update their personal profile information (e.g., name, phone number, address).

**1.2. Administrator Functions:**
*   **Manage students:** Admins can manage student accounts in the database (view, add, edit, remove, or block students).
*   **Manage teacher:** Admins have the authority to manage teacher accounts, including assigning subjects or removing accounts.
*   **Update exam details:** Admins can configure and update overall exam schedules, rules, and system-level details for upcoming exams.

**1.3. Teacher Functions:**
*   **Manage syllabus:** Teachers can create, view, and update the syllabus and chapters for the subjects they are assigned to teach.
*   **Create question:** Teachers can create question papers, add multiple-choice or written questions, and set up the exam structure.
*   **Validate answers:** Teachers can manually review and validate student submitted answers (e.g., for subjective questions or uploaded answer sheets).
*   **Adding grades:** After validating the answers, teachers can manually input, adjust, and finalize the grades for the students.

**1.4. Student Functions:**
*   **Take exams:** Students can access the portal to take available online exams within the allowed time frame.
*   **View results:** After the exam is graded (either automatically or manually by the teacher), students can view their final scores and results.

---

## 2. Non-Functional Requirements (Supplementary Specification)

**2.1. Usability**
*   The user interface automatically adjusts according to the screen size (responsive). It must be easy to use on both desktop computers and mobile devices.

**2.2. Reliability**
*   The system must operate continuously 24/7. Reliability > 99.9%. The exam session must be safely saved in case of a sudden network disconnection.

**2.3. Performance**
*   The system can respond to at least 500 students accessing, taking the quiz, and submitting simultaneously without crashing. It can store information for 10,000+ users and 50,000+ exam results.

**2.4. Supportability**
*   None.

**2.5. Security**
*   Students can only view their own information and their own exam results. 
*   Avoid SQL Injection and XSS security vulnerabilities. 
*   Use solutions to prevent automated software from flooding the data.
*   *Exam Security:* The system must not expose the correct answers in the client-side source code (HTML/JavaScript) while the student is taking the quiz.

**2.6. Design Constraints**
*   Operates on a web platform. 
*   HTML5 + CSS3 + programming language (e.g., Python/Java/PHP) + MySQL database management system.