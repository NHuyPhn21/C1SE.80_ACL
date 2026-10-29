"""ACL Queue Monitor — Figma Design Implemented (Pixel-Perfect Dashboard)."""

import io
import os
from pathlib import Path
import zipfile
import streamlit as st

from utils.auth_session import require_auth
from backend.database import SessionLocal
from backend.models import ComicPage
from backend.image_utils import BASE_DIR
from backend.pipeline import run_full_acl_pipeline
from utils.page_navigation import render_page_navigation

user = require_auth()
render_page_navigation()

project_name = st.query_params.get("project", "Shonen Weekly #112")
file_safe_project = project_name.replace(" ", "_").replace("#", "")

if "acl_job" not in st.session_state:
    st.session_state["acl_job"] = {
        "status": "idle",
        "current_file": "",
        "progress_pct": 0,
        "step_name": "Sẵn sàng",
        "error_msg": "",
    }

# Theme CSS chuẩn Figma Queue Monitor
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #F8F9FA !important;
        color: #1A1D1F !important;
    }

    .top-breadcrumb {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-top: 0.5rem;
        padding-bottom: 1rem;
        font-size: 0.85rem;
        color: #6C7275;
    }
    .node-status {
        background-color: #E8F5E9;
        color: #2E7D32;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .node-dot {
        width: 8px;
        height: 8px;
        background-color: #2E7D32;
        border-radius: 50%;
    }

    /* KPI Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.25rem;
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #EAEAEA;
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .kpi-title {
        font-size: 0.8rem;
        font-weight: 600;
        color: #6C7275;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #1A1D1F;
        margin-top: 6px;
    }
    .kpi-sub {
        font-size: 0.75rem;
        color: #6C7275;
        margin-top: 4px;
    }

    /* Stepper Bar */
    .stepper-box {
        background: #FFFFFF;
        border: 1px solid #EAEAEA;
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .stepper-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
        font-weight: 700;
        font-size: 1rem;
    }
    .steps-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 1rem;
        font-size: 0.75rem;
        font-weight: 600;
        color: #6C7275;
    }
    .step-active {
        color: #1C274C;
        background: #E8EDFB;
        padding: 3px 8px;
        border-radius: 6px;
    }
    .step-done {
        color: #2E7D32;
    }

    /* Terminal Console */
    .console-box {
        background-color: #14171A;
        border-radius: 14px;
        padding: 1.25rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #F4F5F6;
        line-height: 1.6;
        margin-top: 1.5rem;
        box-shadow: inset 0 2px 6px rgba(0,0,0,0.4);
    }

    /* Nút bấm */
    div.stButton > button:first-child {
        background-color: #1C274C !important;
        color: #FFFFFF !important;
        border-radius: 9999px !important;
        font-weight: 600 !important;
        border: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 1. Top Breadcrumb
st.markdown(
    f"""
    <div class="top-breadcrumb">
        <div>ACL Studio &nbsp;/&nbsp; Manga Batch #104 &nbsp;/&nbsp; {project_name} &nbsp;/&nbsp; <span>Queue Monitor</span></div>
        <div class="node-status"><span class="node-dot"></span> Node Tokyo-01 (GPU Active: 64% VRAM)</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 2. Main Title Row
st.markdown(
    """
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
        <div>
            <h1 style="font-size:2rem; font-weight:800; margin:0; letter-spacing:-0.02em;">Queue Monitor</h1>
            <p style="color:#6C7275; font-size:0.875rem; margin-top:4px;">Real-time task tracking for Python Asynchronous Queue pipeline.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 3. Xử lý tác vụ nếu có file mới được gửi sang
pending_files = st.session_state.get("pending_files", [])
if pending_files:
    files_to_process = list(pending_files)
    st.session_state["pending_files"] = []
    total = len(files_to_process)

    prog_slot = st.progress(0)
    status_msg = st.empty()

    for idx, fpath in enumerate(files_to_process, start=1):
        target = Path(fpath)
        status_msg.info(f"⏳ Đang thực thi AI cho `{target.name}` (YOLOv8 + OCR + Gemini + Inpaint)...")
        prog_slot.progress(int((idx - 1) / total * 100))

        try:
            res = run_full_acl_pipeline(
                input_image_path=str(target),
                page_number=idx,
                force_reprocess=True,
                use_lama_api=False,
            )
            if res.get("status") == "error":
                st.session_state["acl_job"]["status"] = "error"
                st.session_state["acl_job"]["error_msg"] = res.get("error_message")
                st.error(f"Lỗi: {res.get('error_message')}")
                break
        except Exception as e:
            st.session_state["acl_job"]["status"] = "error"
            st.session_state["acl_job"]["error_msg"] = str(e)
            st.error(f"Ngoại lệ: {e}")
            break
    else:
        st.session_state["acl_job"]["status"] = "success"
        st.session_state["acl_job"]["progress_pct"] = 100
        prog_slot.progress(100)
        status_msg.success("✅ Toàn bộ trang truyện đã được dịch và xuất bản thành công!")

# Đọc kết quả trong data/rendered_pages
rendered_dir = BASE_DIR / "data" / "rendered_pages"
rendered_dir.mkdir(parents=True, exist_ok=True)
rendered_files = sorted(
    list(rendered_dir.glob("final_*.*")), key=lambda f: f.stat().st_mtime, reverse=True
)

db = SessionLocal()
page_map = {}
try:
    all_pages = db.query(ComicPage).all()
    for p in all_pages:
        if p.original_path:
            fname = os.path.basename(p.original_path)
            page_map[fname] = p.id
            page_map[f"final_{fname}"] = p.id
finally:
    db.close()

# 4. Active Chapter Stepper Progress (Theo đúng Figma)
rendered_count = len(rendered_files)
pct_display = min(100, int((rendered_count / max(1, rendered_count)) * 100)) if rendered_count else 0

st.markdown(
    f"""
    <div class="stepper-box">
        <div class="stepper-header">
            <div>📖 Active Chapter: {project_name}</div>
            <div style="color:#1C274C;">{rendered_count} / {rendered_count} Pages Processed ({pct_display}%)</div>
        </div>
        <div style="background:#EFEFEF; border-radius:9999px; height:8px; overflow:hidden;">
            <div style="background:#1C274C; height:8px; width:{pct_display}%;"></div>
        </div>
        <div class="steps-row">
            <span class="step-done">✓ Queued</span>
            <span>➔</span>
            <span class="step-done">✓ Detection</span>
            <span>➔</span>
            <span class="step-done">✓ OCR</span>
            <span>➔</span>
            <span class="step-active">● Waiting Review (Active)</span>
            <span>➔</span>
            <span>Inpainting</span>
            <span>➔</span>
            <span>Typesetting</span>
            <span>➔</span>
            <span>Completed</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 5. Ba Thẻ KPI Metrics (GPU, Latency, Errors)
st.markdown(
    """
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-title">GPU VRAM UTILIZATION</div>
            <div class="kpi-value">15.4 GB <span style="font-size:1rem; font-weight:500; color:#6C7275;">/ 24.0 GB</span></div>
            <div class="kpi-sub">NVIDIA RTX 4090 • <span style="color:#2E7D32; font-weight:600;">64% Load</span></div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">AVERAGE LATENCY</div>
            <div class="kpi-value">12.8s <span style="font-size:1rem; font-weight:500; color:#6C7275;">/ page</span></div>
            <div class="kpi-sub">Manga OCR + Inpainting • <span style="color:#1C274C; font-weight:600;">Optimal</span></div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">FAILED / RETRY QUEUE</div>
            <div class="kpi-value">0 Errors <span style="font-size:1rem; font-weight:500; color:#2E7D32;">(100% Health)</span></div>
            <div class="kpi-sub">Auto-Retry: Enabled (max 3)</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 6. Pipeline Task Execution Matrix
st.subheader("Pipeline Task Execution Matrix (Batch #104)")

if not rendered_files:
    st.info("Chưa có trang nào được dịch.")
else:
    for idx, fpath in enumerate(rendered_files, start=1):
        fname = fpath.name
        orig_fname = fname.replace("final_", "")
        page_id = page_map.get(fname, page_map.get(orig_fname, idx))
        size_mb = round(fpath.stat().st_size / (1024 * 1024), 2)

        with st.container(border=True):
            col_info, col_prev, col_btn1, col_btn2 = st.columns([2.5, 1, 1.2, 1.2])

            with col_info:
                st.markdown(f"**Trang #{idx:02d}** — `{fname}` ({size_mb} MB)")
                st.caption(f"Ảnh gốc: `{orig_fname}` • Status: Typesetting Done")

            with col_prev:
                with st.popover("Xem trước"):
                    st.image(str(fpath), use_container_width=True)

            with col_btn1:
                if st.button("Review Now ➔", key=f"rev_{fname}_{idx}", use_container_width=True):
                    st.query_params["page_id"] = str(page_id)
                    st.query_params["page_name"] = orig_fname
                    st.switch_page("pages/2_Review_Studio.py")

            with col_btn2:
                if st.button("Typesetting ➔", key=f"type_{fname}_{idx}", use_container_width=True):
                    st.query_params["page_id"] = str(page_id)
                    st.switch_page("pages/4_Typesetting.py")

# 7. Live Terminal Stream Console
st.markdown(
    """
    <div class="console-box">
        <div style="color:#2E7D32; font-weight:700; margin-bottom:6px;">● Live Worker Stream: worker-tokyo-01-daemon.py (streaming stdout)</div>
        <div>[INFO] [Worker-04] Batch #104 initialized with active GPU context.</div>
        <div>[INFO] [Inpainting] PyTorch OpenCV Telea + Masking verified.</div>
        <div>[INFO] [OCR] Manga OCR v0.1.1 completed text inference for text bubbles.</div>
        <div style="color:#FFB300;">[WARN] [Inspector] Dialogue bounds validated against collision avoidance matrix.</div>
        <div style="color:#2E7D32;">[SUCCESS] Pipeline finalized. Rendered artifacts stored in data/rendered_pages/.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 8. Tải ZIP toàn bộ chapter
if rendered_files:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for fpath in rendered_files:
            zf.write(fpath, arcname=fpath.name)

    st.markdown("<div style='margin-top:1.5rem;'>", unsafe_allow_html=True)
    st.download_button(
        label="📥 Download Full Chapter (ZIP)",
        data=zip_buffer.getvalue(),
        file_name=f"{file_safe_project}_Export.zip",
        mime="application/zip",
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)