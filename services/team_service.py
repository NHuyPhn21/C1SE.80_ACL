"""Database-backed project membership operations for Team Workspace."""

from dataclasses import dataclass

from sqlalchemy import func

from backend.database import SessionLocal, init_db
from backend.models import Project, ProjectMembership, User


class TeamServiceError(RuntimeError):
    pass


@dataclass(frozen=True)
class TeamMember:
    user_id: int
    name: str
    email: str
    role: str
    is_owner: bool = False


class TeamService:
    def __init__(self, session_factory=SessionLocal, *, initialize_database: bool = True) -> None:
        if initialize_database:
            init_db()
        self.session_factory = session_factory

    def get_or_create_project(self, title: str, owner_id: int) -> Project:
        db = self.session_factory()
        try:
            project = (
                db.query(Project)
                .filter(func.lower(Project.title) == title.strip().lower())
                .first()
            )
            if project is None:
                project = (
                    db.query(Project)
                    .filter(Project.owner_id == owner_id)
                    .order_by(Project.created_at.asc())
                    .first()
                )
            if project is None:
                project = Project(owner_id=owner_id, title=title.strip() or "Untitled Project")
                db.add(project)
                db.commit()
                db.refresh(project)
            db.expunge(project)
            return project
        finally:
            db.close()

    def list_members(self, project_id: int) -> list[TeamMember]:
        db = self.session_factory()
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if project is None:
                raise TeamServiceError("Project not found.")

            members = [
                TeamMember(
                    user_id=project.owner.id,
                    name=project.owner.username,
                    email=project.owner.email,
                    role="Project Manager",
                    is_owner=True,
                )
            ]
            memberships = (
                db.query(ProjectMembership)
                .filter(ProjectMembership.project_id == project_id)
                .order_by(ProjectMembership.joined_at.asc())
                .all()
            )
            for membership in memberships:
                if membership.user_id == project.owner_id:
                    continue
                members.append(
                    TeamMember(
                        user_id=membership.user.id,
                        name=membership.user.username,
                        email=membership.user.email,
                        role=membership.project_role,
                    )
                )
            return members
        finally:
            db.close()

    def invite_member(self, project_id: int, email: str, role: str) -> TeamMember:
        normalized_email = email.strip().lower()
        if "@" not in normalized_email:
            raise TeamServiceError("Please enter a valid email address.")

        db = self.session_factory()
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if project is None:
                raise TeamServiceError("Project not found.")
            invited_user = (
                db.query(User).filter(func.lower(User.email) == normalized_email).first()
            )
            if invited_user is None:
                raise TeamServiceError("This email has not registered an ACL account yet.")
            if invited_user.id == project.owner_id:
                raise TeamServiceError("The project owner is already a member.")

            membership = (
                db.query(ProjectMembership)
                .filter(
                    ProjectMembership.project_id == project_id,
                    ProjectMembership.user_id == invited_user.id,
                )
                .first()
            )
            if membership is None:
                membership = ProjectMembership(
                    project_id=project_id,
                    user_id=invited_user.id,
                    project_role=role,
                )
                db.add(membership)
            else:
                membership.project_role = role
            db.commit()
            return TeamMember(
                user_id=invited_user.id,
                name=invited_user.username,
                email=invited_user.email,
                role=membership.project_role,
            )
        except TeamServiceError:
            db.rollback()
            raise
        finally:
            db.close()

    def remove_member(self, project_id: int, user_id: int) -> None:
        db = self.session_factory()
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if project is None:
                raise TeamServiceError("Project not found.")
            if project.owner_id == user_id:
                raise TeamServiceError("The project owner cannot be removed.")
            membership = (
                db.query(ProjectMembership)
                .filter(
                    ProjectMembership.project_id == project_id,
                    ProjectMembership.user_id == user_id,
                )
                .first()
            )
            if membership is None:
                raise TeamServiceError("Project membership not found.")
            db.delete(membership)
            db.commit()
        except TeamServiceError:
            db.rollback()
            raise
        finally:
            db.close()
