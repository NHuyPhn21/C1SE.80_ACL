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
from services.queue_service import QueueService, build_rendered_zip
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


if __name__ == "__main__":
    unittest.main()
