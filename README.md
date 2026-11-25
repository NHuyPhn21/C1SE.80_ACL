# ACL — Automated Comic Localization (C1SE.80)

Hệ thống Web hỗ trợ dịch thuật và biên tập truyện tranh tự động từ tiếng Nhật sang tiếng Việt (**YOLOv8 Bubble Detection → MangaOCR → Interactive Review → LaMa Inpainting → Gemini Batch Translation + Custom Glossary → Collision-Aware Typesetting**).

---

## 1. Yêu cầu hệ thống & Cài đặt môi trường

- **Python 3.11** (khuyến nghị chạy trên Windows 10/11 64-bit, hỗ trợ GPU CUDA nếu có).
- **Node.js 20+** và **npm**.
- File trọng số YOLOv8 đặt tại: `models/yolo/manga_v14/weights/best.pt`.

### Cài đặt Backend (Python)

Mở PowerShell tại thư mục gốc của dự án:

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

*(Nếu PowerShell chặn chạy script lần đầu, chạy lệnh: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`)*

Khởi tạo cơ sở dữ liệu SQLite (`acl.db`):

```powershell
python setup_db.py
```

Sao chép file cấu hình mẫu `.env.example` sang `.env` và cập nhật biến môi trường cần thiết:

```powershell
Copy-Item .env.example .env
```

### Cài đặt Frontend (React + TypeScript + Vite)

```powershell
cd frontend
npm install
cd ..
```

---

## 2. Chạy ứng dụng ở chế độ Development (2 cổng)

Bạn có thể bấm đúp trực tiếp vào 2 file `.bat` ở thư mục gốc hoặc mở 2 cửa sổ PowerShell:

- **Terminal 1 — Backend FastAPI (`http://127.0.0.1:5000`)**:
  ```powershell
  .\run_backend.bat
  ```
  *(Hoặc: `.\venv\Scripts\python.exe -m uvicorn fastapi_app:app --reload --host 127.0.0.1 --port 5000`)*

- **Terminal 2 — Frontend Vite (`http://localhost:5173`)**:
  ```powershell
  .\run_frontend.bat
  ```
  *(Hoặc: `npm --prefix frontend run dev`)*

Truy cập:
- **Giao diện Web ACL**: `http://localhost:5173`
- **Tài liệu API Swagger UI**: `http://127.0.0.1:5000/docs`
- **Health Check**: `http://127.0.0.1:5000/health`

---

## 3. Chạy chế độ Production / Demo 1 cổng duy nhất (Single-Port Deployment)

Khi đã build Frontend (`frontend/dist`), FastAPI (`fastapi_app.py`) tự động phục vụ luôn cả giao diện React SPA lẫn API và ảnh `/media` trên cùng 1 cổng `5000` (rất tiện khi public qua Cloudflare Tunnel / ngrok hoặc đóng gói):

```powershell
npm --prefix frontend run build
.\venv\Scripts\python.exe -m uvicorn fastapi_app:app --host 0.0.0.0 --port 5000
```

Sau đó mở trực tiếp `http://127.0.0.1:5000` trên trình duyệt.

---

## 4. Kiến trúc thư mục

```text
ai_core/         Mô-đun AI: YOLOv8 Detection, MangaOCR, Gemini Translation + Glossary
backend/         FastAPI routes (api.py), SQLAlchemy ORM (models.py), Queue Worker, Image Inpainting & Typesetting
services/        Tầng nghiệp vụ: Auth, Workspace, Team RBAC, Queue & ZIP Export, Review, Typesetting, Settings & Quota
models/          Domain models dùng chung (ApiError, Quota...)
frontend/        Ứng dụng React 19 + TypeScript + Vite (8 màn hình Studio)
assets/fonts/    Bộ font tiếng Việt chuyên dụng cho truyện tranh
data/            Thư mục lưu ảnh gốc upload, ảnh xoá chữ và ảnh xuất bản (gitignored)
tests/           Bộ 73+ Unit & Integration Tests tự động
docs/            Tài liệu Kiểm thử (Test Plan) & Tài liệu tham chiếu Kiến trúc / CSDL
```

---

## 5. Các tính năng nổi bật

1. **Xác thực & Khôi phục mật khẩu**: Đăng ký, đăng nhập (mật khẩu băm an toàn), quên mật khẩu và đặt lại mật khẩu qua token một lần (`/reset-password?token=...`).
2. **Quản lý Đa Dự án & Đa Chương (Multi-Chapter Workspace)**: Tạo/sửa/xoá Project, tạo nhiều Chapter tự tăng số thứ tự, kiểm tra định dạng & giới hạn batch upload (`<= 50 trang`, `<= 100MB`).
3. **Làm việc nhóm & Phân quyền RBAC**: 4 vai trò (`Owner`, `Project Manager`, `Translator`, `Typesetter`) được kiểm soát quyền chặt chẽ ở cả UI lẫn API.
4. **Queue Monitor thời gian thực qua SSE**: Luồng **Server-Sent Events (`GET /api/projects/{id}/queue/stream`)** đẩy tiến độ xử lý từng trang và System Logs tức thì, tự động fallback về polling khi mất mạng.
5. **Interactive Review Studio**: Kéo/thả/vẽ mới/xoá & hoàn tác (Undo) khung bóng thoại trực tiếp trên trang truyện, lưu nháp OCR (`Save OCR Draft`), gắn cờ kiểm duyệt (`Flag Page`), điều hướng nhanh bằng phím `←` / `→`.
6. **Typesetting Studio & Xuất bản ZIP**: Tuỳ chỉnh lời thoại tiếng Việt, cỡ chữ, căn lề (`left | center | right`), tải ảnh lẻ hoặc đóng gói ZIP theo Chapter kèm `RELEASE_MANIFEST.txt`.
7. **Personal Settings, Custom Glossary & API Quota Enforcement**: Lưu Gemini API Key mã hoá Fernet, CRUD từ điển thuật ngữ riêng theo từng bộ truyện, dọn dẹp System Logs và kiểm soát hạn mức tháng (HTTP `429 Too Many Requests`).

---

## 6. Chạy kiểm thử tự động (Automated Tests)

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_api_quota.py tests/test_quota_http.py tests/test_queue_stream.py tests/test_workspace_upload_integration.py tests/test_review_typeset_api.py tests/test_workspace_and_queue.py tests/test_quan_workspace_queue.py tests/test_settings_and_typesetting.py tests/test_sqlite_auth_and_team.py tests/test_review_service.py tests/test_auth_service.py tests/test_password_reset_mailer.py tests/test_error_handler.py -q
```
