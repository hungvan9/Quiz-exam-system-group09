# lab1-group09
## 📖 Giới thiệu dự án
Dự án này là bài tập nhóm thuộc học phần Phân tích Thiết kế Hệ thống. Mục tiêu của đồ án là phân tích yêu cầu, định hình các tác nhân (Actors) và xây dựng **Biểu đồ Use Case (Use Case Diagram)** cùng **Tài liệu Đặc tả kịch bản (Use Case Specification)** cho hệ thống diễn đàn trao đổi học tập nội bộ.

Hệ thống cung cấp các chức năng cốt lõi bao gồm:
* Quản lý người dùng: Đăng ký, đăng nhập, quản lý thông tin thành viên.
* Quản lý nội dung: Soạn thảo, đăng tải bài viết, chủ đề thảo luận.
* Quản trị hệ thống: Kiểm duyệt bài đăng (chấp nhận/từ chối kèm lý do), xét duyệt thành viên mới.

## 👥 Thành viên nhóm & Phân công công việc
Nhóm gồm 5 thành viên, làm việc theo mô hình chuyên môn hóa kết hợp kiểm tra chéo (cross-review) để đảm bảo chất lượng hệ thống.

| STT | Họ và Tên | Vai trò trong dự án | Nhiệm vụ chính |
|:---:|---|---|---|
| 1 | **Phạm Văn Hưng** | Trưởng nhóm / Quản lý Báo cáo | Điều phối dự án, rà soát kiến trúc hệ thống tổng thể, chuẩn hóa logic các Use Case, tổng hợp và định dạng báo cáo tiểu luận cuối cùng. |
| 2 | **[Nhập tên TV 2]** | Chuyên viên Phân tích (Member) | Trích xuất Actor và Use Case cho luồng Khách và Thành viên (Xem tin, Đăng bài với text editor, Nhận thông báo duyệt bài). |
| 3 | **[Nhập tên TV 3]** | Chuyên viên Phân tích (Admin) | Phân tích nghiệp vụ Quản trị viên (Quy trình kiểm duyệt bài viết, Quản lý và phê duyệt quyền thành viên). |
| 4 | **[Nhập tên TV 4]** | Chuyên viên Thiết kế UML | Chuyển hóa dữ liệu phân tích thành biểu đồ Use Case trực quan, đảm bảo đúng chuẩn UML. |
| 5 | **[Nhập tên TV 5]** | Chuyên viên Viết Đặc tả | Soạn thảo tài liệu đặc tả (Mục đích, Tiền điều kiện, Luồng sự kiện chính/phụ) cho các Use Case cốt lõi. |

## 📂 Cấu trúc thư mục (Repository Structure)
```text
Forum-System-Analysis/
├── diagrams/                  # Chứa các file liên quan đến sơ đồ UML
│   ├── use-case-diagram.drawio    # File source sơ đồ Use Case (có thể chỉnh sửa)
│   └── use-case-export.png        # Ảnh sơ đồ đã xuất ra độ phân giải cao
├── docs/                      # Chứa tài liệu đặc tả và báo cáo
│   ├── use-case-specifications.docx # File tài liệu đặc tả chi tiết
│   └── final-report.pdf           # Báo cáo tiểu luận hoàn chỉnh
├── .gitignore                 # File cấu hình bỏ qua các file tạm cục bộ
└── README.md                  # Tài liệu giới thiệu tổng quan dự án
