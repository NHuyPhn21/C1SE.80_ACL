# KẾ HOẠCH VÀ BÁO CÁO KIỂM THỬ HỆ THỐNG (TEST PLAN & EXECUTION REPORT)
## Dự án: Automated Comic Localization (ACL) — Mã Đồ Án: C1SE.80
**Phiên bản tài liệu:** 1.0  
**Người thực hiện (QA / Tester / PO):** Phan Văn Quân  
**Người kiểm duyệt (Scrum Master / Backend Lead):** Phan Nhật Huy  
**Ngày cập nhật:** 17/11/2026  
**Phạm vi:** Sprint 1 & Sprint 2 Integration & End-to-End Verification  

---

## 1. TỔNG QUAN VÀ MỤC TIÊU KIỂM THỬ (OVERVIEW & OBJECTIVES)

Tài liệu này xác định kế hoạch kiểm thử, ma trận kịch bản kiểm thử (Test Matrix) và kết quả thực tế cho toàn bộ 8 màn hình chức năng chính của hệ thống phần mềm **Automated Comic Localization (ACL)**.

### Mục tiêu chính:
1. **Toàn vẹn luồng dữ liệu (Data Integrity):** Đảm bảo tính toán vẹn dữ liệu từ khâu nạp trang truyện gốc (Raw Manga Scans) qua pipeline AI đa tầng (YOLOv8 Bubble Detection ➔ Manga OCR ➔ User Review ➔ LaMa Inpainting ➔ Cloud LLM ➔ Canvas Typesetting).
2. **Bảo mật và phân quyền (RBAC Security):** Thực thi nghiêm ngặt phân quyền vai trò (Owner, Project Manager, Translator, Typesetter), chặn các thao tác trái phép (HTTP 403 Forbidden).
3. **Kiểm soát tính hợp lệ phía Client & Server (Validation & Conflict Prevention):**
   - Giới hạn số lượng trang tải lên ($\le 50$ ảnh/batch) và dung lượng tải lên ($\le 100$ MB/chapter).
   - Kiểm duyệt định dạng ảnh được hỗ trợ (`.jpg`, `.jpeg`, `.png`, `.webp`), từ chối file lạ với HTTP 415.
   - Chặn xung đột xoá Chapter hoặc dọn sạch dữ liệu khi tác vụ nền đang chạy (HTTP 409 Conflict).
4. **Tự động hoá kiểm thử (Automated Integration Testing):** Bổ sung test suite `tests/test_workspace_upload_integration.py` đạt 100% PASS trên môi trường tích hợp.

---

## 2. MÔI TRƯỜNG VÀ CÔNG CỤ KIỂM THỬ (TEST ENVIRONMENT & TOOLS)

| Thành phần | Đặc tả môi trường |
| :--- | :--- |
| **Hệ điều hành** | Windows 10/11 64-bit |
| **Backend Runtime** | Python 3.11.9, FastAPI 0.115+, Uvicorn 0.32+ (Port: 5000) |
| **Cơ sở dữ liệu** | SQLite 3 (`acl.db`), SQLAlchemy 2.0+ ORM |
| **Frontend Runtime** | Node.js v20+, React 19, TypeScript 5.8, Vite 6 (Port: 5173) |
| **Môi trường Test tự động** | `unittest`, `pytest`, `fastapi.testclient.TestClient` |
| **AI Modules (Mocked for Test)** | Ultralytics YOLOv8, Manga-OCR, Google Gemini API Client |
| **Dữ liệu mẫu kiểm thử** | Thư mục `D:\CAPSTONE1_PVQ\test_sample_data\` (ảnh `.jpg`, `.png`, file nén `.zip`, file giả lập lỗi `.txt`) |

---

## 3. TỔNG HỢP KẾT QUẢ KIỂM THỬ TỰ ĐỘNG (AUTOMATED TEST SUMMARY)

Bộ kiểm thử tích hợp tự động cho Workspace & Upload Pipeline được thực thi độc lập:
* **File kiểm thử:** `tests/test_workspace_upload_integration.py`
* **Thời gian thực thi:** 0.765 giây
* **Kết quả:** **7 / 7 Test Cases PASSED (100% OK)**

Toàn bộ test suite của dự án (Authentication, Team, Queue, Review, Settings, Typesetting, Workspace, Upload):
* **Lệnh chạy:** `python -m unittest discover -s tests`
* **Thời gian thực thi:** 10.467 giây
* **Kết quả:** **75 / 75 Tests PASSED (100% OK)**

---

## 4. MA TRẬN KỊCH BẢN KIỂM THỬ CHI TIẾT 8 MÀN HÌNH (DETAILED TEST MATRIX)

### MÀN HÌNH 1: AUTHENTICATION & ACCESS (XÁC THỰC NGƯỜI DÙNG)
| Test ID | Kịch bản kiểm thử | Các bước thực hiện | Kết quả kỳ vọng | Kết quả thực tế | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-AUTH-01** | Đăng nhập tài khoản hợp lệ | 1. Nhập email đã kích hoạt.<br>2. Nhập đúng mật khẩu.<br>3. Bấm **Sign In**. | Đăng nhập thành công, nhận JWT token, điều hướng tới Workspace. | Điều hướng tới Workspace, hiển thị đúng email user. | **PASS** |
| **TC-AUTH-02** | Đăng nhập sai thông tin | 1. Nhập email hợp lệ.<br>2. Nhập sai mật khẩu.<br>3. Bấm **Sign In**. | Báo lỗi `Invalid credentials`, không cấp quyền truy cập. | Hiển thị thông báo lỗi màu đỏ trên thẻ đăng nhập. | **PASS** |
| **TC-AUTH-03** | Đăng ký tài khoản mới | 1. Chuyển tab Register.<br>2. Nhập họ tên, email mới, mật khẩu $\ge 6$ ký tự.<br>3. Bấm Register. | Tạo mới user thành công, mật khẩu băm bcrypt, tự động đăng nhập. | User tạo thành công trong SQLite, vào thẳng Dashboard. | **PASS** |
| **TC-AUTH-04** | Đăng ký trùng email | 1. Đăng ký với email đã tồn tại trong hệ thống. | Hệ thống chặn đăng ký, trả về lỗi 400 `Email already registered`. | Hiển thị lỗi email đã tồn tại. | **PASS** |
| **TC-AUTH-05** | Quên mật khẩu & Đặt lại mật khẩu | 1. Bấm Forgot password.<br>2. Nhập email để nhận mã token reset.<br>3. Nhập token và mật khẩu mới. | Đặt lại mật khẩu thành công, token chỉ dùng 1 lần duy nhất. | Mật khẩu mới được cập nhật, đăng nhập lại thành công. | **PASS** |

---

### MÀN HÌNH 2: WORKSPACE & PROJECT MANAGEMENT (QUẢN LÝ DỰ ÁN)
| Test ID | Kịch bản kiểm thử | Các bước thực hiện | Kết quả kỳ vọng | Kết quả thực tế | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-WS-01** | Tạo dự án mới thành công | 1. Bấm `+ Create New Project`.<br>2. Nhập tiêu đề `"One Piece Volume 1"`.<br>3. Bấm Create. | Dự án xuất hiện trên Grid, người tạo nhận vai trò `Owner`. | Dự án hiển thị ngay lập tức với 0 pages hoàn thành. | **PASS** |
| **TC-WS-02** | Chặn trùng tên dự án cùng Owner | 1. Tạo lại dự án với tên `"One Piece Volume 1"` bằng cùng tài khoản. | Hệ thống từ chối với lỗi 400: *"You already own a project with this title."* | Modal báo lỗi đỏ, không tạo bản ghi trùng lặp. | **PASS** |
| **TC-WS-03** | Cho phép trùng tên khác Owner | 1. Tài khoản User B tạo dự án tên `"One Piece Volume 1"`. | Tạo thành công vì thuộc 2 chủ sở hữu độc lập. | User B quản lý dự án độc lập, không xung đột ID. | **PASS** |
| **TC-WS-04** | Tìm kiếm / Lọc dự án động | 1. Nhập từ khoá vào ô tìm kiếm trên Header (VD: `"Piece"`). | Grid tự lọc real-time chỉ hiển thị các thẻ khớp tiêu đề/mô tả. | Lọc chính xác, hiển thị trạng thái Empty nếu không có kết quả. | **PASS** |
| **TC-WS-05** | Cập nhật thông tin dự án (PUT) | 1. Bấm nút Sửa trên Project Card.<br>2. Sửa tiêu đề và mô tả.<br>3. Lưu thay đổi. | Dữ liệu cập nhật trên Grid và trong database. | Dự án cập nhật tên mới ngay lập tức. | **PASS** |
| **TC-WS-06** | Xoá toàn bộ dự án (DELETE) | 1. Bấm nút Xoá trên Project Card.<br>2. Xác nhận hộp thoại cảnh báo. | Xoá sạch dự án, danh sách chapter, page, OCR và file render. | Thẻ dự án biến mất khỏi Grid, thư mục data được dọn sạch. | **PASS** |

---

### MÀN HÌNH 3: TEAM COLLABORATION & RBAC (PHÂN QUYỀN NHÓM)
| Test ID | Kịch bản kiểm thử | Các bước thực hiện | Kết quả kỳ vọng | Kết quả thực tế | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-RBAC-01** | Mời thành viên với vai trò Translator / Typesetter | 1. Vào màn hình Team.<br>2. Nhập email đồng đội và chọn Role: `Translator`.<br>3. Bấm Invite. | Thành viên được thêm vào dự án với đúng quyền hạn được cấp. | Danh sách Team cập nhật thành viên mới kèm badge vai trò. | **PASS** |
| **TC-RBAC-02** | Chặn quyền Sửa/Xoá Project đối với Translator | 1. Đăng nhập tài khoản Translator.<br>2. Gửi request PUT hoặc DELETE tới `/api/projects/{id}`. | Hệ thống từ chối và trả về mã lỗi **403 Forbidden**. | Chặn thành công 403, Translator không có quyền xoá dự án. | **PASS** |
| **TC-RBAC-03** | Chặn quyền Sửa/Xoá Project đối với Typesetter | 1. Đăng nhập tài khoản Typesetter.<br>2. Gửi request PUT hoặc DELETE tới `/api/projects/{id}`. | Hệ thống từ chối và trả về mã lỗi **403 Forbidden**. | Chặn thành công 403, Typesetter không có quyền quản trị dự án. | **PASS** |
| **TC-RBAC-04** | Xoá thành viên khỏi nhóm | 1. Owner bấm nút Remove trên dòng thành viên. | Xoá quyền truy cập của thành viên khỏi dự án. | Thành viên bị loại bỏ ngay, không còn xem được dự án này. | **PASS** |

---

### MÀN HÌNH 4: CHAPTER STUDIO & UPLOAD PIPELINE (QUẢN LÝ CHAPTER & TẢI ẢNH)
| Test ID | Kịch bản kiểm thử | Các bước thực hiện | Kết quả kỳ vọng | Kết quả thực tế | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-UPL-01** | Tạo nhiều Chapter tự tăng số thứ tự | 1. Tạo Chapter 1.<br>2. Tạo Chapter 2.<br>3. Tạo Chapter 3. | Số `chapter_number` tự động tăng liên tục (1, 2, 3...). | Các chapter được đánh số chuẩn xác, không trùng lặp. | **PASS** |
| **TC-UPL-02** | Đảm bảo không trùng số khi xoá Chapter giữa chừng | 1. Xoá Chapter 2 ở giữa.<br>2. Tạo một Chapter tiếp theo. | Hệ thống lấy `max + 1`, tạo Chapter 4, không xung đột số đã có. | Chapter mới có số thứ tự an toàn, không đè dữ liệu. | **PASS** |
| **TC-UPL-03** | Tải lên các định dạng ảnh hợp lệ (`.jpg`, `.jpeg`, `.png`, `.webp`) | 1. Kéo thả file ảnh hợp lệ vào Dropzone.<br>2. Quan sát danh sách trang tải lên. | Hệ thống nhận diện hợp lệ, tự tăng `page_number` (1, 2, 3...). | Cả 4 định dạng đều được chấp nhận và hiển thị dung lượng. | **PASS** |
| **TC-UPL-04** | Từ chối file không phải ảnh (HTTP 415) | 1. Chọn file `.pdf`, `.txt` hoặc `.exe` tải lên. | Hệ thống chặn từ chối với lỗi **415 Unsupported Media Type**. | Giao diện hiển thị cảnh báo định dạng không hỗ trợ. | **PASS** |
| **TC-UPL-05** | Giới hạn số lượng trang ($\le 50$ files/batch) | 1. Chọn đồng thời 51 file ảnh để tải lên. | Giao diện chặn ngay lập tức: *"Cannot exceed 50 pages per batch"*. | Danh sách không nhận file vượt quá, hiển thị cảnh báo đỏ. | **PASS** |
| **TC-UPL-06** | Giới hạn dung lượng batch ($\le 100$ MB) | 1. Chọn file ảnh có tổng dung lượng $> 100$ MB. | Giao diện chặn: *"Total batch size exceeds 100MB limit"*. | Chặn thành công, ngăn tràn bộ nhớ máy chủ. | **PASS** |
| **TC-UPL-07** | Xoá lẻ từng file ảnh đã chọn | 1. Chọn 3 file ảnh.<br>2. Bấm nút ✕ ở dòng file thứ 2 trước khi bấm Run. | File thứ 2 bị loại khỏi danh sách, danh sách còn lại 2 file. | Xoá mượt mà, tổng số trang sẵn sàng tự giảm từ 3 về 2. | **PASS** |
| **TC-UPL-08** | Chặn xoá Chapter khi Pipeline đang chạy (HTTP 409) | 1. Khởi động AI Pipeline (QueueTask = RUNNING/QUEUED).<br>2. Gọi lệnh xoá Chapter. | Trả về mã lỗi **409 Conflict**: *"Cannot delete chapter while its pipeline is running."* | Thao tác xoá bị từ chối, dữ liệu đang xử lý được bảo vệ. | **PASS** |
| **TC-UPL-09** | Chặn dọn sạch dữ liệu khi Pipeline đang chạy (HTTP 409) | 1. Khởi động AI Pipeline.<br>2. Bấm `Clear old results` trên giao diện. | Trả về mã lỗi **409 Conflict**: *"Cannot clear project data while a pipeline is running."* | Hệ thống từ chối xoá, bảo vệ tiến trình ngầm. | **PASS** |

---

### MÀN HÌNH 5: QUEUE MONITOR STUDIO (THEO DÕI TIẾN TRÌNH AI)
| Test ID | Kịch bản kiểm thử | Các bước thực hiện | Kết quả kỳ vọng | Kết quả thực tế | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-QUE-01** | Bắt đầu chạy tiến trình AI | 1. Chọn Chapter đã có trang.<br>2. Bấm **Start AI Pipeline**. | Chuyển sang màn hình Queue, task chuyển trạng thái `QUEUED` ➔ `RUNNING`. | Tiến trình được kích hoạt, Progress bar bắt đầu chạy. | **PASS** |
| **TC-QUE-02** | Theo dõi 6 giai đoạn xử lý AI | 1. Quan sát Stepper: Detection ➔ OCR ➔ Review ➔ Inpainting ➔ Translation ➔ Typesetting. | Các step chuyển màu xanh tương ứng với tiến độ thực tế. | Hiển thị chính xác từng giai đoạn và thời gian xử lý. | **PASS** |
| **TC-QUE-03** | Dừng/Huỷ tiến trình an toàn | 1. Bấm nút dừng khi task đang chạy. | Task dừng lại, lưu log trạng thái FAILED/STOPPED. | Worker dừng luồng an toàn, không làm hỏng file gốc. | **PASS** |

---

### MÀN HÌNH 6: REVIEW STUDIO (XÉT DUYỆT & HIỆU CHÍNH TEXT)
| Test ID | Kịch bản kiểm thử | Các bước thực hiện | Kết quả kỳ vọng | Kết quả thực tế | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-REV-01** | Hiển thị khung bóng thoại (Bounding Boxes) | 1. Chọn một trang manga đã qua bước Bubble Detection. | Hiển thị toạ độ các khung bóng thoại trực quan trên ảnh. | Toạ độ vẽ chính xác, khớp với bóng thoại tiếng Nhật. | **PASS** |
| **TC-REV-02** | Chỉnh sửa nội dung OCR thô | 1. Click vào một khung text.<br>2. Sửa lại chữ tiếng Nhật nhận diện sai.<br>3. Bấm **Save Draft**. | Bản nháp OCR được lưu lại mà không cần dịch ngay lập tức. | Bản ghi `TextRegion` cập nhật nội dung văn bản mới. | **PASS** |
| **TC-REV-03** | Đánh cờ trang cần dịch lại (Flagging) | 1. Bấm nút **Flag for Review**. | Trang chuyển sang trạng thái `NEEDS_REVIEW`. | Trang được đánh dấu rõ ràng trong danh sách kiểm duyệt. | **PASS** |

---

### MÀN HÌNH 7: TYPESETTING STUDIO (ĐIỀU CHỈNH FONT & XUẤT BẢN)
| Test ID | Kịch bản kiểm thử | Các bước thực hiện | Kết quả kỳ vọng | Kết quả thực tế | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-TYP-01** | Thay đổi kích thước chữ (Font Size) | 1. Chọn khung thoại tiếng Việt.<br>2. Kéo thanh font size hoặc nhập số (VD: 18px ➔ 24px). | Chữ hiển thị co giãn tức thì, vừa vặn khung bóng thoại. | Canvas cập nhật layout chữ tiếng Việt không bị tràn viền. | **PASS** |
| **TC-TYP-02** | Căn lề văn bản (Alignment) | 1. Chọn căn trái (Left), giữa (Center), phải (Right). | Văn bản trong bóng thoại căn chỉnh đúng theo lựa chọn. | Căn lề chuẩn xác theo phong cách truyện tranh. | **PASS** |
| **TC-TYP-03** | Xuất trọn gói file Zip kết quả (Export) | 1. Bấm nút **Export Rendered Chapter**. | Tải về file `.zip` chứa toàn bộ các trang manga đã xoá chữ và gắn bản dịch tiếng Việt. | File zip giải nén mở xem ảnh sắc nét, đầy đủ thứ tự trang. | **PASS** |

---

### MÀN HÌNH 8: PERSONAL SETTINGS & SYSTEM LOGS (CẤU HÌNH & NHẬT KÝ)
| Test ID | Kịch bản kiểm thử | Các bước thực hiện | Kết quả kỳ vọng | Kết quả thực tế | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-SET-01** | Lưu API Key nhà cung cấp AI | 1. Vào Settings.<br>2. Nhập API Key Google Gemini.<br>3. Bấm **Test & Save**. | Kiểm tra kết nối thành công, lưu mã hoá trong cơ sở dữ liệu. | Thông báo kết nối hợp lệ, sẵn sàng dịch thuật tự động. | **PASS** |
| **TC-SET-02** | Quản lý thuật ngữ dịch tuỳ chỉnh (Glossary) | 1. Thêm thuật ngữ: `"Nakama"` ➔ `"Đồng đội"`.<br>2. Bấm Add Glossary. | Thuật ngữ được lưu và áp dụng ưu tiên trong các đợt dịch tới. | Bảng Glossary hiển thị bản ghi mới, cho phép sửa/xoá. | **PASS** |
| **TC-SET-03** | Xem và dọn dẹp nhật ký hệ thống (System Logs) | 1. Xem lịch sử log xử lý của pipeline.<br>2. Bấm **Clear Logs**. | Toàn bộ log cũ được làm sạch để giải phóng dung lượng. | Bảng log reset về rỗng, hệ thống hoạt động ổn định. | **PASS** |

---

## 5. KẾT LUẬN VÀ KIẾN NGHỊ (CONCLUSION & RECOMMENDATIONS)

1. **Đánh giá mức độ hoàn thiện:**
   * Hệ thống phần mềm ACL đã đạt mức độ hoàn thiện **100% các tiêu chí kiểm thử** của Sprint 1 và Sprint 2.
   * Toàn bộ 7 kịch bản kiểm thử tích hợp tự động cho Workspace & Upload Pipeline và 75 bài test toàn hệ thống đều đạt trạng thái **PASS**.
2. **Tuân thủ quy tắc kiến trúc:**
   * Không có xung đột giữa các nhánh phát triển.
   * Logic kiểm soát lỗi và mã HTTP chuẩn RESTful (400, 403, 404, 409, 415, 500) được thực thi nghiêm ngặt cả phía Backend lẫn giao diện Frontend.
3. **Sẵn sàng báo cáo:**
   * Tài liệu kiểm thử này và file báo cáo chi tiết đính kèm (`Document/C1SE.80_TestExecution_Workspace_Upload_1.0.docx`) đã sẵn sàng để nộp lên Hội đồng Đồ án Tốt nghiệp (Capstone Committee).

---
*Biên bản được lập tại Đà Nẵng, ngày 17 tháng 11 năm 2026.*  
**Đại diện QA / Tester:** Phan Văn Quân *(Đã ký)*  
**Trưởng nhóm / Backend Lead:** Phan Nhật Huy *(Đã duyệt)*
