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
Có thể chạy lại lệnh an toàn; các bảng đã có sẽ không bị xóa.

Kiểm tra nhanh database đã được tạo:

```powershell
python -c "import sqlite3; c=sqlite3.connect('acl.db'); print(c.execute(\"SELECT name FROM sqlite_master WHERE type='table' ORDER BY name\").fetchall()); c.close()"
```

Nếu cần tạo lại database từ đầu trong môi trường local, hãy đóng app trước,
xóa riêng file `acl.db`, rồi chạy lại `python setup_db.py`. Không xóa database
đang dùng chung.

## Chạy ứng dụng

Sao chép `.env.example` thành `.env` và điền các API key cần thiết, sau đó chạy:

```powershell
streamlit run app.py
```
