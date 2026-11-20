# 📝 Quiz Examination System

> **Học phần:** Công nghệ Phần mềm  
> **Giảng viên hướng dẫn:** Trần Thị Mỹ Tiên  
> **Nhóm thực hiện:** Nhóm 09  

## 📖 Giới thiệu dự án (Project Description)
**Quiz Examination System** là ứng dụng web tổ chức, quản lý và thực hiện các bài thi trắc nghiệm trực tuyến theo kiến trúc 3 lớp (**Three-Layer Architecture**). Hệ thống phục vụ ba nhóm người dùng chính:
* **Administrator (Quản trị viên):** Quản lý tài khoản người dùng (Student, Teacher), quản lý danh mục môn học và giám sát thống kê hệ thống.
* **Teacher (Giảng viên):** Quản lý đề cương (Syllabus), ngân hàng câu hỏi, cấu hình thời gian/thang điểm đề thi và theo dõi kết quả.
* **Student (Sinh viên):** Đăng ký, đăng nhập, tham gia làm bài thi trực tuyến có đồng hồ đếm ngược, tự động lưu đáp án và xem chi tiết kết quả ngay sau khi nộp bài.

---

## 👥 Thành viên nhóm & Phân công (Team Members)

Công việc được phân chia kế thừa từ giai đoạn Phân tích – Thiết kế sang Lập trình và **Kiểm thử chéo (Cross-Testing)** theo từng mã số sinh viên:

| STT | Họ và tên | Mã số sinh viên | Vai trò Stage 1 – 2 | Phân công Stage 3 (Implementation) & Stage 4 (Testing) |
| :---: | :--- | :---: | :--- | :--- |
| 1 | **Phan Văn Hưng** | `089205018167` | Trưởng nhóm / Requirements & Use Case | • **Tech Lead & Auth/Admin:** Dựng khung 3 lớp, quản lý Git/PR; code chức năng Đăng ký, Đăng nhập (hash password) & Quản lý User/Môn học.<br>• **Testing:** Viết Unit Test luồng thi (`test_exam_process.py`) và kiểm thử chéo module của Vinh. |
| 2 | **Nguyễn Thành Vinh** | `040205023121` | Phân tích DFD & Kiến trúc phần mềm | • **Backend Dev (Luồng thi trực tuyến):** Code module Sinh viên làm bài thi, đếm ngược thời gian, AJAX auto-save đáp án và tự nộp bài.<br>• **Testing:** Viết Unit Test module Giáo viên (`test_teacher_exam.py`) và kiểm thử chéo module của Long. |
| 3 | **Võ Bảo Long** | `040206001273` | Thiết kế Class Diagram & Database | • **DB & Backend Dev (Module Giáo viên):** Viết `schema.sql`, `seed_data.sql`, Data Layer (DAO); code quản lý Syllabus, Ngân hàng câu hỏi & Tạo đề.<br>• **Testing:** Viết Unit Test Auth/Admin (`test_auth_admin.py`) và kiểm thử chéo module của Hưng. |
| 4 | **Lưu Lương Gia Kỳ** | `091207001923` | Thiết kế Giao diện (GUI Design) | • **Frontend Dev (Presentation Layer):** Chuyển đổi 8 bản thiết kế `design/gui/` sang HTML/CSS/JS; ghép giao diện phòng thi & trang kết quả.<br>• **Testing:** Kiểm thử giao diện (UI/UX), luồng tương tác người dùng và độ tương thích hiển thị. |
| 5 | **Nguyễn Đăng Khoa** | `091207009078` | QA / Đặc tả Use Case & Tổng hợp | • **Backend Dev (Chấm điểm) & QA Lead:** Code logic tự động chấm điểm trắc nghiệm, xem lỗi sai & thống kê (`grading_service.py`).<br>• **Testing:** Viết `test_grading.py`, quản lý bộ Test Cases và điều phối **Defect Log** trên GitHub Issues. |

---

## 🚀 Các giai đoạn phát triển (Project Stages)

### Stage 1 – Analysis and Requirements Specification
* **Functional & Non-functional Requirements:** Đặc tả yêu cầu chức năng và phi chức năng cho 3 tác nhân (`Student`, `Teacher`, `Admin`). *(Chi tiết tại `docs/Requirement_and_Design_Document_Group09.pdf`)*
* **System Modeling:**
  * **Use Case Diagram:** Mô phỏng tương tác giữa các tác nhân và hệ thống (`docs/diagrams/Usecase.png`).
  * **Data Flow Diagram (DFD):** Mô tả luồng dữ liệu mức 0 và mức 1 (`docs/diagrams/DFD_Level_0.png`, `docs/diagrams/DFD.png`).
  * **Class Diagram:** Định nghĩa các lớp đối tượng và quan hệ (`docs/diagrams/Class.png`).

### Stage 2 – Design
* **GUI Design:** Thiết kế 8 màn hình giao diện người dùng (Login, Register, Admin Dashboard, Student Dashboard, Active Exam, Exam Results, Teacher Exam Management) tại thư mục `design/gui/`.
* **Software Architecture Design:** Áp dụng kiến trúc 3 lớp (**Three-Layer Architecture**) tách biệt `Presentation Layer`, `Business Logic Layer` và `Data Layer` (`design/architecture.md`).
* **Database Design:** Thiết kế lược đồ cơ sở dữ liệu quan hệ chuẩn hóa 12 bảng (`docs/diagrams/ERD.png` và `database/schema.sql`).

### Stage 3 – Implementation
* **Ngôn ngữ & Framework:** Python 3 (Flask), HTML5/CSS3/JavaScript và MySQL.
* **Tổ chức mã nguồn:** Triển khai đầy đủ 3 lớp trong thư mục `src/`, đảm bảo tính đóng gói, dễ bảo trì và mở rộng.
* **Quản lý phiên bản (Version Control):** Sử dụng GitHub Flow (`main`, `develop`, nhánh tính năng theo MSSV/module `feat/<mssv>-<module>`) kết hợp Pull Request để review code chéo giữa các thành viên.

### Stage 4 – Testing
* **Unit Testing:** Xây dựng bộ kiểm thử tự động bằng `pytest` trong thư mục `tests/` cho các nghiệp vụ cốt lõi (xác thực, tạo đề, lưu bài làm, tự động chấm điểm).
* **Cross-Testing & Defect Management:** Thực hiện kiểm thử chéo theo bảng phân công; mọi lỗi phát hiện được tạo **GitHub Issue** gắn nhãn `bug`, gán cho thành viên phụ trách sửa lỗi (`fix/issue-<id>`) và chỉ đóng sau khi QA kiểm tra lại (re-test).

---

## 🛠️ Công cụ và Công nghệ sử dụng (Tech Stack & Tools)
* **Ngôn ngữ & Backend:** Python 3, Flask, Werkzeug Security, MySQL Connector.
* **Frontend:** HTML5, CSS3, JavaScript (AJAX).
* **Database:** MySQL, MySQL Workbench.
* **Kiểm thử:** Pytest.
* **Phân tích & Thiết kế:** Draw.io, Figma.
* **Quản lý dự án & Source code:** Git, GitHub, GitHub Projects (Kanban), GitHub Issues.

---

## 📂 Cấu trúc thư mục (Repository Structure)

```text
📦 Quiz-exam-system-group09
 ┣ 📂 database                     # Script khởi tạo và dữ liệu mẫu MySQL (Stage 2 & 3)
 ┃ ┣ 📜 schema.sql                 # Script tạo 12 bảng chuẩn ERD
 ┃ ┗ 📜 seed_data.sql              # Dữ liệu mẫu (Admin, Teacher, Student, Đề thi)
 ┣ 📂 design                       # Tài liệu thiết kế chi tiết (Stage 2)
 ┃ ┣ 📂 database                   # File thiết kế CSDL
 ┃ ┣ 📂 gui                        # 8 file PDF thiết kế giao diện (Login, Exam, Result...)
 ┃ ┗ 📜 architecture.md            # Mô tả kiến trúc 3 lớp
 ┣ 📂 docs                         # Tài liệu phân tích & sơ đồ UML (Stage 1)
 ┃ ┣ 📂 diagrams                   # Class.png, DFD_Level_0.png, DFD.png, ERD.png, Usecase.png
 ┃ ┗ 📜 Requirement_and_Design_Document_Group09.pdf
 ┣ 📂 src                          # Mã nguồn ứng dụng Python 3 lớp (Stage 3)
 ┃ ┣ 📂 data_layer                 # Lớp 1: Kết nối MySQL & Truy vấn dữ liệu (DAO)
 ┃ ┣ 📂 business_layer             # Lớp 2: Xử lý nghiệp vụ (Auth, Teacher, Exam, Grading)
 ┃ ┣ 📂 presentation_layer         # Lớp 3: Flask Routes/API, Static (CSS/JS) & Templates (HTML)
 ┃ ┗ 📜 app.py                     # File khởi chạy hệ thống
 ┣ 📂 tests                        # Kiểm thử tự động với Pytest (Stage 4)
 ┃ ┣ 📜 test_auth_admin.py
 ┃ ┣ 📜 test_teacher_exam.py
 ┃ ┣ 📜 test_exam_process.py
 ┃ ┗ 📜 test_grading.py
 ┣ 📜 .gitignore
 ┣ 📜 requirements.txt
 ┗ 📜 README.md
