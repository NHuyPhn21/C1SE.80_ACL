import json
import os
import shutil
import time
from pathlib import Path

from backend.database import SessionLocal
from backend.models import Chapter, ComicPage, TextRegion
from backend.image_utils import (
    process_comic_page,
    BASE_DIR,
    DEFAULT_FONT_PATH,
    resolve_project_path
)
from ai_core.text_extractor import extract_manga_text, DEFAULT_YOLO_WEIGHTS
from ai_core.translator import translate_manga_text


def ensure_default_chapter(db) -> int:
    """Đảm bảo luôn có ít nhất 1 Chapter trong SQLite để không bao giờ lỗi khóa ngoại chapter_id."""
    try:
        chapter = db.query(Chapter).first()
        if chapter:
            return chapter.id
    except Exception:
        pass
    return 1


def run_full_acl_pipeline(
    input_image_path: str,
    chapter_id: int = None,
    page_number: int = 1,
    force_reprocess: bool = False,
    use_lama_api: bool = False
) -> dict:
    """
    Main AI Processing Pipeline (End-to-End 5 bước):
    1. YOLOv8 (manga_v14/best.pt) phát hiện bóng thoại
    2. MangaOCR trích xuất chữ Nhật
    3. Gemini (gemini-3.8-flash) dịch Batch JSON toàn trang trong 1 Request
    4. Topological Mask + Fast Inpainting xóa sạch chữ gốc bảo toàn nét vẽ
    5. Distance-Transform Auto-Typesetting dàn trang tiếng Việt vào tâm thị giác
    """
    t_start = time.time()
    db = SessionLocal()

    try:
        src_path = Path(resolve_project_path(input_image_path)).resolve()
        if not src_path.exists():
            raise FileNotFoundError(f"Không tìm thấy ảnh đầu vào: {input_image_path}")

        # 1. Sao chép ảnh vào thư mục quản lý nếu là ảnh từ bên ngoài
        uploads_dir = BASE_DIR / "data" / "raw_images" / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        dest_path = uploads_dir / src_path.name
        if src_path != dest_path and not str(src_path).startswith(str(BASE_DIR / "data" / "raw_images")):
            shutil.copy2(src_path, dest_path)
            working_img_path = dest_path
        else:
            working_img_path = src_path

        rel_orig_path = str(working_img_path.relative_to(BASE_DIR)).replace("\\", "/")

        # 2. Tìm hoặc tạo mới bản ghi ComicPage trong SQLite
        if chapter_id is None:
            chapter_id = ensure_default_chapter(db)

        page = db.query(ComicPage).filter(ComicPage.original_path.like(f"%{working_img_path.name}")).first()
        if not page:
            page = ComicPage(
                chapter_id=chapter_id,
                page_number=page_number,
                original_path=rel_orig_path,
                status="PROCESSING"
            )
            db.add(page)
            db.commit()
            db.refresh(page)

        # Nếu bật cờ chạy lại từ đầu (force_reprocess), xóa các vùng chữ cũ của trang này
        if force_reprocess:
            db.query(TextRegion).filter(TextRegion.page_id == page.id).delete()
            db.commit()

        existing_regions = db.query(TextRegion).filter(TextRegion.page_id == page.id).all()

        # 3. BƯỚC 1 & 2: Chạy YOLOv8 + MangaOCR nếu trang chưa có dữ liệu vùng chữ
        if not existing_regions:
            print(f"\n🚀 [Bước 1 & 2/5] Chạy YOLOv8 & MangaOCR cho trang: {working_img_path.name} (Page ID: {page.id})")
            extracted_items = extract_manga_text(
                image_path=str(working_img_path),
                yolo_weight_path=DEFAULT_YOLO_WEIGHTS
            )

            for item in extracted_items:
                new_region = TextRegion(
                    page_id=page.id,
                    bbox_json=json.dumps(item["bbox"]),
                    original_text=item["japanese_text"],
                    translated_text=""
                )
                db.add(new_region)
            db.commit()
        else:
            print(f"ℹ️ Trang {working_img_path.name} (Page ID: {page.id}) đã có sẵn {len(existing_regions)} bóng thoại trong DB.")

        # 4. BƯỚC 3: Dịch thuật gộp (Batch JSON Translation) cho các câu chưa dịch trên trang này
        print(f"🌐 [Bước 3/5] Kiểm tra và dịch lời thoại tiếng Việt cho Page ID: {page.id}...")
        translate_manga_text(page_id=page.id)

        # 5. BƯỚC 4 & 5: Tạo Mask bảo vệ viền + Fast Inpainting + Dàn trang tiếng Việt
        print(f"🎨 [Bước 4 & 5/5] Tẩy chữ và dàn trang cho Page ID: {page.id}...")
        final_output_path = process_comic_page(
            page_id=page.id,
            font_path=DEFAULT_FONT_PATH,
            use_lama_api=use_lama_api
        )

        # Cập nhật trạng thái và đường dẫn vào bảng ComicPage
        if final_output_path:
            page.rendered_path = str(Path(final_output_path).relative_to(BASE_DIR)).replace("\\", "/")
            page.status = "COMPLETED"
            db.commit()

        elapsed = round(time.time() - t_start, 2)
        print(f"✅ HOÀN TẤT PIPELINE CHO {working_img_path.name} TRONG {elapsed} GIÂY!\n")

        return {
            "status": "success" if final_output_path else "error",
            "page_id": page.id,
            "original_path": str(working_img_path),
            "final_path": final_output_path,
            "elapsed_seconds": elapsed
        }

    except Exception as e:
        print(f"❌ Lỗi Pipeline tại {input_image_path}: {e}")
        return {
            "status": "error",
            "error_message": str(e)
        }
    finally:
        db.close()

def process_chapter_batch(chapter_folder_path: str, force_reprocess: bool = False, use_lama_api: bool = False) -> list[dict]:
    """
    Xử lý hàng loạt toàn bộ các trang truyện nằm trong một thư mục (Chapter Folder).
    Đầu vào: Đường dẫn tới thư mục chứa raw scans (ví dụ: "data/raw_images/AisazuNihaIrarenai")
    Đầu ra: Danh sách kết quả JSON cho từng trang.
    """
    folder = Path(resolve_project_path(chapter_folder_path))
    if not folder.exists() or not folder.is_dir():
        print(f"❌ Thư mục chương truyện không tồn tại: {chapter_folder_path}")
        return []

    # Lọc tất cả các file ảnh định dạng phổ biến, sắp xếp theo tên (001.jpg, 002.jpg, ...)
    valid_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    image_files = sorted([f for f in folder.iterdir() if f.suffix.lower() in valid_extensions])

    if not image_files:
        print(f"⚠️ Không tìm thấy file ảnh nào trong thư mục: {chapter_folder_path}")
        return []

    print(f"\n📚 BẮT ĐẦU XỬ LÝ HÀNG LOẠT CHƯƠNG TRUYỆN: {folder.name}")
    print(f"📂 Tổng số trang phát hiện: {len(image_files)} trang\n")

    batch_start_time = time.time()
    results = []

    for idx, img_file in enumerate(image_files, start=1):
        print(f"--------------------------------------------------")
        print(f"📖 Đang xử lý trang {idx}/{len(image_files)}: {img_file.name}")
        print(f"--------------------------------------------------")

        res = run_full_acl_pipeline(
            input_image_path=str(img_file),
            page_number=idx,
            force_reprocess=force_reprocess,
            use_lama_api=use_lama_api
        )
        results.append(res)

    total_elapsed = time.time() - batch_start_time
    success_count = sum(1 for r in results if r.get("status") == "success")

    print(f"\n==================================================")
    print(f"🎉 HOÀN TẤT LÔ HÀNG LOẠT CHO THƯ MỤC: {folder.name}")
    print(f"✅ Thành công: {success_count}/{len(image_files)} trang")
    print(f"⏱️ Tổng thời gian: {total_elapsed:.2f} giây (~{total_elapsed/len(image_files):.1f}s/trang)")
    print(f"📁 Thư mục kết quả: data/rendered_pages/")
    print(f"==================================================\n")

    return results
# =====================================================================
# TEST TRỰC TIẾP TRÊN TERMINAL VỚI MỘT TRANG TRUYỆN MỚI BẤT KỲ
# =====================================================================
if __name__ == "__main__":
    # Bạn có thể đổi tên ảnh khác trong thư mục 
    TEST_IMG = r"data/raw_images/AisazuNihaIrarenai/046.jpg"
    res = run_full_acl_pipeline(TEST_IMG, force_reprocess=False)
    print("Kết quả trả về:", json.dumps(res, indent=2, ensure_ascii=False))