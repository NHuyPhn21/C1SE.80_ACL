"""ACL - [ACL-06] Chapter Studio: Batch Image Upload & AI Pipeline Setup (100% Streamlit Native)."""

import os
from pathlib import Path
import streamlit as st

from backend.database import SessionLocal
from backend.models import Chapter, ComicPage, Project, QueueTask
from utils.auth_session import current_user, require_auth

user = require_auth()

# Retrieve active project
curr_proj_id = st.session_state.get("current_project_id", 1)
with SessionLocal() as db:
    proj = db.query(Project).filter_by(id=curr_proj_id).first()
    proj_title = proj.title if proj else "Shonen Weekly #112"

# Page-Scoped CSS (Strict Stitch [ACL-06] Dropzone & Step-Chain Tokens)
st.markdown("""
<style>
    /* Dashed Upload Dropzone */
    .acl-dropzone-box {
        background-color: #FFFFFF;
        border: 2px dashed rgba(37, 50, 111, 0.4);
        border-radius: 20px;
        padding: 44px 24px;
        text-align: center;
        transition: all 0.2s ease-in-out;
        margin-bottom: 24px;
    }
    .acl-dropzone-box:hover {
        border-color: #25326F;
        background-color: #FAFAF8;
    }
    
    .acl-cloud-icon {
        font-size: 46px;
        color: #25326F;
        margin-bottom: 12px;
    }
    
    /* Staging Table */
    .acl-staged-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 14px;
        border-bottom: 1px solid #F4F7F2;
        font-size: 13.5px;
    }
    .acl-staged-row:last-child {
        border-bottom: none;
    }
    
    /* Pipeline Launch Banner */
    .acl-launch-card {
        background-color: #E7EAF5;
        border: 1.5px solid rgba(37, 50, 111, 0.25);
        border-radius: 16px;
        padding: 24px 28px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 24px;
        box-shadow: 0 4px 16px rgba(37, 50, 111, 0.06);
    }
</style>
""", unsafe_allow_html=True)

# 1. Workspace Header matching Stitch [ACL-06]
col_head, col_series_badge = st.columns([3, 1.2])
with col_head:
    st.markdown("""
    <div style="margin-bottom: 6px;">
        <h1 style="font-size: 32px; font-weight: 700; color: #1C1A17; margin: 0; font-family: 'Sora', sans-serif;">Chapter Studio</h1>
        <p style="font-size: 14px; color: #71689F; margin: 2px 0 0 0; font-family: 'Plus Jakarta Sans', sans-serif;">Upload chapter raw scans and configure AI pipeline execution.</p>
    </div>
    """, unsafe_allow_html=True)

with col_series_badge:
    st.markdown(f"""
    <div style="text-align: right; margin-top: 10px;">
        <span style="display: inline-block; padding: 6px 14px; background: #FFFFFF; border: 1.5px solid #E4DFD6; border-radius: 999px; font-size: 12.5px; font-weight: 700; color: #25326F;">
            📁 Series: {proj_title}
        </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border: none; border-top: 1.5px solid #E4DFD6; margin-top: 6px; margin-bottom: 24px;'>", unsafe_allow_html=True)

# 2. Batch Upload Drag-and-Drop Dropzone
st.markdown("""
<div class="acl-dropzone-box">
    <div class="acl-cloud-icon">☁️</div>
    <h3 style="font-size: 22px; font-weight: 700; color: #1C1A17; margin: 0 0 6px 0; font-family: 'Sora', sans-serif;">Drag &amp; drop comic pages here</h3>
    <p style="font-size: 13.5px; color: #71689F; margin: 0; font-family: 'Plus Jakarta Sans', sans-serif;">Accepts JPG, PNG batches up to 50 pages • 100MB max per chapter</p>
</div>
""", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Upload raw comic scans (Drop here or Browse)",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True,
    label_visibility="collapsed",
)

st.write("")

# 3. Uploaded Batch Files Staging Table (Stitch Spec: Staging List with green checkmarks)
with st.container(border=True):
    col_st_h, col_st_clear = st.columns([3, 1])
    with col_st_h:
        file_count_display = len(uploaded_files) if uploaded_files else 24
        st.markdown(f"<h4 style='font-size: 16px; font-weight: 700; color: #1C1A17; margin: 0;'>Uploaded Pages ({file_count_display} files ready)</h4>", unsafe_allow_html=True)
    with col_st_clear:
        if st.button("Clear all", key="clear_all_staged_btn"):
            st.toast("Staging buffer cleared.")

    st.markdown("<hr style='border: none; border-top: 1px solid #E4DFD6; margin: 10px 0 14px 0;'>", unsafe_allow_html=True)

    if uploaded_files:
        for idx, f in enumerate(uploaded_files[:5], start=1):
            st.markdown(f"""
            <div class="acl-staged-row">
                <div>📄 <b>page_{idx:03d}.png</b> <span style="color: #71689F; margin-left: 8px;">({f.size / (1024*1024):.1f} MB)</span></div>
                <div style="color: #2F7A4F; font-weight: 600; font-size: 12.5px;">✓ Ready for detection</div>
            </div>
            """, unsafe_allow_html=True)
        if len(uploaded_files) > 5:
            st.caption(f"+ {len(uploaded_files) - 5} more pages staged in memory.")
    else:
        # Default canonical staging records from Stitch
        staged_defaults = [
            ("page_001.png", "2.4 MB"),
            ("page_002.png", "2.1 MB"),
            ("page_003.png", "2.8 MB"),
        ]
        for name, sz in staged_defaults:
            st.markdown(f"""
            <div class="acl-staged-row">
                <div>📄 <b>{name}</b> <span style="color: #71689F; margin-left: 8px;">({sz})</span></div>
                <div style="color: #2F7A4F; font-weight: 600; font-size: 12.5px;">✓ Ready for detection</div>
            </div>
            """, unsafe_allow_html=True)
        st.caption("+ 21 more pages staged (24 pages total in chapter bundle).")

st.write("")

# 4. Language Configuration & AI Model Selector Row (Two Cards Side-by-Side)
col_cfg1, col_cfg2 = st.columns(2, gap="large")
with col_cfg1:
    with st.container(border=True):
        st.markdown("<h4 style='font-size: 15px; font-weight: 700; margin: 0 0 10px 0;'>Source Language &amp; Detection</h4>", unsafe_allow_html=True)
        src_lang_sel = st.selectbox("Source Language", ["Japanese (Raw Manga) — Active Manga OCR", "Korean (Webtoon)", "English (Scanlation)"])
        bubble_detector = st.selectbox("Bubble Detector Engine", ["YOLOv8 Manga Bubble Detector v2.4 (High Precision)", "DBNet v2"])

with col_cfg2:
    with st.container(border=True):
        st.markdown("<h4 style='font-size: 15px; font-weight: 700; margin: 0 0 10px 0;'>Target Language &amp; Translation</h4>", unsafe_allow_html=True)
        tgt_lang_sel = st.selectbox("Target Language", ["Vietnamese (Artisanal Pâtisserie Localization)", "English (Standard Global)"])
        trans_model = st.selectbox("Translation Model", ["Gemini 2.5 Flash (Ultra-Fast 210ms)", "Gemini 2.5 Pro", "OpenAI GPT-4o"])

# 5. Pipeline Launch Action Card (Stitch Spec: #E7EAF5 surface, step-chain caption, Start AI Pipeline CTA)
st.markdown("""
<div class="acl-launch-card">
    <div>
        <div style="font-size: 18px; font-weight: 700; color: #1C1A17; margin-bottom: 4px; font-family: 'Sora', sans-serif;">
            Ready to process 24 pages in Asynchronous Queue
        </div>
        <div style="font-size: 13px; color: #25326F; font-weight: 600; font-family: 'Plus Jakarta Sans', sans-serif;">
            Queue ➔ YOLOv8 Detection ➔ Manga OCR ➔ Waiting Review ➔ LaMa Inpainting ➔ Typesetting
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")
col_launch_sp, col_launch_btn = st.columns([2, 1])
with col_launch_btn:
    if st.button("Start AI Pipeline →", type="primary", use_container_width=True):
        upload_dir = Path("assets/scans")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Persist Chapter & Task in SQLite
        with SessionLocal() as db:
            new_ch = Chapter(
                project_id=curr_proj_id,
                chapter_number=128,
                chapter_name=f"Chapter 128 — {proj_title}",
            )
            db.add(new_ch)
            db.commit()
            db.refresh(new_ch)
            
            # Save uploaded scans if any
            if uploaded_files:
                for idx, scan in enumerate(uploaded_files, start=1):
                    file_save_path = upload_dir / f"scan_{new_ch.id}_{idx}_{scan.name}"
                    with open(file_save_path, "wb") as f_out:
                        f_out.write(scan.getbuffer())
                    cp = ComicPage(
                        chapter_id=new_ch.id,
                        page_number=idx,
                        original_path=str(file_save_path),
                        clean_path=str(file_save_path),
                    )
                    db.add(cp)
            
            # Queue Task
            q_task = QueueTask(
                chapter_id=new_ch.id,
                status="PROCESSING",
                progress_percent=10,
            )
            db.add(q_task)
            db.commit()
            
        st.session_state["pipeline_started"] = True
        st.toast("⚡ AI Pipeline initiated! Navigating to Queue Monitor...")
        st.switch_page("pages/6_Queue_Monitor.py")
