import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.models import Chapter, ComicPage, Project, TextRegion, User
from services.review_service import save_ocr_and_retranslate


class ReviewServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        self.session_factory = sessionmaker(bind=engine)
        db = self.session_factory()
        user = User(username="Owner", email="owner@example.com", password_hash="x")
        db.add(user)
        db.flush()
        project = Project(owner_id=user.id, title="Manga")
        db.add(project)
        db.flush()
        chapter = Chapter(project_id=project.id, chapter_number=1)
        db.add(chapter)
        db.flush()
        page = ComicPage(chapter_id=chapter.id, page_number=1, original_path="page.png")
        other_page = ComicPage(chapter_id=chapter.id, page_number=2, original_path="page2.png")
        db.add_all([page, other_page])
        db.flush()
        first = TextRegion(page_id=page.id, bbox_json="[0,0,10,10]", original_text="old", translated_text="cu")
        second = TextRegion(page_id=page.id, bbox_json="[0,0,10,10]", original_text="same", translated_text="giu")
        outside = TextRegion(page_id=other_page.id, bbox_json="[0,0,10,10]", original_text="outside", translated_text="ngoai")
        db.add_all([first, second, outside])
        db.commit()
        self.page_id = page.id
        self.first_id = first.id
        self.second_id = second.id
        self.outside_id = outside.id
        db.close()

    def test_changed_ocr_is_saved_then_translated_and_rendered(self) -> None:
        calls = []

        def translator(**kwargs):
            calls.append(("translate", kwargs))
            db = self.session_factory()
            row = db.query(TextRegion).filter(TextRegion.id == self.first_id).one()
            row.translated_text = "moi"
            db.commit()
            db.close()
            return True

        def renderer(**kwargs):
            calls.append(("render", kwargs))
            return "output.png"

        changed = save_ocr_and_retranslate(
            self.page_id,
            {self.first_id: "new", self.second_id: "same", self.outside_id: "hack"},
            session_factory=self.session_factory,
            translator=translator,
            renderer=renderer,
        )
        self.assertEqual(changed, 1)
        self.assertEqual(calls[0], ("translate", {"page_id": self.page_id}))
        self.assertEqual(
            calls[1], ("render", {"page_id": self.page_id, "use_lama_api": False})
        )
        db = self.session_factory()
        self.assertEqual(db.query(TextRegion).filter_by(id=self.first_id).one().original_text, "new")
        self.assertEqual(db.query(TextRegion).filter_by(id=self.outside_id).one().original_text, "outside")
        db.close()

    def test_no_changes_skip_translation_and_rendering(self) -> None:
        changed = save_ocr_and_retranslate(
            self.page_id,
            {self.second_id: "same"},
            session_factory=self.session_factory,
            translator=lambda **_: self.fail("translator should not run"),
            renderer=lambda **_: self.fail("renderer should not run"),
        )
        self.assertEqual(changed, 0)


if __name__ == "__main__":
    unittest.main()
