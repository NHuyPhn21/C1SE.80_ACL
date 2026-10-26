import subprocess
import cv2
import numpy as np
import json
import os
from PIL import Image, ImageDraw, ImageFont
from backend.database import SessionLocal
from backend.models import ComicPage, TextRegion

def generate_mask_for_page(page_id: int, output_dir: str = "data/masks"):
    os.makedirs(output_dir, exist_ok=True)
    db = SessionLocal()
    try:
        page = db.query(ComicPage).filter(ComicPage.id == page_id).first()
        if not page or not os.path.exists(page.original_path):
            return None

        img_gray = cv2.imread(page.original_path, cv2.IMREAD_GRAYSCALE)
        h_img, w_img = img_gray.shape[:2]
        mask = np.zeros((h_img, w_img), dtype=np.uint8)

        regions = db.query(TextRegion).filter(TextRegion.page_id == page_id).all()
        for region in regions:
            bbox = json.loads(region.bbox_json)
            x_min, y_min, x_max, y_max = map(int, bbox)

            # Quét toàn bộ khung bbox (không thu hẹp) để không bỏ sót chữ sát mép như chữ 訂
            x1, y1 = max(0, x_min), max(0, y_min)
            x2, y2 = min(w_img, x_max), min(h_img, y_max)
            roi_w, roi_h = x2 - x1, y2 - y1

            if roi_w <= 10 or roi_h <= 10:
                continue

            roi = img_gray[y1:y2, x1:x2]

            # 1. Phân ngưỡng toàn cục để lấy trọn cả phần ruột đặc của chữ đậm (như わっ!?)
            _, binary = cv2.threshold(roi, 195, 255, cv2.THRESH_BINARY_INV)

            # 2. Tách từng cụm nét mực liên thông
            num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)

            text_mask = np.zeros_like(binary)
            artwork_mask = np.zeros_like(binary)
            roi_area = roi_w * roi_h

            for i in range(1, num_labels):
                x, y, w, h, area = stats[i]

                # Quy tắc 1: Mọi nét chạm vào cạnh khung bbox đều là viền bóng thoại, tóc hoặc nền
                touches_border = (x <= 1) or (y <= 1) or (x + w >= roi_w - 1) or (y + h >= roi_h - 1)

                # Quy tắc 2: Nét vẽ có chiều dài/rộng lớn hơn 60% khung là đường viền nghệ thuật
                too_large = (w > roi_w * 0.60) or (h > roi_h * 0.60) or (area > roi_area * 0.22)

                # Quy tắc 3: Kiểm tra vùng lân cận phải có tỷ lệ giấy trắng cao (loại bỏ screentone tối)
                pad = 4
                patch = roi[max(0, y - pad):min(roi_h, y + h + pad), max(0, x - pad):min(roi_w, x + w + pad)]
                white_ratio = np.mean(patch > 220) if patch.size > 0 else 0

                # Không lọc aspect_ratio để xóa sạch cả dấu chấm lửng (...) và dấu ngã (〜)
                if not touches_border and not too_large and area >= 3 and white_ratio > 0.35:
                    text_mask[labels == i] = 255
                else:
                    artwork_mask[labels == i] = 255

            # 3. Phình mặt nạ chữ ra 4px để bao trùm hết viền răng cưa xám quanh nét chữ Nhật
            kernel_text = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            dilated_text = cv2.dilate(text_mask, kernel_text, iterations=2)

            # 4. Bọc giáp bảo vệ 1px quanh viền bóng thoại và tóc để mặt nạ xóa không bao giờ chạm tới
            kernel_art = np.ones((3, 3), np.uint8)
            protected_artwork = cv2.dilate(artwork_mask, kernel_art, iterations=1)

            clean_roi_mask = cv2.bitwise_and(dilated_text, cv2.bitwise_not(protected_artwork))
            mask[y1:y2, x1:x2] = cv2.bitwise_or(mask[y1:y2, x1:x2], clean_roi_mask)

        filename = os.path.basename(page.original_path)
        mask_path = os.path.join(output_dir, f"mask_{filename}")
        cv2.imwrite(mask_path, mask)
        print(f"✅ Đã tạo ảnh mask bảo toàn viền bóng thoại tại: {mask_path}")
        return mask_path
    finally:
        db.close()


def run_lama_inpainting(image_path: str, mask_path: str, output_dir: str = "data/inpainted_pages"):
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(image_path)
    base_name, _ = os.path.splitext(filename)
    final_output_path = os.path.join(output_dir, f"cleaned_{base_name}.png")

    print(f"🧹 Đang khởi động LaMa Inpainting để tẩy chữ cho: {filename}...")
    command = [
        "iopaint", "run",
        "--model", "lama",
        "--image", image_path,
        "--mask", mask_path,
        "--output", output_dir
    ]
    
    try:
        subprocess.run(command, check=True, text=True, capture_output=True)
        
        found_file = None
        for f in os.listdir(output_dir):
            if f.startswith(base_name) and not f.startswith("cleaned_"):
                found_file = os.path.join(output_dir, f)
                break
        
        if found_file:
            if os.path.exists(final_output_path):
                os.remove(final_output_path)
            os.rename(found_file, final_output_path)

            # HẬU KỲ LÀM SẠCH VỆT XÁM: Đưa các vùng chữ đã tẩy trong bóng thoại về trắng tinh khiết (255)
            cleaned_img = cv2.imread(final_output_path)
            mask_img = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
            if cleaned_img is not None and mask_img is not None:
                cleaned_img[mask_img > 127] = [255, 255, 255]
                cv2.imwrite(final_output_path, cleaned_img)

            print(f"✨ Đã tẩy trắng bóng thoại thành công: {final_output_path}")
            return final_output_path
        else:
            print("❌ Không tìm thấy file đầu ra của iopaint.")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi chạy Inpainting: {e.stderr}")
        return None


def render_translated_text_on_page(page_id: int, inpainted_image_path: str, font_path: str, output_dir: str = "data/rendered_pages"):
    os.makedirs(output_dir, exist_ok=True)
    db = SessionLocal()
    
    try:
        page = db.query(ComicPage).filter(ComicPage.id == page_id).first()
        if not page: return None

        img = Image.open(inpainted_image_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        
        regions = db.query(TextRegion).filter(TextRegion.page_id == page_id).all()
        
        for region in regions:
            if not region.translated_text: continue 
                
            bbox = json.loads(region.bbox_json)
            x1, y1, x2, y2 = map(int, bbox)
            
            raw_width = x2 - x1
            raw_height = y2 - y1
            
            # Tăng lề ngang lên 20% để khối chữ gom gọn vào tâm, không chạm gai nhọn của bóng thoại
            pad_x = int(raw_width * 0.20)
            pad_y = int(raw_height * 0.14)
            
            box_width = raw_width - (pad_x * 2)
            box_height = raw_height - (pad_y * 2)
            
            if box_width <= 20 or box_height <= 20: continue
            
            text = region.translated_text
            max_font = 22 # Giới hạn cỡ chữ 22 để cân đối với bóng thoại dọc của Nhật
            best_font_size = 8
            best_lines = []
            best_line_spacing = 0
            
            for size in range(max_font, 7, -1):
                font = ImageFont.truetype(font_path, size)
                words = text.split()
                lines = []
                current_line = ""
                
                for word in words:
                    test_line = current_line + word + " "
                    if draw.textlength(test_line, font=font) <= box_width:
                        current_line = test_line
                    else:
                        if current_line: lines.append(current_line.strip())
                        current_line = word + " "
                if current_line: lines.append(current_line.strip())
                
                line_spacing = int(size * 0.18)
                total_height = sum([size for _ in lines]) + (len(lines) - 1) * line_spacing
                
                if total_height <= box_height:
                    best_font_size = size
                    best_lines = lines
                    best_line_spacing = line_spacing
                    break
            
            if not best_lines: continue
                
            font = ImageFont.truetype(font_path, best_font_size)
            total_height = sum([best_font_size for _ in best_lines]) + (len(best_lines) - 1) * best_line_spacing
            
            current_y = y1 + pad_y + (box_height - total_height) / 2
            for line in best_lines:
                line_width = draw.textlength(line, font=font)
                current_x = x1 + pad_x + (box_width - line_width) / 2
                
                draw.text(
                    (current_x, current_y), line, font=font, fill="black", 
                    stroke_width=2, stroke_fill="white"
                )
                current_y += best_font_size + best_line_spacing

        filename = os.path.basename(page.original_path)
        output_path = os.path.join(output_dir, f"final_{filename}")
        img.save(output_path)
        print(f"✅ Đã xuất bản thành công tại: {output_path}")
        return output_path

    finally:
        db.close()

if __name__ == "__main__":
    PAGE_ID = 1
    TEST_RAW_IMAGE = r"E:\DatabaseFiles\CAPSTONE1_ACL\C1SE.80_ACL\data\raw_images\AisazuNihaIrarenai\045.jpg" 
    FONT_PATH = r"E:\DatabaseFiles\CAPSTONE1_ACL\C1SE.80_ACL\assets\fonts\HLcomic1_normal.ttf" 
    
    print("=== BẮT ĐẦU CHẠY PIPELINE ACL ===")
    
    # Bước 1: OpenCV sinh ảnh mặt nạ (đen trắng)
    mask_file = generate_mask_for_page(page_id=PAGE_ID)
    
    if mask_file:
        # Bước 2: LaMa Inpainting dùng mask để tẩy chữ gốc
        cleaned_image_file = run_lama_inpainting(image_path=TEST_RAW_IMAGE, mask_path=mask_file)
        
        if cleaned_image_file:
            # Bước 3: Dàn trang tiếng Việt lên bức ảnh đã được tẩy trắng
            render_translated_text_on_page(page_id=PAGE_ID, inpainted_image_path=cleaned_image_file, font_path=FONT_PATH)
            
    print("=== HOÀN THÀNH ===")