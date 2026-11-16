import tempfile
import unittest
import zipfile
from io import BytesIO
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.models import Chapter, ComicPage, ProjectMembership, User
from services.queue_service import QueueService, build_release_manifest, build_rendered_zip
from services.workspace_service import WorkspaceService, WorkspaceServiceError


class WorkspaceAndQueueTests(unittest.TestCase):
    def setUp(self) -> None:
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        self.session_factory = sessionmaker(bind=engine)
        db = self.session_factory()
        owner = User(username="Owner", email="owner@example.com", password_hash="x")
        db.add(owner)
        db.commit()
        self.owner_id = owner.id
        db.close()
        self.workspace = WorkspaceService(
            self.session_factory, initialize_database=False
        )
        self.queue = QueueService(self.session_factory)

    def test_create_project_and_load_dynamic_progress(self) -> None:
        project_id = self.workspace.create_project(
            self.owner_id, "Manga A", "Japanese to Vietnamese"
        )
        db = self.session_factory()
        owner_membership = db.query(ProjectMembership).filter_by(
            project_id=project_id, user_id=self.owner_id
        ).one()
        self.assertEqual(owner_membership.project_role, "Owner")
        chapter = Chapter(project_id=project_id, chapter_number=1)
        db.add(chapter)
        db.flush()
        db.add_all(
            [
                ComicPage(chapter_id=chapter.id, page_number=1, original_path="1.png", status="COMPLETED"),
                ComicPage(chapter_id=chapter.id, page_number=2, original_path="2.png", status="PENDING"),
            ]
        )
        db.commit()
        db.close()

        summary = self.workspace.list_projects(self.owner_id)[0]
        self.assertEqual(summary.total_pages, 2)
        self.assertEqual(summary.completed_pages, 1)
        self.assertEqual(summary.progress_percent, 50)

        progress = self.queue.progress("Manga A")
        self.assertEqual(progress.total_pages, 2)
        self.assertEqual(progress.completed_pages, 1)
        self.assertEqual(progress.percent, 50)

    def test_duplicate_project_title_is_rejected(self) -> None:
        self.workspace.create_project(self.owner_id, "Manga A")
        with self.assertRaises(WorkspaceServiceError):
            self.workspace.create_project(self.owner_id, "Manga A")

    def test_zip_contains_each_rendered_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "final_001.png"
            second = root / "final_002.png"
            first.write_bytes(b"first")
            second.write_bytes(b"second")

            archive_data = build_rendered_zip([first, second])
            with zipfile.ZipFile(BytesIO(archive_data)) as archive:
                self.assertEqual(
                    archive.namelist(), ["final_001.png", "final_002.png"]
                )
                self.assertEqual(archive.read("final_002.png"), b"second")

    def _add_rendered_page(self, project_id: int, number: int, directory: Path, name: str) -> int:
        file = directory / name
        file.write_bytes(name.encode())
        db = self.session_factory()
        chapter = Chapter(project_id=project_id, chapter_number=number, chapter_name=f"Chapter {number}")
        db.add(chapter)
        db.flush()
        db.add(ComicPage(chapter_id=chapter.id, page_number=1, original_path=str(file),
                         rendered_path=str(file), status="COMPLETED"))
        db.commit()
        chapter_id = chapter.id
        db.close()
        return chapter_id

    def test_rendered_files_are_scoped_to_project_and_chapter(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            a = self.workspace.create_project(self.owner_id, "A")
            b = self.workspace.create_project(self.owner_id, "B")
            a1 = self._add_rendered_page(a, 1, root, "a1.png")
            self._add_rendered_page(a, 2, root, "a2.png")
            self._add_rendered_page(b, 1, root, "b1.png")

            names = lambda files: sorted(f.name for f in files)
            self.assertEqual(names(self.queue.rendered_files(project_id=a)), ["a1.png", "a2.png"])
            self.assertEqual(names(self.queue.rendered_files(project_id=a, chapter_id=a1)), ["a1.png"])
            # Unknown project must not fall back to every rendered file on disk.
            self.assertEqual(self.queue.rendered_files("missing"), [])

    def test_zip_includes_release_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / "final_001.png"
            page.write_bytes(b"x")
            manifest = build_release_manifest("Manga A", [("Chapter 1", page)])
            with zipfile.ZipFile(BytesIO(build_rendered_zip([page], manifest))) as archive:
                self.assertIn("RELEASE_MANIFEST.txt", archive.namelist())
                text = archive.read("RELEASE_MANIFEST.txt").decode()
                self.assertIn("Project: Manga A", text)
                self.assertIn("final_001.png", text)

    def test_update_and_delete_project(self) -> None:
        a = self.workspace.create_project(self.owner_id, "A")
        self.workspace.create_project(self.owner_id, "B")
        self.workspace.update_project(a, "A2", "new desc")
        summary = next(p for p in self.workspace.list_projects(self.owner_id) if p.id == a)
        self.assertEqual((summary.title, summary.description), ("A2", "new desc"))
        with self.assertRaises(WorkspaceServiceError):
            self.workspace.update_project(a, "B")
        self.workspace.delete_project(a)
        self.assertEqual([p.title for p in self.workspace.list_projects(self.owner_id)], ["B"])
        with self.assertRaises(WorkspaceServiceError):
            self.workspace.delete_project(a)


if __name__ == "__main__":
    unittest.main()
