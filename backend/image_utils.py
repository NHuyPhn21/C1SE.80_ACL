from PIL import Image, ImageDraw, ImageFont

def draw_text_autofit(image_path, text, bbox, font_path, max_font_size=40, output_path="output.jpg"):
    """
    Hàm chèn chữ tiếng Việt tự động fit vào bounding box và thêm viền trắng.
    
    :param image_path: Đường dẫn ảnh gốc (sau khi đã được LaMa xóa chữ).
    :param text: Chuỗi tiếng Việt cần chèn.
    :param bbox: Tọa độ box dạng tuple (x1, y1, x2, y2).
    :param font_path: Đường dẫn tới file font hỗ trợ tiếng Việt (VD: arial.ttf, Roboto-Regular.ttf).
    :param max_font_size: Cỡ chữ lớn nhất bắt đầu thử nghiệm.
    :param output_path: Đường dẫn lưu ảnh kết quả.
    """
    # Mở ảnh và khởi tạo công cụ vẽ
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    
    x1, y1, x2, y2 = bbox
    box_width = x2 - x1
    box_height = y2 - y1
    
    font_size = max_font_size
    lines = []
    
    # Vòng lặp: Giảm dần font size cho đến khi chữ nằm gọn trong box
    while font_size > 10:  # 10 là cỡ chữ tối thiểu để còn có thể đọc được
        font = ImageFont.truetype(font_path, font_size)
        words = text.split()
        lines = []
        current_line = ""
        
        # 1. Ngắt dòng (Word-wrap) dựa trên chiều rộng pixel thực tế
        for word in words:
            test_line = current_line + word + " "
            # Lấy chiều rộng của test_line
            line_length = draw.textlength(test_line, font=font)
            
            if line_length <= box_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
            
        # 2. Tính toán tổng chiều cao của khối chữ sau khi ngắt dòng
        # Khoảng cách giữa các dòng (line spacing)
        line_spacing = int(font_size * 0.2) 
        total_text_height = sum([font_size for _ in lines]) + (len(lines) - 1) * line_spacing
        
        # 3. Kiểm tra xem khối chữ đã lọt thỏm vào trong chiều cao của box chưa
        if total_text_height <= box_height:
            break # Phù hợp rồi, thoát vòng lặp!
            
        font_size -= 2 # Nếu chưa vừa, giảm cỡ chữ xuống 2 đơn vị và tính lại

    # 4. Bắt đầu vẽ chữ ra ảnh (Căn giữa theo cả chiều dọc và ngang)
    current_y = y1 + (box_height - total_text_height) / 2
    
    for line in lines:
        line_width = draw.textlength(line, font=font)
        current_x = x1 + (box_width - line_width) / 2
        
        # Hàm draw.text hỗ trợ sẵn việc tạo bóng chữ (stroke) cực mượt
        draw.text(
            (current_x, current_y), 
            line, 
            font=font, 
            fill="black",           # Màu chữ chính
            stroke_width=3,         # Độ dày của viền (3 pixel)
            stroke_fill="white"     # Màu viền (trắng) giúp nổi bật trên nền rắc rối
        )
        current_y += font_size + line_spacing

    img.save(output_path)
    print(f"Đã chèn chữ thành công tại: {output_path}")
    return output_path