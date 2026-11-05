import unittest
from datetime import UTC, datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.models import PasswordResetToken, Project, User
from services.auth_service import AuthServiceError, SqliteAuthService, verify_password
from services.team_service import TeamService, TeamServiceError


class SqliteAuthAndTeamTests(unittest.TestCase):
    def setUp(self) -> None:
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        self.session_factory = sessionmaker(bind=engine)
        self.auth = SqliteAuthService(
            self.session_factory, initialize_database=False
        )
        self.team = TeamService(self.session_factory, initialize_database=False)

    def test_register_hashes_password_and_login_reads_database(self) -> None:
        registered = self.auth.register("Huy Phan", "HUY@example.com", "password123")
        self.assertEqual(registered.user.email, "huy@example.com")

        db = self.session_factory()
        stored = db.query(User).filter(User.email == "huy@example.com").one()
        self.assertNotEqual(stored.password_hash, "password123")
        self.assertTrue(verify_password("password123", stored.password_hash))
        db.close()

        logged_in = self.auth.login("huy@example.com", "password123", False)
        self.assertEqual(logged_in.user.id, registered.user.id)

    def test_login_rejects_wrong_password_and_duplicate_registration(self) -> None:
        self.auth.register("Huy Phan", "huy@example.com", "password123")
        with self.assertRaises(AuthServiceError):
            self.auth.login("huy@example.com", "wrongpass", False)
        with self.assertRaises(AuthServiceError):
            self.auth.register("Other", "huy@example.com", "password123")

    def test_password_reset_token_is_single_use_and_changes_password(self) -> None:
        self.auth.register("Huy Phan", "huy@example.com", "password123")

        token = self.auth.request_password_reset("huy@example.com")

        self.assertIsNotNone(token)
        self.assertTrue(self.auth.verify_password_reset_token(str(token)))
        self.auth.reset_password(str(token), "newpassword123")
        self.assertFalse(self.auth.verify_password_reset_token(str(token)))
        with self.assertRaises(AuthServiceError):
            self.auth.login("huy@example.com", "password123", False)
        logged_in = self.auth.login("huy@example.com", "newpassword123", False)
        self.assertEqual(logged_in.user.email, "huy@example.com")

    def test_password_reset_does_not_reveal_unknown_email(self) -> None:
        token = self.auth.request_password_reset("missing@example.com")
        self.assertIsNone(token)

    def test_expired_password_reset_token_is_rejected(self) -> None:
        self.auth.register("Huy Phan", "huy@example.com", "password123")
        token = self.auth.request_password_reset("huy@example.com")
        db = self.session_factory()
        stored = db.query(PasswordResetToken).one()
        stored.expires_at = datetime.now(UTC).replace(tzinfo=None) - timedelta(seconds=1)
        db.commit()
        db.close()

        self.assertFalse(self.auth.verify_password_reset_token(str(token)))
        with self.assertRaisesRegex(AuthServiceError, "invalid or has expired"):
            self.auth.reset_password(str(token), "newpassword123")

    def test_invite_creates_and_updates_project_membership(self) -> None:
        owner = self.auth.register("Owner", "owner@example.com", "password123")
        member = self.auth.register("Member", "member@example.com", "password123")
        project = self.team.get_or_create_project("Manga A", int(owner.user.id))

        invited = self.team.invite_member(project.id, member.user.email, "Translator")
        self.assertEqual(invited.role, "Translator")
        self.team.invite_member(project.id, member.user.email, "Typesetter")

        members = self.team.list_members(project.id)
        self.assertEqual(len(members), 2)
        self.assertEqual(members[1].role, "Typesetter")

        self.team.remove_member(project.id, int(member.user.id))
        self.assertEqual(len(self.team.list_members(project.id)), 1)

        db = self.session_factory()
        self.assertEqual(db.query(Project).count(), 1)
        db.close()

    def test_invite_requires_registered_user(self) -> None:
        owner = self.auth.register("Owner", "owner@example.com", "password123")
        project = self.team.get_or_create_project("Manga A", int(owner.user.id))
        with self.assertRaises(TeamServiceError):
            self.team.invite_member(project.id, "missing@example.com", "Translator")


if __name__ == "__main__":
    unittest.main()
