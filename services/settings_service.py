"""Persistence services for project glossary and encrypted provider keys."""

import base64
import hashlib
import os
import secrets
from dataclasses import dataclass
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

from backend.database import SessionLocal, init_db
from backend.models import ApiKeyConfig, CustomGlossary, Project


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
            return [GlossaryEntry(row.id, row.source_term, row.target_term) for row in rows]
        finally:
            db.close()

    def create_glossary(self, project_id: int, source: str, target: str) -> GlossaryEntry:
        source, target = _validate_terms(source, target)
        db = self.session_factory()
        try:
            row = CustomGlossary(
                project_id=project_id, source_term=source, target_term=target
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return GlossaryEntry(row.id, row.source_term, row.target_term)
        except Exception as exc:
            db.rollback()
            raise SettingsServiceError("Unable to add glossary entry.") from exc
        finally:
            db.close()

    def update_glossary(self, entry_id: int, source: str, target: str) -> None:
        source, target = _validate_terms(source, target)
        db = self.session_factory()
        try:
            row = db.query(CustomGlossary).filter(CustomGlossary.id == entry_id).first()
            if row is None:
                raise SettingsServiceError("Glossary entry not found.")
            row.source_term = source
            row.target_term = target
            db.commit()
        except SettingsServiceError:
            db.rollback()
            raise
        finally:
            db.close()

    def delete_glossary(self, entry_id: int) -> None:
        db = self.session_factory()
        try:
            row = db.query(CustomGlossary).filter(CustomGlossary.id == entry_id).first()
            if row is None:
                raise SettingsServiceError("Glossary entry not found.")
            db.delete(row)
            db.commit()
        except SettingsServiceError:
            db.rollback()
            raise
        finally:
            db.close()

    def save_api_key(self, project_id: int, provider: str, api_key: str) -> None:
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

    def load_api_key(self, project_id: int, provider: str) -> str | None:
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
                return self._fernet.decrypt(row.encrypted_key.encode()).decode()
            except InvalidToken as exc:
                raise SettingsServiceError("Stored API key cannot be decrypted.") from exc
        finally:
            db.close()


def project_for_user(session_factory, owner_id: int, title: str) -> Project:
    db = session_factory()
    try:
        project = db.query(Project).filter(Project.title == title).first()
        if project is None:
            project = db.query(Project).filter(Project.owner_id == owner_id).first()
        if project is None:
            project = Project(owner_id=owner_id, title=title)
            db.add(project)
            db.commit()
            db.refresh(project)
        db.expunge(project)
        return project
    finally:
        db.close()


def _validate_terms(source: str, target: str) -> tuple[str, str]:
    clean_source, clean_target = source.strip(), target.strip()
    if not clean_source or not clean_target:
        raise SettingsServiceError("Both source and target terms are required.")
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
