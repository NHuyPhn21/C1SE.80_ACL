from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./acl.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    import backend.models 
    
    Base.metadata.create_all(bind=engine)
    print("Đã khởi tạo Database acl.db và các bảng thành công!")

if __name__ == "__main__":
    init_db()