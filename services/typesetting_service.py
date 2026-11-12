"""Transactional update and re-render operations for Typesetting Studio."""

from pathlib import Path
from typing import Callable

from backend.database import SessionLocal
from backend.image_utils import BASE_DIR, process_comic_page
from backend.models import ComicPage, TextRegion


class TypesettingServiceError(RuntimeError):
    pass


def save_translation_and_render(
    page_id: int,
    region_id: int,
    translated_text: str,
    font_size: float | None = None,
    *,
    session_factory=SessionLocal,
    renderer: Callable[..., str | None] = process_comic_page,
) -> str:
    clean_text = translated_text.strip()
    if not clean_text:
        raise TypesettingServiceError("Vietnamese dialogue cannot be empty.")

    db = session_factory()
    try:
        region = (
            db.query(TextRegion)
            .filter(TextRegion.id == region_id, TextRegion.page_id == page_id)
            .first()
        )
        page = db.query(ComicPage).filter(ComicPage.id == page_id).first()
        if region is None or page is None:
            raise TypesettingServiceError("Page or text region not found.")

        region.translated_text = clean_text
        if font_size is not None:
            region.font_size = font_size
        db.commit()

        output_path = renderer(page_id=page_id, use_lama_api=False)
        if not output_path:
            raise TypesettingServiceError("The page renderer did not produce an image.")

        page.rendered_path = str(Path(output_path).relative_to(BASE_DIR)).replace("\\", "/")
        page.status = "COMPLETED"
        db.commit()
        return output_path
    except TypesettingServiceError:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise TypesettingServiceError("Unable to save and render the page.") from exc
    finally:
        db.close()
