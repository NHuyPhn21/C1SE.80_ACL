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


def _filter_overlapping_boxes(boxes_with_conf: list[tuple]) -> list[list[int]]:
    """
    Loại bỏ các bounding box bị trùng lặp hoặc nằm lọt lòng nhau (IoU / Containment).
    boxes_with_conf: danh sách [(x1, y1, x2, y2, conf), ...]
    """
    boxes_with_conf.sort(key=lambda b: b[4], reverse=True)
    kept_boxes = []

    for x1, y1, x2, y2, conf in boxes_with_conf:
        area_curr = max(1, (x2 - x1) * (y2 - y1))
        is_duplicate = False

        for kx1, ky1, kx2, ky2 in kept_boxes:
            ix1, iy1 = max(x1, kx1), max(y1, ky1)
            ix2, iy2 = min(x2, kx2), min(y2, ky2)
            inter_w, inter_h = max(0, ix2 - ix1), max(0, iy2 - iy1)
            inter_area = inter_w * inter_h

            if inter_area > 0:
                area_kept = max(1, (kx2 - kx1) * (ky2 - ky1))
                iou = inter_area / float(area_curr + area_kept - inter_area)
                containment = inter_area / float(min(area_curr, area_kept))

                # Nếu trùng nhau > 35% hoặc nằm đè bên trong nhau > 60% -> Bỏ qua box trùng
                if iou > 0.35 or containment > 0.60:
                    is_duplicate = True
                    break

        if not is_duplicate:
            kept_boxes.append([x1, y1, x2, y2])

    return kept_boxes


def extract_manga_text(image_path: str, yolo_weight_path: str = DEFAULT_YOLO_WEIGHTS) -> list[dict]:
    """
    Nhận diện bóng thoại (class_id == 1) và trích xuất chữ tiếng Nhật.
    Trả về danh sách: [{"bbox": [x1, y1, x2, y2], "japanese_text": "..."}, ...]
    """
    yolo_model, mocr = get_ai_models(yolo_weight_path)

    img = Image.open(image_path).convert("RGB")
    print(f"🔍 Đang quét YOLO + MangaOCR trên ảnh: {os.path.basename(image_path)}")

    results = yolo_model(image_path, verbose=False)
    raw_candidates = []

    for r in results:
        for box in r.boxes:
            if int(box.cls[0]) == 1:  # Chỉ lấy text_bubble
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0]) if box.conf is not None else 1.0
                raw_candidates.append((x1, y1, x2, y2, conf))

    # LỌC SẠCH CÁC BOX TRÙNG NHAU TRƯỚC KHI CHẠY MANGA_OCR
    clean_bboxes = _filter_overlapping_boxes(raw_candidates)
    print(f"🧹 Đã lọc từ {len(raw_candidates)} box thô -> còn {len(clean_bboxes)} bóng thoại chuẩn.")

    extracted_data = []
    seen_texts_nearby = []

    for x1, y1, x2, y2 in clean_bboxes:
        cropped_bubble = img.crop((x1, y1, x2, y2))
        japanese_text = mocr(cropped_bubble).strip()
        if not japanese_text:
            continue

        # Chốt chặn phụ: Nếu 2 box nằm sát nhau mà đọc ra cùng 1 câu chữ Nhật giống hệt nhau thì bỏ qua
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        is_same_text_nearby = False
        for prev_text, pcx, pcy in seen_texts_nearby:
            if japanese_text == prev_text and len(japanese_text) > 4:
                if abs(cx - pcx) < 180 and abs(cy - pcy) < 180:
                    is_same_text_nearby = True
                    break
        if is_same_text_nearby:
            continue

        seen_texts_nearby.append((japanese_text, cx, cy))
        bubble_info = {
            "bbox": [x1, y1, x2, y2],
            "japanese_text": japanese_text
        }
        extracted_data.append(bubble_info)
        print(f"  + Bbox {bubble_info['bbox']} -> {japanese_text}")

    # Sắp xếp thứ tự bóng thoại theo chuẩn đọc Manga (Từ phải sang trái, từ trên xuống dưới)
    extracted_data.sort(key=lambda item: (item["bbox"][1] // 100, -item["bbox"][0]))
    return extracted_data