"""Native Streamlit queue monitor for the end-to-end ACL pipeline."""

import io
import zipfile
from pathlib import Path

import streamlit as st

from backend.database import SessionLocal
from backend.image_utils import BASE_DIR
from backend.models import ComicPage
from backend.pipeline import run_full_acl_pipeline
from utils.auth_session import require_auth
from utils.page_navigation import render_page_navigation


user = require_auth()
render_page_navigation()

project_name = st.query_params.get("project", "Shonen Weekly #112")
pending_files = st.session_state.get("pending_files", [])
job = st.session_state.setdefault(
    "acl_job",
    {
        "status": "idle",
        "current_file": "",
        "progress_pct": 0,
        "step_name": "Sẵn sàng",
        "error_msg": "",
    },
)

st.title("Queue Monitor")
st.caption(f"{project_name} · YOLOv8 → MangaOCR → Gemini → Inpainting → Typesetting")

progress_bar = st.progress(
    int(job.get("progress_pct", 0)),
    text=f"{job.get('current_file', '')} · {job.get('step_name', 'Sẵn sàng')}",
)
status_placeholder = st.empty()


def process_pending_files() -> None:
    if not pending_files or job.get("status") == "completed":
        return

    job["status"] = "processing"
    results = []
    total = len(pending_files)

    for index, file_path in enumerate(pending_files, start=1):
        file_name = Path(file_path).name

        def update_progress(step_progress: int, step_name: str) -> None:
            overall = int(((index - 1) * 100 + step_progress) / total)
            job.update(
                current_file=file_name,
                progress_pct=overall,
                step_name=step_name,
            )
            progress_bar.progress(
                overall,
                text=f"{file_name} · {step_name} ({index}/{total})",
            )

        update_progress(0, "Đang khởi tạo")
        result = run_full_acl_pipeline(
            input_image_path=file_path,
            page_number=index,
            force_reprocess=True,
            progress_callback=update_progress,
        )
        results.append(result)
        if result.get("status") != "success":
            job.update(
                status="failed",
                error_msg=(
                    f"{file_name}: "
                    f"{result.get('error_message', 'Lỗi pipeline không xác định')}"
                ),
            )
            status_placeholder.error(job["error_msg"])
            return

    job.update(
        status="completed",
        progress_pct=100,
        step_name="Hoàn tất",
        results=results,
        error_msg="",
    )
    progress_bar.progress(100, text="Đã xử lý xong toàn bộ trang")


if pending_files and job.get("status") in {"queued", "processing"}:
    process_pending_files()
    st.session_state.pop("pending_files", None)
elif job.get("status") == "failed":
    status_placeholder.error(job.get("error_msg", "Pipeline thất bại."))

db = SessionLocal()
try:
    pages = db.query(ComicPage).order_by(ComicPage.id.asc()).all()
    rendered_count = sum(
        1 for page in pages
        if page.status == "COMPLETED" or bool(page.rendered_path)
    )
finally:
    db.close()

total_count = len(pages)
st.subheader("Pipeline Task Execution Matrix")
st.write(
    f"**{rendered_count}/{total_count}** trang đã render · "
    f"**{job.get('status', 'idle').capitalize()}**"
)

for page in pages:
    page_status = page.status or "PENDING"
    col_page, col_status, col_action = st.columns([3, 1.5, 1])
    with col_page:
        st.write(f"Page {page.page_number}: `{Path(page.original_path).name}`")
    with col_status:
        st.caption(page_status)
    with col_action:
        if st.button("Review OCR", key=f"review_{page.id}"):
            st.query_params["page_id"] = str(page.id)
            st.switch_page("pages/2_Review_Studio.py")

rendered_paths = [
    BASE_DIR / page.rendered_path
    for page in pages
    if page.rendered_path and (BASE_DIR / page.rendered_path).exists()
]
if rendered_paths:
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for rendered_path in rendered_paths:
            zip_file.write(rendered_path, arcname=f"pages/{rendered_path.name}")
    st.download_button(
        "📥 Download Full Chapter (ZIP)",
        data=archive.getvalue(),
        file_name=f"{project_name.replace(' ', '_')}_localized.zip",
        mime="application/zip",
        use_container_width=True,
    )
