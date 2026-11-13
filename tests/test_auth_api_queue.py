"""Automated tests for authentication, FastAPI endpoints, and queue execution."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.models import Chapter, ComicPage, Project, QueueTask, SystemLog, User
from backend import queue_worker
from fastapi_app import app
from models.auth import AuthResult, AuthTokens, User as AuthUser
from services.auth_service import AuthServiceError


class AuthAndApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_endpoint(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    @patch("backend.api.SqliteAuthService")
    def test_login_endpoint_returns_user_and_tokens(self, service_type: Mock) -> None:
        service_type.return_value.login.return_value = AuthResult(
            user=AuthUser(
                id="12",
                email="editor@example.com",
                full_name="Editor",
                role="USER",
            ),
            tokens=AuthTokens(
                access_token="access-token",
                refresh_token="refresh-token",
                expires_in=3600,
            ),
        )

        response = self.client.post(
            "/api/auth/login",
            json={
                "email": "editor@example.com",
                "password": "password123",
                "remember_me": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"]["email"], "editor@example.com")
        self.assertEqual(response.json()["tokens"]["access_token"], "access-token")
        service_type.return_value.login.assert_called_once_with(
            "editor@example.com", "password123", True
        )

    @patch("backend.api.SqliteAuthService")
    def test_login_endpoint_maps_auth_failure_to_401(self, service_type: Mock) -> None:
        service_type.return_value.login.side_effect = AuthServiceError(
            "Invalid email or password."
        )

        response = self.client.post(
            "/api/auth/login",
            json={"email": "editor@example.com", "password": "wrong"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Invalid email or password.")

    def test_login_endpoint_rejects_incomplete_payload(self) -> None:
        response = self.client.post(
            "/api/auth/login", json={"email": "editor@example.com"}
        )

        self.assertEqual(response.status_code, 422)

    @patch("backend.api.SqliteAuthService")
    def test_register_endpoint_returns_created_account(self, service_type: Mock) -> None:
        service_type.return_value.register.return_value = AuthResult(
            user=AuthUser(
                id="13",
                email="new@example.com",
                full_name="New Editor",
                role="USER",
            ),
            tokens=AuthTokens(access_token="new-access", expires_in=3600),
        )

        response = self.client.post(
            "/api/auth/register",
            json={
                "full_name": "New Editor",
                "email": "new@example.com",
                "password": "password123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"]["full_name"], "New Editor")
        self.assertEqual(response.json()["tokens"]["access_token"], "new-access")
        service_type.return_value.register.assert_called_once_with(
            "New Editor", "new@example.com", "password123"
        )

    @patch("backend.api.send_password_reset_email")
    @patch("backend.api.SqliteAuthService")
    def test_forgot_password_sends_reset_link_for_known_account(
        self, service_type: Mock, send_email: Mock
    ) -> None:
        service_type.return_value.request_password_reset.return_value = "reset-token"

        with patch.dict("os.environ", {"APP_BASE_URL": "http://frontend.test"}):
            response = self.client.post(
                "/api/auth/forgot-password",
                json={"email": "editor@example.com"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn("reset link", response.json()["message"])
        send_email.assert_called_once_with(
            "editor@example.com",
            "http://frontend.test/reset-password?token=reset-token",
        )

    @patch("backend.api.WorkspaceService")
    def test_create_project_endpoint_serializes_service_result(
        self, workspace_type: Mock
    ) -> None:
        workspace = workspace_type.return_value
        workspace.create_project.return_value = 21
        workspace.list_projects.return_value = [
            SimpleNamespace(
                id=21,
                title="Manga Project",
                description="Japanese to Vietnamese",
                total_pages=8,
                completed_pages=2,
                progress_percent=25,
            )
        ]

        response = self.client.post(
            "/api/projects?user_id=5",
            json={
                "title": "Manga Project",
                "description": "Japanese to Vietnamese",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["progress_percent"], 25)
        workspace.create_project.assert_called_once_with(
            5, "Manga Project", "Japanese to Vietnamese"
        )


class QueueApiAndWorkerTests(unittest.TestCase):
    def setUp(self) -> None:
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        self.session_factory = sessionmaker(bind=engine)
        self.client = TestClient(app)

        db = self.session_factory()
        user = User(
            username="Queue Owner",
            email="queue@example.com",
            password_hash="test-only",
        )
        db.add(user)
        db.flush()
        project = Project(owner_id=user.id, title="Queue Project", description="")
        db.add(project)
        db.flush()
        chapter = Chapter(
            project_id=project.id,
            chapter_number=1,
            chapter_name="Chapter 1",
        )
        db.add(chapter)
        db.flush()
        db.add_all(
            [
                ComicPage(
                    chapter_id=chapter.id,
                    page_number=1,
                    original_path="data/page-1.png",
                    status="COMPLETED",
                ),
                ComicPage(
                    chapter_id=chapter.id,
                    page_number=2,
                    original_path="data/page-2.png",
                    status="PENDING",
                ),
            ]
        )
        db.commit()
        self.project_id = project.id
        self.chapter_id = chapter.id
        db.close()

    def test_queue_endpoint_serializes_real_database_state(self) -> None:
        with patch("backend.api.SessionLocal", self.session_factory):
            response = self.client.get(f"/api/projects/{self.project_id}/queue")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["total_pages"], 2)
        self.assertEqual(payload["completed_pages"], 1)
        self.assertEqual([page["status"] for page in payload["pages"]], ["COMPLETED", "PENDING"])

    def test_queue_endpoint_returns_404_for_unknown_project(self) -> None:
        with patch("backend.api.SessionLocal", self.session_factory):
            response = self.client.get("/api/projects/99999/queue")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Project not found")

    def test_start_queue_creates_task_log_and_submits_worker(self) -> None:
        with (
            patch("backend.api.SessionLocal", self.session_factory),
            patch("backend.api.submit_pipeline_task") as submit,
        ):
            response = self.client.post(
                f"/api/projects/{self.project_id}/queue/start",
                json={"chapter_id": self.chapter_id},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["task"]["status"], "QUEUED")
        db = self.session_factory()
        try:
            task = db.query(QueueTask).one()
            log = db.query(SystemLog).one()
            self.assertEqual(log.message, "Pipeline queued.")
            submit.assert_called_once_with(task.id, self.chapter_id)
        finally:
            db.close()

    def test_start_queue_rejects_chapter_from_another_project(self) -> None:
        with patch("backend.api.SessionLocal", self.session_factory):
            response = self.client.post(
                f"/api/projects/{self.project_id + 999}/queue/start",
                json={"chapter_id": self.chapter_id},
            )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Chapter not found")

    def test_worker_marks_empty_chapter_as_failed(self) -> None:
        db = self.session_factory()
        empty_chapter = Chapter(
            project_id=self.project_id,
            chapter_number=2,
            chapter_name="Empty",
        )
        db.add(empty_chapter)
        db.flush()
        task = QueueTask(chapter_id=empty_chapter.id, status="QUEUED", progress_percent=0)
        db.add(task)
        db.commit()
        task_id = task.id
        chapter_id = empty_chapter.id
        db.close()

        with patch.object(queue_worker, "SessionLocal", self.session_factory):
            queue_worker._run_pipeline_task(task_id, chapter_id)

        db = self.session_factory()
        try:
            updated = db.get(QueueTask, task_id)
            self.assertEqual(updated.status, "FAILED")
            self.assertIn("no uploaded pages", updated.logs[-1].message)
        finally:
            db.close()

    def test_worker_completes_successful_pipeline(self) -> None:
        db = self.session_factory()
        task = QueueTask(chapter_id=self.chapter_id, status="QUEUED", progress_percent=0)
        db.add(task)
        db.commit()
        task_id = task.id
        db.close()

        with (
            patch.object(queue_worker, "SessionLocal", self.session_factory),
            patch.object(
                queue_worker,
                "run_full_acl_pipeline",
                return_value={"status": "success"},
            ) as pipeline,
        ):
            queue_worker._run_pipeline_task(task_id, self.chapter_id)

        db = self.session_factory()
        try:
            updated = db.get(QueueTask, task_id)
            self.assertEqual(updated.status, "COMPLETED")
            self.assertEqual(updated.progress_percent, 100)
            self.assertEqual(pipeline.call_count, 2)
            self.assertEqual(updated.logs[-1].message, "Pipeline completed successfully.")
        finally:
            db.close()

    def test_worker_pauses_when_ocr_requires_review(self) -> None:
        db = self.session_factory()
        task = QueueTask(chapter_id=self.chapter_id, status="QUEUED", progress_percent=0)
        db.add(task)
        db.commit()
        task_id = task.id
        db.close()

        with (
            patch.object(queue_worker, "SessionLocal", self.session_factory),
            patch.object(
                queue_worker,
                "run_full_acl_pipeline",
                return_value={"status": "awaiting_review"},
            ),
        ):
            queue_worker._run_pipeline_task(task_id, self.chapter_id)

        db = self.session_factory()
        try:
            updated = db.get(QueueTask, task_id)
            self.assertEqual(updated.status, "AWAITING_REVIEW")
            self.assertEqual(updated.progress_percent, 60)
            self.assertIn("review text", updated.logs[-1].message)
        finally:
            db.close()

    def test_task_updates_clamp_progress_to_valid_range(self) -> None:
        db = self.session_factory()
        task = QueueTask(chapter_id=self.chapter_id, status="QUEUED", progress_percent=0)
        db.add(task)
        db.commit()
        task_id = task.id
        db.close()

        with patch.object(queue_worker, "SessionLocal", self.session_factory):
            queue_worker._write_task_update(task_id, progress=150)

        db = self.session_factory()
        try:
            self.assertEqual(db.get(QueueTask, task_id).progress_percent, 100)
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
