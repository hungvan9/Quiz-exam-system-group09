# EVIDENCE OF TOOL USAGE AND TASK ASSIGNMENT
**Project:** Quiz Examination System  
**Group:** Group 09  

---

## 1. Phân công công việc nhóm (Task Assignment)

Công việc được phân chia kế thừa xuyên suốt từ Stage 1–2 (Phân tích & Thiết kế) sang Stage 3–4 (Lập trình & Kiểm thử chéo)[cite: 1]:

| STT | Họ và tên | Mã số sinh viên | Vai trò Stage 1 – 2 | Phân công Stage 3 (Implementation) & Stage 4 (Testing) |
| :-: | :--- | :---: | :--- | :--- |
| 1 | **Phan Văn Hưng** | `089205018167` | Trưởng nhóm / Requirements & Use Case[cite: 1] | • **Tech Lead & Auth/Admin:** Dựng khung 3 lớp, quản lý Git/PR; code chức năng Đăng ký, Đăng nhập (hash password) & Quản lý User/Môn học[cite: 1].<br>• **Testing:** Viết Unit Test luồng thi (`test_exam_process.py`) và kiểm thử chéo module của Vinh[cite: 1]. |
| 2 | **Nguyễn Thành Vinh** | `040205023121` | Phân tích DFD & Kiến trúc phần mềm[cite: 1] | • **Backend Dev (Luồng thi trực tuyến):** Code module Sinh viên làm bài thi, đếm ngược thời gian, AJAX auto-save đáp án và tự nộp bài[cite: 1].<br>• **Testing:** Viết Unit Test module Giáo viên (`test_teacher_exam.py`) và kiểm thử chéo module của Long[cite: 1]. |
| 3 | **Võ Bảo Long** | `040206001273` | Thiết kế Class Diagram & Database[cite: 1] | • **DB & Backend Dev (Module Giáo viên):** Viết `schema.sql`, `seed_data.sql`, Data Layer (DAO); code quản lý Syllabus, Ngân hàng câu hỏi & Tạo đề[cite: 1].<br>• **Testing:** Viết Unit Test Auth/Admin (`test_auth_admin.py`) và kiểm thử chéo module của Hưng[cite: 1]. |
| 4 | **Lưu Lương Gia Kỳ** | `091207001923` | Thiết kế Giao diện (GUI Design)[cite: 1] | • **Frontend Dev (Presentation Layer):** Chuyển đổi 8 bản thiết kế `design/gui/` sang HTML/CSS/JS; ghép giao diện phòng thi & trang kết quả[cite: 1].<br>• **Testing:** Kiểm thử giao diện (UI/UX), luồng tương tác người dùng và độ tương thích hiển thị[cite: 1]. |
| 5 | **Nguyễn Đăng Khoa** | `091207009078` | QA / Đặc tả Use Case & Tổng hợp[cite: 1] | • **Backend Dev (Chấm điểm) & QA Lead:** Code logic tự động chấm điểm trắc nghiệm, xem lỗi sai & thống kê (`grading_service.py`)[cite: 1].<br>• **Testing:** Viết `test_grading.py`, quản lý bộ Test Cases và điều phối Defect Log trên GitHub Issues[cite: 1]. |

---

## 2. Minh chứng sử dụng công cụ (Evidence of Tool Usage)

1. **Quản lý mã nguồn & làm việc nhóm (GitHub):**[cite: 1, 30]
   * Link Repository: `https://github.com/<username>/Quiz-exam-system-group09`
   * Minh chứng Commit, Branch & Pull Requests: `[Chèn ảnh chụp lịch sử Commit và Pull Requests trên GitHub của 5 thành viên]`[cite: 1]
   * Quản lý lỗi (Defect Log trên GitHub Issues): `[Chèn ảnh chụp tab Issues ghi nhận và xử lý bug]`[cite: 1]

2. **Phân tích & Thiết kế hệ thống (diagrams.net & Figma):**[cite: 30]
   * Dùng **diagrams.net** vẽ DFD Level 0, DFD Level 1, Use Case Diagram, Class Diagram và ERD (lưu tại `docs/diagrams/`)[cite: 30].
   * Dùng **Figma** thiết kế 8 màn hình giao diện (lưu tại `design/gui/`)[cite: 1, 30, 108].
   * `[Chèn ảnh chụp workspace diagrams.net và Figma]`

3. **Lập trình & Kiểm thử tự động (VS Code, Excel, pytest):**[cite: 30]
   * Dùng **VS Code** lập trình ứng dụng Python 3 lớp kết nối MySQL[cite: 5, 30].
   * Dùng **Excel** thiết kế bảng Test Cases theo đúng Testing Document Template (`TC01`...)[cite: 30, 105, 106].
   * Dùng **`pytest`** chạy 4 file Unit Test trong thư mục `tests/`[cite: 30, 109].
   * `[Chèn ảnh chụp màn hình Terminal chạy lệnh pytest pass toàn bộ test cases]`

4. **Đóng gói & Triển khai (Docker):**[cite: 30]
   * Sử dụng `Dockerfile` và `docker-compose.yml` để đóng gói ứng dụng Python và MySQL[cite: 5, 109].
   * `[Chèn ảnh chụp Terminal chạy lệnh docker-compose up --build hoặc Docker Desktop đang chạy container]`