"""Task 5: review draft/flag endpoints and typesetting alignment."""

import json
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.models import Chapter, ComicPage, Project, TextRegion, User
from fastapi_app import app
from services.review_service import ReviewServiceError
from services.typesetting_service import TypesettingServiceError, save_translation_and_render


class ReviewEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    @patch("backend.api._page_response", return_value={"id": 5, "status": "REVIEW_DRAFT"})
    @patch("backend.api.save_ocr_draft", return_value=1)
    def test_ocr_draft_endpoint_saves_without_translating(self, save, _page) -> None:
        response = self.client.post("/api/pages/5/ocr-draft", json={"regions": {"3": "  hello "}})
        self.assertEqual(response.status_code, 200)
        save.assert_called_once_with(5, {3: "  hello "})
        self.assertEqual(response.json()["status"], "REVIEW_DRAFT")

    @patch("backend.api.save_ocr_draft", side_effect=ReviewServiceError("Page not found."))
    def test_ocr_draft_missing_page_is_404(self, _save) -> None:
        self.assertEqual(
            self.client.post("/api/pages/9/ocr-draft", json={"regions": {}}).status_code, 404
        )

    @patch("backend.api._page_response", return_value={"id": 5, "status": "NEEDS_REVIEW"})
    @patch("backend.api.flag_page_for_second_review")
    def test_flag_endpoint(self, flag, _page) -> None:
        response = self.client.post("/api/pages/5/flag")
        self.assertEqual(response.status_code, 200)
        flag.assert_called_once_with(5)
        self.assertEqual(response.json()["status"], "NEEDS_REVIEW")

    def test_typeset_rejects_unknown_alignment(self) -> None:
        response = self.client.post(
            "/api/pages/1/typeset",
            json={"region_id": 1, "translated_text": "x", "alignment": "justify"},
        )
        self.assertEqual(response.status_code, 422)


class TypesettingAlignmentTests(unittest.TestCase):
    def setUp(self) -> None:
        engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
        Base.metadata.create_all(engine)
        self.factory = sessionmaker(bind=engine)
        db = self.factory()
        user = User(username="u", email="u@example.com", password_hash="x")
        db.add(user)
        db.flush()
        project = Project(owner_id=user.id, title="P")
        db.add(project)
        db.flush()
        chapter = Chapter(project_id=project.id, chapter_number=1)
        db.add(chapter)
        db.flush()
        page = ComicPage(chapter_id=chapter.id, page_number=1, original_path="data/a.png")
        db.add(page)
        db.flush()
        region = TextRegion(page_id=page.id, bbox_json=json.dumps([0, 0, 50, 50]))
        db.add(region)
        db.commit()
        self.page_id, self.region_id = page.id, region.id
        db.close()

    def test_alignment_is_persisted(self) -> None:
        from backend.image_utils import BASE_DIR

        save_translation_and_render(
            self.page_id, self.region_id, "Xin chào", 20, "right",
            session_factory=self.factory,
            renderer=lambda **_: str(BASE_DIR / "data" / "rendered_pages" / "x.png"),
        )
        region = self.factory().query(TextRegion).get(self.region_id)
        self.assertEqual((region.alignment, region.font_size), ("right", 20))

    def test_invalid_alignment_rejected(self) -> None:
        with self.assertRaises(TypesettingServiceError):
            save_translation_and_render(
                self.page_id, self.region_id, "x", None, "justify",
                session_factory=self.factory, renderer=lambda **_: "x",
            )


if __name__ == "__main__":
    unittest.main()
