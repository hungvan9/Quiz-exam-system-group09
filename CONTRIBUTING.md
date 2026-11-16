# 🤝 Hướng dẫn Làm việc nhóm & Quy trình Phát triển (Stage 3 & Stage 4)
**Dự án:** Quiz Examination System — Nhóm 09  
**Repository:** `https://github.com/hungvan9/Quiz-exam-system-group09.git`

Tài liệu này quy định cách thức cài đặt môi trường, chia nhánh Git, chuẩn giao tiếp giữa các lớp code và quy trình kiểm thử chéo (Cross-Testing) cho 5 thành viên trong nhóm.

---

## 1. Bảng phân công nhiệm vụ & Nhánh làm việc theo MSSV

Mỗi thành viên phụ trách code một phân hệ độc lập trên nhánh riêng và **kiểm thử chéo** cho một thành viên khác:

| Thành viên & MSSV | Nhánh Git (`feat/...`) | File phụ trách chính (Stage 3) | Nhiệm vụ Kiểm thử chéo (Stage 4) |
| :--- | :--- | :--- | :--- |
| **Phan Văn Hưng**<br>`089205018167` | `feat/089205018167-auth-admin` | • `src/app.py`, `db_connection.py`<br>• `user_dao.py`, `auth_service.py`<br>• Routes & logic Auth, Admin (User/Subject) | • Review & Merge toàn bộ PR.<br>• Viết `tests/test_exam_process.py` và test luồng làm bài thi của **Vinh**. |
| **Nguyễn Thành Vinh**<br>`040204023121` | `feat/040204023121-take-exam` | • `attempt_result_dao.py` (phần Attempt)<br>• `exam_service.py` (vào thi, đếm ngược, AJAX auto-save, tự nộp bài) | • Viết `tests/test_teacher_exam.py` và test chức năng ngân hàng câu hỏi, tạo đề của **Long**. |
| **Võ Bảo Long**<br>`040206001273` | `feat/040206001273-teacher-exam` | • `database/schema.sql`, `seed_data.sql`<br>• `course_exam_dao.py`, `teacher_service.py` (Syllabus, QuestionBank, Exam) | • Viết `tests/test_auth_admin.py` và test chức năng đăng ký, phân quyền, quản lý User của **Hưng**. |
| **Lưu Lương Gia Kỳ**<br>`091207001923` | `feat/091207001923-frontend-ui` | • Toàn bộ `src/presentation_layer/templates/` và `static/` (CSS/JS) khớp với 8 file ở `design/gui/` | • Kiểm thử giao diện (UI/UX), luồng bấm nút, hiển thị đồng hồ & bảng câu hỏi trên trình duyệt. |
| **Nguyễn Đăng Khoa**<br>`091207009078` | `feat/091207009078-grading-qa` | • `attempt_result_dao.py` (phần Result)<br>• `grading_service.py` (chấm điểm tự động, xem lỗi sai, thống kê) | • Viết `tests/test_grading.py`.<br>• Quản lý toàn bộ **Defect Log** (GitHub Issues) và điều phối re-test. |

---

## 2. Hướng dẫn cài đặt môi trường lần đầu (Dành cho cả 5 thành viên)

Mở Terminal / Git Bash tại thư mục muốn lưu dự án và thực hiện lần lượt các bước sau:

```bash
# Bước 1: Clone repo về máy và chuyển sang nhánh tích hợp develop
git clone https://github.com/hungvan9/Quiz-exam-system-group09.git
cd Quiz-exam-system-group09
git checkout develop

# Bước 2: Tạo và kích hoạt môi trường ảo Python
python -m venv venv
# Nếu dùng Windows:
venv\Scripts\activate
# Nếu dùng Linux / macOS:
source venv/bin/activate

# Bước 3: Cài đặt thư viện
pip install -r requirements.txt
```

**Thiết lập Database MySQL:**
1. Mở MySQL Workbench (hoặc MySQL CLI) và chạy file `database/schema.sql` trước, sau đó chạy `database/seed_data.sql`.
2. Cấu hình thông tin tài khoản MySQL cục bộ của bạn trong file `src/data_layer/db_connection.py` (không commit mật khẩu cá nhân lên GitHub).

---

## 3. Quy trình Git & GitHub Workflow hàng ngày

### Bước 1: Tạo nhánh làm việc riêng từ `develop`
Tuyệt đối **không code trực tiếp trên `main` hoặc `develop`**. Trước khi bắt đầu làm, hãy cập nhật `develop` mới nhất rồi tách nhánh theo đúng MSSV của mình:

```bash
git checkout develop
git pull origin develop
git checkout -b feat/<mssv>-<ten-module>
# Ví dụ: git checkout -b feat/040204023121-take-exam
```

### Bước 2: Quy tắc viết code chuẩn Kiến trúc 3 lớp
Để tránh xung đột file (Merge Conflict) và đảm bảo điểm kiến trúc phần mềm:
* **`src/data_layer/` (DAO):** Chỉ chứa các câu lệnh SQL (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) và trả về dữ liệu dạng `dict` hoặc `list`. Không viết logic tính điểm hay kiểm tra điều kiện ở đây.
* **`src/business_layer/` (Service):** Chỉ gọi các hàm từ `data_layer`, xử lý nghiệp vụ (hash mật khẩu, kiểm tra hết giờ, tính điểm) và trả kết quả về cho `presentation_layer`.
* **`src/presentation_layer/` (Routes & Templates):** Nhận request từ người dùng, gọi hàm từ `business_layer` và render file HTML hoặc trả về JSON cho AJAX.

### Bước 3: Commit và đẩy code lên GitHub
Viết thông điệp commit rõ ràng theo tiền tố (`feat:`, `fix:`, `test:`, `style:`, `docs:`):

```bash
git add .
git commit -m "feat(exam): implement auto-save student answers API"
git push -u origin feat/<mssv>-<ten-module>
```

### Bước 4: Tạo Pull Request (PR) & Review chéo
1. Truy cập GitHub của nhóm -> Tab **Pull Requests** -> Bấm **New pull request**.
2. Chọn **`base: develop`** `<-` **`compare: feat/<mssv>-<ten-module>`**.
3. Trong phần **Reviewers** bên phải, chọn **Phan Văn Hưng** (Tech Lead) và **thành viên kiểm thử chéo** của bạn.
4. Sau khi được duyệt (Approve), Tech Lead sẽ bấm **Merge pull request** vào `develop`.

---

## 4. Quy ước dữ liệu liên kết giữa các thành viên (Integration Contracts)

Để code của 5 người ghép lại chạy mượt ngay từ lần đầu, cả nhóm thống nhất dùng chung các biến Session và Trạng thái sau:

* **Biến Flask `session` sau khi đăng nhập (Hưng cung cấp cho cả nhóm dùng):**
  * `session['user_id']`: `int` (ID trong bảng `Users`)
  * `session['role']`: `str` (`'STUDENT'`, `'TEACHER'`, hoặc `'ADMIN'`)
  * `session['name']`: `str` (Họ tên hiển thị trên thanh Header)
* **Trạng thái bài thi (`Exams`):** `'Draft'` | `'Published'` | `'Completed'` *(Long lưu đúng chuỗi này để Vinh chỉ lấy danh sách đề `'Published'` cho sinh viên thi).*
* **Trạng thái lượt thi (`Exam_Attempts.status`):** `'IN_PROGRESS'` | `'SUBMITTED'` | `'EXPIRED'` *(Vinh cập nhật sang `'SUBMITTED'` hoặc `'EXPIRED'` khi nộp bài để Khoa chạy hàm chấm điểm).*

---

## 5. Quy trình Kiểm thử & Quản lý lỗi (Stage 4 - Testing & Defect Log)

### Chạy Unit Test tự động
Mỗi thành viên viết các hàm kiểm thử trong file `tests/test_*.py` tương ứng với bảng phân công ở Mục 1. Chạy toàn bộ test bằng lệnh:

```bash
pytest -v
```

### Quy trình báo lỗi và sửa lỗi trên GitHub Issues (Bắt buộc)
Khi kiểm thử chéo phát hiện chức năng chạy sai hoặc lỗi giao diện:

1. **Người phát hiện lỗi (Tester):**
   * Vào tab **Issues** -> **New issue**.
   * Đặt tiêu đề ngắn gọn: `[BUG] Không tự nộp bài khi đồng hồ đếm ngược về 00:00`.
   * Nội dung mô tả rõ: **Các bước tái hiện (Steps to reproduce)**, **Kết quả thực tế**, và **Kết quả mong đợi**.
   * Gắn nhãn (`Labels`): chọn **`bug`**.
   * Giao việc (`Assignees`): chọn đúng thành viên phụ trách module đó.
2. **Người sửa lỗi (Developer):**
   * Tạo nhánh sửa lỗi từ `develop`: `git checkout -b fix/issue-<số-issue>`.
   * Sửa lỗi xong, tạo Pull Request vào `develop` và ghi dòng **`Closes #<số-issue>`** trong phần mô tả PR.
3. **Xác nhận đóng lỗi (Re-test):**
   * Sau khi PR được merge vào `develop`, Tester kéo code mới về chạy kiểm thử lại. Nếu lỗi đã hết mới xác nhận đóng Issue.