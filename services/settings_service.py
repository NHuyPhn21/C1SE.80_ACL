
"""Persistence services for project glossary and encrypted provider keys."""

import base64
import hashlib
import os
import secrets
from dataclasses import dataclass
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import or_

from backend.database import SessionLocal, init_db
from backend.models import (
    ApiKeyConfig,
    Chapter,
    ComicPage,
    CustomGlossary,
    Project,
    ProjectMembership,
    QueueTask,
    SystemLog,
    TextRegion,
)


class SettingsServiceError(RuntimeError):
    pass


@dataclass(frozen=True)
class GlossaryEntry:
    id: int
    source_term: str
    target_term: str


class SettingsService:
    def __init__(
        self,
        session_factory=SessionLocal,
        *,
        encryption_secret: str | None = None,
        initialize_database: bool = True,
    ) -> None:
        if initialize_database:
            init_db()
        self.session_factory = session_factory
        self._fernet = Fernet(_fernet_key(encryption_secret or _local_secret()))

    def list_glossary(self, project_id: int) -> list[GlossaryEntry]:
        db = self.session_factory()
        try:
            rows = (
                db.query(CustomGlossary)
                .filter(CustomGlossary.project_id == project_id)
                .order_by(CustomGlossary.created_at.asc(), CustomGlossary.id.asc())
                .all()
            )
            return [
                GlossaryEntry(row.id, row.source_term, row.target_term)
                for row in rows
            ]
        finally:
            db.close()

    def create_glossary(
        self,
        project_id: int,
        source: str,
        target: str,
    ) -> GlossaryEntry:
        source, target = _validate_terms(source, target)
        db = self.session_factory()
        try:
            row = CustomGlossary(
                project_id=project_id,
                source_term=source,
                target_term=target,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return GlossaryEntry(row.id, row.source_term, row.target_term)
        except Exception as exc:
            db.rollback()
            raise SettingsServiceError(
                "Unable to add glossary entry."
            ) from exc
        finally:
            db.close()

    def update_glossary(
        self,
        entry_id: int,
        source: str,
        target: str,
    ) -> GlossaryEntry:
        source, target = _validate_terms(source, target)
        db = self.session_factory()
        try:
            row = (
                db.query(CustomGlossary)
                .filter(CustomGlossary.id == entry_id)
                .first()
            )
            if row is None:
                raise SettingsServiceError("Glossary entry not found.")

            row.source_term = source
            row.target_term = target
            db.commit()
            db.refresh(row)
            return GlossaryEntry(row.id, row.source_term, row.target_term)
        except SettingsServiceError:
            db.rollback()
            raise
        finally:
            db.close()

    def delete_glossary(self, entry_id: int) -> None:
        db = self.session_factory()
        try:
            row = (
                db.query(CustomGlossary)
                .filter(CustomGlossary.id == entry_id)
                .first()
            )
            if row is None:
                raise SettingsServiceError("Glossary entry not found.")

            db.delete(row)
            db.commit()
        except SettingsServiceError:
            db.rollback()
            raise
        finally:
            db.close()

    def save_api_key(
        self,
        project_id: int,
        provider: str,
        api_key: str,
    ) -> None:
        clean_key = api_key.strip()
        if not clean_key:
            raise SettingsServiceError("API key is required.")

        db = self.session_factory()
        try:
            row = (
                db.query(ApiKeyConfig)
                .filter(
                    ApiKeyConfig.project_id == project_id,
                    ApiKeyConfig.provider == provider,
                )
                .first()
            )

            encrypted = self._fernet.encrypt(clean_key.encode()).decode()

            if row is None:
                row = ApiKeyConfig(
                    project_id=project_id,
                    provider=provider,
                    encrypted_key=encrypted,
                    is_active=True,
                )
                db.add(row)
            else:
                row.encrypted_key = encrypted
                row.is_active = True

            db.commit()
        finally:
            db.close()

    def load_api_key(
        self,
        project_id: int,
        provider: str,
    ) -> str | None:
        db = self.session_factory()
        try:
            row = (
                db.query(ApiKeyConfig)
                .filter(
                    ApiKeyConfig.project_id == project_id,
                    ApiKeyConfig.provider == provider,
                    ApiKeyConfig.is_active.is_(True),
                )
                .first()
            )

            if row is None:
                return None

            try:
                return self._fernet.decrypt(
                    row.encrypted_key.encode()
                ).decode()
            except InvalidToken as exc:
                raise SettingsServiceError(
                    "Stored API key cannot be decrypted."
                ) from exc
        finally:
            db.close()

    def load_api_key_for_pipeline(
        self,
        project_id: int,
        provider: str = "gemini",
    ) -> str | None:
        return self.load_api_key(project_id, provider)

    def clear_logs(self, user_id: int, project_id: int | None = None) -> int:
        db = self.session_factory()
        try:
            member_project_ids = db.query(ProjectMembership.project_id).filter(
                ProjectMembership.user_id == user_id
            )
            project_query = db.query(Project.id).filter(
                or_(
                    Project.owner_id == user_id,
                    Project.id.in_(member_project_ids),
                )
            )
            if project_id is not None:
                project_query = project_query.filter(Project.id == project_id)

            accessible_ids = [row[0] for row in project_query.all()]
            if not accessible_ids:
                return 0

            task_ids = [
                row[0]
                for row in db.query(QueueTask.id)
                .join(Chapter, QueueTask.chapter_id == Chapter.id)
                .filter(Chapter.project_id.in_(accessible_ids))
                .all()
            ]
            if not task_ids:
                return 0

            deleted = (
                db.query(SystemLog)
                .filter(SystemLog.task_id.in_(task_ids))
                .delete(synchronize_session=False)
            )
            db.commit()
            return int(deleted or 0)
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def get_quota_usage(self, user_id: int) -> dict:
        monthly_limit = max(1, int(os.getenv("ACL_MONTHLY_QUOTA", "500")))
        db = self.session_factory()
        try:
            member_project_ids = db.query(ProjectMembership.project_id).filter(
                ProjectMembership.user_id == user_id
            )
            accessible_ids = [
                row[0]
                for row in db.query(Project.id)
                .filter(
                    or_(
                        Project.owner_id == user_id,
                        Project.id.in_(member_project_ids),
                    )
                )
                .all()
            ]
            if not accessible_ids:
                return {
                    "requests_this_month": 0,
                    "monthly_limit": monthly_limit,
                    "usage_percent": 0,
                    "translated_bubbles": 0,
                    "completed_pages": 0,
                    "glossary_terms": 0,
                }

            translated_bubbles = (
                db.query(TextRegion)
                .join(ComicPage, TextRegion.page_id == ComicPage.id)
                .join(Chapter, ComicPage.chapter_id == Chapter.id)
                .filter(
                    Chapter.project_id.in_(accessible_ids),
                    TextRegion.translated_text.isnot(None),
                    TextRegion.translated_text != "",
                )
                .count()
            )
            completed_pages = (
                db.query(ComicPage)
                .join(Chapter, ComicPage.chapter_id == Chapter.id)
                .filter(
                    Chapter.project_id.in_(accessible_ids),
                    ComicPage.status == "COMPLETED",
                )
                .count()
            )
            pipeline_tasks = (
                db.query(QueueTask)
                .join(Chapter, QueueTask.chapter_id == Chapter.id)
                .filter(Chapter.project_id.in_(accessible_ids))
                .count()
            )
            glossary_terms = (
                db.query(CustomGlossary)
                .filter(CustomGlossary.project_id.in_(accessible_ids))
                .count()
            )
            requests_this_month = translated_bubbles + pipeline_tasks
            usage_percent = min(100, round((requests_this_month / monthly_limit) * 100))
            return {
                "requests_this_month": requests_this_month,
                "monthly_limit": monthly_limit,
                "usage_percent": usage_percent,
                "translated_bubbles": translated_bubbles,
                "completed_pages": completed_pages,
                "glossary_terms": glossary_terms,
            }
        finally:
            db.close()


def project_for_user(
    session_factory,
    owner_id: int,
    title: str,
) -> Project:
    db = session_factory()
    try:
        project = (
            db.query(Project)
            .filter(Project.title == title)
            .first()
        )

        if project is None:
            project = (
                db.query(Project)
                .filter(Project.owner_id == owner_id)
                .first()
            )

        if project is None:
            project = Project(
                owner_id=owner_id,
                title=title,
            )
            db.add(project)
            db.commit()
            db.refresh(project)

        db.expunge(project)
        return project
    finally:
        db.close()


def _validate_terms(
    source: str,
    target: str,
) -> tuple[str, str]:
    clean_source = source.strip()
    clean_target = target.strip()

    if not clean_source or not clean_target:
        raise SettingsServiceError(
            "Both source and target terms are required."
        )

    return clean_source, clean_target


def _fernet_key(secret: str) -> bytes:
    digest = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def _local_secret() -> str:
    secret = os.getenv("ACL_CONFIG_SECRET", "").strip()

    if secret:
        return secret

    secret_path = Path(__file__).parents[1] / ".acl_config_secret"

    if secret_path.exists():
        return secret_path.read_text(encoding="utf-8").strip()

    secret = secrets.token_urlsafe(32)
    secret_path.write_text(secret, encoding="utf-8")
    secret_path.chmod(0o600)
    os.environ["ACL_CONFIG_SECRET"] = secret

    return secret
