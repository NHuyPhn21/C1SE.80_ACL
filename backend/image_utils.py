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

        img = cv2.imread(page.original_path)
        h, w = img.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)

        regions = db.query(TextRegion).filter(TextRegion.page_id == page_id).all()
        for region in regions:
            bbox = json.loads(region.bbox_json)
            x_min, y_min, x_max, y_max = map(int, bbox)
            cv2.rectangle(mask, (x_min, y_min), (x_max, y_max), 255, -1)

        filename = os.path.basename(page.original_path)
        mask_path = os.path.join(output_dir, f"mask_{filename}")
        cv2.imwrite(mask_path, mask)
        return mask_path
    finally:
        db.close()


def render_translated_text_on_page(page_id: int, inpainted_image_path: str, font_path: str, output_dir: str = "data/rendered_pages"):
    os.makedirs(output_dir, exist_ok=True)
    db = SessionLocal()
    
    try:
        page = db.query(ComicPage).filter(ComicPage.id == page_id).first()
        if not page:
            return None

        img = Image.open(inpainted_image_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        
        regions = db.query(TextRegion).filter(TextRegion.page_id == page_id).all()
        print(f"✍️ Đang chèn chữ cho {len(regions)} bong bóng thoại...")
        
        for region in regions:
            if not region.translated_text:
                continue 
                
            bbox = json.loads(region.bbox_json)
            x1, y1, x2, y2 = map(int, bbox)
            
            raw_width = x2 - x1
            raw_height = y2 - y1
            
            # 1. Padding linh hoạt nhẹ nhàng (8% kích thước bóng thoại)
            padding = int(min(raw_width * 0.08, raw_height * 0.08))
            
            box_width = raw_width - (padding * 2)
            box_height = raw_height - (padding * 2)
            
            if box_width <= 20 or box_height <= 20:
                continue
            
            text = region.translated_text
            font_size = 28
            lines = []
            
            while font_size > 8: 
                try:
                    font = ImageFont.truetype(font_path, font_size)
                except IOError:
                    print(f"❌ Lỗi: Không tìm thấy font tại {font_path}")
                    return None
                    
                words = text.split()
                lines = []
                current_line = ""
                
                for word in words:
                    test_line = current_line + word + " "
                    line_length = draw.textlength(test_line, font=font)
                    
                    if line_length <= box_width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line.strip())
                        current_line = word + " "
                
                if current_line:
                    lines.append(current_line.strip())
                    
                # 2. Giảm khoảng cách dòng (line spacing) để khối chữ liên kết chặt chẽ hơn
                line_spacing = int(font_size * 0.05)
                total_text_height = sum([font_size for _ in lines]) + (len(lines) - 1) * line_spacing
                
                if total_text_height <= box_height:
                    break 
                    
                font_size -= 2 

            current_y = (y1 + padding) + (box_height - total_text_height) / 2
            for line in lines:
                line_width = draw.textlength(line, font=font)
                current_x = (x1 + padding) + (box_width - line_width) / 2
                
                # 3. Hạ viền stroke_width xuống 1 để chữ không bị trương phình
                draw.text(
                    (current_x, current_y), 
                    line, 
                    font=font, 
                    fill="black", 
                    stroke_width=0, 
                    stroke_fill="white"
                )
                current_y += font_size + line_spacing

        filename = os.path.basename(page.original_path)
        output_path = os.path.join(output_dir, f"final_{filename}")
        img.save(output_path)
        print(f"✅ Đã xuất bản thành công tại: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    TEST_CLEANED_IMAGE = r"E:\DatabaseFiles\CAPSTONE1_ACL\C1SE.80_ACL\data\raw_images\AisazuNihaIrarenai\045.jpg" 
    FONT_PATH = r"E:\DatabaseFiles\CAPSTONE1_ACL\C1SE.80_ACL\assets\fonts\HLcomic1_normal.ttf" 
    
    render_translated_text_on_page(page_id=1, inpainted_image_path=TEST_CLEANED_IMAGE, font_path=FONT_PATH)