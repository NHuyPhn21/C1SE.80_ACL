import os
from PIL import Image
from ultralytics import YOLO
from manga_ocr import MangaOcr

def extract_manga_text(image_path, yolo_weight_path):
    """
    Hàm nhận diện bóng thoại và trích xuất chữ tiếng Nhật
    """
    print("⏳ Đang tải mô hình YOLO và Manga OCR (có thể mất vài giây lần đầu)...")
    
    # 1. Load mô hình YOLO (trỏ đúng tới file best.pt của bạn)
    yolo_model = YOLO(yolo_weight_path)
    
    # 2. Load mô hình Manga OCR
    mocr = MangaOcr()
    
    # Mở ảnh gốc để chuẩn bị cắt
    img = Image.open(image_path).convert("RGB")
    
    # 3. Chạy YOLO để lấy tọa độ
    print(f"🔍 Đang quét ảnh: {image_path}")
    results = yolo_model(image_path, verbose=False) # verbose=False để tắt bớt log rác
    
    extracted_data = []
    
    # 4. Duyệt qua các kết quả nhận diện được
    for r in results:
        boxes = r.boxes
        for box in boxes:
            # box.cls chứa ID của nhãn (0 là panel, 1 là text_bubble)
            class_id = int(box.cls[0])
            
            # Chỉ xử lý nếu nó là text_bubble
            if class_id == 1:
                # Lấy tọa độ (x_min, y_min, x_max, y_max) và ép kiểu về số nguyên
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # Cắt ảnh bong bóng thoại
                cropped_bubble = img.crop((x1, y1, x2, y2))
                
                # Gọi Manga OCR đọc chữ trên ảnh vừa cắt
                japanese_text = mocr(cropped_bubble)
                
                # Lưu lại thông tin để sau này đẩy vào Database
                bubble_info = {
                    "bbox": [x1, y1, x2, y2],
                    "japanese_text": japanese_text
                }
                extracted_data.append(bubble_info)
                
                print(f"Tọa độ {bubble_info['bbox']} -> Chữ đọc được: {japanese_text}")
                
    return extracted_data

if __name__ == "__main__":
    # Đổi đường dẫn này thành ảnh bất kỳ trong tập data/raw_images của bạn để test thử
    TEST_IMAGE_PATH = r"E:\DatabaseFiles\CAPSTONE1_ACL\C1SE.80_ACL\data\raw_images\AisazuNihaIrarenai\045.jpg"
    
    # Đường dẫn tới file trọng số bạn vừa train thành công hôm qua
    YOLO_WEIGHT_PATH = "models/yolo/manga_v14/weights/best.pt"
    
    # Chạy thử luồng
    results = extract_manga_text(TEST_IMAGE_PATH, YOLO_WEIGHT_PATH)
    
    print("\n✅ HOÀN TẤT TRÍCH XUẤT! Tổng số bóng thoại tìm thấy:", len(results))