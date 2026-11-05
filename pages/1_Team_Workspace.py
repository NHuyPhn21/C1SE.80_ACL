"""Database-backed Team Workspace and project role assignment (100% Streamlit Native, 100% Matching Stitch UI)."""

import base64
from html import escape
import os
from pathlib import Path
import socket
import streamlit as st

from services.team_service import TeamService, TeamServiceError
from services.workspace_service import WorkspaceService
from utils.auth_session import logout, require_auth
from utils.page_navigation import render_page_navigation

user = require_auth()
render_page_navigation("Team Roles")

try:
    current_user_id = int(user.id)
except (ValueError, TypeError):
    st.error("Invalid user account. Please log in again.")
    st.stop()

team_service = TeamService()
workspace_service = WorkspaceService()

# 1. Thống nhất xác định Project xuyên suốt giữa các trang
user_projects = []
try:
    user_projects = workspace_service.list_projects(current_user_id)
except Exception:
    pass

default_proj_title = user_projects[0].title if user_projects else "shinn"
project_title = st.query_params.get("project", st.session_state.get("current_project_title", default_proj_title))

project = team_service.get_or_create_project(project_title, current_user_id)
st.session_state["current_project_id"] = project.id
st.session_state["current_project_title"] = project.title
st.query_params["project_id"] = str(project.id)
st.query_params["project"] = project.title

# 2. Đọc thông số phần cứng thật
hostname = "Local-Node"
try:
    hostname = socket.gethostname()
except Exception:
    pass

user_initials = (user.full_name[:2] if user.full_name else "PH").upper()
user_display_name = user.full_name or "Phan Văn Quân"

# Avatar check
BASE_DIR = Path(__file__).resolve().parents[1]
avatar_data_uri = None
for ext in (".png", ".jpg", ".jpeg"):
    candidate = BASE_DIR / "data" / "avatars" / f"user_{user.id}{ext}"
    if candidate.exists():
        mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
        b64 = base64.b64encode(candidate.read_bytes()).decode("ascii")
        avatar_data_uri = f"data:{mime};base64,{b64}"
        break

# 3. CSS cục bộ chuẩn xác 100% theo Image 2 (Figma / Stitch Design)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background-color: #F8F9FA !important;
        color: #1A1D1F !important;
    }
    
    [data-testid="stMainBlockContainer"],
    .stMainBlockContainer {
        padding: 1.25rem 2.25rem 4rem 2.25rem !important;
        max-width: 1360px !important;
        margin-left: 0 !important;
    }
    [data-testid="stAppViewBlockContainer"] {
        padding-left: 0 !important;
    }

    /* TOP NAVBAR ROW: Đồng bộ 100% Figma, Phẳng, Tinh tế */
    [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"]:first-of-type {
        align-items: center !important;
        min-height: 42px !important;
        margin: 0 !important;
        gap: 0.65rem !important;
    }
    [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"]:first-of-type [data-testid="stColumn"] {
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: stretch !important;
        min-height: 42px !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"]:first-of-type [data-testid="stColumn"] > div[data-testid="stVerticalBlock"] {
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: stretch !important;
        min-height: 42px !important;
        margin: 0 !important;
        gap: 0 !important;
    }
    [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"]:first-of-type [data-testid="stElementContainer"] {
        display: flex !important;
        align-items: center !important;
        min-height: 38px !important;
        height: 38px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Breadcrumb */
    .top-breadcrumb-box {
        display: inline-flex !important;
        align-items: center !important;
        gap: 6px !important;
        height: 38px !important;
        line-height: 38px !important;
        white-space: nowrap !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .top-breadcrumb-bold {
        font-weight: 800 !important;
        font-size: 1.05rem !important;
        color: #1C274C !important;
        letter-spacing: -0.02em !important;
    }
    .top-breadcrumb-slash {
        font-size: 1.05rem !important;
        color: #CBD5E1 !important;
        font-weight: 400 !important;
        margin: 0 1px !important;
        user-select: none !important;
    }
    .top-breadcrumb-current {
        font-size: 1.0rem !important;
        color: #475569 !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em !important;
    }

    /* Search input */
    [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stTextInput"] {
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
    }
    [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stWidgetLabel"] {
        display: none !important;
    }
    [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stTextInputRootElement"] {
        height: 38px !important;
        min-height: 38px !important;
        max-height: 38px !important;
        border-radius: 9999px !important;
        border: 1px solid #E2E8F0 !important;
        background-color: #F8FAFC !important;
        display: flex !important;
        align-items: center !important;
    }
    [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stTextInputRootElement"] input {
        height: 36px !important;
        border: none !important;
        padding: 0 16px !important;
        font-size: 0.88rem !important;
        color: #334155 !important;
        background: transparent !important;
    }

    /* Node badge */
    .node-status-ready {
        height: 38px !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 7px !important;
        background: #EFF6FF !important;
        color: #1E40AF !important;
        border: 1px solid #DBEAFE !important;
        border-radius: 9999px !important;
        padding: 0 14px !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        white-space: nowrap !important;
    }

    /* Topbar buttons */
    [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"]:first-of-type [data-testid="stPopover"] {
        margin: 0 !important;
        padding: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"]:first-of-type [data-testid="stColumn"]:nth-child(4) [data-testid="stPopover"] button,
    [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"]:first-of-type [data-testid="stColumn"]:nth-child(5) [data-testid="stPopover"] button {
        width: 38px !important;
        height: 38px !important;
        border-radius: 50% !important;
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        padding: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
    }
    [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"]:first-of-type [data-testid="stColumn"]:nth-child(4) [data-testid="stPopover"] button svg,
    [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"]:first-of-type [data-testid="stColumn"]:nth-child(5) [data-testid="stPopover"] button svg {
        display: none !important;
    }
    [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"]:first-of-type [data-testid="stColumn"]:nth-child(6) [data-testid="stPopover"] button {
        height: 38px !important;
        background-color: #FFFFFF !important;
        border: 1.5px solid #1C274C !important;
        border-radius: 9999px !important;
        padding: 3px 8px 3px 4px !important;
        gap: 4px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"]:first-of-type [data-testid="stColumn"]:nth-child(6) [data-testid="stPopover"] button p {
        background-color: #1C274C !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 11px !important;
        border-radius: 50% !important;
        width: 28px !important;
        height: 28px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 !important;
    }

    .top-nav-divider {
        height: 1px;
        background-color: #E2E8F0;
        margin-top: 0.75rem;
        margin-bottom: 1.5rem;
        width: 100%;
    }

    /* Sub-Navigation Buttons (Image 2) */
    .subnav-btn div[data-testid="stButton"] > button {
        background-color: #FFFFFF !important;
        color: #1C274C !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 9999px !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        padding: 5px 14px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03) !important;
        transition: all 0.15s ease !important;
    }
    .subnav-btn div[data-testid="stButton"] > button:hover {
        background-color: #F8FAFC !important;
        border-color: #CBD5E1 !important;
        color: #0F172A !important;
    }

    /* RBAC Sync Badge */
    .rbac-sync-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.78rem;
        font-weight: 700;
        color: #475569;
        background: #F1F5F9;
        padding: 5px 12px;
        border-radius: 9999px;
        border: 1px solid #E2E8F0;
    }
    .rbac-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: #16A34A;
    }

    /* Main Page Header */
    .main-page-title {
        font-size: 2.15rem;
        font-weight: 800;
        color: #111827;
        margin: 0;
        letter-spacing: -0.03em;
    }
    .main-page-sub {
        color: #64748B;
        font-size: 0.95rem;
        margin-top: 4px;
        margin-bottom: 1.5rem;
    }

    /* + Invite Member Button (Solid Navy Pill) */
    .invite-btn-wrap div[data-testid="stButton"] > button {
        background-color: #1C274C !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 9999px !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        padding: 0.65rem 1.45rem !important;
        box-shadow: 0 4px 14px rgba(28, 39, 76, 0.22) !important;
        transition: all 0.2s ease !important;
    }
    .invite-btn-wrap div[data-testid="stButton"] > button:hover {
        background-color: #0F172A !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 18px rgba(28, 39, 76, 0.35) !important;
    }

    /* Top 3 Metric Cards (Image 2) */
    .team-metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.25rem 1.4rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.02);
        margin-bottom: 1.5rem;
    }
    .team-metric-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .team-metric-value-row {
        display: flex;
        align-items: baseline;
        gap: 8px;
    }
    .team-metric-num {
        font-size: 1.75rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.02em;
    }
    .team-active-tag {
        font-size: 0.75rem;
        font-weight: 700;
        color: #16A34A;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    .team-metric-sub {
        font-size: 0.78rem;
        color: #64748B;
        margin-top: 2px;
    }
    .team-metric-icon-box {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }

    /* Quick Invite Box (Image 2) */
    .quick-invite-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.02);
        margin-bottom: 1.5rem;
    }
    .quick-invite-title {
        font-size: 0.8rem;
        font-weight: 800;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Quick Invite Send Button */
    .send-invite-btn div[data-testid="stButton"] > button {
        background-color: #1C274C !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 9999px !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        height: 38px !important;
        transition: all 0.15s ease !important;
    }
    .send-invite-btn div[data-testid="stButton"] > button:hover {
        background-color: #0F172A !important;
    }

    /* Members Card Table (Image 2) */
    .members-card-wrap {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.35rem 1.5rem;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.02);
        margin-bottom: 1.5rem;
    }
    .members-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 1rem;
        border-bottom: 1px solid #F1F5F9;
        margin-bottom: 1rem;
    }
    .members-heading {
        font-size: 1.15rem;
        font-weight: 800;
        color: #0F172A;
    }
    .members-badge-count {
        background: #F1F5F9;
        color: #475569;
        font-size: 0.8rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 9999px;
        margin-left: 6px;
    }
    .table-th-row {
        display: flex;
        font-size: 0.72rem;
        font-weight: 800;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #F1F5F9;
        margin-bottom: 0.5rem;
    }
    .member-table-row {
        display: flex;
        align-items: center;
        padding: 0.85rem 0;
        border-bottom: 1px solid #F8FAFC;
    }
    .avatar-member-circle {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: #1C274C;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 13px;
        flex-shrink: 0;
    }
    .member-role-pill {
        background: #F5F3FF;
        color: #7C3AED;
        border: 1px solid #DDD6FE;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 3px 12px;
        border-radius: 9999px;
        display: inline-block;
    }
    .action-owner-pill {
        background: #F1F5F9;
        color: #64748B;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 9999px;
        display: inline-block;
    }

    /* Role Permissions Guide (Image 2 Bottom Box) */
    .guide-card-wrap {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.35rem 1.5rem;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.02);
    }
    .guide-header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.25rem;
    }
    .guide-title {
        font-size: 0.95rem;
        font-weight: 800;
        color: #1E293B;
    }
    .guide-col-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.15rem;
        height: 100%;
    }
    .guide-col-title {
        font-size: 0.85rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .guide-col-desc {
        font-size: 0.78rem;
        color: #64748B;
        line-height: 1.5;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 4. TOP NAVBAR ROW (100% Đồng bộ Figma Image 2)
nav_col_left, nav_col_search, nav_col_node, nav_col_bell, nav_col_gear, nav_col_user = st.columns(
    [2.3, 3.1, 2.3, 0.42, 0.42, 0.85], vertical_alignment="center"
)

with nav_col_left:
    st.markdown(
        f"""
        <div class="top-breadcrumb-box">
            <span class="top-breadcrumb-bold">ACL Studio</span>
            <span class="top-breadcrumb-slash">/</span>
            <span class="top-breadcrumb-bold">Projects</span>
            <span class="top-breadcrumb-slash">/</span>
            <span class="top-breadcrumb-bold">{escape(project.title)}</span>
            <span class="top-breadcrumb-slash">/</span>
            <span class="top-breadcrumb-current">Team Workspace</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with nav_col_search:
    search_team_kw = st.text_input(
        "Filter workspace",
        placeholder="🔍 Filter workspace...",
        label_visibility="collapsed",
        key="top_navbar_team_search",
    )

with nav_col_node:
    st.markdown(
        f"""
        <div class="node-status-ready">
            <span>⚙</span>
            <span>Node: {hostname} (Ready)</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with nav_col_bell:
    with st.popover("🔔", use_container_width=True):
        st.markdown("**Notifications**")
        st.caption("No new unread system notifications.")

with nav_col_gear:
    with st.popover("🎛️", use_container_width=True):
        st.markdown("**Workspace Settings**")
        st.caption("RBAC Enforcement: Active")
        st.caption("Encryption: SOC2 Ingestion Standard")

with nav_col_user:
    with st.popover(label=f"{user_initials}", use_container_width=True):
        if avatar_data_uri:
            avatar_html = f'<img src="{avatar_data_uri}" style="width:44px; height:44px; border-radius:50%; object-fit:cover; flex-shrink:0; border:1px solid #E2E8F0;" />'
        else:
            avatar_html = f'<div style="width:44px; height:44px; border-radius:50%; background:#1C274C; color:#FFFFFF; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:16px; flex-shrink:0;">{user_initials}</div>'

        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:12px; padding:4px 0 10px 0;">
                {avatar_html}
                <div>
                    <div style="font-weight:700; font-size:15px; color:#111827; line-height:1.2;">{escape(user_display_name)}</div>
                    <div style="font-size:12px; color:#64748B; margin:2px 0 4px 0;">{escape(user.email or '')}</div>
                    <div>
                        <span style="background:#EFF6FF; color:#2563EB; font-size:11px; font-weight:700; padding:2px 8px; border-radius:9999px; display:inline-flex; align-items:center; gap:4px;">
                            <span style="width:5px; height:5px; border-radius:50%; background:#2563EB;"></span>
                            Lead Editor
                        </span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/1_Workspace.py", label="Projects", icon="📁")
        st.page_link("pages/3_Settings.py", label="Personal Settings", icon="👤")
        st.divider()
        if st.button("🚪 Sign out", key="team_popover_signout_btn", use_container_width=True):
            logout()
            st.switch_page("pages/0_Login.py")

st.markdown('<div class="top-nav-divider"></div>', unsafe_allow_html=True)

# 5. SUB-NAVIGATION ROW (Image 2: Back to Projects, Open Chapter Studio, RBAC Sync)
sub_c1, sub_c2, sub_c_space, sub_c_sync = st.columns([1.6, 1.8, 3.5, 2.3], vertical_alignment="center")
with sub_c1:
    st.markdown('<div class="subnav-btn">', unsafe_allow_html=True)
    if st.button("← Back to Projects", key="btn_subnav_back_proj", use_container_width=True):
        st.switch_page("pages/1_Workspace.py")
    st.markdown("</div>", unsafe_allow_html=True)

with sub_c2:
    st.markdown('<div class="subnav-btn">', unsafe_allow_html=True)
    if st.button("Open Chapter Studio →", key="btn_subnav_open_studio", use_container_width=True):
        st.switch_page("pages/2_Chapter_Studio.py")
    st.markdown("</div>", unsafe_allow_html=True)

with sub_c_sync:
    st.markdown(
        """
        <div style="display:flex; justify-content:flex-end;">
            <div class="rbac-sync-badge">
                <span class="rbac-dot"></span>
                <span>RBAC Sync: Enforced & Active</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# 6. Modal Dialog Mời Thành Viên (Trigger từ + Invite Member)
@st.dialog("Invite Team Member")
def invite_member_dialog() -> None:
    with st.form("invite_member_modal_form"):
        email = st.text_input("Colleague Email *", placeholder="colleague@studio.com")
        role = st.selectbox("Assigned Role", ["Translator", "Typesetter", "Project Manager"])
        submitted = st.form_submit_button("Send Invitation", use_container_width=True)
    if submitted:
        if not email.strip():
            st.error("Please enter a valid colleague email address.")
            return
        try:
            invited = team_service.invite_member(project.id, email.strip(), role)
            st.success(f"Added {invited.name} as {invited.role} successfully!")
            st.rerun()
        except TeamServiceError as exc:
            st.error(f"Invite error: {exc}")

# 7. PAGE HEADING & INVITE BUTTON (Image 2)
head_col, invite_btn_col = st.columns([3.8, 1.3], vertical_alignment="center")
with head_col:
    st.markdown('<h1 class="main-page-title">Team Workspace & Roles</h1>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="main-page-sub">Assign roles and permissions for project: <strong>{escape(project.title)}</strong></p>',
        unsafe_allow_html=True,
    )
with invite_btn_col:
    st.markdown('<div class="invite-btn-wrap">', unsafe_allow_html=True)
    if st.button("👥 + Invite Member", key="btn_open_invite_dialog", use_container_width=True):
        invite_member_dialog()
    st.markdown("</div>", unsafe_allow_html=True)

# 8. TOP 3 METRIC CARDS (Image 2)
members = team_service.list_members(project.id)

card_c1, card_c2, card_c3 = st.columns(3, gap="large")
with card_c1:
    st.markdown(
        f"""
        <div class="team-metric-card">
            <div>
                <div class="team-metric-label">TOTAL MEMBERS</div>
                <div class="team-metric-value-row">
                    <span class="team-metric-num">{len(members)}</span>
                    <span class="team-active-tag">● Active</span>
                </div>
                <div class="team-metric-sub">Full editorial team assigned</div>
            </div>
            <div class="team-metric-icon-box">👥</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with card_c2:
    st.markdown(
        """
        <div class="team-metric-card">
            <div>
                <div class="team-metric-label">ASSIGNED WORKLOAD</div>
                <div class="team-metric-value-row">
                    <span class="team-metric-num">0 / 0</span>
                    <span style="font-size:0.85rem; color:#64748B; font-weight:600;">Pages</span>
                </div>
                <div class="team-metric-sub">No pending tasks overloaded</div>
            </div>
            <div class="team-metric-icon-box">☑️</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with card_c3:
    st.markdown(
        """
        <div class="team-metric-card">
            <div>
                <div class="team-metric-label">ACCESS LEVEL</div>
                <div class="team-metric-num" style="font-size:1.25rem; font-weight:800; color:#0F172A; margin:4px 0;">Private Workspace</div>
                <div>
                    <span style="background:#F1F5F9; color:#475569; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:6px; border:1px solid #E2E8F0;">
                        SOC2 Ingestion Encrypted
                    </span>
                </div>
            </div>
            <div class="team-metric-icon-box">🛡️</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# 9. QUICK INVITE BAR (Image 2)
st.markdown(
    """
    <div class="quick-invite-card">
        <div class="quick-invite-title">
            <span>✉</span>
            <span>QUICK INVITE:</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Inline form row positioned inside quick invite box
st.markdown("<div style='margin-top:-64px; margin-bottom:28px; padding: 0 1.5rem;'>", unsafe_allow_html=True)
q_in_email, q_in_role, q_in_btn = st.columns([3.8, 1.8, 1.4], vertical_alignment="center")
with q_in_email:
    q_email_val = st.text_input(
        "Colleague Email",
        placeholder="colleague@studio.com",
        label_visibility="collapsed",
        key="quick_invite_email_val",
    )
with q_in_role:
    q_role_val = st.selectbox(
        "Role",
        ["Translator", "Typesetter", "Project Manager"],
        label_visibility="collapsed",
        key="quick_invite_role_val",
    )
with q_in_btn:
    st.markdown('<div class="send-invite-btn">', unsafe_allow_html=True)
    if st.button("▶ Send Invite", key="quick_send_invite_btn", use_container_width=True):
        if not q_email_val.strip():
            st.error("Please enter a valid colleague email.")
        else:
            try:
                invited = team_service.invite_member(project.id, q_email_val.strip(), q_role_val)
                st.success(f"Added {invited.name} as {invited.role} successfully!")
                st.rerun()
            except TeamServiceError as exc:
                st.error(f"Invite error: {exc}")
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# 10. WORKSPACE MEMBERS TABLE (Image 2)
translators_count = len([m for m in members if m.role == "Translator"])
typesetters_count = len([m for m in members if m.role == "Typesetter"])

st.markdown(
    f"""
    <div class="members-card-wrap">
        <div class="members-card-header">
            <div style="display:flex; align-items:center;">
                <span class="members-heading">Workspace Members</span>
                <span class="members-badge-count">{len(members)}</span>
            </div>
            <div style="font-size:0.8rem; color:#64748B; font-weight:600;">
                <span>Filter: </span>
                <strong style="color:#0F172A;">All ({len(members)})</strong> &nbsp;•&nbsp;
                <span>Translators ({translators_count})</span> &nbsp;•&nbsp;
                <span>Typesetters ({typesetters_count})</span>
            </div>
        </div>
        <div class="table-th-row">
            <div style="flex:2.8;">MEMBER NAME & EMAIL</div>
            <div style="flex:1.4;">ASSIGNED ROLE</div>
            <div style="flex:2.2;">ACTIVE TASKS</div>
            <div style="flex:1.0; text-align:right;">ACTIONS</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Render each member row natively with active action buttons
st.markdown("<div style='margin-top:-38px; margin-bottom:28px; padding: 0 1.5rem;'>", unsafe_allow_html=True)
for member in members:
    m_initials = (member.name[:2] if member.name else "U").upper()
    owner_crown = " 👑" if member.is_owner else ""
    role_display = "Owner" if member.is_owner else member.role
    
    row_c1, row_c2, row_c3, row_c4 = st.columns([2.8, 1.4, 2.2, 1.0], vertical_alignment="center")
    with row_c1:
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:12px; padding:4px 0;">
                <div class="avatar-member-circle">{m_initials}</div>
                <div>
                    <div style="font-weight:700; color:#0F172A; font-size:0.92rem;">{escape(member.name)}{owner_crown}</div>
                    <div style="color:#64748B; font-size:0.78rem;">{escape(member.email)}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with row_c2:
        st.markdown(
            f'<span class="member-role-pill">{escape(role_display)}</span>',
            unsafe_allow_html=True,
        )
    with row_c3:
        st.markdown(
            """
            <div style="font-size:0.8rem; color:#475569; display:flex; align-items:center; gap:6px;">
                <span style="width:6px; height:6px; border-radius:50%; background:#16A34A; display:inline-block;"></span>
                <span>Overall Supervision • 0 pages</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with row_c4:
        if member.is_owner:
            st.markdown(
                '<div style="text-align:right;"><span class="action-owner-pill">Owner</span></div>',
                unsafe_allow_html=True,
            )
        else:
            if st.button("Remove", key=f"btn_del_mem_{member.user_id}", use_container_width=True):
                try:
                    team_service.remove_member(project.id, member.user_id)
                    st.success(f"Removed {member.name} from project.")
                    st.rerun()
                except TeamServiceError as exc:
                    st.error(f"Error removing member: {exc}")
st.markdown("</div>", unsafe_allow_html=True)

# 11. ROLE PERMISSIONS GUIDE (Image 2 Bottom Card)
st.markdown(
    """
    <div class="guide-card-wrap">
        <div class="guide-header-row">
            <span class="guide-title">@ Role Permissions Guide</span>
            <span style="font-size:0.75rem; font-weight:700; color:#64748B; background:#F1F5F9; border:1px solid #E2E8F0; padding:3px 10px; border-radius:6px;">
                Security Scope: Project-Level Only
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div style='margin-top:-20px; padding: 0 1.5rem 1.5rem 1.5rem;'>", unsafe_allow_html=True)
g_c1, g_c2, g_c3 = st.columns(3, gap="medium")
with g_c1:
    st.markdown(
        """
        <div class="guide-col-box">
            <div class="guide-col-title">
                <span style="color:#1E40AF;">●</span>
                <span>Project Manager</span>
            </div>
            <div class="guide-col-desc">
                Highest operational tier inside project sandbox. Oversees pipeline deadlines and structural review.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with g_c2:
    st.markdown(
        """
        <div class="guide-col-box">
            <div class="guide-col-title">
                <span style="color:#16A34A;">●</span>
                <span>Translator</span>
            </div>
            <div class="guide-col-desc">
                Dedicated linguist workspace. Focused on textual accuracy, reading direction nuances, and terminology consistency.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with g_c3:
    st.markdown(
        """
        <div class="guide-col-box">
            <div class="guide-col-title">
                <span style="color:#2563EB;">●</span>
                <span>Typesetter</span>
            </div>
            <div class="guide-col-desc">
                Visual craftsmanship tier. Manages letter spacing, balloon padding, SFX styling, and font typography pairings.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
st.markdown("</div>", unsafe_allow_html=True)
