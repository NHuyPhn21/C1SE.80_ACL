"""Integration tests for Workspace management, RBAC, Chapter numbering, file upload, and conflict handling.

Covers Leader's Task C specification:
- Project creation, duplicate name rejection, PUT/DELETE with RBAC (Translator/Typesetter blocked 403)
- Chapter creation auto-increment numbering without duplicates
- POST /api/upload supporting .jpg, .jpeg, .png, .webp with page_number auto-increment
- Rejecting non-image formats (.pdf, .txt, .exe) with HTTP 415 Unsupported Media Type
- Deleting single chapter & clearing project data with HTTP 409 Conflict check when task is RUNNING/QUEUED
"""

import io
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.models import Chapter, ComicPage, Project, ProjectMembership, QueueTask, TextRegion, User
from fastapi_app import app
from services.team_service import TeamService
from services.workspace_service import WorkspaceService


class WorkspaceUploadIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=self.engine)
        self.TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        # Patch SessionLocal across backend.api, backend.database, and services
        self.patchers = [
            patch("backend.api.SessionLocal", self.TestingSessionLocal),
            patch("backend.database.SessionLocal", self.TestingSessionLocal),
            patch(
                "backend.api.WorkspaceService",
                lambda: WorkspaceService(
                    session_factory=self.TestingSessionLocal,
                    initialize_database=False,
                ),
            ),
            patch(
                "backend.api.TeamService",
                lambda: TeamService(
                    session_factory=self.TestingSessionLocal,
                    initialize_database=False,
                ),
            ),
        ]
        for patcher in self.patchers:
            patcher.start()

        self.client = TestClient(app)

        # Seed test users: Owner, Translator, Typesetter, and Another Owner
        db = self.TestingSessionLocal()
        self.owner = User(
            username="owner_user", email="owner@acl.local", password_hash="hash1"
        )
        self.translator = User(
            username="trans_user", email="translator@acl.local", password_hash="hash2"
        )
        self.typesetter = User(
            username="typeset_user", email="typesetter@acl.local", password_hash="hash3"
        )
        self.other_owner = User(
            username="other_owner", email="other@acl.local", password_hash="hash4"
        )
        db.add_all([self.owner, self.translator, self.typesetter, self.other_owner])
        db.commit()
        db.refresh(self.owner)
        db.refresh(self.translator)
        db.refresh(self.typesetter)
        db.refresh(self.other_owner)
        db.close()

    def tearDown(self) -> None:
        for patcher in reversed(self.patchers):
            patcher.stop()

    def test_create_project_and_prevent_duplicate_name_for_same_owner(self) -> None:
        """Owner can create project; duplicate title by same owner returns 400; another owner can reuse title."""
        res1 = self.client.post(
            f"/api/projects?user_id={self.owner.id}",
            json={"title": "One Piece Raw", "description": "Adventure manga"},
        )
        self.assertEqual(res1.status_code, 200)
        project_data = res1.json()
        self.assertEqual(project_data["title"], "One Piece Raw")

        # Duplicate title by same owner -> 400 Bad Request
        res_dup = self.client.post(
            f"/api/projects?user_id={self.owner.id}",
            json={"title": "One Piece Raw", "description": "Duplicate attempt"},
        )
        self.assertEqual(res_dup.status_code, 400)
        self.assertIn("project with this title", res_dup.json()["detail"].lower())

        # Another owner creating same title -> 200 OK
        res_other = self.client.post(
            f"/api/projects?user_id={self.other_owner.id}",
            json={"title": "One Piece Raw", "description": "Different owner project"},
        )
        self.assertEqual(res_other.status_code, 200)

    def test_put_and_delete_project_rbac_enforcement(self) -> None:
        """Translator and Typesetter get 403 Forbidden when updating or deleting a project."""
        # Create project owned by self.owner
        res = self.client.post(
            f"/api/projects?user_id={self.owner.id}",
            json={"title": "RBAC Test Manga", "description": "Original description"},
        )
        self.assertEqual(res.status_code, 200)
        project_id = res.json()["id"]

        # Add Translator and Typesetter as members
        db = self.TestingSessionLocal()
        db.add(ProjectMembership(project_id=project_id, user_id=self.translator.id, project_role="Translator"))
        db.add(ProjectMembership(project_id=project_id, user_id=self.typesetter.id, project_role="Typesetter"))
        db.commit()
        db.close()

        # Translator attempts PUT -> 403 Forbidden
        put_trans = self.client.put(
            f"/api/projects/{project_id}?user_id={self.translator.id}",
            json={"title": "Hacked Title", "description": "Hacked Desc"},
        )
        self.assertEqual(put_trans.status_code, 403)

        # Typesetter attempts PUT -> 403 Forbidden
        put_typeset = self.client.put(
            f"/api/projects/{project_id}?user_id={self.typesetter.id}",
            json={"title": "Hacked Title", "description": "Hacked Desc"},
        )
        self.assertEqual(put_typeset.status_code, 403)

        # Translator attempts DELETE -> 403 Forbidden
        del_trans = self.client.delete(
            f"/api/projects/{project_id}?user_id={self.translator.id}"
        )
        self.assertEqual(del_trans.status_code, 403)

        # Typesetter attempts DELETE -> 403 Forbidden
        del_typeset = self.client.delete(
            f"/api/projects/{project_id}?user_id={self.typesetter.id}"
        )
        self.assertEqual(del_typeset.status_code, 403)

        # Owner attempts PUT -> 200 OK
        put_owner = self.client.put(
            f"/api/projects/{project_id}?user_id={self.owner.id}",
            json={"title": "Updated Title", "description": "Updated Desc"},
        )
        self.assertEqual(put_owner.status_code, 200)
        self.assertEqual(put_owner.json()["title"], "Updated Title")

        # Owner attempts DELETE -> 200 OK
        del_owner = self.client.delete(
            f"/api/projects/{project_id}?user_id={self.owner.id}"
        )
        self.assertEqual(del_owner.status_code, 200)

    def test_chapter_auto_increment_numbering(self) -> None:
        """Chapters automatically increment numbering and prevent duplicate numbers even if deleted."""
        res_proj = self.client.post(
            f"/api/projects?user_id={self.owner.id}",
            json={"title": "Chapter Increment Manga", "description": "Test chapters"},
        )
        project_id = res_proj.json()["id"]

        # Create Chapter 1
        res_c1 = self.client.post(
            f"/api/projects/{project_id}/chapters",
            json={"chapter_name": "First Chapter"},
        )
        self.assertEqual(res_c1.status_code, 200)
        c1 = res_c1.json()
        self.assertEqual(c1["chapter_number"], 1)

        # Create Chapter 2
        res_c2 = self.client.post(
            f"/api/projects/{project_id}/chapters",
            json={"chapter_name": "Second Chapter"},
        )
        self.assertEqual(res_c2.status_code, 200)
        c2 = res_c2.json()
        self.assertEqual(c2["chapter_number"], 2)

        # Delete Chapter 2, then create next chapter -> chapter_number remains consistent without duplicate
        del_c2 = self.client.delete(
            f"/api/projects/{project_id}/chapters/{c2['id']}?user_id={self.owner.id}"
        )
        self.assertEqual(del_c2.status_code, 200)

        res_c2_new = self.client.post(
            f"/api/projects/{project_id}/chapters",
            json={"chapter_name": "New Second Chapter"},
        )
        self.assertEqual(res_c2_new.status_code, 200)
        self.assertEqual(res_c2_new.json()["chapter_number"], 2)

        # Create Chapter 3
        res_c3 = self.client.post(
            f"/api/projects/{project_id}/chapters",
            json={"chapter_name": "Third Chapter"},
        )
        self.assertEqual(res_c3.status_code, 200)
        c3 = res_c3.json()
        self.assertEqual(c3["chapter_number"], 3)

        # Delete Chapter 1 midway (gap scenario)
        del_c1 = self.client.delete(
            f"/api/projects/{project_id}/chapters/{c1['id']}?user_id={self.owner.id}"
        )
        self.assertEqual(del_c1.status_code, 200)

        # Create next chapter -> max is 3, so new chapter number is 4 (no collision with existing 2 or 3)
        res_c4 = self.client.post(
            f"/api/projects/{project_id}/chapters",
            json={"chapter_name": "Fourth Chapter"},
        )
        self.assertEqual(res_c4.status_code, 200)
        self.assertEqual(res_c4.json()["chapter_number"], 4)

    @patch("ai_core.text_extractor.extract_manga_text")
    def test_upload_supported_formats_and_auto_increment_pages(self, mock_extract) -> None:
        """Upload accepts .jpg, .jpeg, .png, .webp and auto-increments page_number."""
        mock_extract.return_value = [
            {"bbox": [10, 10, 50, 50], "japanese_text": "テストテキスト"}
        ]

        # Setup project & chapter
        res_proj = self.client.post(
            f"/api/projects?user_id={self.owner.id}",
            json={"title": "Upload Format Manga", "description": "Test upload"},
        )
        project_id = res_proj.json()["id"]
        res_c = self.client.post(
            f"/api/projects/{project_id}/chapters",
            json={"chapter_name": "Upload Chapter"},
        )
        chapter_id = res_c.json()["id"]

        dummy_image_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"

        formats = ["page1.jpg", "page2.jpeg", "page3.png", "page4.webp"]
        for expected_num, filename in enumerate(formats, start=1):
            response = self.client.post(
                "/api/upload",
                params={"chapter_id": chapter_id},
                files={"file": (filename, dummy_image_data, "image/octet-stream")},
            )
            self.assertEqual(
                response.status_code,
                200,
                f"Failed for {filename}: {response.text}",
            )
            page_data = response.json()
            self.assertEqual(page_data["page_number"], expected_num)
            self.assertEqual(page_data["status"], "EXTRACTED")
            self.assertEqual(len(page_data["regions"]), 1)

    def test_upload_unsupported_formats_returns_415(self) -> None:
        """Upload rejects .pdf, .txt, .exe with HTTP 415 Unsupported Media Type."""
        res_proj = self.client.post(
            f"/api/projects?user_id={self.owner.id}",
            json={"title": "Invalid Format Manga", "description": "Test rejection"},
        )
        chapter_id = self.client.post(
            f"/api/projects/{res_proj.json()['id']}/chapters",
            json={"chapter_name": "Chapter 1"},
        ).json()["id"]

        invalid_files = [
            ("document.pdf", b"%PDF-1.4...", "application/pdf"),
            ("notes.txt", b"plain text data", "text/plain"),
            ("program.exe", b"MZ\x90\x00binary", "application/octet-stream"),
        ]

        for filename, content, mime in invalid_files:
            response = self.client.post(
                "/api/upload",
                params={"chapter_id": chapter_id},
                files={"file": (filename, content, mime)},
            )
            self.assertEqual(
                response.status_code,
                415,
                f"Expected 415 for {filename}, got {response.status_code}",
            )
            self.assertIn("Unsupported image format", response.json()["detail"])

    def test_delete_chapter_conflict_409_when_task_running_or_queued(self) -> None:
        """DELETE chapter returns 409 Conflict if task is RUNNING or QUEUED."""
        res_proj = self.client.post(
            f"/api/projects?user_id={self.owner.id}",
            json={"title": "Task Conflict Chapter Manga", "description": ""},
        )
        project_id = res_proj.json()["id"]
        res_c = self.client.post(
            f"/api/projects/{project_id}/chapters",
            json={"chapter_name": "Active Chapter"},
        )
        chapter_id = res_c.json()["id"]

        # Insert active QueueTask (RUNNING)
        db = self.TestingSessionLocal()
        task = QueueTask(chapter_id=chapter_id, status="RUNNING", progress_percent=30)
        db.add(task)
        db.commit()
        db.refresh(task)
        task_id = task.id
        db.close()

        # Delete chapter while task is RUNNING -> 409 Conflict
        res_del_running = self.client.delete(
            f"/api/projects/{project_id}/chapters/{chapter_id}?user_id={self.owner.id}"
        )
        self.assertEqual(res_del_running.status_code, 409)
        self.assertIn("running", res_del_running.json()["detail"].lower())

        # Change task status to QUEUED -> still 409 Conflict
        db = self.TestingSessionLocal()
        t = db.query(QueueTask).filter_by(id=task_id).one()
        t.status = "QUEUED"
        db.commit()
        db.close()

        res_del_queued = self.client.delete(
            f"/api/projects/{project_id}/chapters/{chapter_id}?user_id={self.owner.id}"
        )
        self.assertEqual(res_del_queued.status_code, 409)
        self.assertIn("running", res_del_queued.json()["detail"].lower())

        # Mark task as COMPLETED -> 200 OK
        db = self.TestingSessionLocal()
        t = db.query(QueueTask).filter_by(id=task_id).one()
        t.status = "COMPLETED"
        db.commit()
        db.close()

        res_del_ok = self.client.delete(
            f"/api/projects/{project_id}/chapters/{chapter_id}?user_id={self.owner.id}"
        )
        self.assertEqual(res_del_ok.status_code, 200)

    def test_delete_project_data_conflict_409_when_task_running_or_queued(self) -> None:
        """DELETE /api/projects/{id}/data returns 409 Conflict if task is RUNNING or QUEUED."""
        res_proj = self.client.post(
            f"/api/projects?user_id={self.owner.id}",
            json={"title": "Clear Data Conflict Manga", "description": ""},
        )
        project_id = res_proj.json()["id"]
        res_c = self.client.post(
            f"/api/projects/{project_id}/chapters",
            json={"chapter_name": "Data Chapter"},
        )
        chapter_id = res_c.json()["id"]

        # Insert active QueueTask (RUNNING)
        db = self.TestingSessionLocal()
        task = QueueTask(chapter_id=chapter_id, status="RUNNING", progress_percent=50)
        db.add(task)
        db.commit()
        db.refresh(task)
        task_id = task.id
        db.close()

        # Delete project data while task is RUNNING -> 409 Conflict
        res_del = self.client.delete(
            f"/api/projects/{project_id}/data?user_id={self.owner.id}"
        )
        self.assertEqual(res_del.status_code, 409)
        self.assertIn("running", res_del.json()["detail"].lower())

        # Change task status to FAILED -> 200 OK
        db = self.TestingSessionLocal()
        t = db.query(QueueTask).filter_by(id=task_id).one()
        t.status = "FAILED"
        db.commit()
        db.close()

        res_del_ok = self.client.delete(
            f"/api/projects/{project_id}/data?user_id={self.owner.id}"
        )
        self.assertEqual(res_del_ok.status_code, 200)
        self.assertIn("deleted", res_del_ok.json()["message"].lower())


if __name__ == "__main__":
    unittest.main()
