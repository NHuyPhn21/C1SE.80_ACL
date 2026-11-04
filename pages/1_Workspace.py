"""ACL Project Workspace Dashboard — Streamlit Native (No iFrame)."""

import os
from pathlib import Path
import streamlit as st

from utils.auth_session import require_auth
from backend.database import SessionLocal
from backend.models import ComicPage
from backend.image_utils import BASE_DIR
from utils.page_navigation import render_page_navigation

user = require_auth()
render_page_navigation()

user_initials = (user.full_name[:2] if user.full_name else "PH").upper()
user_name = user.full_name or "Phan Nhat Huy"

# Đếm số trang đã hoàn thành thực tế từ ổ đĩa
rendered_dir = BASE_DIR / "data" / "rendered_pages"
rendered_files = list(rendered_dir.glob("final_*.*")) if rendered_dir.exists() else []
real_done_count = len(rendered_files)
progress_percent = min(100, int((real_done_count / 24) * 100)) if real_done_count > 0 else 0

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
        padding-bottom: 0.75rem;
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
    .project-card {
        background: #FFFFFF;
        border: 1px solid #EAEAEA;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.02);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #EAEAEA;
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.02);
    }
    .badge-status {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    div.stButton > button:first-child {
        border-radius: 9999px !important;
        font-weight: 600 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Top Bar
st.markdown(
    """
    <div class="top-breadcrumb">
        <div><strong>ACL Studio</strong> &nbsp;/&nbsp; Projects</div>
        <div class="node-status"><span class="node-dot"></span> Node Tokyo-01 (GPU idle)</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Header
c_head, c_btn = st.columns([2.5, 1])
with c_head:
    st.markdown(
        """
        <h1 style="font-size:2rem; font-weight:800; margin:0; letter-spacing:-0.02em;">Projects</h1>
        <p style="color:#6C7275; font-size:0.875rem; margin-top:4px;">Manage your ongoing comic localization series and translation pipelines.</p>
        """,
        unsafe_allow_html=True,
    )
with c_btn:
    st.markdown("<div style='padding-top:1rem;'>", unsafe_allow_html=True)
    if st.button("Start Localizing Chapter ➔", key="btn_new_proj", use_container_width=True):
        st.switch_page("pages/2_Chapter_Studio.py")
    st.markdown("</div>", unsafe_allow_html=True)

# 3 Project Cards
col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    st.markdown(
        f"""
        <div class="project-card">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="font-size:1.15rem; font-weight:700; margin:0;">AisazuNihaIrarenai</h3>
                    <span style="font-family:'JetBrains Mono', monospace; font-size:0.8rem; color:#6C7275; border:1px solid #EAEAEA; padding:2px 8px; border-radius:50%;">01</span>
                </div>
                <div style="font-size:0.8rem; color:#6C7275; margin-top:4px;">Raw Manga • Japanese ➔ Vietnamese</div>
                <div style="margin-top:12px;">
                    <span class="badge-status" style="background:#E6F4EA; color:#137333;">
                        <span style="width:6px; height:6px; background:#137333; border-radius:50%;"></span>
                        {real_done_count} Pages Rendered
                    </span>
                </div>
                <div style="margin-top:1.5rem;">
                    <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#6C7275; margin-bottom:4px;">
                        <span>Database Status: Active</span>
                        <strong style="color:#137333;">{real_done_count} Pages Ready</strong>
                    </div>
                    <div style="background:#E8EAED; border-radius:9999px; height:6px; overflow:hidden;">
                        <div style="background:#1C274C; height:6px; width:{progress_percent}%;"></div>
                    </div>
                </div>
            </div>
            <div style="margin-top:2rem; padding-top:1rem; border-top:1px solid #F0F0F0; font-size:0.8rem; color:#6C7275;">
                Series ID: <code>Aisazu-01</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Open Chapter Studio ➔", key="btn_proj_1", use_container_width=True):
        st.query_params["project"] = "AisazuNihaIrarenai"
        st.switch_page("pages/2_Chapter_Studio.py")

with col2:
    st.markdown(
        """
        <div class="project-card">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="font-size:1.15rem; font-weight:700; margin:0;">One Piece — Chapter 1115</h3>
                    <span style="font-family:'JetBrains Mono', monospace; font-size:0.8rem; color:#6C7275; border:1px solid #EAEAEA; padding:2px 8px; border-radius:50%;">02</span>
                </div>
                <div style="font-size:0.8rem; color:#6C7275; margin-top:4px;">19 pages • Japanese ➔ Vietnamese</div>
                <div style="margin-top:12px;">
                    <span class="badge-status" style="background:#EDE7F6; color:#5E35B1;">
                        💧 Inpainting
                    </span>
                </div>
                <div style="margin-top:1.5rem;">
                    <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#6C7275; margin-bottom:4px;">
                        <span>Progress: 14/19 Pages Processed</span>
                        <strong>68%</strong>
                    </div>
                    <div style="background:#E8EAED; border-radius:9999px; height:6px; overflow:hidden;">
                        <div style="background:#1C274C; height:6px; width:68%;"></div>
                    </div>
                </div>
            </div>
            <div style="margin-top:2rem; padding-top:1rem; border-top:1px solid #F0F0F0; font-size:0.8rem; color:#6C7275;">
                Series ID: <code>OP-1115</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("View Queue Monitor ➔", key="btn_proj_2", use_container_width=True):
        st.query_params["project"] = "One Piece — Chapter 1115"
        st.switch_page("pages/5_Queue_Monitor.py")

with col3:
    st.markdown(
        """
        <div class="project-card">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="font-size:1.15rem; font-weight:700; margin:0;">Jujutsu Kaisen — Special</h3>
                    <span style="font-family:'JetBrains Mono', monospace; font-size:0.8rem; color:#6C7275; border:1px solid #EAEAEA; padding:2px 8px; border-radius:50%;">03</span>
                </div>
                <div style="font-size:0.8rem; color:#6C7275; margin-top:4px;">32 pages • English ➔ Vietnamese</div>
                <div style="margin-top:12px;">
                    <span class="badge-status" style="background:#E6F4EA; color:#137333;">
                        ✓ Completed
                    </span>
                </div>
                <div style="margin-top:1.5rem;">
                    <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#6C7275; margin-bottom:4px;">
                        <span>Progress: 32/32 Pages Complete</span>
                        <strong>100%</strong>
                    </div>
                    <div style="background:#E8EAED; border-radius:9999px; height:6px; overflow:hidden;">
                        <div style="background:#137333; height:6px; width:100%;"></div>
                    </div>
                </div>
            </div>
            <div style="margin-top:2rem; padding-top:1rem; border-top:1px solid #F0F0F0; font-size:0.8rem; color:#6C7275;">
                Series ID: <code>JJK-SP</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Open Review Studio ➔", key="btn_proj_3", use_container_width=True):
        st.query_params["project"] = "Jujutsu Kaisen — Special"
        st.switch_page("pages/2_Review_Studio.py")

# 3 Stat Cards
st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)
sc1, sc2, sc3 = st.columns(3, gap="medium")
with sc1:
    st.markdown(
        """
        <div class="metric-card">
            <div style="font-size:0.75rem; color:#6C7275; font-weight:600; text-transform:uppercase;">Active Projects</div>
            <div style="font-size:1.75rem; font-weight:800; margin-top:4px;">3 <span style="font-size:0.85rem; color:#2E7D32;">+1 this week</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with sc2:
    st.markdown(
        """
        <div class="metric-card">
            <div style="font-size:0.75rem; color:#6C7275; font-weight:600; text-transform:uppercase;">In Queue</div>
            <div style="font-size:1.75rem; font-weight:800; margin-top:4px;">19 <span style="font-size:0.85rem; color:#6C7275;">pages pending OCR</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with sc3:
    st.markdown(
        """
        <div class="metric-card">
            <div style="font-size:0.75rem; color:#6C7275; font-weight:600; text-transform:uppercase;">Storage Allocation</div>
            <div style="font-size:1.75rem; font-weight:800; margin-top:4px;">1.2 GB <span style="font-size:0.85rem; color:#6C7275;">/ 10 GB (12%)</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )