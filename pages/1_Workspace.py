"""Dynamic project Workspace backed by SQLite."""

from html import escape

import streamlit as st

from services.workspace_service import WorkspaceService, WorkspaceServiceError
from utils.auth_session import require_auth
from utils.page_navigation import render_page_navigation


user = require_auth()
render_page_navigation()

try:
    user_id = int(user.id)
except ValueError:
    st.error("Your local account is invalid. Please sign out and register again.")
    st.stop()

workspace_service = WorkspaceService()

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [data-testid="stAppViewContainer"] { font-family:'Plus Jakarta Sans',sans-serif; background:#F8F9FA; color:#1A1D1F; }
    .workspace-title { font-size:2rem; font-weight:800; margin:.5rem 0 0; }
    .workspace-subtitle { color:#6C7275; margin:.25rem 0 1.5rem; }
    .project-card { background:#FFF; border:1px solid #EAEAEA; border-radius:16px; padding:1.35rem; min-height:210px; box-shadow:0 8px 30px rgba(20,25,35,.04); }
    .project-card h3 { margin:0; font-size:1.1rem; }
    .project-desc { color:#6C7275; font-size:.82rem; min-height:42px; margin:.5rem 0 1.3rem; }
    .progress-track { height:7px; border-radius:999px; background:#E8EAED; overflow:hidden; }
    .progress-fill { height:100%; border-radius:inherit; background:#25326F; }
    div.stButton > button { border-radius:999px; font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.dialog("Create New Project")
def create_project_dialog() -> None:
    with st.form("create_project_form"):
        title = st.text_input("Project title", placeholder="Series or chapter name")
        description = st.text_area(
            "Description", placeholder="Language pair, editorial notes, or scope"
        )
        submitted = st.form_submit_button("Create project", use_container_width=True)
    if submitted:
        try:
            workspace_service.create_project(user_id, title, description)
            st.success("Project created successfully.")
            st.rerun()
        except WorkspaceServiceError as exc:
            st.error(str(exc))


header_col, action_col = st.columns([2.5, 1])
with header_col:
    st.caption("ACL Studio / Projects")
    st.markdown('<h1 class="workspace-title">Projects</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="workspace-subtitle">Manage localization projects from live database records.</p>',
        unsafe_allow_html=True,
    )
with action_col:
    st.write("")
    if st.button("Create New Project", use_container_width=True):
        create_project_dialog()

projects = workspace_service.list_projects(user_id)
if not projects:
    with st.container(border=True):
        st.subheader("No projects yet")
        st.write("Create your first project to start uploading and processing manga pages.")
else:
    for start in range(0, len(projects), 3):
        columns = st.columns(3, gap="medium")
        for column, project in zip(columns, projects[start : start + 3]):
            with column:
                st.markdown(
                    f"""
                    <article class="project-card">
                      <div style="display:flex;justify-content:space-between;gap:1rem;align-items:start">
                        <h3>{escape(project.title)}</h3>
                        <code>#{project.id:02d}</code>
                      </div>
                      <p class="project-desc">{escape(project.description)}</p>
                      <div style="display:flex;justify-content:space-between;font-size:.78rem;margin-bottom:.45rem;color:#6C7275">
                        <span>{project.completed_pages}/{project.total_pages} pages complete</span>
                        <strong>{project.progress_percent}%</strong>
                      </div>
                      <div class="progress-track"><div class="progress-fill" style="width:{project.progress_percent}%"></div></div>
                    </article>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    "Open Chapter Studio",
                    key=f"open_project_{project.id}",
                    use_container_width=True,
                ):
                    st.query_params["project"] = project.title
                    st.switch_page("pages/2_Chapter_Studio.py")

total_pages = sum(project.total_pages for project in projects)
completed_pages = sum(project.completed_pages for project in projects)
metric_projects, metric_pages, metric_completed = st.columns(3)
metric_projects.metric("Accessible Projects", len(projects))
metric_pages.metric("Total Pages", total_pages)
metric_completed.metric("Completed Pages", completed_pages)
