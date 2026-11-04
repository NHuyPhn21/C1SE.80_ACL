"""Database-backed Team Workspace and project role assignment."""

from html import escape

import streamlit as st

from services.team_service import TeamService, TeamServiceError
from utils.auth_session import require_auth
from utils.page_navigation import render_page_navigation


user = require_auth()
render_page_navigation()

project_name = st.query_params.get("project", "Shonen Weekly #112")
team_service = TeamService()

try:
    current_user_id = int(user.id)
except ValueError:
    st.error("Your local account is invalid. Please sign out and register again.")
    st.stop()

project = team_service.get_or_create_project(project_name, current_user_id)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [data-testid="stAppViewContainer"] { font-family:'Plus Jakarta Sans',sans-serif; background:#F8F9FA; color:#1A1D1F; }
    .team-head { margin:.5rem 0 1.5rem; }
    .team-head h1 { font-size:2rem; font-weight:800; margin:0; }
    .team-head p { color:#6C7275; margin:.3rem 0 0; }
    .member-row { display:flex; justify-content:space-between; gap:1rem; align-items:center; padding:14px; background:#FAFAFA; border:1px solid #EEE; border-radius:12px; margin-bottom:8px; }
    .role-pill { background:#E8EDFB; color:#1C274C; padding:5px 11px; border-radius:999px; font-size:.75rem; font-weight:700; white-space:nowrap; }
    div.stButton > button { border-radius:999px; font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.caption(f"ACL Studio / Projects / {project.title} / Team Workspace")
st.markdown(
    f"""
    <div class="team-head">
      <h1>Team Workspace &amp; Roles</h1>
      <p>Manage registered ACL members for <strong>{escape(project.title)}</strong>.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.container(border=True):
    st.markdown("#### Quick Invite Member")
    email_col, role_col, button_col = st.columns([2, 1.3, 1])
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

members = team_service.list_members(project.id)
metric_members, metric_roles, metric_access = st.columns(3)
metric_members.metric("Total Members", len(members))
metric_roles.metric("Assigned Roles", len({member.role for member in members}))
metric_access.metric("Access", "Private")

with st.container(border=True):
    st.markdown("### Workspace Members")
    for member in members:
        owner_suffix = " (Owner)" if member.is_owner else ""
        st.markdown(
            f"""
            <div class="member-row">
              <div><strong>{escape(member.name)}</strong><br><span style="color:#6C7275;font-size:.82rem">{escape(member.email)}</span></div>
              <span class="role-pill">{escape(member.role)}{owner_suffix}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
