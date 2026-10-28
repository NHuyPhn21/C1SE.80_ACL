import base64
import json
import os
import time
from pathlib import Path
import cv2
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont
from backend.database import SessionLocal
from backend.models import ComicPage, TextRegion

# Tự động lấy đường dẫn thư mục gốc của dự án (chạy được trên mọi máy Windows/Linux/Cloud)
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_FONT_PATH = str(BASE_DIR / "assets" / "fonts" / "HLcomic1_normal.ttf")


def resolve_project_path(file_path: str) -> str:
    """Chuẩn hóa đường dẫn để tương thích cả Windows lẫn Linux khi đưa lên mạng."""
    if not file_path:
        return ""
    normalized = file_path.replace("\\", "/")
    if os.path.exists(normalized):
        return normalized
    # Nếu trong DB lưu đường dẫn tương đối, ghép với BASE_DIR
    candidate = BASE_DIR / normalized
    if candidate.exists():
        return str(candidate)
    return file_path


def generate_mask_for_page(page_id: int, output_dir: str = "data/masks"):
    out_dir_path = BASE_DIR / output_dir
    out_dir_path.mkdir(parents=True, exist_ok=True)
    db = SessionLocal()
    try:
        page = db.query(ComicPage).filter(ComicPage.id == page_id).first()
        if not page:
            return None

        orig_path = resolve_project_path(page.original_path)
        if not os.path.exists(orig_path):
            print(f"❌ Không tìm thấy ảnh gốc tại: {orig_path}")
            return None

        img_gray = cv2.imread(orig_path, cv2.IMREAD_GRAYSCALE)
        h_img, w_img = img_gray.shape[:2]
        mask = np.zeros((h_img, w_img), dtype=np.uint8)

        regions = db.query(TextRegion).filter(TextRegion.page_id == page_id).all()
        for region in regions:
            bbox = json.loads(region.bbox_json)
            x_min, y_min, x_max, y_max = map(int, bbox)

            x1, y1 = max(0, x_min), max(0, y_min)
            x2, y2 = min(w_img, x_max), min(h_img, y_max)
            roi_w, roi_h = x2 - x1, y2 - y1

            if roi_w <= 10 or roi_h <= 10:
                continue

            roi = img_gray[y1:y2, x1:x2]

            # 1. Phân ngưỡng toàn cục bắt trọn cả ruột chữ đậm
            _, binary = cv2.threshold(roi, 195, 255, cv2.THRESH_BINARY_INV)

            # 2. Tách từng cụm nét mực liên thông
            num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)

            text_mask = np.zeros_like(binary)
            artwork_mask = np.zeros_like(binary)
            roi_area = roi_w * roi_h

            for i in range(1, num_labels):
                x, y, w, h, area = stats[i]

                touches_border = (x <= 1) or (y <= 1) or (x + w >= roi_w - 1) or (y + h >= roi_h - 1)
                too_large = (w > roi_w * 0.60) or (h > roi_h * 0.60) or (area > roi_area * 0.22)

                pad = 4
                patch = roi[max(0, y - pad):min(roi_h, y + h + pad), max(0, x - pad):min(roi_w, x + w + pad)]
                white_ratio = np.mean(patch > 220) if patch.size > 0 else 0

                if not touches_border and not too_large and area >= 3 and white_ratio > 0.35:
                    text_mask[labels == i] = 255
                else:
                    artwork_mask[labels == i] = 255

            # 3. Phình mặt nạ chữ 4px và bọc giáp bảo vệ 1px quanh viền bóng thoại/tóc
            kernel_text = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            dilated_text = cv2.dilate(text_mask, kernel_text, iterations=2)

            kernel_art = np.ones((3, 3), np.uint8)
            protected_artwork = cv2.dilate(artwork_mask, kernel_art, iterations=1)

            clean_roi_mask = cv2.bitwise_and(dilated_text, cv2.bitwise_not(protected_artwork))
            mask[y1:y2, x1:x2] = cv2.bitwise_or(mask[y1:y2, x1:x2], clean_roi_mask)

        filename = os.path.basename(orig_path)
        mask_path = str(out_dir_path / f"mask_{filename}")
        cv2.imwrite(mask_path, mask)
        print(f"✅ Đã tạo ảnh mask bảo toàn viền bóng thoại tại: {mask_path}")
        return mask_path
    finally:
        db.close()


def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def run_lama_inpainting(
    image_path: str,
    mask_path: str,
    output_dir: str = "data/inpainted_pages",
    use_lama_api: bool = False,
    api_url: str = "http://127.0.0.1:8080/api/v1/inpaint"
):
    """
    Cơ chế Hybrid Inpainting:
    - Mặc định (use_lama_api=False): Dùng thuật toán OpenCV Telea + Làm trắng thông minh (0.05s/trang),
      không cần bật Server phụ, chạy cực nhẹ trên mọi Cloud Server.
    - Nếu bật use_lama_api=True: Gọi tới LaMa Server và tự động fallback về OpenCV nếu Server tắt.
    """
    t0 = time.time()
    out_dir_path = BASE_DIR / output_dir
    out_dir_path.mkdir(parents=True, exist_ok=True)

    img_real_path = resolve_project_path(image_path)
    filename = os.path.basename(img_real_path)
    base_name, _ = os.path.splitext(filename)
    final_output_path = str(out_dir_path / f"cleaned_{base_name}.png")

    mask_img = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    if mask_img is None:
        return None

    # Tùy chọn 1: Thử gọi LaMa API nếu được bật
    if use_lama_api:
        try:
            payload = {
                "image": encode_image_to_base64(img_real_path),
                "mask": encode_image_to_base64(mask_path),
                "hd_strategy": "Resize",
                "hd_strategy_resize_limit": 1280
            }
            response = requests.post(api_url, json=payload, timeout=15)
            response.raise_for_status()

            with open(final_output_path, "wb") as f:
                f.write(response.content)

            cleaned_img = cv2.imread(final_output_path)
            if cleaned_img is not None:
                cleaned_img[mask_img > 127] = [255, 255, 255]
                cv2.imwrite(final_output_path, cleaned_img)

            print(f"✨ Đã tẩy trắng qua LaMa API ({time.time() - t0:.2f}s): {final_output_path}")
            return final_output_path
        except Exception:
            print("⚠️ LaMa API không phản hồi, tự động chuyển sang chế độ OpenCV siêu tốc...")

    # Tùy chọn 2 (Mặc định & Khuyên dùng cho Web): Tẩy siêu tốc bằng OpenCV Telea + White Fill
    orig_img = cv2.imread(img_real_path)
    if orig_img is None:
        return None

    # Nội suy mượt vùng viền bằng thuật toán Telea, sau đó làm trắng tinh khiết phần ruột chữ
    cleaned_img = cv2.inpaint(orig_img, mask_img, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    cleaned_img[mask_img > 127] = [255, 255, 255]

    cv2.imwrite(final_output_path, cleaned_img)
    print(f"🚀 Đã tẩy trắng siêu tốc ({time.time() - t0:.2f}s): {final_output_path}")
    return final_output_path


def get_bubble_safe_zone(img_gray_cleaned: np.ndarray, x1: int, y1: int, x2: int, y2: int):
    raw_w = x2 - x1
    raw_h = y2 - y1
    roi = img_gray_cleaned[y1:y2, x1:x2]

    _, white_mask = cv2.threshold(roi, 230, 255, cv2.THRESH_BINARY)

    kernel = np.ones((3, 3), np.uint8)
    white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_CLOSE, kernel)
    white_mask = cv2.erode(white_mask, kernel, iterations=1)

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(white_mask, connectivity=8)
    best_label = -1

    cx_init, cy_init = raw_w // 2, raw_h // 2
    if num_labels > 1:
        center_label = labels[cy_init, cx_init]
        if center_label != 0 and stats[center_label, cv2.CC_STAT_AREA] > (raw_w * raw_h * 0.15):
            best_label = center_label
        else:
            max_score = 0
            for i in range(1, num_labels):
                area = stats[i, cv2.CC_STAT_AREA]
                if area < (raw_w * raw_h * 0.1):
                    continue
                bx, by, bw, bh, _ = stats[i]
                dist_to_center = np.hypot((bx + bw / 2) - cx_init, (by + bh / 2) - cy_init)
                score = area / (dist_to_center + 10.0)
                if score > max_score:
                    max_score = score
                    best_label = i

    if best_label == -1:
        return (x1 + raw_w / 2.0, y1 + raw_h / 2.0, raw_w * 0.72, raw_h * 0.76)

    bubble_mask = np.uint8(labels == best_label) * 255

    padded = cv2.copyMakeBorder(bubble_mask, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    dist = cv2.distanceTransform(padded, cv2.DIST_L2, 5)[1:-1, 1:-1]

    max_dist = dist.max()
    if max_dist <= 2:
        return (x1 + raw_w / 2.0, y1 + raw_h / 2.0, raw_w * 0.72, raw_h * 0.76)

    core_y, core_x = np.where(dist >= max_dist * 0.55)
    weights = dist[core_y, core_x] ** 2
    local_cx = float(np.average(core_x, weights=weights))
    local_cy = float(np.average(core_y, weights=weights))

    bx, by, bw, bh, _ = stats[best_label]
    avail_half_w = min(local_cx - bx, (bx + bw) - local_cx)
    avail_half_h = min(local_cy - by, (by + bh) - local_cy)

    safe_w = max(avail_half_w * 2 * 0.72, raw_w * 0.42)
    safe_h = max(avail_half_h * 2 * 0.84, raw_h * 0.50)

    return (x1 + local_cx, y1 + local_cy, safe_w, safe_h)


def render_translated_text_on_page(
    page_id: int,
    inpainted_image_path: str,
    font_path: str = DEFAULT_FONT_PATH,
    output_dir: str = "data/rendered_pages"
):
    out_dir_path = BASE_DIR / output_dir
    out_dir_path.mkdir(parents=True, exist_ok=True)
    db = SessionLocal()

    try:
        page = db.query(ComicPage).filter(ComicPage.id == page_id).first()
        if not page:
            return None

        resolved_font = resolve_project_path(font_path)
        img = Image.open(inpainted_image_path).convert("RGB")
        img_gray_cleaned = cv2.imread(inpainted_image_path, cv2.IMREAD_GRAYSCALE)
        draw = ImageDraw.Draw(img)

        # Cache bộ font từ size 8 đến 22 vào RAM để không phải đọc ổ cứng lặp lại hàng trăm lần
        max_font = 22
        font_cache = {
            size: ImageFont.truetype(resolved_font, size)
            for size in range(8, max_font + 1)
        }

        regions = db.query(TextRegion).filter(TextRegion.page_id == page_id).all()

        for region in regions:
            if not region.translated_text:
                continue

            bbox = json.loads(region.bbox_json)
            x1, y1, x2, y2 = map(int, bbox)

            h_img, w_img = img_gray_cleaned.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w_img, x2), min(h_img, y2)
            if x2 - x1 <= 20 or y2 - y1 <= 20:
                continue

            center_x, center_y, box_width, box_height = get_bubble_safe_zone(
                img_gray_cleaned, x1, y1, x2, y2
            )

            text = region.translated_text.strip()
            best_font_size = 8
            best_lines = []
            best_line_spacing = 2

            for size in range(max_font, 7, -1):
                font = font_cache[size]
                words = text.split()
                lines = []
                current_line = ""

                for word in words:
                    test_line = (current_line + " " + word).strip()
                    if draw.textlength(test_line, font=font) <= box_width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)

                line_spacing = max(2, int(size * 0.18))
                full_text = "\n".join(lines)

                t_left, t_top, t_right, t_bottom = draw.multiline_textbbox(
                    (0, 0), full_text, font=font, spacing=line_spacing, align="center"
                )
                actual_w = t_right - t_left
                actual_h = t_bottom - t_top

                if actual_w <= box_width and actual_h <= box_height:
                    best_font_size = size
                    best_lines = lines
                    best_line_spacing = line_spacing
                    break

            if not best_lines:
                best_lines = [text]

            font = font_cache[best_font_size]
            full_text = "\n".join(best_lines)

            t_left, t_top, t_right, t_bottom = draw.multiline_textbbox(
                (0, 0), full_text, font=font, spacing=best_line_spacing, align="center"
            )
            text_w = t_right - t_left
            text_h = t_bottom - t_top

            draw_x = center_x - (text_w / 2.0) - t_left
            draw_y = center_y - (text_h / 2.0) - t_top

            draw.multiline_text(
                (draw_x, draw_y),
                full_text,
                font=font,
                fill="black",
                spacing=best_line_spacing,
                align="center",
                stroke_width=2,
                stroke_fill="white"
            )

        filename = os.path.basename(resolve_project_path(page.original_path))
        output_path = str(out_dir_path / f"final_{filename}")
        img.save(output_path, quality=95)
        print(f"✅ Đã xuất bản thành công tại: {output_path}")
        return output_path

    finally:
        db.close()


def process_comic_page(page_id: int, font_path: str = DEFAULT_FONT_PATH, use_lama_api: bool = False):
    """
    Hàm tổng hợp 1-click dùng để gọi trực tiếp từ giao diện Web (Streamlit / FastAPI).
    Trả về đường dẫn ảnh hoàn chỉnh sau khi dịch.
    """
    db = SessionLocal()
    try:
        page = db.query(ComicPage).filter(ComicPage.id == page_id).first()
        if not page:
            return None
        orig_path = resolve_project_path(page.original_path)
    finally:
        db.close()

    mask_file = generate_mask_for_page(page_id=page_id)
    if not mask_file:
        return None

    cleaned_file = run_lama_inpainting(
        image_path=orig_path,
        mask_path=mask_file,
        use_lama_api=use_lama_api
    )
    if not cleaned_file:
        return None

    return render_translated_text_on_page(
        page_id=page_id,
        inpainted_image_path=cleaned_file,
        font_path=font_path
    )


if __name__ == "__main__":
    t_start = time.time()
    print("=== BẮT ĐẦU CHẠY PIPELINE ACL SIÊU TỐC ===")
    final_img = process_comic_page(page_id=1, use_lama_api=False)
    print(f"=== HOÀN THÀNH TOÀN BỘ TRONG {time.time() - t_start:.2f} GIÂY ===")