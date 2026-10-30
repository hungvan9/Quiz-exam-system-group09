# Software Architecture Document
**Project:** Quiz Examination System  

## 1. Architectural Pattern
The system is designed based on the **MVC (Model-View-Controller)** / **3-Tier Architecture** pattern to separate the user interface, business logic, and database layer. This ensures scalability, security, and maintainability.

## 2. System Layers (3-Tier Architecture)

### 2.1. Presentation Layer (Client-Side / View)
*   **Role:** Handles user interaction, displays data (quizzes, results), and receives user input.
*   **Technologies:** HTML5, CSS3, JavaScript.
*   **Access:** Accessed via Web Browser by Students, Teachers, and Admins.

### 2.2. Application Layer (Server-Side / Controller)
*   **Role:** Processes business logic (Authentication, Timer calculation, Auto-grading, Session management). It acts as a bridge between the Presentation Layer and the Data Layer.
*   **Technologies:** [Điền ngôn ngữ Backend của nhóm vào đây, ví dụ: Python (Flask/Django) / PHP / Java].

### 2.3. Data Layer (Database / Model)
*   **Role:** Stores and manages system data safely (User accounts, Question banks, Exam results).
*   **Technologies:** MySQL Database.

## 3. Communication Flow
1. The user (Client) sends an HTTP Request (e.g., Submit Exam) through the Web Browser.
2. The Server intercepts the request, processes the answers, and calculates the score.
3. The Server interacts with the MySQL Database to store the results.
4. The Database returns a success status.
5. The Server sends an HTTP Response back to the Client to display the final score.