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
    - Mặc định (use_lama_api=False): Dùng thuật toán OpenCV Telea + Làm trắng thông minh (0.05s/trang).
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

    orig_img = cv2.imread(img_real_path)
    if orig_img is None:
        return None

    cleaned_img = cv2.inpaint(orig_img, mask_img, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    cleaned_img[mask_img > 127] = [255, 255, 255]

    cv2.imwrite(final_output_path, cleaned_img)
    print(f"🚀 Đã tẩy trắng siêu tốc ({time.time() - t0:.2f}s): {final_output_path}")
    return final_output_path


def get_bubble_safe_zone(
    img_gray_cleaned: np.ndarray,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    occupied_mask: np.ndarray = None
):
    """
    Tìm tâm thị giác của bóng thoại bằng Distance Transform + Connected Components,
    đồng thời tự động trừ đi phần diện tích đã bị các bóng thoại trước chiếm chỗ (occupied_mask).
    """
    raw_w = x2 - x1
    raw_h = y2 - y1
    roi = img_gray_cleaned[y1:y2, x1:x2]

    _, white_mask = cv2.threshold(roi, 230, 255, cv2.THRESH_BINARY)

    # KỸ THUẬT CHỐNG ĐÈ CHỮ KHI 2 BÓNG THOẠI DÍNH NHAU:
    # Khóa vùng đã có chữ của bóng thoại trước thành màu đen (0) để thuật toán tự tìm nửa bóng thoại còn trống
    if occupied_mask is not None:
        occ_roi = occupied_mask[y1:y2, x1:x2]
        white_mask = cv2.bitwise_and(white_mask, cv2.bitwise_not(occ_roi))

    kernel = np.ones((3, 3), np.uint8)
    white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_CLOSE, kernel)
    white_mask = cv2.erode(white_mask, kernel, iterations=1)

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(white_mask, connectivity=8)
    best_label = -1

    cx_init, cy_init = raw_w // 2, raw_h // 2
    if num_labels > 1:
        center_label = labels[cy_init, cx_init]
        if center_label != 0 and stats[center_label, cv2.CC_STAT_AREA] > (raw_w * raw_h * 0.12):
            best_label = center_label
        else:
            max_score = 0
            for i in range(1, num_labels):
                area = stats[i, cv2.CC_STAT_AREA]
                if area < (raw_w * raw_h * 0.08):
                    continue
                bx, by, bw, bh, _ = stats[i]
                dist_to_center = np.hypot((bx + bw / 2) - cx_init, (by + bh / 2) - cy_init)
                score = area / (dist_to_center + 10.0)
                if score > max_score:
                    max_score = score
                    best_label = i

    if best_label == -1:
        return (x1 + raw_w / 2.0, y1 + raw_h / 2.0, raw_w * 0.70, raw_h * 0.72)

    bubble_mask = np.uint8(labels == best_label) * 255

    padded = cv2.copyMakeBorder(bubble_mask, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    dist = cv2.distanceTransform(padded, cv2.DIST_L2, 5)[1:-1, 1:-1]

    max_dist = dist.max()
    if max_dist <= 2:
        return (x1 + raw_w / 2.0, y1 + raw_h / 2.0, raw_w * 0.70, raw_h * 0.72)

    # Nâng ngưỡng hạt nhân từ 0.55 lên 0.65 để khóa chặt vào phần bụng phình to nhất của nửa bóng thoại đang xét
    core_y, core_x = np.where(dist >= max_dist * 0.65)
    weights = dist[core_y, core_x] ** 2
    local_cx = float(np.average(core_x, weights=weights))
    local_cy = float(np.average(core_y, weights=weights))

    # Quét tia ngang & dọc từ tâm thị giác (local_cx, local_cy) tới rìa vùng trắng trống
    row_pixels = bubble_mask[int(local_cy), :] > 0
    col_pixels = bubble_mask[:, int(local_cx)] > 0

    left = int(local_cx)
    while left > 0 and row_pixels[left - 1]:
        left -= 1
    right = int(local_cx)
    while right < raw_w - 1 and row_pixels[right + 1]:
        right += 1

    top = int(local_cy)
    while top > 0 and col_pixels[top - 1]:
        top -= 1
    bottom = int(local_cy)
    while bottom < raw_h - 1 and col_pixels[bottom + 1]:
        bottom += 1

    avail_half_w = min(local_cx - left, right - local_cx)
    avail_half_h = min(local_cy - top, bottom - local_cy)

    safe_w = max(avail_half_w * 2 * 0.82, max_dist * 1.40, raw_w * 0.38)
    safe_h = max(avail_half_h * 2 * 0.85, max_dist * 1.40, raw_h * 0.45)

    safe_w = min(safe_w, raw_w * 0.76)
    safe_h = min(safe_h, raw_h * 0.76)

    return (x1 + local_cx, y1 + local_cy, safe_w, safe_h)


def _deduplicate_db_regions(regions: list) -> list:
    """
    Khử các vùng chữ bị lưu trùng trong Database (do các lần chạy trước chưa có bộ lọc YOLO IoU
    hoặc 2 box lồng nhau đọc ra cùng một câu chữ Nhật).
    """
    kept = []
    for r in regions:
        if not r.translated_text or not r.translated_text.strip():
            continue

        bbox = json.loads(r.bbox_json)
        x1, y1, x2, y2 = map(int, bbox[:4])
        area_curr = max(1, (x2 - x1) * (y2 - y1))
        orig_clean = (r.original_text or "").strip()

        is_dup = False
        for kr, kx1, ky1, kx2, ky2 in kept:
            ix1, iy1 = max(x1, kx1), max(y1, ky1)
            ix2, iy2 = min(x2, kx2), min(y2, ky2)
            inter_area = max(0, ix2 - ix1) * max(0, iy2 - iy1)
            area_kept = max(1, (kx2 - kx1) * (ky2 - ky1))

            iou = inter_area / float(area_curr + area_kept - inter_area) if inter_area > 0 else 0
            containment = inter_area / float(min(area_curr, area_kept)) if inter_area > 0 else 0

            # 1. Nếu 2 box đè lên nhau quá nhiều (> 40% IoU hoặc > 60% nằm lọt lòng nhau)
            if iou > 0.40 or containment > 0.60:
                is_dup = True
                break

            # 2. Nếu 2 box giao nhau (hoặc sát nhau) và câu tiếng Nhật gốc giống nhau (ví dụ ID 57 & ID 64)
            k_orig = (kr.original_text or "").strip()
            if orig_clean and k_orig and len(orig_clean) >= 4 and len(k_orig) >= 4:
                if (orig_clean in k_orig or k_orig in orig_clean) and inter_area > 0:
                    is_dup = True
                    break

        if not is_dup:
            kept.append((r, x1, y1, x2, y2))

    return [item[0] for item in kept]


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

        h_img, w_img = img_gray_cleaned.shape[:2]

        # BẢN ĐỒ CHỐNG VA CHẠM TOÀN TRANG (0 = vùng trống, 255 = vùng đã có chữ chiếm chỗ)
        occupied_mask = np.zeros((h_img, w_img), dtype=np.uint8)

        # Cache bộ font từ size 8 đến 22 vào RAM
        max_font = 22
        font_cache = {
            size: ImageFont.truetype(resolved_font, size)
            for size in range(8, max_font + 1)
        }

        raw_regions = db.query(TextRegion).filter(TextRegion.page_id == page_id).all()
        # Lọc sạch các bóng thoại bị trùng trong Database trước khi vẽ
        regions = _deduplicate_db_regions(raw_regions)

        # Ưu tiên vẽ các bóng thoại có khung gọn trước, khung to bao trùm vẽ sau để né chính xác
        regions.sort(key=lambda r: (
            (json.loads(r.bbox_json)[2] - json.loads(r.bbox_json)[0]) *
            (json.loads(r.bbox_json)[3] - json.loads(r.bbox_json)[1])
        ))

        for region in regions:
            bbox = json.loads(region.bbox_json)
            x1, y1, x2, y2 = map(int, bbox[:4])

            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w_img, x2), min(h_img, y2)
            if x2 - x1 <= 20 or y2 - y1 <= 20:
                continue

            # Truyền occupied_mask vào để tự động né vùng chữ đã vẽ của bóng thoại kế bên
            center_x, center_y, box_width, box_height = get_bubble_safe_zone(
                img_gray_cleaned, x1, y1, x2, y2, occupied_mask=occupied_mask
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

            # ĐÁNH DẤU VÙNG VỪA VẼ VÀO OCCUPIED_MASK (kèm khoảng đệm 10px) ĐỂ BÓNG THOẠI KẾ BÊN TỰ ĐỘNG NÉ
            pad_occ = 10
            occ_x1 = max(0, int(center_x - max(text_w, box_width * 0.75) / 2.0 - pad_occ))
            occ_y1 = max(0, int(center_y - max(text_h, box_height * 0.75) / 2.0 - pad_occ))
            occ_x2 = min(w_img, int(center_x + max(text_w, box_width * 0.75) / 2.0 + pad_occ))
            occ_y2 = min(h_img, int(center_y + max(text_h, box_height * 0.75) / 2.0 + pad_occ))
            occupied_mask[occ_y1:occ_y2, occ_x1:occ_x2] = 255

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