"""Native Streamlit project workspace backed by SQLite."""

from pathlib import Path

import streamlit as st

from backend.database import SessionLocal, init_db
from backend.models import Project, ProjectMembership, User
from utils.auth_session import require_auth
from utils.page_navigation import render_page_navigation


user = require_auth()
render_page_navigation()
init_db()

base_dir = Path(__file__).parents[1]
thumbnail_dir = base_dir / "assets" / "thumbnails"

db = SessionLocal()
try:
    db_user = db.query(User).filter_by(email=user.email).first()
    if not db_user:
        db_user = User(
            username=user.full_name or user.email.split("@")[0],
            email=user.email,
            password_hash="session-authenticated",
            role="editor",
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    if st.session_state.pop("workspace_create_project", False):
        title = st.session_state.pop("new_project_title", "").strip()
        description = st.session_state.pop("new_project_description", "").strip()
        if title:
            project = Project(
                owner_id=db_user.id,
                title=title,
                description=description or "Japanese → Vietnamese",
            )
            db.add(project)
            db.commit()
            db.refresh(project)
            db.add(
                ProjectMembership(
                    project_id=project.id,
                    user_id=db_user.id,
                    project_role="Owner",
                )
            )
            db.commit()

    projects = db.query(Project).order_by(Project.id.asc()).all()
    project_cards = []
    for project in projects:
        pages = [page for chapter in project.chapters for page in chapter.pages]
        completed = sum(
            1 for page in pages
            if page.status == "COMPLETED" or bool(page.rendered_path)
        )
        project_cards.append((project, len(pages), completed))
finally:
    db.close()

st.title("Workspace")
st.caption("Projects and pipeline status from SQLite")

with st.expander("Create new project"):
    with st.form("create_project"):
        st.text_input("Project name", key="new_project_title")
        st.text_input(
            "Description",
            value="Japanese → Vietnamese",
            key="new_project_description",
        )
        if st.form_submit_button("Create project"):
            st.session_state["workspace_create_project"] = True
            st.rerun()

if not project_cards:
    st.info("Chưa có project nào. Hãy tạo project mới hoặc mở Chapter Studio để upload.")

for project, total_pages, completed_pages in project_cards:
    progress = round(completed_pages / total_pages * 100) if total_pages else 0
    with st.container(border=True):
        left, right = st.columns([1.5, 1])
        with left:
            st.subheader(project.title)
            st.caption(project.description or "Japanese → Vietnamese")
            st.progress(progress, text=f"{completed_pages}/{total_pages} pages rendered")
            st.caption(f"Status: {'Completed' if total_pages and progress == 100 else 'Ready for ingestion'}")
        with right:
            thumbnail_name = (
                "one_piece_1115.jpg"
                if "one piece" in project.title.lower()
                else "jujutsu_kaisen_sp.jpg"
                if "jujutsu" in project.title.lower()
                else "shonen_112.jpg"
            )
            thumbnail = thumbnail_dir / thumbnail_name
            if thumbnail.exists():
                st.image(str(thumbnail), use_container_width=True)
            if st.button("Open Chapter Studio", key=f"chapter_{project.id}"):
                st.query_params["project"] = project.title
                st.switch_page("pages/2_Chapter_Studio.py")
            if total_pages:
                if st.button("Open Queue Monitor", key=f"queue_{project.id}"):
                    st.query_params["project"] = project.title
                    st.switch_page("pages/5_Queue_Monitor.py")
