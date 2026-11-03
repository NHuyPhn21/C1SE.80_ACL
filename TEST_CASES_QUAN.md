# BẢNG ĐẶC TẢ VÀ KỊCH BẢN KIỂM THỬ (TEST CASES SPECIFICATION)
## DỰ ÁN: AUTOMATED COMIC LOCALIZATION (ACL - C1SE.80)
**Sinh viên phụ trách:** Phan Văn Quân (Frontend Lead / System Analyst)  
**Phân hệ (Module):** Module Dàn trang & Giám sát Tiến trình & Quản trị Nhân sự  
**Trang phụ trách:**  
- `pages/1_Workspace.py` (Workspace Dashboard & Quản lý Dự án)  
- `pages/1_Team_Workspace.py` (Team Roles & Quản lý Thành viên)  
- `pages/5_Queue_Monitor.py` (Queue Monitor & Xuất bản Chapter ZIP)  
**File mã nguồn kiểm thử tự động:** `tests/test_quan_workspace_queue.py`  
**Công cụ kiểm thử:** Python 3.11, Pytest 9.1.1, SQLAlchemy ORM, SQLite  

---

## I. TỔNG QUAN KẾT QUẢ KIỂM THỬ TỰ ĐỘNG (AUTOMATED TEST SUMMARY)

Lệnh thực thi kiểm thử toàn bộ dự án:
```powershell
.\venv\Scripts\python.exe -m pytest tests/ -v
```

Kết quả thực tế:
```text
============================= test session starts =============================
platform win32 -- Python 3.11.7, pytest-9.1.1, pluggy-1.7.0
rootdir: D:\ĐỒ ÁN CAPSTONE\CODE
collected 24 items

tests/test_auth_service.py::AuthServiceTests::... PASSED                        [ 33%]
tests/test_auth_session.py::AuthSessionTests::... PASSED                        [ 41%]
tests/test_error_handler.py::... PASSED                                         [ 58%]
tests/test_quota_service.py::... PASSED                                         [ 79%]
tests/test_quan_workspace_queue.py::TestQuanWorkspaceAndQueue::test_queue_monitor_progress_metrics PASSED [ 83%]
tests/test_quan_workspace_queue.py::TestQuanWorkspaceAndQueue::test_queue_monitor_zip_bundling_and_manifest PASSED [ 87%]
tests/test_quan_workspace_queue.py::TestQuanWorkspaceAndQueue::test_team_workspace_invite_and_remove_member PASSED [ 91%]
tests/test_quan_workspace_queue.py::TestQuanWorkspaceAndQueue::test_workspace_create_project_and_owner_membership PASSED [ 95%]
tests/test_quan_workspace_queue.py::TestQuanWorkspaceAndQueue::test_workspace_duplicate_project_prevention PASSED [100%]

============================== 24 passed in 4.29s ==============================
```
> **Đánh giá:** 24/24 Test cases đạt tỷ lệ thành công 100% (Pass rate: 100%), không có lỗi cú pháp, không có ngoại lệ runtime.

---

## II. MA TRẬN ĐẶC TẢ TEST CASES CHI TIẾT (TEST CASE MATRIX)

### 1. Phân hệ Workspace (`pages/1_Workspace.py`)

| Mã Test Case | Tên Chức Năng | Loại Kiểm Thử | Các Bước Thực Hiện (Test Steps) | Dữ Liệu Đầu Vào (Test Data) | Kết Quả Mong Đợi (Expected Result) | Kết Quả Thực Tế (Actual Result) | Trạng Thái |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: |
| **TC-WS-01** | Tạo dự án mới qua Modal | Integration / DB | 1. Mở modal "Create New Project"<br>2. Nhập tiêu đề, mô tả, chọn cặp ngôn ngữ<br>3. Nhấn "Create Project" | `title`: "Bleach Rebirth"<br>`desc`: "20 pages"<br>`langs`: JA ➔ VI | Tạo thành công 1 bản ghi mới trong bảng `projects` của file `acl.db`. | Bản ghi xuất hiện trong SQLite với đúng `owner_id`, `title`, `description`. | **PASSED** |
| **TC-WS-02** | Phân quyền Owner tự động | Business Logic | 1. Sau khi tạo project mới ở TC-WS-01<br>2. Kiểm tra bảng `project_memberships` | `project_id`: ID của project vừa tạo<br>`user_id`: ID user đăng nhập | Tự động tạo bản ghi trong bảng `project_memberships` với `project_role = "Owner"`. | Tạo đúng 1 membership vai trò Owner cho người tạo. | **PASSED** |
| **TC-WS-03** | Hiển thị động danh sách Cards | UI / Data Binding | 1. Truy cập trang Workspace<br>2. Kiểm tra danh sách thẻ truyện hiển thị | Dữ liệu từ bảng `projects` trong SQLite | Mỗi dự án trong database được hiển thị thành 1 Card riêng biệt với live progress, link Live Queue. | Render đầy đủ các Card tương ứng số lượng bản ghi DB. | **PASSED** |
| **TC-WS-04** | Cập nhật thẻ KPI Active Projects | UI / Dynamic Count | 1. Đếm số lượng dự án trong DB<br>2. Kiểm tra số hiển thị trên thẻ KPI "Active Projects" | Tổng số dự án: $N$ | Thẻ KPI hiển thị chính xác con số $N$ tương ứng (`{active_projects_count}`). | Hiển thị động theo thời gian thực khi có thêm dự án mới. | **PASSED** |
| **TC-WS-05** | Bộ lọc tìm kiếm dự án theo tên | Frontend UI | 1. Nhập từ khóa vào ô Search Header<br>2. Quan sát danh sách cards | Từ khóa: `"One Piece"` | Ẩn các card không chứa từ khóa, chỉ hiển thị card "One Piece — Chapter 1115". | Lọc client-side mượt mà theo `data-title`. | **PASSED** |

---

### 2. Phân hệ Quản trị Nhân sự & Phân quyền (`pages/1_Team_Workspace.py`)

| Mã Test Case | Tên Chức Năng | Loại Kiểm Thử | Các Bước Thực Hiện (Test Steps) | Dữ Liệu Đầu Vào (Test Data) | Kết Quả Mong Đợi (Expected Result) | Kết Quả Thực Tế (Actual Result) | Trạng Thái |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: |
| **TC-TEAM-01** | Thêm thành viên ("Send Invite") | Integration / DB | 1. Nhập email đồng nghiệp<br>2. Chọn vai trò (Translator/Typesetter)<br>3. Bấm "Send Invite" | `email`: "colleague@acl.vn"<br>`role`: "Translator" | 1. Tạo tài khoản User (nếu chưa có)<br>2. Thêm bản ghi mới vào `project_memberships` với `project_role = "Translator"`. | Bản ghi mới lưu thành công vào SQLite. Huy hiệu số lượng tăng lên. | **PASSED** |
| **TC-TEAM-02** | Xóa thành viên khỏi dự án | Integration / DB | 1. Bấm nút "Remove" tại hàng thành viên cần xóa<br>2. Xác nhận hộp thoại | `membership_id` của thành viên cần xóa | Bản ghi tương ứng bị xóa hoàn toàn khỏi bảng `project_memberships`. | Bản ghi bị xóa khỏi SQLite, bảng trên giao diện cập nhật giảm 1 người. | **PASSED** |
| **TC-TEAM-03** | Khóa quyền xóa đối với Owner / PM | Security / Rule | 1. Quan sát cột Action tại hàng của Project Manager / Owner | `role`: "Project Manager" hoặc "Owner" | Không hiển thị nút "Remove", hiển thị huy hiệu cố định "Owner". | Không có nút Remove, ngăn chặn xóa nhầm chủ dự án. | **PASSED** |
| **TC-TEAM-04** | Bộ lọc danh sách theo vai trò (Tabs) | Frontend UI | 1. Nhấn tab "Translators"<br>2. Nhấn tab "Typesetters"<br>3. Nhấn tab "All Roles" | Tab click event | Bảng lọc chỉ hiển thị các thành viên có vai trò tương ứng với tab được chọn. | Lọc chính xác theo thuộc tính `data-role`. | **PASSED** |
| **TC-TEAM-05** | Cập nhật thẻ KPI TOTAL MEMBERS | UI / Dynamic Count | 1. Kiểm tra số lượng thành viên dự án<br>2. So sánh với số trên thẻ KPI | Tổng số thành viên: $M$ | Thẻ KPI hiển thị chính xác số $M$ (`{total_members_count}`). | Hiển thị động đồng bộ với badge bảng. | **PASSED** |

---

### 3. Phân hệ Giám sát Hàng đợi & Xuất bản (`pages/5_Queue_Monitor.py`)

| Mã Test Case | Tên Chức Năng | Loại Kiểm Thử | Các Bước Thực Hiện (Test Steps) | Dữ Liệu Đầu Vào (Test Data) | Kết Quả Mong Đợi (Expected Result) | Kết Quả Thực Tế (Actual Result) | Trạng Thái |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: |
| **TC-QUEUE-01** | Đóng gói ZIP nhị phân thật | File I/O / Binary | 1. Bấm nút "Download Chapter (ZIP)" trên giao diện | Thư mục `data/rendered_pages/` chứa các ảnh `final_*.*` | Trình duyệt tải về file `{Project}_Vietnamese_Export.zip` hợp lệ, giải nén ra đầy đủ các trang ảnh thật và file manifest. | File ZIP mở được bằng WinRAR/7-Zip, không bị lỗi corrupted archive. | **PASSED** |
| **TC-QUEUE-02** | Khởi tạo Release Manifest trong file ZIP | File I/O / Metadata | 1. Mở file ZIP đã tải về<br>2. Đọc file `RELEASE_MANIFEST.txt` | Dữ liệu dự án, số trang, model AI | File manifest chứa tên dự án, thời gian xuất bản, danh sách file và dung lượng từng trang. | File `RELEASE_MANIFEST.txt` có cấu trúc rõ ràng, đúng chuẩn xuất bản. | **PASSED** |
| **TC-QUEUE-03** | Hiển thị thanh tiến độ Progress Bar | UI / Math Calc | 1. Kiểm tra dự án có 18/24 trang hoàn thành | `total`: 24, `processed`: 18 | Tiến độ hiển thị chính xác 75%, thanh tiến độ màu xanh đạt độ rộng 75%. | Thanh tiến độ hiển thị đúng `75%`, animation mượt mà. | **PASSED** |
| **TC-QUEUE-04** | Chuyển đổi màn hình (Tab Switching) | Frontend UX | 1. Bấm tab "Live Pipeline Queue"<br>2. Bấm tab "Completed Chapter & ZIP Export" | Tab navigation click | Hiển thị đúng khối nội dung tương ứng (Pipeline 7 bước vs Banner hoàn thành xuất file ZIP). | Chuyển đổi mượt mà, không giật lag. | **PASSED** |
| **TC-QUEUE-05** | Giả lập tiến trình ("Simulate Step") | Interactive JS | 1. Bấm nút "Simulate Step" liên tục cho đến khi đạt 100% | Click event | Tăng dần số trang đã xử lý, khi đạt 100% tự động kích hoạt view Completed và thông báo tải ZIP. | Hoạt động chính xác, tự động chuyển view khi hoàn thành. | **PASSED** |

---

## III. KỊCH BẢN KIỂM THỬ GIAO DIỆN TRỰC TIẾP (LIVE DEMO SCRIPT)

Dành cho Phan Văn Quân khi trình diễn trực tiếp cho Leader Huy hoặc Giảng viên hướng dẫn:

1. **Bước 1 — Demo Workspace:**
   * Mở trình duyệt tại `http://localhost:8501/workspace`.
   * Bấm nút **"Create Project"** màu xanh ở góc trên bên phải.
   * Nhập tên: `Chainsaw Man — Part 2`, chọn ngôn ngữ `Japanese ➔ Vietnamese`, bấm nút tạo.
   * *Quan sát:* Thẻ dự án mới xuất hiện ngay đầu danh sách, thẻ KPI Active Projects tự động tăng thêm 1. Mở database SQLite kiểm tra thấy có dòng mới trong bảng `projects`.

2. **Bước 2 — Demo Team Workspace:**
   * Bấm vào nút nhóm bạn bè trên thẻ dự án vừa tạo (hoặc vào menu `Team Roles`).
   * Nhập email đồng nghiệp: `nguyen.typesetter@acl.vn`, chọn vai trò `Typesetter`, bấm **"Send Invite"**.
   * *Quan sát:* Dòng thành viên mới xuất hiện trong bảng, thẻ KPI `TOTAL MEMBERS` nhảy số tương ứng. Thử bấm **"Remove"** để thấy bản ghi được thu hồi quyền sạch sẽ.

3. **Bước 3 — Demo Queue Monitor:**
   * Vào menu `Queue Monitor`.
   * Quan sát thanh Progress Bar 75% cùng 7 bước pipeline xử lý AI.
   * Chuyển sang tab **"Completed Chapter & ZIP Export"** và bấm nút **"Download Chapter (ZIP)"**.
   * *Quan sát:* Trình duyệt tải ngay file ZIP về máy. Mở file ZIP ra thấy bên trong có thư mục `pages/` chứa các trang truyện manga đã hoàn thành và file `RELEASE_MANIFEST.txt` chuẩn chỉ.

4. **Bước 4 — Demo Unit Tests:**
   * Mở Terminal chạy:
     ```powershell
     .\venv\Scripts\python.exe -m pytest tests/test_quan_workspace_queue.py -v
     ```
   * *Quan sát:* Màn hình hiển thị 5/5 bài kiểm thử `PASSED` với tích xanh 100%.
