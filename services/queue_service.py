"""Queue progress and rendered chapter export helpers."""

import io
import zipfile
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

from backend.database import SessionLocal
from backend.image_utils import resolve_project_path
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

    def rendered_files(
        self,
        project_name: str | None = None,
        chapter_id: int | None = None,
        *,
        project_id: int | None = None,
    ) -> list[Path]:
        """Return rendered pages scoped to one project (and optionally one chapter).

        There is intentionally no directory-wide fallback: pages of other
        projects must never leak into an export.
        """
        return [path for _, path in self.rendered_entries(project_name, chapter_id, project_id=project_id)]

    def rendered_entries(
        self,
        project_name: str | None = None,
        chapter_id: int | None = None,
        *,
        project_id: int | None = None,
    ) -> list[tuple[Chapter, Path]]:
        db = self.session_factory()
        try:
            if project_id is None:
                project = db.query(Project).filter(Project.title == project_name).first()
                if project is None:
                    return []
                project_id = project.id
            query = (
                db.query(ComicPage, Chapter)
                .join(Chapter, ComicPage.chapter_id == Chapter.id)
                .filter(Chapter.project_id == project_id, ComicPage.rendered_path.isnot(None))
            )
            if chapter_id is not None:
                query = query.filter(Chapter.id == chapter_id)
            entries: list[tuple[Chapter, Path]] = []
            for page, chapter in query.order_by(Chapter.chapter_number.asc(), ComicPage.page_number.asc()).all():
                resolved = Path(resolve_project_path(page.rendered_path))
                if resolved.exists() and resolved.is_file():
                    entries.append((chapter, resolved))
            return entries
        finally:
            db.close()


def build_release_manifest(project_title: str, entries: list[tuple[str, Path]]) -> str:
    """Plain-text manifest listing what is inside an export archive."""
    lines = [
        f"Project: {project_title}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total pages: {len(entries)}",
        "",
    ]
    current = None
    for chapter_label, path in entries:
        if chapter_label != current:
            current = chapter_label
            lines.append(f"[{chapter_label}]")
        lines.append(f"  - {path.name}")
    return "\n".join(lines) + "\n"


def build_rendered_zip(files: list[Path], manifest: str | None = None) -> bytes:
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
        if manifest is not None:
            archive.writestr("RELEASE_MANIFEST.txt", manifest)
    return output.getvalue()
