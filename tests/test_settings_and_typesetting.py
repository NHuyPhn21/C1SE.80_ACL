import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.image_utils import BASE_DIR
from backend.models import ApiKeyConfig, Chapter, ComicPage, Project, TextRegion, User
from services.settings_service import SettingsService
from services.typesetting_service import save_translation_and_render


class SettingsAndTypesettingTests(unittest.TestCase):
    def setUp(self) -> None:
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        self.session_factory = sessionmaker(bind=engine)
        db = self.session_factory()
        user = User(
            username="Owner",
            email="owner@example.com",
            password_hash="test",
        )
        db.add(user)
        db.flush()
        project = Project(owner_id=user.id, title="Manga A")
        db.add(project)
        db.flush()
        chapter = Chapter(project_id=project.id, chapter_number=1)
        db.add(chapter)
        db.flush()
        page = ComicPage(
            chapter_id=chapter.id,
            page_number=1,
            original_path="data/raw_images/page.png",
        )
        db.add(page)
        db.flush()
        region = TextRegion(
            page_id=page.id,
            bbox_json="[0, 0, 10, 10]",
            original_text="こんにちは",
            translated_text="Xin chao",
        )
        db.add(region)
        db.commit()
        self.project_id = project.id
        self.page_id = page.id
        self.region_id = region.id
        db.close()

    def test_glossary_crud(self) -> None:
        service = SettingsService(
            self.session_factory,
            encryption_secret="test-secret",
            initialize_database=False,
        )
        entry = service.create_glossary(self.project_id, "先生", "Thay")
        service.update_glossary(entry.id, "先生", "Thay giao")
        self.assertEqual(service.list_glossary(self.project_id)[0].target_term, "Thay giao")
        service.delete_glossary(entry.id)
        self.assertEqual(service.list_glossary(self.project_id), [])

    def test_api_key_is_encrypted_and_can_be_loaded(self) -> None:
        service = SettingsService(
            self.session_factory,
            encryption_secret="test-secret",
            initialize_database=False,
        )
        service.save_api_key(self.project_id, "gemini", "secret-api-key")
        db = self.session_factory()
        stored = db.query(ApiKeyConfig).one()
        self.assertNotEqual(stored.encrypted_key, "secret-api-key")
        db.close()
        self.assertEqual(
            service.load_api_key(self.project_id, "gemini"), "secret-api-key"
        )

    def test_save_translation_calls_renderer_and_updates_page(self) -> None:
        expected_output = BASE_DIR / "data" / "rendered_pages" / "final_page.png"
        calls = []

        def fake_renderer(**kwargs):
            calls.append(kwargs)
            return str(expected_output)

        output = save_translation_and_render(
            self.page_id,
            self.region_id,
            "Xin chao moi",
            session_factory=self.session_factory,
            renderer=fake_renderer,
        )
        self.assertEqual(output, str(expected_output))
        self.assertEqual(calls, [{"page_id": self.page_id, "use_lama_api": False}])

        db = self.session_factory()
        self.assertEqual(db.query(TextRegion).one().translated_text, "Xin chao moi")
        page = db.query(ComicPage).one()
        self.assertEqual(page.rendered_path, "data/rendered_pages/final_page.png")
        self.assertEqual(page.status, "COMPLETED")
        db.close()


if __name__ == "__main__":
    unittest.main()
