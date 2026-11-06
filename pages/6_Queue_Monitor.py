"""ACL - [ACL-09] Queue Monitor & [ACL-09-DONE] Chapter Processing Complete & ZIP Export."""

from __future__ import annotations

import io
import time
import zipfile
import streamlit as st

from backend.database import SessionLocal
from backend.models import Chapter, ComicPage, Project, QueueTask
from utils.auth_session import require_auth

# Guard: Ensure authenticated user
user = require_auth()

# Initialize session state for Queue Monitor demo mode
if "queue_view_mode" not in st.session_state:
    st.session_state["queue_view_mode"] = "active"  # "active" (ACL-09) or "done" (ACL-09-DONE)
if "queue_paused" not in st.session_state:
    st.session_state["queue_paused"] = False

# Scoped CSS for Stitch [ACL-09] and [ACL-09-DONE]
css_styles = (
    '<style>'
    '.block-container { padding-top: 1.8rem !important; padding-bottom: 2rem !important; max-width: 1220px !important; margin: 0 auto !important; }'
    '.acl-header-row { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px; }'
    '.acl-title { font-family: "Sora", sans-serif; font-size: 28px; font-weight: 700; color: #1C1A17; margin: 0 0 4px 0; }'
    '.acl-subtitle { font-family: "Plus Jakarta Sans", sans-serif; font-size: 13.5px; color: #71689F; margin: 0; }'
    
    '/* Progress Card */'
    '.acl-progress-card { background: #FFFFFF; border: 1.5px solid #E4DFD6; border-radius: 14px; padding: 22px 24px; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.03); }'
    '.acl-progress-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 12px; }'
    '.acl-progress-title { font-family: "Sora", sans-serif; font-size: 18px; font-weight: 700; color: #1C1A17; }'
    '.acl-progress-stat { font-family: "JetBrains Mono", monospace; font-size: 13.5px; font-weight: 600; color: #25326F; }'
    
    '/* Custom Progress Bar */'
    '.acl-bar-track { width: 100%; height: 12px; background: #E4DFD6; border-radius: 999px; overflow: hidden; margin-bottom: 18px; }'
    '.acl-bar-fill { height: 100%; background: linear-gradient(90deg, #25326F 0%, #3B4B1F 100%); border-radius: 999px; transition: width 0.3s ease; }'
    
    '/* 7-Stage Pipeline Breadcrumb */'
    '.acl-pipeline-steps { display: flex; align-items: center; justify-content: space-between; gap: 4px; overflow-x: auto; padding-top: 4px; }'
    '.acl-step-item { display: flex; align-items: center; gap: 6px; font-family: "Plus Jakarta Sans", sans-serif; font-size: 12px; font-weight: 600; color: #71689F; white-space: nowrap; }'
    '.acl-step-item.active { color: #25326F; font-weight: 700; background: #E7EAF5; padding: 4px 10px; border-radius: 999px; border: 1px solid rgba(37,50,111,0.25); }'
    '.acl-step-item.done { color: #2F7A4F; font-weight: 600; }'
    '.acl-step-arrow { color: #C4BFB5; font-size: 11px; margin: 0 2px; }'
    
    '/* Success Banner [ACL-09-DONE] */'
    '.acl-done-banner { background: #E6F0E9; border: 2px solid #2F7A4F; border-radius: 16px; padding: 28px 32px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 16px rgba(47,122,79,0.08); }'
    '.acl-done-left { display: flex; align-items: center; gap: 20px; }'
    '.acl-done-icon { width: 52px; height: 52px; border-radius: 50%; background: #2F7A4F; color: #FFFFFF; display: flex; align-items: center; justify-content: center; font-size: 26px; font-weight: 800; flex-shrink: 0; box-shadow: 0 4px 10px rgba(47,122,79,0.25); }'
    '.acl-done-title { font-family: "Sora", sans-serif; font-size: 22px; font-weight: 700; color: #2F7A4F; margin: 0 0 4px 0; }'
    '.acl-done-desc { font-family: "Plus Jakarta Sans", sans-serif; font-size: 14px; color: #1C1A17; margin: 0; }'
    
    '/* Metrics 3-Card Grid */'
    '.acl-metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }'
    '.acl-metric-card { background: #FFFFFF; border: 1.5px solid #E4DFD6; border-radius: 12px; padding: 18px 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.02); }'
    '.acl-metric-label { font-family: "Plus Jakarta Sans", sans-serif; font-size: 12px; font-weight: 600; color: #71689F; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }'
    '.acl-metric-val { font-family: "Sora", sans-serif; font-size: 22px; font-weight: 700; color: #1C1A17; }'
    '.acl-metric-sub { font-family: "JetBrains Mono", monospace; font-size: 11.5px; color: #2F7A4F; margin-top: 4px; }'
    
    '/* Tasks Table */'
    '.acl-tasks-wrap { background: #FFFFFF; border: 1.5px solid #E4DFD6; border-radius: 14px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.03); margin-bottom: 24px; }'
    '.acl-table { width: 100%; border-collapse: collapse; text-align: left; }'
    '.acl-table th { background: #F4F7F2; padding: 12px 18px; font-family: "Plus Jakarta Sans", sans-serif; font-size: 11.5px; font-weight: 700; color: #1C1A17; text-transform: uppercase; letter-spacing: 0.6px; border-bottom: 1.5px solid #E4DFD6; }'
    '.acl-table td { padding: 13px 18px; font-family: "Plus Jakarta Sans", sans-serif; font-size: 13px; color: #1C1A17; border-bottom: 1px solid #F0ECE4; }'
    '.acl-table tr:last-child td { border-bottom: none; }'
    '.acl-table tr:hover td { background: #FAF9F6; }'
    
    '/* Table Status Badges */'
    '.acl-badge { display: inline-flex; align-items: center; gap: 5px; padding: 3px 10px; border-radius: 999px; font-size: 11.5px; font-weight: 600; font-family: "Plus Jakarta Sans", sans-serif; }'
    '.acl-badge-green { background: #E6F0E9; color: #2F7A4F; }'
    '.acl-badge-amber { background: #FBE1C8; color: #8B4E0A; }'
    '.acl-badge-navy { background: #E7EAF5; color: #25326F; }'
    '.acl-badge-grey { background: #F0F0F0; color: #71689F; }'
    '.acl-pulse { width: 6px; height: 6px; border-radius: 50%; background: currentColor; animation: pulse-dot 1.5s infinite; }'
    '@keyframes pulse-dot { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }'
    '</style>'
)
st.markdown(css_styles, unsafe_allow_html=True)

# ==============================================================================
# TOP STATE SWITCHER (Interactive toggle between [ACL-09] and [ACL-09-DONE])
# ==============================================================================
col_ctrl1, col_ctrl2 = st.columns([65, 35])
with col_ctrl1:
    st.markdown(
        '<div class="acl-header-row">'
        '<div>'
        '<h1 class="acl-title">Queue Monitor</h1>'
        '<p class="acl-subtitle">'
        + ("All chapter tasks completed successfully." if st.session_state["queue_view_mode"] == "done" else "Real-time task tracking for Python Asynchronous Queue pipeline.")
        + '</p>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )
with col_ctrl2:
    st.write("")
    col_mode_btn1, col_mode_btn2 = st.columns([1, 1])
    with col_mode_btn1:
        if st.session_state["queue_view_mode"] == "done":
            if st.button("⚡ Switch to Active Queue (ACL-09)", use_container_width=True):
                st.session_state["queue_view_mode"] = "active"
                st.rerun()
        else:
            if st.button("🎉 Switch to Complete (ACL-09-DONE)", type="primary", use_container_width=True):
                st.session_state["queue_view_mode"] = "done"
                st.rerun()
    with col_mode_btn2:
        if st.session_state["queue_view_mode"] == "active":
            pause_label = "▶ Resume Queue" if st.session_state["queue_paused"] else "⏸ Pause Queue"
            if st.button(pause_label, use_container_width=True):
                st.session_state["queue_paused"] = not st.session_state["queue_paused"]
                st.rerun()
        else:
            if st.button("← Workspace", use_container_width=True):
                st.switch_page("pages/1_Workspace.py")

# ==============================================================================
# STATE A: [ACL-09] REAL-TIME PIPELINE PROGRESS TRACKER (68% PROGRESS)
# ==============================================================================
if st.session_state["queue_view_mode"] == "active":
    # 1. Overall Progress Card
    progress_pct = 68
    progress_card_html = (
        '<div class="acl-progress-card">'
        '<div class="acl-progress-header">'
        '<span class="acl-progress-title">Active Chapter: Shonen Weekly #112</span>'
        '<span class="acl-progress-stat">16 / 24 Pages Processed (68%)</span>'
        '</div>'
        '<div class="acl-bar-track">'
        f'<div class="acl-bar-fill" style="width: {progress_pct}%;"></div>'
        '</div>'
        '<div class="acl-pipeline-steps">'
        '<span class="acl-step-item done">✓ Queued</span><span class="acl-step-arrow">➔</span>'
        '<span class="acl-step-item done">✓ Detection</span><span class="acl-step-arrow">➔</span>'
        '<span class="acl-step-item done">✓ OCR</span><span class="acl-step-arrow">➔</span>'
        '<span class="acl-step-item active"><span class="acl-pulse"></span> Waiting Review (Active)</span><span class="acl-step-arrow">➔</span>'
        '<span class="acl-step-item">Inpainting</span><span class="acl-step-arrow">➔</span>'
        '<span class="acl-step-item">Typesetting</span><span class="acl-step-arrow">➔</span>'
        '<span class="acl-step-item">Completed</span>'
        '</div>'
        '</div>'
    )
    st.markdown(progress_card_html, unsafe_allow_html=True)

    # 2. Controls & Auto-Refresh Bar
    col_q_sub1, col_q_sub2 = st.columns([70, 30])
    with col_q_sub1:
        st.markdown(
            '<div style="font-family: \'Sora\', sans-serif; font-size: 17px; font-weight: 700; color: #1C1A17; margin-bottom: 12px;">'
            'Detailed Page Tasks Telemetry'
            '</div>',
            unsafe_allow_html=True,
        )
    with col_q_sub2:
        col_ref_sel, col_rev_link = st.columns([1, 1])
        with col_ref_sel:
            st.selectbox("Refresh Rate", ["Auto-refresh: 5s", "Auto-refresh: 10s", "Manual only"], label_visibility="collapsed")
        with col_rev_link:
            if st.button("Review Page 13 ➔", type="primary", use_container_width=True):
                st.session_state["review_page_idx"] = 13
                st.switch_page("pages/4_Review_Studio.py")

    # 3. Detailed Page Tasks Table (Exact Stitch Specification)
    tasks_table_html = (
        '<div class="acl-tasks-wrap">'
        '<table class="acl-table">'
        '<thead>'
        '<tr>'
        '<th style="width: 12%;">PAGE</th>'
        '<th style="width: 22%;">FILENAME</th>'
        '<th style="width: 22%;">CURRENT STAGE</th>'
        '<th style="width: 24%;">STATUS BADGE</th>'
        '<th style="width: 20%;">UPDATED</th>'
        '</tr>'
        '</thead>'
        '<tbody>'
        '<tr>'
        '<td><strong>Page 001–012</strong></td>'
        '<td style="font-family: \'JetBrains Mono\', monospace; font-size: 12px; color: #71689F;">page_001.png – page_012.png</td>'
        '<td>Batch Completed</td>'
        '<td><span class="acl-badge acl-badge-green">✓ Completed</span></td>'
        '<td style="font-family: \'JetBrains Mono\', monospace; font-size: 12px; color: #71689F;">12:05:30</td>'
        '</tr>'
        '<tr>'
        '<td><strong>Page 013</strong></td>'
        '<td style="font-family: \'JetBrains Mono\', monospace; font-size: 12px; color: #71689F;">page_013.png</td>'
        '<td>Manual OCR Verification</td>'
        '<td><span class="acl-badge acl-badge-navy"><span class="acl-pulse"></span> Waiting Review</span></td>'
        '<td style="font-family: \'JetBrains Mono\', monospace; font-size: 12px; color: #71689F;">12:06:14 (Active)</td>'
        '</tr>'
        '<tr>'
        '<td><strong>Page 014</strong></td>'
        '<td style="font-family: \'JetBrains Mono\', monospace; font-size: 12px; color: #71689F;">page_014.png</td>'
        '<td>LaMa Neural Inpainting</td>'
        '<td><span class="acl-badge acl-badge-amber"><span class="acl-pulse"></span> Inpainting (Processing)</span></td>'
        '<td style="font-family: \'JetBrains Mono\', monospace; font-size: 12px; color: #71689F;">12:06:22</td>'
        '</tr>'
        '<tr>'
        '<td><strong>Page 015</strong></td>'
        '<td style="font-family: \'JetBrains Mono\', monospace; font-size: 12px; color: #71689F;">page_015.png</td>'
        '<td>Manga-OCR Inference</td>'
        '<td><span class="acl-badge acl-badge-amber"><span class="acl-pulse"></span> OCR Extraction</span></td>'
        '<td style="font-family: \'JetBrains Mono\', monospace; font-size: 12px; color: #71689F;">12:06:25</td>'
        '</tr>'
        '<tr>'
        '<td><strong>Page 016</strong></td>'
        '<td style="font-family: \'JetBrains Mono\', monospace; font-size: 12px; color: #71689F;">page_016.png</td>'
        '<td>YOLOv8 Bubble Segmentation</td>'
        '<td><span class="acl-badge acl-badge-amber"><span class="acl-pulse"></span> YOLO Detection</span></td>'
        '<td style="font-family: \'JetBrains Mono\', monospace; font-size: 12px; color: #71689F;">12:06:28</td>'
        '</tr>'
        '<tr>'
        '<td><strong>Page 017–024</strong></td>'
        '<td style="font-family: \'JetBrains Mono\', monospace; font-size: 12px; color: #71689F;">page_017.png – page_024.png</td>'
        '<td>Asynchronous Queue FIFO</td>'
        '<td><span class="acl-badge acl-badge-grey">Queued in FIFO</span></td>'
        '<td style="font-family: \'JetBrains Mono\', monospace; font-size: 12px; color: #71689F;">Waiting worker</td>'
        '</tr>'
        '</tbody>'
        '</table>'
        '</div>'
    )
    st.markdown(tasks_table_html, unsafe_allow_html=True)

# ==============================================================================
# STATE B: [ACL-09-DONE] COMPLETION STATE & 1-CLICK ZIP EXPORT
# ==============================================================================
else:
    # 1. Full-Width Success Announcement Banner
    banner_html = (
        '<div class="acl-done-banner">'
        '<div class="acl-done-left">'
        '<div class="acl-done-icon">✓</div>'
        '<div>'
        '<h2 class="acl-done-title">Chapter Localization 100% Complete!</h2>'
        '<p class="acl-done-desc">All 24 pages have been detected, cleaned, translated, and typeset with zero errors.</p>'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(banner_html, unsafe_allow_html=True)

    # 2. Dynamic In-Memory ZIP Archive Builder
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        manifest_text = (
            "ACL Automated Comic Localization — Export Package Manifest\n"
            "===========================================================\n"
            "Series: Shonen Weekly #112 / Sousou no Frieren Ch. 128\n"
            "Total Localized Pages: 24\n"
            "Source Language: Japanese (JA)\n"
            "Target Language: Vietnamese (VI)\n"
            "Translation Provider: Gemini 1.5 Pro + Series Custom Glossary\n"
            "Typesetting Engine: HarfBuzz SVG Vector Engine\n"
            "Timestamp: 2026-11-06T11:30:00Z\n"
            "Team: Team C1SE.80\n"
        )
        zf.writestr("MANIFEST.txt", manifest_text)
        for p_idx in range(1, 25):
            page_meta = (
                f"ACL Page {p_idx:02d} Metadata\n"
                f"Series: Shonen Weekly #112\n"
                f"Page File: page_{p_idx:02d}_typeset.png\n"
                f"Status: Typeset Approved\n"
            )
            zf.writestr(f"pages/page_{p_idx:02d}_metadata.txt", page_meta)

    zip_buffer.seek(0)

    # 3. Final Summary Metrics Row (3 White Cards)
    metrics_row_html = (
        '<div class="acl-metrics-grid">'
        '<div class="acl-metric-card">'
        '<div class="acl-metric-label">Total Pages Localized</div>'
        '<div class="acl-metric-val">24 Pages</div>'
        '<div class="acl-metric-sub">✓ 100% Verified</div>'
        '</div>'
        '<div class="acl-metric-card">'
        '<div class="acl-metric-label">Average Processing Time</div>'
        '<div class="acl-metric-val">14.2 s / page</div>'
        '<div class="acl-metric-sub">⚡ cuDNN12.1 Accelerated</div>'
        '</div>'
        '<div class="acl-metric-card">'
        '<div class="acl-metric-label">Translation Provider</div>'
        '<div class="acl-metric-val" style="font-size: 18px;">Gemini 1.5 Pro</div>'
        '<div class="acl-metric-sub">+ Custom Series Glossary</div>'
        '</div>'
        '</div>'
    )
    st.markdown(metrics_row_html, unsafe_allow_html=True)

    # 4. Action Row with Download Button
    col_dl1, col_dl2 = st.columns([60, 40])
    with col_dl1:
        st.download_button(
            label="📦 Download Chapter (ZIP) ↓",
            data=zip_buffer,
            file_name="Shonen_Weekly_112_Localized_VI.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True,
        )
    with col_dl2:
        if st.button("Configure Next Chapter Studio ➔", use_container_width=True):
            st.switch_page("pages/3_Chapter_Studio.py")

    st.write("")

    # 5. Completed Pages Table
    completed_table_html = (
        '<div class="acl-tasks-wrap">'
        '<div style="padding: 16px 20px; font-family: \'Sora\', sans-serif; font-size: 15px; font-weight: 700; border-bottom: 1px solid #E4DFD6; background: #FAF9F6;">'
        'Localized Chapter Pages Output List'
        '</div>'
        '<table class="acl-table">'
        '<thead>'
        '<tr>'
        '<th style="width: 15%;">PAGE</th>'
        '<th style="width: 30%;">RENDERED ASSET</th>'
        '<th style="width: 25%;">DIALOGUE BUBBLES</th>'
        '<th style="width: 30%;">STATUS</th>'
        '</tr>'
        '</thead>'
        '<tbody>'
        '<tr>'
        '<td><strong>Pages 001–024</strong></td>'
        '<td style="font-family: \'JetBrains Mono\', monospace; font-size: 12px; color: #25326F;">page_001_clean.png – page_024_clean.png</td>'
        '<td>142 Bubbles Inpainted & Typeset</td>'
        '<td><span class="acl-badge acl-badge-green">✓ Ready for Distribution</span></td>'
        '</tr>'
        '</tbody>'
        '</table>'
        '</div>'
    )
    st.markdown(completed_table_html, unsafe_allow_html=True)
