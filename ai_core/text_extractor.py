import os
from pathlib import Path
import torch
from PIL import Image
from ultralytics import YOLO
from manga_ocr import MangaOcr

# --- BẢN VÁ PYTORCH 2.5+ CHO ULTRALYTICS YOLO ---
_original_load = torch.load
def patched_load(*args, **kwargs):
    kwargs["weights_only"] = False
    return _original_load(*args, **kwargs)
torch.load = patched_load

# Tự động xác định thư mục gốc và đường dẫn trọng số YOLO
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_YOLO_WEIGHTS = str(BASE_DIR / "models" / "yolo" / "manga_v14" / "weights" / "best.pt")

# --- BIẾN TOÀN CỤC LƯU CACHE MODEL TRONG RAM/VRAM ---
_YOLO_MODEL = None
_MOCR_MODEL = None


def get_ai_models(yolo_weight_path: str = DEFAULT_YOLO_WEIGHTS):
    """Chỉ tải YOLO và MangaOCR vào RAM/GPU đúng 1 lần duy nhất trong suốt phiên chạy."""
    global _YOLO_MODEL, _MOCR_MODEL

    if _YOLO_MODEL is None:
        print(f"⏳ [Init] Đang nạp mô hình YOLOv8 từ: {yolo_weight_path}...")
        _YOLO_MODEL = YOLO(yolo_weight_path)

    if _MOCR_MODEL is None:
        print("⏳ [Init] Đang nạp mô hình MangaOCR vào bộ nhớ...")
        _MOCR_MODEL = MangaOcr()

    return _YOLO_MODEL, _MOCR_MODEL


def extract_manga_text(image_path: str, yolo_weight_path: str = DEFAULT_YOLO_WEIGHTS) -> list[dict]:
    """
    Nhận diện bóng thoại (class_id == 1) và trích xuất chữ tiếng Nhật.
    Trả về danh sách: [{"bbox": [x1, y1, x2, y2], "japanese_text": "..."}, ...]
    """
    yolo_model, mocr = get_ai_models(yolo_weight_path)

    img = Image.open(image_path).convert("RGB")
    print(f"🔍 Đang quét YOLO + MangaOCR trên ảnh: {os.path.basename(image_path)}")

    results = yolo_model(image_path, verbose=False)
    extracted_data = []

    for r in results:
        for box in r.boxes:
            class_id = int(box.cls[0])

            # Chỉ xử lý nếu nhãn là text_bubble (ID = 1)
            if class_id == 1:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cropped_bubble = img.crop((x1, y1, x2, y2))
                japanese_text = mocr(cropped_bubble).strip()

                if japanese_text:
                    bubble_info = {
                        "bbox": [x1, y1, x2, y2],
                        "japanese_text": japanese_text
                    }
                    extracted_data.append(bubble_info)
                    print(f"  + Bbox {bubble_info['bbox']} -> {japanese_text}")

    # Sắp xếp thứ tự bóng thoại theo chuẩn đọc Manga (Từ phải sang trái, từ trên xuống dưới)
    extracted_data.sort(key=lambda item: (item["bbox"][1] // 100, -item["bbox"][0]))
    return extracted_data