# I. Functional Requirements
The Quiz Examination System requires the following basic features:

**1. Authentication and Account Management:**
* Users (Students and Administrators) can log into the system.
* New users can register for a student account.
* Users can update their personal profile information and use the reset password function if they forget their password.

**2. Quiz & Question Management (Administrator):**
* **Manage questions:** Admins can manage (create, view, update, delete) multiple-choice questions in the system's question bank. Each question must have at least two options and one correct answer.
* **Manage quizzes:** Admins can create new quizzes by selecting questions from the bank, setting the total number of questions, assigning a time limit (e.g., 45 minutes), and changing the quiz status (Available/Closed).
* **View statistics:** Admins can view the exam results, scores, and submission times of all students.

**3. Exam Execution (Student):**
* **Browse quizzes:** Students can view a list of available quizzes.
* **Take the exam:** Students can select a quiz and start doing the test. The system must display a real-time countdown timer on the screen.
* **Submit the exam:** Students can choose answers, change their choices, and submit the test before the time runs out. If the countdown timer reaches zero, the system will automatically submit the student's current answers.

**4. Grading and Results:**
* Upon submission, the system will automatically calculate the student's score based on the correct answers.
* Students can view their final score immediately after submitting the test.
* Students can view their exam history and past scores.

---

# II. Supplementary Specification (Non-Functional Requirements)

**Usability**
* The user interface automatically adjusts according to the screen size (responsive). It must be easy to use on both desktop computers and mobile devices.

**Reliability**
* The system must operate continuously 24/7. Reliability > 99.9%. The exam session must be safely saved in case of a sudden network disconnection.

**Performance**
* The system can respond to at least 500 students accessing, taking the quiz, and submitting simultaneously without crashing. It can store information for 10,000+ users and 50,000+ exam results.

**Supportability**
* None.

**Security**
* Students can only view their own information and their own exam results.
* Avoid SQL Injection and XSS security vulnerabilities.
* Use solutions to prevent automated software from flooding the data.
* *Exam Security:* The system must not expose the correct answers in the client-side source code (HTML/JavaScript) while the student is taking the quiz.

**Design Constraints**
* Operates on a web platform.
* HTML5 + CSS3 + programming language (e.g., Python/Java/PHP) + MySQL database management system.