"""Database-backed Team Workspace and project role assignment — Screen ACL-05.

Pixel-perfect implementation of Google Stitch Project 'UX/UI_ACL'.
Real SQLite authentication and team membership records, zero mock data.
"""

from html import escape
import streamlit as st

from services.team_service import TeamService, TeamServiceError
from services.workspace_service import WorkspaceService
from utils.auth_session import require_auth
from utils.page_navigation import render_page_navigation

user = require_auth()
render_page_navigation()

team_service = TeamService()
workspace_service = WorkspaceService()

try:
    current_user_id = int(user.id)
except ValueError:
    st.error("Your local account is invalid. Please sign out and register again.")
    st.stop()

# Determine project dynamically without mock names
user_projects = []
try:
    user_projects = workspace_service.list_projects(current_user_id)
except Exception:
    pass

default_proj = user_projects[0].title if user_projects else "Local Manga"
project_name = st.query_params.get("project", default_proj)

project = team_service.get_or_create_project(project_name, current_user_id)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #F8F9FA !important;
        color: #1A1D1F !important;
    }

    /* Top Breadcrumb */
    .top-breadcrumb {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-top: 0.25rem;
        padding-bottom: 0.85rem;
        font-size: 0.85rem;
        color: #6C7275;
    }
    .top-breadcrumb span {
        font-weight: 600;
        color: #1A1D1F;
    }

    /* Header */
    .team-head {
        margin-bottom: 1.25rem;
    }
    .team-head h1 {
        font-size: 2rem;
        font-weight: 800;
        color: #1A1D1F;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .team-head p {
        color: #6C7275;
        font-size: 0.875rem;
        margin-top: 4px;
    }

    /* KPI Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.25rem;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #EAEAEA;
        border-radius: 16px;
        padding: 1.25rem 1.35rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-title {
        font-size: 0.75rem;
        font-weight: 700;
        color: #6C7275;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        font-size: 1.9rem;
        font-weight: 800;
        color: #1A1D1F;
        margin: 8px 0 4px;
        letter-spacing: -0.02em;
    }
    .kpi-sub {
        font-size: 0.75rem;
        color: #6C7275;
    }

    /* Section Cards */
    .section-card {
        background: #FFFFFF;
        border: 1px solid #EAEAEA;
        border-radius: 16px;
        padding: 1.35rem 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        margin-bottom: 1.25rem;
    }

    .role-pill {
        background: #E8EDFB;
        color: #1C274C;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
        white-space: nowrap;
        display: inline-block;
    }
    .role-pill-owner {
        background: #E8F5E9;
        color: #2E7D32;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
        white-space: nowrap;
        display: inline-block;
    }

    /* Button Styling */
    div.stButton > button {
        border-radius: 9999px !important;
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:first-child {
        background-color: #1C274C !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #25326F !important;
        transform: translateY(-1px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 1. Top Breadcrumb
st.markdown(
    f"""
    <div class="top-breadcrumb">
        <div>ACL Studio &nbsp;/&nbsp; Projects &nbsp;/&nbsp; {escape(project.title)} &nbsp;/&nbsp; <span>Team Workspace</span></div>
        <div style="font-weight:600; color:#2E7D32; font-size:0.75rem; background:#E8F5E9; padding:4px 12px; border-radius:9999px;">
            ● Role Management Active
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 2. Main Title Row
st.markdown(
    f"""
    <div class="team-head">
      <h1>Team Workspace &amp; Roles</h1>
      <p>Manage registered ACL team members and permission roles for <strong>{escape(project.title)}</strong>.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# 3. Quick Invite Member Section
st.markdown(
    """
    <div class="section-card">
        <h4 style="font-size:1rem; font-weight:700; color:#1A1D1F; margin:0 0 1rem;">Invite Team Member</h4>
    """,
    unsafe_allow_html=True,
)
email_col, role_col, button_col = st.columns([2, 1.3, 1], vertical_alignment="center")
with email_col:
    invite_email = st.text_input(
        "Colleague email",
        placeholder="colleague@studio.com",
        label_visibility="collapsed",
        key="team_invite_email",
    )
with role_col:
    invite_role = st.selectbox(
        "Role",
        ["Translator", "Typesetter", "Project Manager"],
        label_visibility="collapsed",
        key="team_invite_role",
    )
with button_col:
    if st.button("Send Invite", use_container_width=True):
        try:
            invited = team_service.invite_member(project.id, invite_email, invite_role)
            st.success(f"Added {invited.name} as {invited.role}.")
            st.rerun()
        except TeamServiceError as exc:
            st.error(str(exc))
st.markdown("</div>", unsafe_allow_html=True)

# 4. KPI Metrics Cards
members = team_service.list_members(project.id)
st.markdown(
    f"""
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-title">TOTAL MEMBERS</div>
            <div class="kpi-value">{len(members)}</div>
            <div class="kpi-sub">Collaborators assigned to project</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">ASSIGNED ROLES</div>
            <div class="kpi-value">{len({member.role for member in members})}</div>
            <div class="kpi-sub">Distinct localization permissions</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">ACCESS POLICY</div>
            <div class="kpi-value">Private</div>
            <div class="kpi-sub">Restricted to invited members</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 5. Members List Section
st.markdown(
    """
    <div style="margin-top:1.5rem; margin-bottom:0.75rem;">
        <h3 style="font-size:1.2rem; font-weight:800; color:#1A1D1F; margin:0;">
            Workspace Members
        </h3>
    </div>
    """,
    unsafe_allow_html=True,
)

if not members:
    st.info("No members assigned to this project yet.")
else:
    for member in members:
        owner_suffix = " (Owner)" if member.is_owner else ""
        pill_cls = "role-pill-owner" if member.is_owner else "role-pill"

        info_col, role_col, action_col = st.columns([2.4, 1.2, 0.8], vertical_alignment="center")
        with info_col:
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; gap:12px; padding:6px 0;">
                    <div style="width:36px; height:36px; border-radius:50%; background:#1C274C; color:#FFF; font-weight:800; font-size:0.8rem; display:flex; align-items:center; justify-content:center;">
                        {escape(member.name[:2].upper())}
                    </div>
                    <div>
                        <div style="font-weight:700; font-size:0.9rem; color:#1A1D1F;">{escape(member.name)}</div>
                        <div style="font-size:0.78rem; color:#6C7275;">{escape(member.email)}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with role_col:
            st.markdown(
                f'<span class="{pill_cls}">{escape(member.role)}{owner_suffix}</span>',
                unsafe_allow_html=True,
            )
        with action_col:
            if not member.is_owner:
                if st.button("Remove", key=f"remove_member_{member.user_id}", use_container_width=True):
                    try:
                        team_service.remove_member(project.id, member.user_id)
                        st.success(f"Removed {member.name} from the project.")
                        st.rerun()
                    except TeamServiceError as exc:
                        st.error(str(exc))

        st.markdown("<hr style='margin: 4px 0 8px; border:none; border-top:1px solid #F0F2F5;' />", unsafe_allow_html=True)
