"""ACL Chapter Studio — Figma Design Implemented (Pixel-Perfect Saas UI)."""

from pathlib import Path
import streamlit as st

from utils.auth_session import require_auth
from backend.image_utils import BASE_DIR
from utils.page_navigation import render_page_navigation

user = require_auth()
render_page_navigation()

project_name = st.query_params.get("project", "Shonen Weekly #112")
raw_manga_dir = BASE_DIR / "data" / "raw_images" / "AisazuNihaIrarenai"
uploads_dir = BASE_DIR / "data" / "raw_images" / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)

if "acl_job" not in st.session_state:
    st.session_state["acl_job"] = {
        "status": "idle",
        "current_file": "",
        "progress_pct": 0,
        "step_name": "Sẵn sàng",
        "error_msg": "",
    }

# Theme CSS chuẩn Figma
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #F8F9FA !important;
        color: #1A1D1F !important;
    }
    
    /* Breadcrumb & Top Bar */
    .top-breadcrumb {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-top: 0.5rem;
        padding-bottom: 1rem;
        font-size: 0.85rem;
        color: #6C7275;
    }
    .top-breadcrumb span {
        font-weight: 600;
        color: #1A1D1F;
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

    /* Header */
    .header-box {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1.5rem;
    }
    .header-title {
        font-size: 2rem;
        font-weight: 800;
        color: #1A1D1F;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .header-sub {
        font-size: 0.875rem;
        color: #6C7275;
        margin-top: 4px;
    }
    .project-badge {
        background: #FFFFFF;
        border: 1px solid #EFEFEF;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #1A1D1F;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }

    /* Staging Table Card */
    .section-card {
        background: #FFFFFF;
        border: 1px solid #EAEAEA;
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        margin-top: 1.25rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.02);
    }
    .card-header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #F4F4F4;
        margin-bottom: 1rem;
    }
    .card-header-title {
        font-weight: 700;
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .staged-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 14px;
        background: #FAFAFA;
        border-radius: 10px;
        margin-bottom: 8px;
        font-size: 0.85rem;
    }
    .status-pill {
        background: #E8F5E9;
        color: #2E7D32;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    /* Bottom Action Bar */
    .launch-bar {
        background: #E8EDFB;
        border: 1px solid #D2DCF9;
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        margin-top: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .launch-title {
        font-size: 1rem;
        font-weight: 700;
        color: #1C274C;
        margin: 0;
    }
    .launch-desc {
        font-size: 0.8rem;
        color: #485A8A;
        margin-top: 4px;
    }
    
    /* Nút bấm chuẩn Figma */
    div.stButton > button:first-child {
        background-color: #1C274C !important;
        color: #FFFFFF !important;
        border-radius: 9999px !important;
        padding: 0.65rem 2rem !important;
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(28, 39, 76, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #25326F !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(28, 39, 76, 0.25) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 1. Top Breadcrumb & Status
st.markdown(
    f"""
    <div class="top-breadcrumb">
        <div>ACL Studio &nbsp;/&nbsp; Projects &nbsp;/&nbsp; {project_name} &nbsp;/&nbsp; <span>Chapter Studio</span></div>
        <div class="node-status"><span class="node-dot"></span> Node Tokyo-01 (GPU idle)</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 2. Main Header
st.markdown(
    f"""
    <div class="header-box">
        <div>
            <h1 class="header-title">Chapter Studio</h1>
            <p class="header-sub">Upload chapter raw scans and configure AI pipeline execution.</p>
        </div>
        <div class="project-badge">📖 Project: {project_name}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 3. Dropzone Kéo Thả Ảnh
uploaded_files = st.file_uploader(
    "Drag & drop comic pages here (Accepts JPG, PNG batches • 100MB max per chapter):",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True,
    help="Kéo thả hoặc chọn trực tiếp file truyện từ máy tính của bạn.",
)

final_targets_to_run = []

# Xử lý lưu file khi người dùng upload
if uploaded_files:
    for up_file in uploaded_files:
        dest_file = uploads_dir / up_file.name
        with open(dest_file, "wb") as f_out:
            f_out.write(up_file.getbuffer())
        final_targets_to_run.append(str(dest_file))

# Nếu chưa upload thì kiểm tra thư mục mẫu
if not final_targets_to_run and raw_manga_dir.exists():
    sample_files = sorted(
        [f for f in raw_manga_dir.iterdir() if f.suffix.lower() in {".jpg", ".png", ".webp"}]
    )
    if sample_files:
        final_targets_to_run = [str(sample_files[0])]  # Mặc định chọn 1 trang để chạy

# 4. Uploaded Pages Card (Staging List)
items_html = ""
display_files = final_targets_to_run[:5]
for fpath in display_files:
    p = Path(fpath)
    size_mb = round(p.stat().st_size / (1024 * 1024), 2)
    items_html += f"""
    <div class="staged-item">
        <div style="display:flex; align-items:center; gap:10px;">
            <span style="font-size:18px;">📄</span>
            <div>
                <strong>{p.name}</strong> <span style="color:#6C7275; font-size:0.75rem;">({size_mb} MB)</span>
            </div>
        </div>
        <span class="status-pill">✓ Ready for detection</span>
    </div>
    """

total_ready = len(final_targets_to_run)
st.markdown(
    f"""
    <div class="section-card">
        <div class="card-header-row">
            <div class="card-header-title">
                <span>📁</span> Uploaded Pages ({total_ready} files ready)
            </div>
            <div style="font-size:0.8rem; color:#D32F2F; cursor:pointer;">Clear all</div>
        </div>
        {items_html}
    </div>
    """,
    unsafe_allow_html=True,
)

# 5. Language Configuration (2 Cards)
col_src, col_tgt = st.columns(2)
with col_src:
    st.markdown(
        """
        <div class="section-card" style="margin-top:1rem;">
            <div style="font-weight:700; font-size:0.9rem; margin-bottom:8px;">🌐 Source Language</div>
            <div style="padding:10px; background:#F8F9FA; border-radius:8px; border:1px solid #EAEAEA; font-size:0.85rem; font-weight:600;">
                Japanese (Raw Manga)
            </div>
            <div style="font-size:0.75rem; color:#6C7275; margin-top:8px;">⚙️ Active Engine: Manga OCR v0.1.1 (GPU Accelerated)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_tgt:
    st.markdown(
        """
        <div class="section-card" style="margin-top:1rem;">
            <div style="font-weight:700; font-size:0.9rem; margin-bottom:8px;">🎯 Target Language</div>
            <div style="padding:10px; background:#F8F9FA; border-radius:8px; border:1px solid #EAEAEA; font-size:0.85rem; font-weight:600;">
                Vietnamese
            </div>
            <div style="font-size:0.75rem; color:#2E7D32; margin-top:8px;">🤖 Translator: Gemini 1.5 Pro + Custom Glossary</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# 6. Bottom Launch Bar & Nút kích hoạt
c_bar_text, c_bar_btn = st.columns([2.5, 1])
with c_bar_text:
    st.markdown(
        f"""
        <div style="padding-top:1.8rem;">
            <h4 class="launch-title">Ready to process {total_ready} pages in Asynchronous Queue</h4>
            <div class="launch-desc">Queue ➔ YOLOv8 Detection ➔ Manga OCR ➔ Waiting Review ➔ Inpainting ➔ Typesetting</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c_bar_btn:
    st.markdown("<div style='padding-top:1.5rem;'>", unsafe_allow_html=True)
    if st.button("Start AI Pipeline ▶", use_container_width=True):
        if not final_targets_to_run:
            st.error("Vui lòng tải lên ít nhất 1 trang truyện!")
        else:
            st.session_state["pending_files"] = final_targets_to_run
            st.session_state["acl_job"] = {
                "status": "pending",
                "current_file": Path(final_targets_to_run[0]).name,
                "progress_pct": 5,
                "step_name": f"Khởi tạo pipeline cho {Path(final_targets_to_run[0]).name}...",
                "error_msg": "",
            }
            st.switch_page("pages/5_Queue_Monitor.py")
    st.markdown("</div>", unsafe_allow_html=True)