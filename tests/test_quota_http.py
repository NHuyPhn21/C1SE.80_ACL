import unittest
from unittest.mock import MagicMock, patch
from unittest.mock import patch

from fastapi.testclient import TestClient

from fastapi_app import app
from services.settings_service import SettingsServiceError


class QuotaHttpTests(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    @patch("backend.api.SettingsService")
    @patch("backend.api.SessionLocal")
    def test_queue_start_returns_429_when_quota_exceeded(
        self,
        session_local,
        settings_service,
    ):
        db = session_local.return_value

        # Simulate an existing chapter.
        chapter = db.query.return_value.filter.return_value.first.return_value
        chapter.id = 10
        chapter.project_id = 1

        settings_service.return_value.consume_project_quota.side_effect = (
            SettingsServiceError(
                "Monthly AI processing quota exceeded."
            )
        )

        response = self.client.post(
            "/api/projects/1/queue/start",
            json={"chapter_id": 10},
        )

        self.assertEqual(response.status_code, 429)
        self.assertIn(
            "quota exceeded",
            response.json()["detail"].lower(),
        )

        db.add.assert_not_called()
        db.commit.assert_not_called()

    @patch("backend.api.SettingsService")
    @patch("backend.api.SessionLocal")
    def test_queue_start_returns_404_for_missing_chapter(
        self,
        session_local,
        settings_service,
    ):
        db = session_local.return_value
        db.query.return_value.filter.return_value.first.return_value = None

        response = self.client.post(
            "/api/projects/1/queue/start",
            json={"chapter_id": 999},
        )

        self.assertEqual(response.status_code, 404)
        settings_service.return_value.consume_project_quota.assert_not_called()


    @patch("backend.api.SettingsService")
    @patch("backend.api.SessionLocal")
    def test_translate_returns_429_without_calling_gemini(
        self,
        session_local,
        settings_service,
    ):
        db = session_local.return_value

        page = MagicMock()
        page.id = 10
        page.chapter.project_id = 1

        region = MagicMock()
        region.id = 20
        region.original_text = "Original text"
        region.translated_text = "Old translation"

        query = db.query.return_value
        query.filter.return_value.first.return_value = page
        query.filter.return_value.all.return_value = [region]

        settings_service.return_value.consume_project_quota.side_effect = (
            SettingsServiceError(
                "Monthly AI processing quota exceeded."
            )
        )

        response = self.client.post(
            "/api/translate",
            json={
                "page_id": 10,
                "regions": {"20": "Hello world"},
            },
        )

        self.assertEqual(response.status_code, 429)
        self.assertIn(
            "quota exceeded",
            response.json()["detail"].lower(),
        )

        settings_service.return_value.consume_project_quota.assert_called_once_with(
            project_id=1,
            action="translate",
        )

        db.rollback.assert_called_once()
        db.commit.assert_not_called()

if __name__ == "__main__":
    unittest.main()
