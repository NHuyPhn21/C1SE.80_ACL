"""FastAPI API for the ACL localization pipeline."""

import json
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.database import SessionLocal, init_db
from backend.image_utils import BASE_DIR, resolve_project_path
from backend.models import ApiKeyConfig, Chapter, ComicPage, CustomGlossary, Project, QueueTask, SystemLog, TextRegion, User
from backend.schemas import (
    BubbleUpdateRequest,
    BubbleCreateRequest,
    BubbleRestoreRequest,
    ApiKeyRequest,
    ChapterCreateRequest,
    ForgotPasswordRequest,
    GlossaryCreateRequest,
    LoginRequest,
    ProjectCreateRequest,
    QueueStartRequest,
    RegisterRequest,
    TeamInviteRequest,
    TranslationRequest,
    TypesettingUpdateRequest,
)
from services.auth_service import AuthServiceError, SqliteAuthService
from services.password_reset_mailer import (
    PasswordResetDeliveryError,
    send_password_reset_email,
)
from services.workspace_service import WorkspaceService, WorkspaceServiceError
from services.team_service import TeamService, TeamServiceError
from services.queue_service import QueueService, build_rendered_zip
from services.typesetting_service import TypesettingServiceError, save_translation_and_render
from services.settings_service import SettingsService
from backend.queue_worker import submit_pipeline_task


router = APIRouter(prefix="/api")
UPLOADS_DIR = BASE_DIR / "data" / "raw_images" / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
init_db()


def _ensure_chapter(db: Session, chapter_id: int | None) -> Chapter:
    if chapter_id is not None:
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if chapter is None:
            raise HTTPException(status_code=404, detail="Chapter not found")
        return chapter

    user = db.query(User).first()
    if user is None:
        user = User(
            username="api-user",
            email="api@acl.local",
            password_hash="api-managed",
            role="editor",
        )
        db.add(user)
        db.flush()

    project = db.query(Project).filter(Project.owner_id == user.id).first()
    if project is None:
        project = Project(
            owner_id=user.id,
            title="API Uploads",
            description="Uploaded manga pages",
        )
        db.add(project)
        db.flush()

    chapter = Chapter(
        project_id=project.id,
        chapter_number=1,
        chapter_name="API Uploads",
    )
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    return chapter


def _serialize_region(region: TextRegion) -> dict:
    return {
        "id": region.id,
        "bbox": json.loads(region.bbox_json),
        "original_text": region.original_text or "",
        "translated_text": region.translated_text or "",
        "font_family": region.font_family,
        "font_size": region.font_size,
        "alignment": region.alignment,
    }


def _serialize_page(page: ComicPage) -> dict:
    def media_url(path: str | None) -> str | None:
        if not path:
            return None
        relative = path.removeprefix("data/")
        return f"/media/{relative}"

    return {
        "id": page.id,
        "page_number": page.page_number,
        "status": page.status,
        "original_url": media_url(page.original_path),
        "clean_url": media_url(page.clean_path),
        "rendered_url": media_url(page.rendered_path),
        "regions": [_serialize_region(region) for region in page.text_regions],
    }


@router.post("/auth/login")
def login(request: LoginRequest) -> dict:
    try:
        result = SqliteAuthService().login(
            request.email,
            request.password,
            request.remember_me,
        )
        return {
            "user": {
                "id": result.user.id,
                "email": result.user.email,
                "full_name": result.user.full_name,
                "role": result.user.role,
            },
            "tokens": {
                "access_token": result.tokens.access_token,
                "refresh_token": result.tokens.refresh_token,
                "expires_in": result.tokens.expires_in,
            },
        }
    except AuthServiceError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.post("/auth/register")
def register(request: RegisterRequest) -> dict:
    try:
        result = SqliteAuthService().register(
            request.full_name,
            request.email,
            request.password,
        )
        return {
            "user": {
                "id": result.user.id,
                "email": result.user.email,
                "full_name": result.user.full_name,
                "role": result.user.role,
            },
            "tokens": {
                "access_token": result.tokens.access_token,
                "refresh_token": result.tokens.refresh_token,
                "expires_in": result.tokens.expires_in,
            },
        }
    except AuthServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/auth/forgot-password")
def forgot_password(request: ForgotPasswordRequest) -> dict:
    try:
        token = SqliteAuthService().request_password_reset(request.email)
        if token:
            base_url = os.getenv("APP_BASE_URL", "http://localhost:5173").rstrip("/")
            send_password_reset_email(
                request.email.strip().lower(),
                f"{base_url}/reset-password?token={token}",
            )
        return {
            "message": (
                "If an account exists for that email, a reset link will arrive "
                "within a few minutes."
            )
        }
    except (AuthServiceError, PasswordResetDeliveryError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _serialize_project(summary) -> dict:
    return {
        "id": summary.id,
        "title": summary.title,
        "description": summary.description,
        "total_pages": summary.total_pages,
        "completed_pages": summary.completed_pages,
        "progress_percent": summary.progress_percent,
    }


@router.get("/projects")
def list_projects(user_id: int) -> list[dict]:
    return [_serialize_project(project) for project in WorkspaceService().list_projects(user_id)]


@router.post("/projects")
def create_project(user_id: int, request: ProjectCreateRequest) -> dict:
    try:
        project_id = WorkspaceService().create_project(
            user_id,
            request.title,
            request.description,
        )
        project = next(
            project for project in WorkspaceService().list_projects(user_id)
            if project.id == project_id
        )
        return _serialize_project(project)
    except WorkspaceServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/projects/{project_id}/members")
def list_project_members(project_id: int) -> list[dict]:
    try:
        return [
            {
                "user_id": member.user_id,
                "name": member.name,
                "email": member.email,
                "role": member.role,
                "is_owner": member.is_owner,
            }
            for member in TeamService().list_members(project_id)
        ]
    except TeamServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/projects/{project_id}/members")
def invite_project_member(project_id: int, request: TeamInviteRequest) -> dict:
    try:
        member = TeamService().invite_member(project_id, request.email, request.role)
        return {
            "user_id": member.user_id,
            "name": member.name,
            "email": member.email,
            "role": member.role,
            "is_owner": member.is_owner,
        }
    except TeamServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/projects/{project_id}/chapters")
def create_chapter(project_id: int, request: ChapterCreateRequest) -> dict:
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        chapter_number = db.query(Chapter).filter(Chapter.project_id == project_id).count() + 1
        chapter = Chapter(
            project_id=project_id,
            chapter_number=chapter_number,
            chapter_name=request.chapter_name.strip() or f"Chapter {chapter_number}",
        )
        db.add(chapter)
        db.commit()
        db.refresh(chapter)
        return {
            "id": chapter.id,
            "project_id": chapter.project_id,
            "chapter_number": chapter.chapter_number,
            "chapter_name": chapter.chapter_name,
            "pages": [],
        }
    finally:
        db.close()


@router.get("/settings")
def get_settings(user_id: int) -> dict:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "user": {
                "id": user.id,
                "full_name": user.username,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            },
            "providers": {
                "gemini": db.query(ApiKeyConfig).join(Project).filter(
                    Project.owner_id == user_id,
                    ApiKeyConfig.provider == "gemini",
                    ApiKeyConfig.is_active.is_(True),
                ).first() is not None,
                "sendgrid": bool(os.getenv("SENDGRID_API_KEY") and os.getenv("SENDGRID_FROM_EMAIL")),
            },
        }
    finally:
        db.close()


@router.post("/settings/api-key")
def save_settings_api_key(user_id: int, request: ApiKeyRequest) -> dict[str, str]:
    db = SessionLocal()
    try:
        project = db.query(Project).filter(
            Project.id == request.project_id,
            Project.owner_id == user_id,
        ).first()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        SettingsService().save_api_key(request.project_id, request.provider, request.api_key)
        return {"message": "API key saved securely."}
    finally:
        db.close()


@router.post("/settings/api-key/test")
def test_settings_api_key(request: ApiKeyRequest) -> dict[str, str]:
    try:
        from ai_core.translator import _gemini_client

        client = _gemini_client(request.api_key)
        if client is None:
            raise HTTPException(status_code=400, detail="Gemini API key is required.")
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
            contents="Reply with the single word OK.",
        )
        if not (response.text or "").strip():
            raise HTTPException(status_code=502, detail="Gemini returned an empty response.")
        return {"message": "Gemini connection successful."}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Gemini connection failed: {exc}") from exc


@router.post("/settings/api-key/test-saved")
def test_saved_settings_api_key(user_id: int, project_id: int) -> dict[str, str]:
    db = SessionLocal()
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.owner_id == user_id,
        ).first()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        api_key = SettingsService().load_api_key_for_pipeline(project_id)
        if not api_key:
            raise HTTPException(status_code=400, detail="No saved Gemini API key for this project.")
        return test_settings_api_key(ApiKeyRequest(project_id=project_id, api_key=api_key))
    finally:
        db.close()


@router.get("/settings/glossary")
def get_glossary(user_id: int) -> list[dict]:
    db = SessionLocal()
    try:
        rows = (
            db.query(CustomGlossary)
            .join(Project, CustomGlossary.project_id == Project.id)
            .filter(Project.owner_id == user_id)
            .order_by(CustomGlossary.created_at.desc())
            .all()
        )
        return [{"id": row.id, "project_id": row.project_id, "source_term": row.source_term, "target_term": row.target_term} for row in rows]
    finally:
        db.close()


@router.get("/settings/logs")
def get_settings_logs(user_id: int) -> list[dict]:
    db = SessionLocal()
    try:
        rows = (
            db.query(SystemLog)
            .join(QueueTask, SystemLog.task_id == QueueTask.id)
            .join(Chapter, QueueTask.chapter_id == Chapter.id)
            .join(Project, Chapter.project_id == Project.id)
            .filter(Project.owner_id == user_id)
            .order_by(SystemLog.timestamp.desc())
            .limit(200)
            .all()
        )
        return [{"id": row.id, "level": row.level, "message": row.message, "timestamp": row.timestamp.isoformat() if row.timestamp else None} for row in rows]
    finally:
        db.close()


@router.post("/settings/glossary")
def create_glossary(user_id: int, request: GlossaryCreateRequest) -> dict:
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == request.project_id, Project.owner_id == user_id).first()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        if not request.source_term.strip() or not request.target_term.strip():
            raise HTTPException(status_code=400, detail="Both glossary terms are required")
        row = CustomGlossary(project_id=project.id, source_term=request.source_term.strip(), target_term=request.target_term.strip())
        db.add(row)
        db.commit()
        db.refresh(row)
        return {"id": row.id, "project_id": row.project_id, "source_term": row.source_term, "target_term": row.target_term}
    finally:
        db.close()


@router.get("/projects/{project_id}/chapters")
def list_project_chapters(project_id: int) -> list[dict]:
    db = SessionLocal()
    try:
        if db.query(Project).filter(Project.id == project_id).first() is None:
            raise HTTPException(status_code=404, detail="Project not found")
        chapters = (
            db.query(Chapter)
            .filter(Chapter.project_id == project_id)
            .order_by(Chapter.chapter_number.asc())
            .all()
        )
        return [
            {
                "id": chapter.id,
                "project_id": chapter.project_id,
                "chapter_number": chapter.chapter_number,
                "chapter_name": chapter.chapter_name,
                "pages": [],
            }
            for chapter in chapters
        ]
    finally:
        db.close()


@router.delete("/projects/{project_id}/chapters/{chapter_id}")
def delete_project_chapter(project_id: int, chapter_id: int) -> dict[str, int | str]:
    db = SessionLocal()
    try:
        chapter = db.query(Chapter).filter(
            Chapter.id == chapter_id,
            Chapter.project_id == project_id,
        ).first()
        if chapter is None:
            raise HTTPException(status_code=404, detail="Chapter not found")
        active_task = next(
            (
                task for task in chapter.queue_tasks
                if task.status in {"QUEUED", "RUNNING"}
            ),
            None,
        )
        if active_task is not None:
            raise HTTPException(
                status_code=409,
                detail="Cannot delete a chapter while its pipeline is running.",
            )

        page_paths: list[Path] = []
        for page in chapter.pages:
            for path_value in (page.original_path, page.clean_path, page.rendered_path):
                if path_value:
                    resolved = Path(resolve_project_path(path_value)).resolve()
                    data_root = (BASE_DIR / "data").resolve()
                    if resolved.is_file() and data_root in resolved.parents:
                        page_paths.append(resolved)

        db.delete(chapter)
        db.commit()
        for path in set(page_paths):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
        return {"deleted_chapter_id": chapter_id, "message": "Chapter and its pages were deleted."}
    finally:
        db.close()


@router.delete("/projects/{project_id}/data")
def delete_project_data(project_id: int) -> dict[str, int | str]:
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        for chapter in project.chapters:
            if any(task.status in {"QUEUED", "RUNNING"} for task in chapter.queue_tasks):
                raise HTTPException(
                    status_code=409,
                    detail="Cannot clear project data while a pipeline is running.",
                )
        chapter_count = len(project.chapters)
        page_paths: set[Path] = set()
        for chapter in project.chapters:
            for page in chapter.pages:
                for path_value in (page.original_path, page.clean_path, page.rendered_path):
                    if path_value:
                        resolved = Path(resolve_project_path(path_value)).resolve()
                        data_root = (BASE_DIR / "data").resolve()
                        if resolved.is_file() and data_root in resolved.parents:
                            page_paths.add(resolved)
        project.chapters.clear()
        db.commit()
        for path in page_paths:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
        return {"deleted_chapters": chapter_count, "message": "All project chapter data was deleted."}
    finally:
        db.close()


def _serialize_queue(db: Session, project_id: int) -> dict:
    chapters = (
        db.query(Chapter)
        .filter(Chapter.project_id == project_id)
        .order_by(Chapter.id.desc())
        .limit(1)
        .all()
    )
    chapter_ids = [chapter.id for chapter in chapters]
    pages = (
        db.query(ComicPage)
        .filter(ComicPage.chapter_id.in_(chapter_ids))
        .order_by(ComicPage.page_number.asc())
        .all()
        if chapter_ids
        else []
    )
    tasks = (
        db.query(QueueTask)
        .filter(QueueTask.chapter_id.in_(chapter_ids))
        .order_by(QueueTask.created_at.desc())
        .all()
        if chapter_ids
        else []
    )
    task = tasks[0] if tasks else None
    return {
        "project_id": project_id,
        "chapter_id": task.chapter_id if task else (chapter_ids[0] if chapter_ids else None),
        "task": {
            "id": task.id,
            "status": task.status,
            "progress_percent": task.progress_percent,
        } if task else None,
        "total_pages": len(pages),
        "completed_pages": sum(page.status == "COMPLETED" for page in pages),
        "failed_pages": sum(page.status == "FAILED" for page in pages),
        "pages": [
            {
                "id": page.id,
                "page_number": page.page_number,
                "filename": Path(page.original_path).name,
                "status": page.status,
                "rendered": bool(page.rendered_path),
            }
            for page in pages
        ],
        "logs": [
            {"level": log.level, "message": log.message, "timestamp": log.timestamp.isoformat()}
            for log in (task.logs[:30] if task else [])
        ],
    }


@router.get("/projects/{project_id}/queue")
def get_project_queue(project_id: int) -> dict:
    db = SessionLocal()
    try:
        if db.query(Project).filter(Project.id == project_id).first() is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return _serialize_queue(db, project_id)
    finally:
        db.close()


@router.post("/projects/{project_id}/queue/start")
def start_project_queue(project_id: int, request: QueueStartRequest) -> dict:
    db = SessionLocal()
    try:
        chapter = db.query(Chapter).filter(
            Chapter.id == request.chapter_id,
            Chapter.project_id == project_id,
        ).first()
        if chapter is None:
            raise HTTPException(status_code=404, detail="Chapter not found")
        task = QueueTask(chapter_id=chapter.id, status="QUEUED", progress_percent=0)
        db.add(task)
        db.flush()
        db.add(SystemLog(task_id=task.id, level="INFO", message="Pipeline queued."))
        db.commit()
        task_id = task.id
        submit_pipeline_task(task_id, chapter.id)
        return _serialize_queue(db, project_id)
    finally:
        db.close()


@router.get("/projects/{project_id}/queue/export")
def export_project_queue(project_id: int):
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        files = QueueService().rendered_files(project.title)
        if not files:
            raise HTTPException(status_code=404, detail="No rendered pages available")
        archive = build_rendered_zip(files)
        return StreamingResponse(
            iter([archive]),
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{project.title}-rendered.zip"'},
        )
    finally:
        db.close()


@router.post("/upload")
async def upload_page(
    file: UploadFile = File(...),
    chapter_id: int | None = None,
) -> dict:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(status_code=415, detail="Unsupported image format")

    target = UPLOADS_DIR / f"{uuid.uuid4().hex}{suffix}"
    target.write_bytes(await file.read())

    db = SessionLocal()
    try:
        chapter = _ensure_chapter(db, chapter_id)
        page_count = (
            db.query(ComicPage)
            .filter(ComicPage.chapter_id == chapter.id)
            .count()
        )
        relative_path = target.relative_to(BASE_DIR).as_posix()
        page = ComicPage(
            chapter_id=chapter.id,
            page_number=page_count + 1,
            original_path=relative_path,
            status="PROCESSING",
        )
        db.add(page)
        db.commit()
        db.refresh(page)

        from ai_core.text_extractor import extract_manga_text

        extracted = extract_manga_text(str(target))
        page.status = "EXTRACTED"
        for item in extracted:
            db.add(
                TextRegion(
                    page_id=page.id,
                    bbox_json=json.dumps(item["bbox"]),
                    original_text=item["japanese_text"],
                    translated_text="",
                )
            )
        db.commit()
        db.refresh(page)
        return _serialize_page(page)
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        page = locals().get("page")
        if page is not None:
            page.status = "FAILED"
            db.commit()
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        db.close()


@router.post("/translate")
def translate_page(request: TranslationRequest) -> dict:
    db = SessionLocal()
    try:
        page = db.query(ComicPage).filter(ComicPage.id == request.page_id).first()
        if page is None:
            raise HTTPException(status_code=404, detail="Page not found")

        regions = {
            region.id: region
            for region in db.query(TextRegion)
            .filter(TextRegion.page_id == page.id)
            .all()
        }
        source = {}
        for region_id, text in request.regions.items():
            region = regions.get(region_id)
            if region is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Text region {region_id} not found",
                )
            region.original_text = text.strip()
            region.translated_text = ""
            source[str(region_id)] = region.original_text

        if source:
            from ai_core.translator import translate_batch_dict

            api_key = SettingsService().load_api_key_for_pipeline(page.chapter.project_id)
            translated = translate_batch_dict(source, api_key=api_key)
            for region_id, text in translated.items():
                region = regions.get(int(region_id))
                if region is not None:
                    region.translated_text = text.strip()
        db.commit()
        db.refresh(page)
        return _serialize_page(page)
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        db.close()


@router.post("/pages/{page_id}/ocr")
def rerun_page_ocr(page_id: int) -> dict:
    db = SessionLocal()
    try:
        page = db.query(ComicPage).filter(ComicPage.id == page_id).first()
        if page is None:
            raise HTTPException(status_code=404, detail="Page not found")
        image_path = Path(resolve_project_path(page.original_path))
        if not image_path.is_file():
            raise HTTPException(status_code=404, detail="Original page image not found")

        from PIL import Image
        from ai_core.text_extractor import get_ai_models

        _, mocr = get_ai_models()
        image = Image.open(image_path).convert("RGB")
        for region in page.text_regions:
            if region.original_text.strip():
                continue
            x1, y1, x2, y2 = json.loads(region.bbox_json)
            crop = image.crop((x1, y1, x2, y2))
            region.original_text = mocr(crop).strip()
            region.translated_text = ""
        db.commit()
        db.refresh(page)
        return _serialize_page(page)
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        db.close()


@router.get("/chapters/{chapter_id}")
def get_chapter(chapter_id: int) -> dict:
    db = SessionLocal()
    try:
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if chapter is None:
            raise HTTPException(status_code=404, detail="Chapter not found")
        return {
            "id": chapter.id,
            "project_id": chapter.project_id,
            "chapter_number": chapter.chapter_number,
            "chapter_name": chapter.chapter_name,
            "pages": [_serialize_page(page) for page in chapter.pages],
        }
    finally:
        db.close()


@router.put("/bubbles/{region_id}")
@router.put("/update-bubble/{region_id}")
def update_bubble(region_id: int, request: BubbleUpdateRequest) -> dict:
    db = SessionLocal()
    try:
        region = db.query(TextRegion).filter(TextRegion.id == region_id).first()
        if region is None:
            raise HTTPException(status_code=404, detail="Text region not found")
        if request.translated_text is not None:
            region.translated_text = request.translated_text.strip()
        if request.bbox is not None:
            region.bbox_json = json.dumps(request.bbox)
        if request.font_size is not None:
            region.font_size = request.font_size
        db.commit()
        db.refresh(region)
        return _serialize_region(region)
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        db.close()


@router.post("/pages/{page_id}/bubbles")
def create_bubble(page_id: int, request: BubbleCreateRequest) -> dict:
    db = SessionLocal()
    try:
        page = db.query(ComicPage).filter(ComicPage.id == page_id).first()
        if page is None:
            raise HTTPException(status_code=404, detail="Page not found")
        x1, y1, x2, y2 = request.bbox
        if x2 <= x1 or y2 <= y1:
            raise HTTPException(status_code=422, detail="Bubble coordinates are invalid")
        region = TextRegion(
            page_id=page_id,
            bbox_json=json.dumps([x1, y1, x2, y2]),
            original_text=request.original_text.strip(),
            translated_text="",
        )
        db.add(region)
        db.commit()
        db.refresh(region)
        return _serialize_region(region)
    finally:
        db.close()


@router.post("/bubbles/restore")
def restore_bubble(request: BubbleRestoreRequest) -> dict:
    db = SessionLocal()
    try:
        if db.query(TextRegion).filter(TextRegion.id == request.region_id).first():
            raise HTTPException(status_code=409, detail="Bubble ID is already in use")
        page = db.query(ComicPage).filter(ComicPage.id == request.page_id).first()
        if page is None:
            raise HTTPException(status_code=404, detail="Page not found")
        x1, y1, x2, y2 = request.bbox
        if x2 <= x1 or y2 <= y1:
            raise HTTPException(status_code=422, detail="Bubble coordinates are invalid")
        region = TextRegion(
            id=request.region_id,
            page_id=request.page_id,
            bbox_json=json.dumps([x1, y1, x2, y2]),
            original_text=request.original_text.strip(),
            translated_text=request.translated_text.strip(),
            font_size=request.font_size,
        )
        db.add(region)
        db.commit()
        db.refresh(region)
        return _serialize_region(region)
    finally:
        db.close()


@router.delete("/bubbles/{region_id}")
def delete_bubble(region_id: int) -> dict:
    db = SessionLocal()
    try:
        region = db.query(TextRegion).filter(TextRegion.id == region_id).first()
        if region is None:
            raise HTTPException(status_code=404, detail="Text region not found")
        deleted = {
            "id": region.id,
            "page_id": region.page_id,
            "bbox": json.loads(region.bbox_json),
            "original_text": region.original_text or "",
            "translated_text": region.translated_text or "",
            "font_size": region.font_size,
        }
        db.delete(region)
        db.commit()
        return {"deleted_region_id": region_id, "message": "Bubble deleted.", "region": deleted}
    finally:
        db.close()


@router.post("/pages/{page_id}/typeset")
def typeset_page(page_id: int, request: TypesettingUpdateRequest) -> dict:
    try:
        save_translation_and_render(
            page_id=page_id,
            region_id=request.region_id,
            translated_text=request.translated_text,
            font_size=request.font_size,
        )
    except TypesettingServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    db = SessionLocal()
    try:
        page = db.query(ComicPage).filter(ComicPage.id == page_id).first()
        if page is None:
            raise HTTPException(status_code=404, detail="Page not found")
        return _serialize_page(page)
    finally:
        db.close()
