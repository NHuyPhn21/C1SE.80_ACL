from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models import Base 

# Tạo file acl.db ở ngay thư mục gốc của dự án
SQLALCHEMY_DATABASE_URL = "sqlite:///./acl.db"

# Khởi tạo engine kết nối (check_same_thread=False là bắt buộc khi dùng SQLite với Streamlit)
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Khởi tạo session để sau này các hàm CRUD gọi tới
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Lệnh quan trọng nhất: Quét tất cả các class kế thừa từ Base và tạo thành các bảng trong SQLite
    Base.metadata.create_all(bind=engine)
    print("Đã khởi tạo Database acl.db và các bảng thành công!")

if __name__ == "__main__":
    init_db()