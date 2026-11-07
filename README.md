# ACL

## Cài đặt môi trường

Yêu cầu Python 3.11 trên Windows.

Mở PowerShell tại thư mục project và chạy:

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Nếu PowerShell chặn chạy script kích hoạt môi trường, chạy một lần:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Sau đó kích hoạt lại môi trường bằng `.\venv\Scripts\Activate.ps1`.

## Tạo database

Database sử dụng SQLite và được lưu tại `acl.db` ở thư mục gốc project. Sau khi
cài dependencies, chạy:

```powershell
python setup_db.py
```

Lệnh này gọi `backend.database.init_db()` và tạo các bảng theo model hiện tại.
Schema hiện tại bao gồm bảng `password_reset_tokens` cho quy trình đặt lại mật
khẩu. Lệnh khởi tạo chỉ tạo các bảng còn thiếu; để tạo database sạch hoàn toàn,
đóng server, xóa riêng `acl.db`, rồi chạy lại `python setup_db.py`.

Kiểm tra nhanh database đã được tạo:

```powershell
python -c "import sqlite3; c=sqlite3.connect('acl.db'); print(c.execute(\"SELECT name FROM sqlite_master WHERE type='table' ORDER BY name\").fetchall()); c.close()"
```

## Chạy ứng dụng React + FastAPI

Sao chép `.env.example` thành `.env` và điền các API key cần thiết. Mở hai
PowerShell riêng:

```powershell
.\run_backend.bat
```

```powershell
.\run_frontend.bat
```

Frontend mở tại `http://localhost:5173`, API docs tại
`http://localhost:8000/docs`.

API chính:

- `POST /api/auth/login` — xác thực tài khoản local.
- `POST /api/auth/register` — tạo tài khoản mới trong bảng `users`.
- `GET /api/projects?user_id={id}` — đọc project thật theo owner/membership.
- `POST /api/projects?user_id={id}` — tạo project mới trong SQLite.
- `GET /api/projects/{id}/queue` — đọc tiến độ queue và từng trang thật.
- `POST /api/projects/{id}/queue/start` — tạo queue task cho chapter.
- `GET /api/projects/{id}/queue/export` — tải ZIP các trang đã render.
- `POST /api/upload` — lưu ảnh và chạy YOLO/MangaOCR.
- `POST /api/translate` — dịch các vùng chữ của một trang.
- `GET /api/chapters/{chapter_id}` — đọc chapter, pages và bubbles.
- `PUT /api/update-bubble/{region_id}` — lưu bản dịch hoặc tọa độ kéo thả.
- `POST /api/pages/{page_id}/typeset` — lưu bản dịch, font size và render lại trang.
- `POST /api/projects/{project_id}/queue/start` — tạo task và chạy pipeline AI chapter ở worker nền.
- `GET /api/settings?user_id={id}` — đọc trạng thái tài khoản và provider mà không trả secret.
- `GET /api/settings/glossary?user_id={id}` — đọc glossary thật của các project người dùng sở hữu.
- `POST /api/settings/glossary?user_id={id}` — thêm một term vào glossary của project.
- `GET /api/settings/logs?user_id={id}` — đọc system logs của các pipeline task.

## Cấu trúc thư mục

```text
backend/       FastAPI routes, request schemas, database models and utilities
ai_core/       YOLO, MangaOCR and Gemini integration
services/      Auth, workspace, queue, review and typesetting services
models/        Shared API/auth domain models
frontend/      React/Vite application
  src/api/     Domain API modules and shared request client
  src/features Authentication and application screens
tests/         Backend and service tests
assets/fonts/  Fonts required by the image renderer
data/          Runtime uploads and rendered output (ignored by Git)
```

Legacy Streamlit pages, components, session helpers, mock quota/evaluation
adapters and design-only assets are not part of the current application.

Queue Monitor tự động cập nhật trạng thái task mỗi 5 giây. Worker nền xử lý lần lượt
các trang trong chapter, cập nhật tiến độ và log vào SQLite; lỗi từng trang sẽ đánh
dấu task là `FAILED` và ghi nguyên nhân vào system log.
