"""Task 3 & Task 5: review draft/flag endpoints, password reset endpoints, and typesetting alignment."""

import json
import unittest
from unittest.mock import patch

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.api import flag_page, reset_password, save_page_ocr_draft, verify_reset_token
from backend.database import Base
from backend.models import Chapter, ComicPage, Project, TextRegion, User
from backend.schemas import (
    OcrDraftRequest,
    ResetPasswordRequest,
    TypesettingUpdateRequest,
    VerifyResetTokenRequest,
)
from services.review_service import ReviewServiceError
from services.typesetting_service import TypesettingServiceError, save_translation_and_render


class ReviewEndpointTests(unittest.TestCase):
    @patch("backend.api._page_response", return_value={"id": 5, "status": "REVIEW_DRAFT"})
    @patch("backend.api.save_ocr_draft", return_value=1)
    def test_ocr_draft_endpoint_saves_without_translating(self, save, _page) -> None:
        result = save_page_ocr_draft(5, OcrDraftRequest(regions={3: "  hello "}))
        save.assert_called_once_with(5, {3: "  hello "})
        self.assertEqual(result["status"], "REVIEW_DRAFT")

    @patch("backend.api.save_ocr_draft", side_effect=ReviewServiceError("Page not found."))
    def test_ocr_draft_missing_page_is_404(self, _save) -> None:
        with self.assertRaises(HTTPException) as ctx:
            save_page_ocr_draft(9, OcrDraftRequest(regions={}))
        self.assertEqual(ctx.exception.status_code, 404)

    @patch("backend.api._page_response", return_value={"id": 5, "status": "NEEDS_REVIEW"})
    @patch("backend.api.flag_page_for_second_review")
    def test_flag_endpoint(self, flag, _page) -> None:
        result = flag_page(5)
        flag.assert_called_once_with(5)
        self.assertEqual(result["status"], "NEEDS_REVIEW")

    def test_typeset_rejects_unknown_alignment(self) -> None:
        with self.assertRaises(ValidationError):
            TypesettingUpdateRequest(
                region_id=1,
                translated_text="x",
                alignment="justify",  # type: ignore[arg-type]
            )

    @patch("backend.api.SqliteAuthService")
    def test_verify_and_reset_password_endpoints(self, mock_auth_cls) -> None:
        mock_auth_cls.return_value.verify_password_reset_token.return_value = True
        verified = verify_reset_token(VerifyResetTokenRequest(token="tok-123"))
        self.assertEqual(verified, {"valid": True})

        res = reset_password(ResetPasswordRequest(token="tok-123", new_password="newpassword123"))
        mock_auth_cls.return_value.reset_password.assert_called_once_with("tok-123", "newpassword123")
        self.assertEqual(res["message"], "Password reset successfully.")


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
        db = self.factory()
        try:
            region = db.get(TextRegion, self.region_id)
            assert region is not None
            self.assertEqual((region.alignment, region.font_size), ("right", 20))
        finally:
            db.close()

    def test_invalid_alignment_rejected(self) -> None:
        with self.assertRaises(TypesettingServiceError):
            save_translation_and_render(
                self.page_id, self.region_id, "x", None, "justify",
                session_factory=self.factory, renderer=lambda **_: "x",
            )


if __name__ == "__main__":
    unittest.main()
