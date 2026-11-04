# BẢNG ĐẶC TẢ VÀ KỊCH BẢN KIỂM THỬ (TEST CASES SPECIFICATION)
## DỰ ÁN: AUTOMATED COMIC LOCALIZATION (ACL - C1SE.80)

**Sinh viên thực hiện:** Phan Văn Quân (Frontend Lead / System Analyst)  
**Phân hệ (Module):** Quản trị Dự án, Phân quyền Nhóm, Giám sát Pipeline AI & Xuất bản ZIP  
**Các trang phụ trách:**  
- `pages/1_Workspace.py` (Workspace Dashboard & Quản lý Dự án Manga)  
- `pages/1_Team_Workspace.py` (Team Roles & Quản lý Thành viên Nhóm)  
- `pages/5_Queue_Monitor.py` (Queue Monitor, Stepper 7 Bước & Xuất bản File ZIP)  
- `utils/auth_session.py` (Bảo toàn Phiên Đăng nhập & Thoát Iframe)  
**Tệp mã nguồn kiểm thử tự động:**  
- `tests/test_quan_workspace_queue.py`  
- `tests/test_auth_session.py`  
**Môi trường & Công cụ kiểm thử:** Python 3.11.7, Pytest 9.1.1, SQLite 3, SQLAlchemy ORM, Windows 11  

---

## I. TỔNG QUAN KẾT QUẢ KIỂM THỬ TỰ ĐỘNG (AUTOMATED TEST SUMMARY)

### 1. Kết quả kiểm thử toàn diện toàn bộ dự án
Thực thi lệnh kiểm thử:
```powershell
.\venv\Scripts\python.exe -m pytest tests/
```
```text
============================= test session starts =============================
platform win32 -- Python 3.11.7, pytest-9.1.1, pluggy-1.7.0
rootdir: D:\ĐỒ ÁN CAPSTONE\CODE
plugins: anyio-4.14.2
collected 37 items

tests\test_auth_service.py .........                                     [ 24%]
tests\test_auth_session.py ...                                           [ 32%]
tests\test_error_handler.py ....                                         [ 43%]
tests\test_quan_workspace_queue.py .....                                 [ 56%]
tests\test_quota_service.py ....                                         [ 67%]
tests\test_review_service.py ..                                          [ 72%]
tests\test_settings_and_typesetting.py ...                               [ 81%]
tests\test_sqlite_auth_and_team.py ....                                  [ 91%]
tests\test_workspace_and_queue.py ...                                    [100%]

============================= 37 passed in 6.30s ==============================
```

### 2. Kết quả kiểm thử riêng các module của Phan Văn Quân
Thực thi lệnh kiểm thử chuyên sâu:
```powershell
.\venv\Scripts\python.exe -m pytest tests/test_quan_workspace_queue.py tests/test_auth_session.py -v
```
```text
tests/test_quan_workspace_queue.py::TestQuanWorkspaceAndQueue::test_queue_monitor_progress_metrics PASSED [ 12%]
tests/test_quan_workspace_queue.py::TestQuanWorkspaceAndQueue::test_queue_monitor_zip_bundling_and_manifest PASSED [ 25%]
tests/test_quan_workspace_queue.py::TestQuanWorkspaceAndQueue::test_team_workspace_invite_and_remove_member PASSED [ 37%]
tests/test_quan_workspace_queue.py::TestQuanWorkspaceAndQueue::test_workspace_create_project_and_owner_membership PASSED [ 50%]
tests/test_quan_workspace_queue.py::TestQuanWorkspaceAndQueue::test_workspace_duplicate_project_prevention PASSED [ 62%]
tests/test_auth_session.py::AuthSessionTests::test_refresh_keeps_existing_rotating_token_when_omitted PASSED [ 75%]
tests/test_auth_session.py::AuthSessionTests::test_refresh_replaces_rotated_refresh_token PASSED [ 87%]
tests/test_auth_session.py::AuthSessionTests::test_session_persistence_and_logout PASSED [100%]

============================== 8 passed in 3.10s ==============================
```
> **Đánh giá chung:** Tỷ lệ thành công đạt **100% (Pass rate: 100%)**. Toàn bộ các logic nghiệp vụ về SQLite, phân quyền nhân sự, tạo file ZIP nén và lưu phiên đăng nhập đều đạt chuẩn chất lượng sản phẩm Capstone.

---

## II. MA TRẬN TEST CASES CHI TIẾT (TEST CASE SPECIFICATION MATRIX)

### 1. Phân hệ Workspace Dashboard (`pages/1_Workspace.py`)

| Mã Test Case | Tên Chức Năng | Loại Test | Các Bước Thực Hiện (Test Steps) | Dữ Liệu Đầu Vào | Kết Quả Mong Đợi (Expected) | Kết Quả Thực Tế (Actual) | Trạng Thái |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: |
| **TC-WS-01** | Tạo dự án mới qua Modal Overlay | Integration / DB | 1. Bấm nút "+ Create Project"<br>2. Nhập thông tin bộ truyện<br>3. Bấm "Confirm Create" | `title`: "Chainsaw Man Chapter 150"<br>`desc`: "JP ➔ VI" | Tạo thành công 1 bản ghi trong bảng `projects` của file `acl.db`. | Bản ghi xuất hiện trong SQLite với đúng `owner_id`, `title`, `description`. | **PASSED** |
| **TC-WS-02** | Phân quyền tự động cho Chủ sở hữu | Business Logic | 1. Tạo project mới<br>2. Truy vấn bảng `project_memberships` | `project_id`: ID project vừa tạo<br>`user_id`: ID tài khoản đăng nhập | Tự động tạo bản ghi membership với vai trò `project_role = "Owner"`. | Tạo đúng 1 membership vai trò Owner cho người tạo. | **PASSED** |
| **TC-WS-03** | Hiển thị động thẻ dự án từ SQLite | Data Binding | 1. Mở trang Workspace<br>2. So sánh danh sách card với DB | Dữ liệu thực từ bảng `projects` trong `acl.db` | Hiển thị đúng các thẻ truyện thật, không hiển thị tên giả (Jujutsu, One Piece). | Hiển thị chính xác các truyện thật (`shinn`, v.v.). | **PASSED** |
| **TC-WS-04** | Nhận diện cấu hình phần cứng thật | System Metric | 1. Mở trang Workspace<br>2. Quan sát thẻ Runner Node ở góc trên | Đọc qua thư viện `socket` và `psutil` của Python | Hiển thị tên máy thật (`Node LAPTOP-KE2DT432`), RAM thật và số nhân CPU thật. | Hiển thị chính xác tên máy và dung lượng RAM của thiết bị đang chạy. | **PASSED** |
| **TC-WS-05** | Thoát iframe điều hướng Chapter Studio | UX / Navigation | 1. Bấm nút "Mở Chapter Studio ➔" trên thẻ dự án | Event click `navigateParent` | Toàn bộ cửa sổ trình duyệt chuyển sang `pages/2_Chapter_Studio.py?project=...`, không bị kẹt iframe. | Trình duyệt chuyển trang mượt mà, giữ nguyên tên dự án trên breadcrumb. | **PASSED** |
| **TC-WS-06** | Tìm kiếm dự án theo thời gian thực | Frontend DOM | 1. Nhập từ khóa vào ô tìm kiếm ở header | Từ khóa: `"shinn"` | Tự động ẩn các dự án không khớp, chỉ hiển thị dự án có chứa từ khóa. | Tìm kiếm client-side tức thì 0ms, không reload lại trang. | **PASSED** |

---

### 2. Phân hệ Quản trị Nhân sự & Phân quyền (`pages/1_Team_Workspace.py`)

| Mã Test Case | Tên Chức Năng | Loại Test | Các Bước Thực Hiện (Test Steps) | Dữ Liệu Đầu Vào | Kết Quả Mong Đợi (Expected) | Kết Quả Thực Tế (Actual) | Trạng Thái |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: |
| **TC-TEAM-01** | Mời thành viên mới vào dự án | Integration / DB | 1. Nhập email đồng nghiệp<br>2. Chọn vai trò "Translator"<br>3. Bấm "Gửi Lời Mời" | `email`: "colleague.trans@acl.vn"<br>`role`: "Translator" | Tự động tạo tài khoản (nếu chưa có) và thêm bản ghi vào `project_memberships`. | Bản ghi xuất hiện trong SQLite và bảng thành viên cập nhật ngay. | **PASSED** |
| **TC-TEAM-02** | Xóa thành viên khỏi dự án | DB Cascade | 1. Nhấn nút "Remove" tại dòng thành viên<br>2. Xác nhận hộp thoại Confirm | `member_id` của thành viên cần xóa | Bản ghi membership bị xóa khỏi bảng `project_memberships`, thành viên mất quyền. | Dòng thành viên biến mất khỏi giao diện, DB xóa sạch bản ghi. | **PASSED** |
| **TC-TEAM-03** | Khóa quyền xóa đối với Owner | Security Rule | 1. Quan sát dòng thành viên có vai trò `Owner` | Tài khoản chủ sở hữu dự án | Không hiển thị nút "Remove" hoặc nút bị vô hiệu hóa, ngăn chặn xóa nhầm Owner. | Dòng Owner hiển thị huy hiệu Trưởng nhóm và không có nút xóa. | **PASSED** |
| **TC-TEAM-04** | Bộ lọc danh sách theo vai trò (Tabs) | Frontend DOM | 1. Bấm tab "Translators"<br>2. Bấm tab "Typesetters"<br>3. Bấm tab "All Roles" | Tab click event | Bảng chỉ hiển thị các thành viên có vai trò tương ứng với tab được chọn. | Lọc client-side tức thì theo thuộc tính `data-role`. | **PASSED** |
| **TC-TEAM-05** | Cập nhật thẻ KPI Tổng thành viên | Dynamic Count | 1. Kiểm tra số lượng thành viên dự án<br>2. So sánh với thẻ KPI | Dữ liệu từ bảng `project_memberships` | Thẻ KPI hiển thị chính xác tổng số thành viên thực tế của dự án. | Hiển thị động theo thời gian thực khi thêm/xóa thành viên. | **PASSED** |

---

### 3. Phân hệ Giám sát Hàng đợi & Xuất bản (`pages/5_Queue_Monitor.py`)

| Mã Test Case | Tên Chức Năng | Loại Test | Các Bước Thực Hiện (Test Steps) | Dữ Liệu Đầu Vào | Kết Quả Mong Đợi (Expected) | Kết Quả Thực Tế (Actual) | Trạng Thái |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: |
| **TC-QUEUE-01** | Đóng gói ZIP nhị phân thật | File I/O / Binary | 1. Bấm nút "📁 Tải ZIP Toàn Bộ Chapter" | Các file ảnh `final_*.*` trong `data/rendered_pages/` | Trình duyệt tải về file ZIP hợp lệ chứa các trang truyện đã dịch và file manifest. | File ZIP mở được bằng WinRAR/7-Zip, ảnh hiển thị nguyên vẹn. | **PASSED** |
| **TC-QUEUE-02** | Tạo Release Manifest trong file ZIP | File Metadata | 1. Giải nén file ZIP đã tải về<br>2. Mở file `RELEASE_MANIFEST.txt` | Dữ liệu dự án, số trang, model AI | Manifest ghi rõ tên project, thời gian xuất bản, dung lượng và danh sách từng file ảnh. | File manifest có cấu trúc chuẩn chỉ, đầy đủ metadata. | **PASSED** |
| **TC-QUEUE-03** | Thông báo khi chưa có ảnh hoàn thành | UX / Validation | 1. Khi thư mục `data/rendered_pages/` rỗng<br>2. Bấm nút "Export ZIP" | 0 ảnh render | Hiển thị thông báo tiếng Việt lịch sự hướng dẫn người dùng vào Chapter Studio tải ảnh. | Bật popup thông báo rõ ràng, không bị crash code hay ném lỗi đỏ. | **PASSED** |
| **TC-QUEUE-04** | Phân trang bảng tác vụ (Pagination) | Interactive UI | 1. Khi danh sách ảnh > 5 trang<br>2. Bấm nút [ 2 ] hoặc [ > ] ở chân bảng | Số trang: 2, 3... | Bảng chuyển sang hiển thị các tác vụ của trang tiếp theo, nút trang sáng màu xanh. | Chuyển trang bảng mượt mà, phân trang đúng số lượng file. | **PASSED** |
| **TC-QUEUE-05** | Lọc trạng thái tác vụ hàng đợi | Frontend Filter | 1. Bấm tab "Queued"<br>2. Bấm tab "Completed"<br>3. Bấm tab "All" | Filter click event | Bảng lọc nhanh các dòng tác vụ theo đúng trạng thái được chọn. | Lọc client-side 0ms, không làm giật hay reload trang web. | **PASSED** |
| **TC-QUEUE-06** | Phòng ngự ngoại lệ Torch DLL (WinError 126) | Exception Handling | 1. Mở trang Queue Monitor trên máy không có CUDA/Torch C++ DLL | Máy Windows thông thường | Trang web vẫn nạp bình thường, bọc `try...except` an toàn, không bị crash màn hình đỏ. | Khắc phục triệt để lỗi `WinError 126 torch_python.dll`, mở trang ổn định. | **PASSED** |
| **TC-QUEUE-07** | Live Worker Terminal Stream | Console UI | 1. Quan sát hộp đen Terminal ở chân trang Queue Monitor | Thông số Worker và Hostname | Hiển thị log mô phỏng tiến trình AI (YOLOv8, OCR, Inpainting, Typesetting) với tên node thật. | Giao diện đen chuẩn JetBrains Mono hiển thị chuyên nghiệp. | **PASSED** |

---

### 4. Phân hệ Quản lý Phiên Đăng nhập & Điều hướng (`utils/auth_session.py`)

| Mã Test Case | Tên Chức Năng | Loại Test | Các Bước Thực Hiện (Test Steps) | Dữ Liệu Đầu Vào | Kết Quả Mong Đợi (Expected) | Kết Quả Thực Tế (Actual) | Trạng Thái |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: |
| **TC-AUTH-01** | Lưu phiên đăng nhập an toàn | Persistence | 1. Đăng nhập thành công<br>2. Kiểm tra file `data/.auth_session.json` | Token và thông tin User đăng nhập | Tự động tạo file `.auth_session.json` chứa thông tin phiên đăng nhập đã mã hóa. | File session được ghi thành công với trạng thái `authenticated: true`. | **PASSED** |
| **TC-AUTH-02** | Khôi phục phiên khi reload hoặc đổi trang | Session Recovery | 1. Đang ở Workspace, bấm F5 hoặc chuyển sang Queue Monitor | Streamlit WebSocket reconnect | Tự động đọc lại `.auth_session.json` và duy trì tài khoản, không bị văng ra trang Login. | Người dùng giữ nguyên trạng thái đăng nhập, trải nghiệm liền mạch. | **PASSED** |
| **TC-AUTH-03** | Đăng xuất triệt để (Clean Sign Out) | Session Cleanup | 1. Bấm nút "Sign Out" ở menu profile | Click Sign Out | Xóa sạch file `.auth_session.json`, xóa `st.session_state` và chuyển hướng về `0_Login.py`. | Người dùng bị đăng xuất an toàn, không thể back lại nếu chưa đăng nhập lại. | **PASSED** |

---

## III. KỊCH BẢN KIỂM THỬ TRỰC TIẾP (LIVE DEMO SCRIPT)
*Dành cho Phan Văn Quân khi trình diễn trực tiếp trước Giảng viên hướng dẫn hoặc Hội đồng bảo vệ Đồ án Capstone:*

### Bước 1 — Demo Quản lý Dự án (Workspace):
1. Mở trình duyệt tại địa chỉ `http://localhost:8501/workspace`.
2. Giới thiệu thẻ **Runner Node** góc phải: Hệ thống tự động nhận diện cấu hình thật của máy tính (`Node LAPTOP-KE2DT432`, RAM, số nhân CPU).
3. Bấm nút **"Create Project"** màu xanh.
4. Nhập tên dự án: `Chainsaw Man Chapter 150`, chọn cặp ngôn ngữ `Japanese ➔ Vietnamese`, bấm **"Confirm Create"**.
5. *Kết quả:* Thẻ truyện mới xuất hiện ngay trên bảng điều khiển. Mở SQLite kiểm tra thấy bảng `projects` và `project_memberships` đã được ghi dữ liệu sống thời gian thực.

### Bước 2 — Demo Quản trị Nhóm & Phân quyền (Team Roles):
1. Bấm nút nhóm hoặc mở menu `Team Roles`.
2. Nhập email đồng nghiệp: `colleague.trans@acl.vn`, chọn vai trò `Translator`, bấm **"Send Invite"**.
3. *Kết quả:* Dòng thành viên mới xuất hiện ngay lập tức trong bảng, thẻ KPI `TOTAL MEMBERS` tự động tăng lên.
4. Thử bấm nút **"Remove"** trên một thành viên để minh họa tính năng thu hồi quyền thành công.

### Bước 3 — Demo Giám sát Tiến trình & Xuất bản ZIP (Queue Monitor):
1. Chuyển sang trang `Queue Monitor`.
2. Trình bày **Quy trình 7 bước AI Localization Pipeline** trên thanh Stepper chuẩn.
3. Minh họa tính năng **Phân trang bảng** bằng cách bấm các nút `[ 1 ]`, `[ 2 ]`, `[ > ]`.
4. Bấm nút **"📁 Export ZIP"**: Trình duyệt tải ngay file ZIP hoàn chỉnh về máy tính.
5. Mở file ZIP để hội đồng thấy rõ cấu trúc các file ảnh manga đã dịch và file `RELEASE_MANIFEST.txt` được đóng gói tự động.

### Bước 4 — Demo Kiểm thử Tự động (Automated Pytest):
1. Mở terminal PowerShell và thực thi:
   ```powershell
   .\venv\Scripts\python.exe -m pytest tests/test_quan_workspace_queue.py tests/test_auth_session.py -v
   ```
2. *Kết quả:* Cả 8/8 tests chuyên sâu của phân hệ Frontend đều hiển thị tích xanh `PASSED 100%`.
