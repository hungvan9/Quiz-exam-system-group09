# 📝 Quiz Examination System

> **Học phần:** [Công nghệ Phần mềm]
> **Giảng viên hướng dẫn:** Trần Thị Mỹ Tiên
> **Nhóm thực hiện:** Nhóm 09

## 📖 Giới thiệu dự án (Project Description)
Quiz Examination System là một ứng dụng phần mềm được xây dựng nhằm mục đích tổ chức, quản lý và thực hiện các bài thi trắc nghiệm trực tuyến. Hệ thống cung cấp các chức năng cho hai đối tượng người dùng chính:
*   **Administrator (Giảng viên/Quản trị viên):** Quản lý ngân hàng câu hỏi, tạo đề thi, thiết lập thời gian và xem thống kê kết quả.
*   **Student (Sinh viên/Học sinh):** Đăng nhập, tham gia làm bài thi trắc nghiệm với thời gian đếm ngược và xem điểm ngay sau khi nộp bài.

## 👥 Thành viên nhóm (Team Members)
| STT | Họ và tên | Mã số sinh viên | Vai trò / Phân công chính |
| :---: | :--- | :---: | :--- |
| 1 | Phan Văn Hưng | 089205018167 | Trưởng nhóm / Phân tích Requirements & Use Case |
| 2 | [Tên TV 2] | [MSSV] | Phân tích Luồng dữ liệu (DFD) & Kiến trúc phần mềm |
| 3 | [Tên TV 3] | [MSSV] | Thiết kế Cấu trúc (Class Diagram) & Database |
| 4 | [Tên TV 4] | [MSSV] | Thiết kế Giao diện (GUI Design) |
| 5 | [Tên TV 5] | [MSSV] | QA / Viết đặc tả Use Case & Tổng hợp tài liệu |

---

## 🚀 Các giai đoạn phát triển (Project Stages)

### Stage 1 – Analysis and Requirements Specification
*   **Functional & Non-functional Requirements:** Đặc tả yêu cầu hệ thống bằng ngôn ngữ tự nhiên (Xem chi tiết tại `docs/requirements.md`).
*   **System Modeling:**
    *   **Use Case Diagram:** Mô phỏng tương tác giữa người dùng (Actor) và hệ thống.
    *   **Data Flow Diagram (DFD):** Mô tả luồng dữ liệu của các tiến trình xử lý.
    *   **Class Diagram:** Định nghĩa các lớp đối tượng và mối quan hệ trong hệ thống.
    *   *(Các biểu đồ được lưu tại thư mục `docs/diagrams/`)*

### Stage 2 – Design
*   **GUI Design:** Thiết kế giao diện đồ họa người dùng (Wireframes/Mockups) nhằm mang lại trải nghiệm làm bài thi trực quan, dễ sử dụng. *(File thiết kế: `design/gui/`)*
*   **Software Architecture Design:** Áp dụng kiến trúc [Tên kiến trúc - ví dụ: MVC / 3-Tier] để tách biệt giao diện, logic xử lý và cơ sở dữ liệu.
*   **Database Design:** Thiết kế lược đồ cơ sở dữ liệu quan hệ (ERD), bao gồm các bảng, thuộc tính, khóa chính (PK), khóa ngoại (FK) và các mối quan hệ. *(File SQL/ERD: `design/database/`)*

---

## 🛠️ Công cụ và Công nghệ sử dụng (Tech Stack & Tools)
*   **Quản lý dự án & Source code:** GitHub, GitHub Projects (Kanban).
*   **Phân tích & Thiết kế biểu đồ:** Draw.io 
*   **Thiết kế Database:** MySQL Workbench.
*   **Thiết kế GUI:** Figma 
*   **Soạn thảo tài liệu:** Markdown, Microsoft Word.

---

## 📂 Cấu trúc thư mục (Repository Structure)
Quy ước lưu trữ file trên GitHub của nhóm để dễ dàng theo dõi:
```text
📦 Quiz-Examination-System
 ┣ 📂 docs                   # Tài liệu phân tích (Stage 1)
 ┃ ┣ 📂 diagrams             # File ảnh export của DFD, Use Case, Class Diagram
 ┃ ┣ 📜 requirements.md      # Đặc tả yêu cầu bằng văn bản
 ┃ ┗ 📜 usecase-specs.md     # Đặc tả chi tiết từng Use Case
 ┣ 📂 design                 # Tài liệu thiết kế (Stage 2)
 ┃ ┣ 📂 gui                  # Hình ảnh mockup/wireframe giao diện
 ┃ ┣ 📂 database             # File ERD (.png) và script tạo bảng (.sql)
 ┃ ┗ 📜 architecture.md      # Mô tả kiến trúc phần mềm
 ┗ 📜 README.md              # File thông tin chung của dự án
