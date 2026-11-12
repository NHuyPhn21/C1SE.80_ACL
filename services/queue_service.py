"""Queue progress and rendered chapter export helpers."""

import io
import zipfile
from dataclasses import dataclass
from pathlib import Path

from backend.database import SessionLocal
from backend.image_utils import BASE_DIR, resolve_project_path
from backend.models import Chapter, ComicPage, Project


@dataclass(frozen=True)
class QueueProgress:
    total_pages: int
    completed_pages: int
    failed_pages: int

    @property
    def percent(self) -> int:
        if not self.total_pages:
            return 0
        return min(100, round(self.completed_pages / self.total_pages * 100))


class QueueService:
    def __init__(self, session_factory=SessionLocal) -> None:
        self.session_factory = session_factory

    def progress(self, project_name: str) -> QueueProgress:
        db = self.session_factory()
        try:
            query = db.query(ComicPage).join(Chapter, ComicPage.chapter_id == Chapter.id)
            project = db.query(Project).filter(Project.title == project_name).first()
            if project is not None:
                query = query.filter(Chapter.project_id == project.id)
            pages = query.all()
            return QueueProgress(
                total_pages=len(pages),
                completed_pages=sum(page.status == "COMPLETED" for page in pages),
                failed_pages=sum(page.status == "FAILED" for page in pages),
            )
        finally:
            db.close()

    def rendered_files(self, project_name: str) -> list[Path]:
        db = self.session_factory()
        try:
            query = (
                db.query(ComicPage)
                .join(Chapter, ComicPage.chapter_id == Chapter.id)
                .filter(ComicPage.rendered_path.isnot(None))
            )
            project = db.query(Project).filter(Project.title == project_name).first()
            if project is not None:
                query = query.filter(Chapter.project_id == project.id)
            paths = []
            for page in query.order_by(ComicPage.page_number.asc()).all():
                resolved = Path(resolve_project_path(page.rendered_path))
                if resolved.exists() and resolved.is_file():
                    paths.append(resolved)
            if paths:
                return paths
        finally:
            db.close()

        rendered_dir = BASE_DIR / "data" / "rendered_pages"
        if not rendered_dir.exists():
            return []
        return sorted(rendered_dir.glob("final_*.*"))


def build_rendered_zip(files: list[Path]) -> bytes:
    output = io.BytesIO()
    used_names: set[str] = set()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for index, path in enumerate(files, start=1):
            if not path.exists() or not path.is_file():
                continue
            arcname = path.name
            if arcname in used_names:
                arcname = f"{index:03d}_{arcname}"
            archive.write(path, arcname=arcname)
            used_names.add(arcname)
    return output.getvalue()
