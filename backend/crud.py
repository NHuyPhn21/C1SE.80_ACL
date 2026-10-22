import json
from sqlalchemy.orm import Session
from backend.models import User, Project, Chapter, ComicPage, TextRegion

def save_extracted_data(db: Session, image_path: str, extracted_results: list):
    """Lưu kết quả trích xuất OCR vào Database"""
    
    # 1. Khởi tạo dữ liệu gốc nếu DB rỗng (đảm bảo tính toàn vẹn khóa ngoại)
    user = db.query(User).first()
    if not user:
        user = User(username="admin", email="admin@acl.com", password_hash="hashed_pw")
        db.add(user)
        db.commit()

    project = db.query(Project).first()
    if not project:
        project = Project(owner_id=user.id, title="Dự án Localize Test")
        db.add(project)
        db.commit()

    chapter = db.query(Chapter).first()
    if not chapter:
        chapter = Chapter(project_id=project.id, chapter_number=1, chapter_name="Chapter 1")
        db.add(chapter)
        db.commit()

    # 2. Tạo bản ghi cho trang truyện hiện tại
    page = ComicPage(
        chapter_id=chapter.id, 
        page_number=1, 
        original_path=image_path,
        status='EXTRACTED'
    )
    db.add(page)
    db.commit()
    db.refresh(page) # Lấy page.id vừa được sinh ra

    # 3. Quét mảng OCR và insert vào bảng TextRegion
    for item in extracted_results:
        region = TextRegion(
            page_id=page.id,
            bbox_json=json.dumps(item["bbox"]), # Chuyển list tọa độ thành chuỗi JSON
            original_text=item["japanese_text"]
        )
        db.add(region)
    
    db.commit()
    return page