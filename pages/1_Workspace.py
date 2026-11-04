"""Dynamic project Workspace backed by SQLite — Screen ACL-04.

Pixel-perfect implementation of Google Stitch Project 'UX/UI_ACL'.
Real SQLite database records, zero mock data, responsive project cards.
"""

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

# Theme CSS — Google Stitch / Figma Pixel-Perfect Design
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
    .workspace-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1.25rem;
    }
    .workspace-title {
        font-size: 2rem;
        font-weight: 800;
        color: #1A1D1F;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .workspace-subtitle {
        color: #6C7275;
        font-size: 0.875rem;
        margin-top: 4px;
    }

    /* Project Card */
    .project-card {
        background: #FFFFFF;
        border: 1px solid #EAEAEA;
        border-radius: 16px;
        padding: 1.35rem 1.4rem;
        min-height: 195px;
        box-shadow: 0 4px 20px rgba(20, 25, 35, 0.03);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.2s ease;
        margin-bottom: 0.6rem;
    }
    .project-card:hover {
        border-color: #D2DCF9;
        box-shadow: 0 8px 24px rgba(28, 39, 76, 0.08);
        transform: translateY(-2px);
    }
    .project-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 0.75rem;
    }
    .project-card-title {
        font-size: 1.1rem;
        font-weight: 800;
        color: #1A1D1F;
        margin: 0;
        line-height: 1.3;
    }
    .project-card-id {
        background: #E8EDFB;
        color: #1C274C;
        font-size: 0.75rem;
        font-weight: 800;
        padding: 3px 8px;
        border-radius: 6px;
        white-space: nowrap;
    }
    .project-desc {
        color: #6C7275;
        font-size: 0.82rem;
        min-height: 38px;
        margin: 0.5rem 0 1rem;
        line-height: 1.45;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .progress-track {
        height: 7px;
        border-radius: 999px;
        background: #E8EAED;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        border-radius: inherit;
        background: #1C274C;
        transition: width 0.3s ease;
    }
    .progress-info {
        display: flex;
        justify-content: space-between;
        font-size: 0.78rem;
        margin-bottom: 0.45rem;
        color: #6C7275;
    }

    /* KPI Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.25rem;
        margin-top: 1.75rem;
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


@st.dialog("Create New Project")
def create_project_dialog() -> None:
    with st.form("create_project_form"):
        st.markdown("#### Series Details")
        title = st.text_input("Project title", placeholder="Series or chapter name (e.g. Bleach Chapter 01)")
        description = st.text_area(
            "Description", placeholder="Language pair, editorial notes, or scope (e.g. Japanese to Vietnamese)"
        )
        submitted = st.form_submit_button("Create project", use_container_width=True)
    if submitted:
        try:
            workspace_service.create_project(user_id, title, description)
            st.success("Project created successfully.")
            st.rerun()
        except WorkspaceServiceError as exc:
            st.error(str(exc))


# 1. Top Breadcrumb
st.markdown(
    """
    <div class="top-breadcrumb">
        <div>ACL Studio &nbsp;/&nbsp; <span>Projects</span></div>
        <div style="font-weight:600; color:#2E7D32; font-size:0.75rem; background:#E8F5E9; padding:4px 12px; border-radius:9999px;">
            ● SQLite Database Connected
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 2. Main Title Row with Create Button
header_col, action_col = st.columns([2.5, 1], vertical_alignment="center")
with header_col:
    st.markdown('<h1 class="workspace-title">Projects</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="workspace-subtitle">Manage manga localization projects and chapter series from live database records.</p>',
        unsafe_allow_html=True,
    )
with action_col:
    if st.button("+ Create New Project", use_container_width=True):
        create_project_dialog()

# 3. Search & Filter Bar
projects = workspace_service.list_projects(user_id)

search_col, filter_info = st.columns([2, 1], vertical_alignment="center")
with search_col:
    search_term = st.text_input(
        "Search projects",
        placeholder="🔍 Search projects by title...",
        label_visibility="collapsed",
        key="search_project_input",
    )

if search_term:
    projects = [p for p in projects if search_term.lower() in p.title.lower()]

# 4. Projects Grid
if not projects:
    if search_term:
        st.info(f"No projects found matching '{search_term}'.")
    else:
        st.markdown(
            """
            <div style="background:#FFFFFF; border:1px dashed #D2DCF9; border-radius:20px; padding:3rem 2rem; text-align:center; margin: 1.5rem 0; box-shadow:0 4px 20px rgba(0,0,0,0.02);">
                <div style="font-size:3rem; margin-bottom:12px;">📁</div>
                <h2 style="font-size:1.35rem; font-weight:800; color:#1A1D1F; margin:0 0 8px;">No Projects Yet</h2>
                <p style="color:#6C7275; font-size:0.9rem; max-width:480px; margin:0 auto 1.5rem; line-height:1.5;">
                    Create your first manga localization project to start uploading chapter scans, configuring translation pairs, and tracking pipeline progress.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_empty_btn = st.columns([1, 1.2, 1])[1]
        with col_empty_btn:
            if st.button("+ Create Your First Project", key="create_first_proj_btn", use_container_width=True):
                create_project_dialog()
else:
    for start in range(0, len(projects), 3):
        columns = st.columns(3, gap="medium")
        for column, project in zip(columns, projects[start : start + 3]):
            with column:
                progress_color = "#2E7D32" if project.progress_percent == 100 else "#1C274C"
                st.markdown(
                    f"""
                    <article class="project-card">
                      <div>
                          <div class="project-card-header">
                            <h3 class="project-card-title">{escape(project.title)}</h3>
                            <code class="project-card-id">#{project.id:02d}</code>
                          </div>
                          <p class="project-desc">{escape(project.description or 'Manga translation project')}</p>
                      </div>
                      <div>
                          <div class="progress-info">
                            <span>{project.completed_pages}/{project.total_pages} pages complete</span>
                            <strong>{project.progress_percent}%</strong>
                          </div>
                          <div class="progress-track">
                            <div class="progress-fill" style="width:{project.progress_percent}%; background:{progress_color};"></div>
                          </div>
                      </div>
                    </article>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    "Open Chapter Studio ➔",
                    key=f"open_project_{project.id}",
                    use_container_width=True,
                ):
                    st.query_params["project"] = project.title
                    st.switch_page("pages/2_Chapter_Studio.py")

# 5. Footer Overview KPIs
all_user_projects = workspace_service.list_projects(user_id)
total_pages = sum(p.total_pages for p in all_user_projects)
completed_pages = sum(p.completed_pages for p in all_user_projects)

st.markdown(
    f"""
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-title">ACCESSIBLE PROJECTS</div>
            <div class="kpi-value">{len(all_user_projects)}</div>
            <div class="kpi-sub">Active series in your workspace</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">TOTAL PAGES</div>
            <div class="kpi-value">{total_pages}</div>
            <div class="kpi-sub">Pages registered across all chapters</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">COMPLETED PAGES</div>
            <div class="kpi-value">{completed_pages}</div>
            <div class="kpi-sub">Rendered spreads ready for publishing</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
