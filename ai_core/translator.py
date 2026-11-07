import os
import json
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False

from backend.database import SessionLocal
from backend.models import TextRegion

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

def _safe_log(message: str) -> None:
    """Keep worker logs usable on Windows consoles with legacy encodings."""
    print(message.encode("ascii", "backslashreplace").decode("ascii"))


def _valid_translation(value: object) -> bool:
    text = str(value).strip()
    return bool(text and text not in {"...", "…", "N/A", "null"})


def _gemini_client(api_key: str | None = None):
    """Create Gemini client with provided API key. Key MUST be provided."""
    if not api_key:
        return None
    
    api_key = api_key.strip()
    if not api_key:
        return None
    
    return (
        genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=120000),
        )
        if (genai and types)
        else None
    )


def _openai_client(api_key: str | None = None):
    """Create OpenAI client with provided API key."""
    if not api_key or not OpenAI:
        return None
    
    api_key = api_key.strip()
    if not api_key:
        return None
    
    return OpenAI(api_key=api_key, timeout=120.0)


def _deepl_client(api_key: str | None = None):
    """Create DeepL client with provided API key."""
    if not api_key:
        return None
    
    api_key = api_key.strip()
    if not api_key:
        return None
    
    try:
        import deepl
        return deepl.Translator(api_key)
    except ImportError:
        return None


def _run_with_timeout(function, timeout_seconds: int):
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(function)
    try:
        return future.result(timeout=timeout_seconds)
    except FutureTimeoutError as exc:
        future.cancel()
        raise TimeoutError(
            f"Translation provider timed out after {timeout_seconds} seconds"
        ) from exc
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


def translate_batch_dict(
    ja_dict: dict[str, str],
    api_key: str | None = None,
    project_id: int | None = None,
) -> dict[str, str]:
    """
    Dịch toàn bộ bóng thoại 1 trang trong 1 Request Gemini.
    API key MUST be provided either directly or via project_id from database.
    
    Args:
        ja_dict: Dict[str, str] - mapping {region_id: original_text}
        api_key: Gemini API key (if not provided, will load from database via project_id)
        project_id: Project ID to load API key from database (required if api_key not provided)
    
    Returns:
        Dict[str, str]: Translated text mapping, empty dict if translation failed
    """
    if not ja_dict:
        return {}

    # Load API keys from database
    gemini_key = None
    deepl_key = None
    
    if project_id:
        try:
            from services.settings_service import SettingsService
            settings = SettingsService()
            
            # Load DeepL key first (preferred)
            deepl_key = settings.load_api_key_for_pipeline(project_id, provider="deepl")
            if deepl_key:
                _safe_log(f"✓ Loaded DeepL API key from database for project {project_id}")
            
            # Load Gemini key
            gemini_key = settings.load_api_key_for_pipeline(project_id, provider="gemini")
            if gemini_key:
                _safe_log(f"✓ Loaded Gemini API key from database for project {project_id}")
                
        except Exception as e:
            _safe_log(f"❌ ERROR: Failed to load API keys from database: {e}")
            return {}
    
    # Use provided api_key as Gemini key if given
    if api_key and not gemini_key:
        gemini_key = api_key

    prompt = (
        "You are a professional manga translator. Translate the following Japanese dialogue "
        "to Vietnamese naturally, concisely, emotionally, and with consistent pronouns across the page.\n"
        "CRITICAL: Return ONLY a valid JSON object with EXACT same keys (IDs) as input, "
        "values are Vietnamese translations. No markdown, no extra text.\n\n"
        f"Input data:\n{json.dumps(ja_dict, ensure_ascii=False, indent=2)}"
    )

    configured_model = os.getenv("GEMINI_MODEL", "").strip()
    candidate_models = list(dict.fromkeys(
        model for model in (
            configured_model,
            "gemini-3.6-flash",
            "gemini-2.5-flash",
            "gemini-3.5-flash",
            "gemini-3.8-flash",
            "gemini-flash-latest",
        )
        if model
    ))

    # === TRY DEEPL FIRST (Fast & Stable) ===
    if deepl_key:
        _safe_log(f"→ Sending {len(ja_dict)} regions to DeepL...")
        deepl_client = _deepl_client(deepl_key)
        if deepl_client:
            try:
                translated = {}
                for key, source_text in ja_dict.items():
                    if not source_text.strip():
                        continue
                    try:
                        result = deepl_client.translate_text(
                            source_text,
                            source_lang="JA",
                            target_lang="VI"
                        )
                        if result and result.text:
                            translated[key] = result.text.strip()
                    except Exception as e:
                        _safe_log(f"  ✗ ID {key}: {str(e)[:80]}")
                
                if len(translated) == len(ja_dict):
                    _safe_log(f"✓ DeepL translated all {len(translated)} regions successfully!")
                    return translated
                elif translated:
                    _safe_log(f"✓ DeepL partial: {len(translated)}/{len(ja_dict)} translated")
                    return translated
                else:
                    _safe_log("⚠️ DeepL returned no valid translations")
            except Exception as e:
                _safe_log(f"⚠️ DeepL error: {str(e)[:300]}")
        else:
            _safe_log("⚠️ DeepL client unavailable")
    else:
        _safe_log("⚠️ No DeepL API key found, trying Gemini...")

    # === TRY GEMINI (Single model, short timeout) ===
    if gemini_key:
        _safe_log(f"→ Sending {len(ja_dict)} regions to Gemini [gemini-3.6-flash]...")
        client = _gemini_client(gemini_key)
        if client:
            try:
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.3,
                        max_output_tokens=8192,
                    ),
                )
                response_text = (response.text or "").strip()
                _safe_log(f"  Raw response length: {len(response_text)} chars")
                
                if response_text.startswith("```"):
                    response_text = response_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                
                parsed = json.loads(response_text)
                if isinstance(parsed, dict):
                    translations = {}
                    for key in ja_dict:
                        if key in parsed and _valid_translation(parsed[key]):
                            translations[key] = str(parsed[key]).strip()
                    
                    if len(translations) == len(ja_dict):
                        _safe_log(f"✓ Gemini translated {len(translations)} regions successfully!")
                        return translations
                    elif translations:
                        _safe_log(f"✓ Gemini partial: {len(translations)}/{len(ja_dict)} translated")
                        return translations
                    else:
                        _safe_log("⚠️ Gemini returned no valid translations")
                else:
                    _safe_log(f"⚠️ Gemini response is not a dict")
            except Exception as e:
                err_str = str(e)
                _safe_log(f"⚠️ Gemini error: {err_str[:200]}")
        else:
            _safe_log("⚠️ Gemini client unavailable")
    else:
        _safe_log("⚠️ No Gemini API key found")

    _safe_log("❌ All translation providers failed")
    return {}


def translate_manga_text(
    page_id: int = None,
    batch_size: int = 1000,  # Gộp tất cả câu trong 1 request
    project_id: int | None = None,
):
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
            _safe_log("✅ Tất cả các bóng thoại đều đã có bản dịch!")
            return True

        _safe_log(f"🚀 Bắt đầu dịch GỘP (Batch Mode) cho {len(valid_regions)} bóng thoại...")
        t_start = time.time()

        # Keep requests small enough for long pages and avoid provider request timeouts.
        for i in range(0, len(valid_regions), batch_size):
            chunk = valid_regions[i : i + batch_size]
            payload = {str(r.id): r.original_text.strip() for r in chunk}

            _safe_log(f"⚡ Đang gửi 1 Request gộp {len(chunk)} câu thoại...")
            translated_map = translate_batch_dict(
                payload,
                api_key=None,
                project_id=project_id
            )

            if not translated_map:
                _safe_log(
                    f"❌ Không nhận được phản hồi dịch cho lô "
                    f"{i + 1}-{i + len(chunk)}. Lô này sẽ được đánh dấu chưa dịch."
                )
                continue

            # Cập nhật toàn bộ kết quả vào SQLite chỉ trong 1 lần commit
            for r in chunk:
                vi_text = translated_map.get(str(r.id), "").strip()
                if vi_text:
                    r.translated_text = vi_text
                    _safe_log(f"  [ID {r.id}] {r.original_text[:30]}... ➔ {vi_text[:30]}...")

            db.commit()

        _safe_log(f"🎉 Hoàn tất dịch {len(valid_regions)} bóng thoại chỉ trong {time.time() - t_start:.2f} giây!")
        return True

    except Exception as e:
        _safe_log(f"❌ Lỗi hệ thống khi dịch: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    translate_manga_text()
