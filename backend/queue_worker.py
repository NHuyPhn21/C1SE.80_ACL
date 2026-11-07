"""Background execution for chapter localization queue tasks."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from backend.database import SessionLocal
from backend.models import ComicPage, QueueTask, SystemLog
from backend.pipeline import run_full_acl_pipeline


_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="acl-pipeline")


def _write_task_update(task_id: int, *, status: str | None = None,
                       progress: int | None = None, level: str | None = None,
                       message: str | None = None) -> None:
    db = SessionLocal()
    try:
        task = db.query(QueueTask).filter(QueueTask.id == task_id).first()
        if task is None:
            return
        if status is not None:
            task.status = status
        if progress is not None:
            task.progress_percent = max(0, min(100, progress))
        if level is not None and message is not None:
            db.add(SystemLog(task_id=task_id, level=level, message=message))
        task.updated_at = datetime.utcnow()
        db.commit()
    finally:
        db.close()


def submit_pipeline_task(task_id: int, chapter_id: int) -> None:
    """Submit a chapter task and return without blocking the HTTP request."""
    _executor.submit(_run_pipeline_task, task_id, chapter_id)


def _run_pipeline_task(task_id: int, chapter_id: int) -> None:
    db = SessionLocal()
    try:
        pages = (
            db.query(ComicPage)
            .filter(ComicPage.chapter_id == chapter_id)
            .order_by(ComicPage.page_number.asc())
            .all()
        )
        page_inputs = [(page.id, page.original_path, page.page_number) for page in pages]
        project_id = pages[0].chapter.project_id if pages else None
    finally:
        db.close()

    if not page_inputs:
        _write_task_update(
            task_id,
            status="FAILED",
            level="ERROR",
            message="Pipeline stopped: chapter has no uploaded pages.",
        )
        return

    _write_task_update(
        task_id,
        status="RUNNING",
        progress=0,
        level="INFO",
        message=f"Pipeline started for {len(page_inputs)} page(s).",
    )
    failed = False
    awaiting_review = False

    for index, (_, input_path, page_number) in enumerate(page_inputs):
        base_progress = index * 100 // len(page_inputs)

        def report(progress: int, step: str) -> None:
            overall = base_progress + round(progress / len(page_inputs))
            _write_task_update(
                task_id,
                status="RUNNING",
                progress=overall,
                level="INFO",
                message=f"Page {page_number}: {step} ({progress}%).",
            )

        result = run_full_acl_pipeline(
            input_path,
            chapter_id=chapter_id,
            page_number=page_number,
            progress_callback=report,
            project_id=project_id,
        )
        if result.get("status") == "awaiting_review":
            awaiting_review = True
            _write_task_update(
                task_id,
                progress=round((index + 1) * 100 / len(page_inputs)),
                level="INFO",
                message=f"Page {page_number}: OCR complete, awaiting review.",
            )
            continue
        if result.get("status") != "success":
            failed = True
            _write_task_update(
                task_id,
                level="ERROR",
                message=f"Page {page_number} failed: {result.get('error_message', 'Unknown error')}",
            )
            break

        _write_task_update(
            task_id,
            progress=round((index + 1) * 100 / len(page_inputs)),
            level="INFO",
            message=f"Page {page_number} completed.",
        )

    if failed:
        _write_task_update(task_id, status="FAILED")
    elif awaiting_review:
        _write_task_update(
            task_id,
            status="AWAITING_REVIEW",
            progress=60,
            level="INFO",
            message="OCR complete. Please review text in Review Studio, then translate to continue.",
        )
    else:
        _write_task_update(
            task_id,
            status="COMPLETED",
            progress=100,
            level="INFO",
            message="Pipeline completed successfully.",
        )
