import os
import json
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv
from backend.database import SessionLocal
from backend.models import TextRegion

load_dotenv()

# Khởi tạo Client theo chuẩn Google GenAI SDK mới
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def translate_batch_dict(ja_dict: dict[str, str]) -> dict[str, str]:
    """
    Dịch toàn bộ bóng thoại trong 1 trang chỉ với 1 Request.
    Tối ưu hóa thời gian chờ (Fail-fast) và gộp Batch cho cả Fallback.
    """
    if not ja_dict:
        return {}

    prompt = (
        "Bạn là một dịch giả truyện tranh (manga) chuyên nghiệp.\n"
        "Hãy dịch danh sách các câu thoại tiếng Nhật dưới đây sang tiếng Việt tự nhiên, "
        "ngắn gọn, giàu cảm xúc và thống nhất đại từ xưng hô giữa các nhân vật trong cùng trang truyện.\n"
        "YÊU CẦU BẮT BUỘC: Chỉ trả về một JSON Object hợp lệ giữ nguyên chính xác các key (ID) ban đầu, "
        "value là bản dịch tiếng Việt tương ứng.\n\n"
        f"Dữ liệu tiếng Nhật:\n{json.dumps(ja_dict, ensure_ascii=False, indent=2)}"
    )

    candidate_models = ["gemini-3.8-flash"]

    if client:
        for model_name in candidate_models:
            # Chỉ thử tối đa 2 lần, nghỉ ngắn 2 giây để không làm chậm Pipeline
            for attempt in range(2):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=0.3,
                        ),
                    )
                    return json.loads(response.text)

                except Exception as api_error:
                    err_msg = str(api_error)
                    print(f"⚠️ Cảnh báo [{model_name} - Lần {attempt + 1}/2]: {err_msg}")
                    if any(code in err_msg for code in ["503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED"]):
                        if attempt == 0:
                            print("⏳ Đợi 2 giây rồi thử lại lần cuối...")
                            time.sleep(2)
                    else:
                        break

    # --- LỚP BẢO HIỂM SIÊU TỐC (1-REQUEST BATCH FALLBACK) ---
    print("⚡ Đang kích hoạt Fallback Translator (Chế độ gộp 1-Request, tốn ~0.5s)...")
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source="ja", target="vi")

        keys = list(ja_dict.keys())
        # Gom toàn bộ câu thoại bằng ký tự phân tách dòng để gửi đi trong 1 lần duy nhất
        combined_text = "\n ||| \n".join(ja_dict[k].strip() for k in keys)
        translated_combined = translator.translate(combined_text)

        translated_parts = [p.strip() for p in translated_combined.split("|||")]

        # Nếu số lượng câu tách ra khớp hoàn toàn
        if len(translated_parts) == len(keys):
            return dict(zip(keys, translated_parts))

        # Nếu bị lệch dòng thì tách theo '\n'
        lines = [line.strip(" |") for line in translated_combined.splitlines() if line.strip()]
        if len(lines) == len(keys):
            return dict(zip(keys, lines))

        # Trường hợp hiếm bị gộp dòng mới dịch lẻ
        return {k: translator.translate(v) if v.strip() else "" for k, v in ja_dict.items()}

    except Exception as fb_err:
        print(f"⚠️ Lỗi Fallback Translator: {fb_err}")
        return {}


def translate_manga_text(page_id: int = None, batch_size: int = 30):
    """
    Quét các bóng thoại chưa dịch trong SQLite và dịch theo từng lô (Batch).
    - Nếu truyền vào page_id: Chỉ dịch các bóng thoại của trang đó (dùng cho Pipeline).
    - Nếu không truyền page_id: Dịch toàn bộ các bóng thoại còn trống trong DB.
    """
    db = SessionLocal()
    try:
        query = db.query(TextRegion).filter(
            (TextRegion.translated_text == None) | (TextRegion.translated_text == "")
        )
        if page_id is not None:
            query = query.filter(TextRegion.page_id == page_id)

        regions = query.all()

        # Lọc các vùng thực sự có chữ tiếng Nhật
        valid_regions = [
            r for r in regions
            if r.original_text and r.original_text.strip()
        ]

        if not valid_regions:
            print("✅ Tất cả các bóng thoại đều đã có bản dịch!")
            return True

        print(f"🚀 Bắt đầu dịch GỘP (Batch Mode) cho {len(valid_regions)} bóng thoại...")
        t_start = time.time()

        # Chia thành từng lô tối đa 30 bóng thoại / 1 Request để tối ưu ngữ cảnh và token
        for i in range(0, len(valid_regions), batch_size):
            chunk = valid_regions[i : i + batch_size]
            payload = {str(r.id): r.original_text.strip() for r in chunk}

            print(f"⚡ Đang gửi 1 Request gộp {len(chunk)} câu thoại lên Gemini...")
            translated_map = translate_batch_dict(payload)

            if not translated_map:
                print("❌ Không nhận được phản hồi dịch cho lô này. Vui lòng kiểm tra lại GEMINI_API_KEY.")
                continue

            # Cập nhật toàn bộ kết quả vào SQLite chỉ trong 1 lần commit
            for r in chunk:
                vi_text = translated_map.get(str(r.id), "").strip()
                if vi_text:
                    r.translated_text = vi_text
                    print(f"  [ID {r.id}] {r.original_text}  ➔  {vi_text}")

            db.commit()

        print(f"🎉 Hoàn tất dịch {len(valid_regions)} bóng thoại chỉ trong {time.time() - t_start:.2f} giây!")
        return True

    except Exception as e:
        print(f"❌ Lỗi hệ thống khi dịch: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    translate_manga_text()