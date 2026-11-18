import unittest
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from backend.api import start_project_queue, translate_page
from backend.schemas import QueueStartRequest, TranslationRequest
from services.settings_service import SettingsServiceError


class QuotaHttpTests(unittest.TestCase):
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

        with self.assertRaises(HTTPException) as ctx:
            start_project_queue(1, QueueStartRequest(chapter_id=10))

        self.assertEqual(ctx.exception.status_code, 429)
        self.assertIn(
            "quota exceeded",
            str(ctx.exception.detail).lower(),
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

        with self.assertRaises(HTTPException) as ctx:
            start_project_queue(1, QueueStartRequest(chapter_id=999))

        self.assertEqual(ctx.exception.status_code, 404)
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

        with self.assertRaises(HTTPException) as ctx:
            translate_page(TranslationRequest(page_id=10, regions={20: "Hello world"}))

        self.assertEqual(ctx.exception.status_code, 429)
        self.assertIn(
            "quota exceeded",
            str(ctx.exception.detail).lower(),
        )

        settings_service.return_value.consume_project_quota.assert_called_once_with(
            project_id=1,
            action="translate",
        )

        db.rollback.assert_called_once()
        db.commit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
