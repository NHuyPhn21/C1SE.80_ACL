"""ACL Team Workspace & Role Assignment — Streamlit Native (No iFrame)."""

import streamlit as st

from utils.auth_session import require_auth
from utils.page_navigation import render_page_navigation

user = require_auth()
render_page_navigation()

project_name = st.query_params.get("project", "Shonen Weekly #112")

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
    .metric-box {
        background: #FFFFFF;
        border: 1px solid #EAEAEA;
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .panel-card {
        background: #FFFFFF;
        border: 1px solid #EAEAEA;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.02);
        margin-top: 1.5rem;
    }
    .member-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 14px;
        background: #FAFAFA;
        border-radius: 10px;
        margin-bottom: 8px;
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
    f"""
    <div class="top-breadcrumb">
        <div>ACL Studio &nbsp;/&nbsp; Projects &nbsp;/&nbsp; {project_name} &nbsp;/&nbsp; <strong>Team Workspace</strong></div>
        <div class="node-status"><span class="node-dot"></span> RBAC Sync: Enforced &amp; Active</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown(
    f"""
    <div style="margin-bottom:1.5rem;">
        <h1 style="font-size:2rem; font-weight:800; margin:0; letter-spacing:-0.02em;">Team Workspace &amp; Roles</h1>
        <p style="color:#6C7275; font-size:0.875rem; margin-top:4px;">Assign roles and permissions for project: <strong>{project_name}</strong></p>
    </div>
    """,
    unsafe_allow_html=True,
)

# 3 KPI Cards
k1, k2, k3 = st.columns(3, gap="medium")
with k1:
    st.markdown(
        """
        <div class="metric-box">
            <div style="font-size:0.75rem; color:#6C7275; font-weight:700; text-transform:uppercase;">Total Members</div>
            <div style="font-size:1.75rem; font-weight:800; margin-top:4px;">3 <span style="font-size:0.85rem; color:#2E7D32;">● Active</span></div>
            <div style="font-size:0.75rem; color:#6C7275; margin-top:4px;">Full editorial team assigned</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        """
        <div class="metric-box">
            <div style="font-size:0.75rem; color:#6C7275; font-weight:700; text-transform:uppercase;">Assigned Workload</div>
            <div style="font-size:1.75rem; font-weight:800; margin-top:4px;">24 / 24 <span style="font-size:0.85rem; color:#6C7275;">Pages</span></div>
            <div style="background:#E8EAED; border-radius:9999px; height:6px; margin-top:6px; overflow:hidden;">
                <div style="background:#137333; height:6px; width:100%;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        """
        <div class="metric-box">
            <div style="font-size:0.75rem; color:#6C7275; font-weight:700; text-transform:uppercase;">Access Level</div>
            <div style="font-size:1.25rem; font-weight:800; margin-top:6px;">Private Workspace</div>
            <div style="font-size:0.75rem; color:#2E7D32; margin-top:4px;">✓ SOC2 Type II Ingestion Encrypted</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Quick Invite Bar
with st.container(border=True):
    st.markdown("#### Quick Invite Member")
    c_email, c_role, c_send = st.columns([2, 1.5, 1], gap="medium")
    with c_email:
        new_email = st.text_input("Colleague Email:", placeholder="colleague@studio.com", label_visibility="collapsed")
    with c_role:
        new_role = st.selectbox("Role Assignment:", options=["Translator", "Typesetter", "Project Manager"], label_visibility="collapsed")
    with c_send:
        if st.button("Send Invite ➔", use_container_width=True):
            if new_email and "@" in new_email:
                st.success(f"Đã gửi thư mời tới {new_email} với vai trò {new_role}!")
            else:
                st.error("Vui lòng nhập email hợp lệ!")

# Danh sách thành viên hiện tại
st.markdown(
    """
    <div class="panel-card">
        <h3 style="font-size:1.1rem; font-weight:700; margin:0 0 1rem 0;">Workspace Members</h3>
        <div class="member-row">
            <div>
                <strong>Phan Nhat Huy</strong> <span style="color:#6C7275; font-size:0.8rem;">(nhathuyphan21@gmail.com)</span>
                <div style="font-size:0.75rem; color:#6C7275; margin-top:2px;">Overall Supervision • 24 pages</div>
            </div>
            <div>
                <span style="background:#E8EDFB; color:#1C274C; padding:4px 10px; border-radius:9999px; font-size:0.75rem; font-weight:700;">Project Manager (Owner)</span>
            </div>
        </div>
        <div class="member-row">
            <div>
                <strong>Phan Van Quan</strong> <span style="color:#6C7275; font-size:0.8rem;">(phanvanquann26@gmail.com)</span>
                <div style="font-size:0.75rem; color:#6C7275; margin-top:2px;">Reviewing Pages 1–12 • Manga OCR Transcription</div>
            </div>
            <div>
                <span style="background:#E8F5E9; color:#2E7D32; padding:4px 10px; border-radius:9999px; font-size:0.75rem; font-weight:700;">Translator</span>
            </div>
        </div>
        <div class="member-row">
            <div>
                <strong>Phan Thanh Hoang</strong> <span style="color:#6C7275; font-size:0.8rem;">(phanhoang0705@gmail.com)</span>
                <div style="font-size:0.75rem; color:#6C7275; margin-top:2px;">Typesetting Canvas Pages 13–24 • Collision Avoidance</div>
            </div>
            <div>
                <span style="background:#FFF3E0; color:#E65100; padding:4px 10px; border-radius:9999px; font-size:0.75rem; font-weight:700;">Typesetter</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)