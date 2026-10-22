import os
import time
from google import genai
from dotenv import load_dotenv
from backend.database import SessionLocal
from backend.models import TextRegion

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def translate_manga_text():
    db = SessionLocal()
    try:
        regions = db.query(TextRegion).filter(
            (TextRegion.translated_text == None) | (TextRegion.translated_text == "")
        ).all()

        if not regions:
            print("Tất cả các bóng thoại đã được dịch!")
            return

        print(f"🚀 Bắt đầu dịch {len(regions)} bóng thoại bằng Gemini SDK mới...")
        
        for region in regions:
            prompt = f"""
            Bạn là một dịch giả truyện tranh (manga) chuyên nghiệp.
            Hãy dịch câu thoại tiếng Nhật sau sang tiếng Việt một cách tự nhiên, sắc thái cảm xúc rõ ràng.
            Chỉ trả về nội dung bản dịch, tuyệt đối không giải thích hay thêm dấu ngoặc kép.
            
            Tiếng Nhật: {region.original_text}
            """
            
            # Cơ chế Retry: Thử lại tối đa 3 lần nếu server Google bị lỗi 503
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = client.models.generate_content(
                        model='gemini-3.8-flash', 
                        contents=prompt,
                    )
                    translated_text = response.text.strip()
                    region.translated_text = translated_text
                    
                    print(f"Gốc: {region.original_text}\n-> Dịch: {translated_text}\n{'-'*40}")
                    
                    # Nghỉ 2 giây giữa mỗi lần gọi để tránh bị Google giới hạn rate limit
                    time.sleep(2)
                    
                    # Thành công thì lưu tạm vào DB và thoát vòng lặp retry để dịch câu tiếp theo
                    db.commit()
                    break 
                    
                except Exception as api_error:
                    if attempt < max_retries - 1:
                        # 1. In ra lỗi thật để xem Google đang báo gì (429 Quota, 400 Safety, hay 503)
                        print(f"⚠️ Lỗi thật sự: {api_error}") 
                        
                        # 2. Nghỉ hẳn 35 giây để lách luật "2 request/phút" của bản Pro Free Tier
                        print(f"⏳ Đang đứng đợi ({attempt + 1}/{max_retries}) sau 35 giây...")
                        time.sleep(35) 
                    else:
                        print(f"❌ Thất bại sau {max_retries} lần thử cho câu: {region.original_text}. Bỏ qua.")
            
        print("✅ Đã xử lý xong luồng dịch thuật tiếng Việt!")
        
    except Exception as e:
        print(f"❌ Lỗi hệ thống: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    translate_manga_text()