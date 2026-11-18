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
            db.flush()
            db.add(
                ProjectMembership(
                    project_id=project.id,
                    user_id=owner_id,
                    project_role="Owner",
                )
            )
            db.commit()
            return project.id
        except WorkspaceServiceError:
            db.rollback()
            raise
        finally:
            db.close()

    def update_project(self, project_id: int, title: str, description: str = "") -> None:
        clean_title = title.strip()
        if not clean_title:
            raise WorkspaceServiceError("Project title is required.")
        db = self.session_factory()
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if project is None:
                raise WorkspaceServiceError("Project not found.")
            duplicate = (
                db.query(Project)
                .filter(
                    Project.owner_id == project.owner_id,
                    Project.title == clean_title,
                    Project.id != project_id,
                )
                .first()
            )
            if duplicate:
                raise WorkspaceServiceError("You already own a project with this title.")
            project.title = clean_title
            project.description = description.strip() or None
            db.commit()
        except WorkspaceServiceError:
            db.rollback()
            raise
        finally:
            db.close()

    def delete_project(self, project_id: int) -> list[str]:
        """Delete a project and everything under it.

        Returns the stored file paths of its pages so the caller can remove
        them from disk after the database commit succeeds.
        """
        db = self.session_factory()
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if project is None:
                raise WorkspaceServiceError("Project not found.")
            for chapter in project.chapters:
                if any(task.status in {"QUEUED", "RUNNING"} for task in chapter.queue_tasks):
                    raise WorkspaceServiceError(
                        "Cannot delete a project while a pipeline is running."
                    )
            paths = [
                path
                for chapter in project.chapters
                for page in chapter.pages
                for path in (page.original_path, page.clean_path, page.rendered_path)
                if path
            ]
            db.delete(project)
            db.commit()
            return paths
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
