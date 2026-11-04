"""OCR correction and re-translation workflow for Review Studio."""

from collections.abc import Callable, Mapping

from backend.database import SessionLocal
from backend.models import ComicPage, TextRegion


class ReviewServiceError(RuntimeError):
    pass


def save_ocr_and_retranslate(
    page_id: int,
    edited_texts: Mapping[int, str],
    *,
    session_factory=SessionLocal,
    translator: Callable[..., bool] | None = None,
    renderer: Callable[..., str | None] | None = None,
) -> int:
    if translator is None:
        from ai_core.translator import translate_manga_text

        translator = translate_manga_text
    if renderer is None:
        from backend.image_utils import process_comic_page

        renderer = process_comic_page
    db = session_factory()
    changed = 0
    try:
        page = db.query(ComicPage).filter(ComicPage.id == page_id).first()
        if page is None:
            raise ReviewServiceError("Page not found.")

        regions = {
            region.id: region
            for region in db.query(TextRegion)
            .filter(TextRegion.page_id == page_id)
            .all()
        }
        for region_id, text in edited_texts.items():
            region = regions.get(int(region_id))
            clean_text = text.strip()
            if region is None or not clean_text or region.original_text == clean_text:
                continue
            region.original_text = clean_text
            region.translated_text = ""
            changed += 1
        db.commit()
    except ReviewServiceError:
        db.rollback()
        raise
    finally:
        db.close()

    if not changed:
        return 0
    if not translator(page_id=page_id):
        raise ReviewServiceError("OCR was saved, but translation failed.")
    if not renderer(page_id=page_id, use_lama_api=False):
        raise ReviewServiceError("Translation completed, but page rendering failed.")
    return changed
