"""Project dashboard queries and creation operations."""

from dataclasses import dataclass

from sqlalchemy import or_

from backend.database import SessionLocal, init_db
from backend.models import Chapter, ComicPage, Project, ProjectMembership


class WorkspaceServiceError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProjectSummary:
    id: int
    title: str
    description: str
    total_pages: int
    completed_pages: int

    @property
    def progress_percent(self) -> int:
        if not self.total_pages:
            return 0
        return min(100, round(self.completed_pages / self.total_pages * 100))


class WorkspaceService:
    def __init__(self, session_factory=SessionLocal, *, initialize_database: bool = True) -> None:
        if initialize_database:
            init_db()
        self.session_factory = session_factory

    def create_project(self, owner_id: int, title: str, description: str = "") -> int:
        clean_title = title.strip()
        if not clean_title:
            raise WorkspaceServiceError("Project title is required.")
        db = self.session_factory()
        try:
            duplicate = (
                db.query(Project)
                .filter(Project.owner_id == owner_id, Project.title == clean_title)
                .first()
            )
            if duplicate:
                raise WorkspaceServiceError("You already own a project with this title.")
            project = Project(
                owner_id=owner_id,
                title=clean_title,
                description=description.strip() or None,
            )
            db.add(project)
            db.commit()
            db.refresh(project)
            return project.id
        except WorkspaceServiceError:
            db.rollback()
            raise
        finally:
            db.close()

    def list_projects(self, user_id: int) -> list[ProjectSummary]:
        db = self.session_factory()
        try:
            membership_project_ids = db.query(ProjectMembership.project_id).filter(
                ProjectMembership.user_id == user_id
            )
            projects = (
                db.query(Project)
                .filter(
                    or_(
                        Project.owner_id == user_id,
                        Project.id.in_(membership_project_ids),
                    )
                )
                .order_by(Project.created_at.desc(), Project.id.desc())
                .all()
            )
            summaries = []
            for project in projects:
                page_query = (
                    db.query(ComicPage)
                    .join(Chapter, ComicPage.chapter_id == Chapter.id)
                    .filter(Chapter.project_id == project.id)
                )
                total = page_query.count()
                completed = page_query.filter(ComicPage.status == "COMPLETED").count()
                summaries.append(
                    ProjectSummary(
                        id=project.id,
                        title=project.title,
                        description=project.description or "Japanese to Vietnamese localization",
                        total_pages=total,
                        completed_pages=completed,
                    )
                )
            return summaries
        finally:
            db.close()
