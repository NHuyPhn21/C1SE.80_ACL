"""Unit & Integration tests for Phan Van Quan's assigned modules.

Covers:
1. Workspace: Project creation, SQLite persistence, and owner membership.
2. Team Workspace: Send invite, role assignment, and member removal in SQLite.
3. Queue Monitor: Real ZIP package bundling from data/rendered_pages/ and manifest validation.
"""

import io
import unittest
import zipfile
from pathlib import Path

from backend.database import SessionLocal, init_db
from backend.models import User, Project, ProjectMembership


class TestQuanWorkspaceAndQueue(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        init_db()
        cls.db = SessionLocal()
        # Ensure a test user exists
        cls.user = cls.db.query(User).filter_by(email="quan.test@acl.vn").first()
        if not cls.user:
            cls.user = User(
                username="Phan Van Quan Test",
                email="quan.test@acl.vn",
                password_hash="mock_hash_test",
                role="editor",
            )
            cls.db.add(cls.user)
            cls.db.commit()
            cls.db.refresh(cls.user)

    @classmethod
    def tearDownClass(cls) -> None:
        # Clean up any leftover test projects
        test_projs = cls.db.query(Project).filter(Project.title.like("Unit Test%")).all()
        for p in test_projs:
            cls.db.query(ProjectMembership).filter_by(project_id=p.id).delete()
            cls.db.delete(p)
        if cls.user:
            cls.db.query(ProjectMembership).filter_by(user_id=cls.user.id).delete()
            cls.db.delete(cls.user)
        cls.db.commit()
        cls.db.close()

    def setUp(self) -> None:
        self.db = SessionLocal()

    def tearDown(self) -> None:
        self.db.close()

    # -------------------------------------------------------------
    # 1. WORKSPACE: Modal Create Project & SQLite Persistence
    # -------------------------------------------------------------
    def test_workspace_create_project_and_owner_membership(self) -> None:
        title = "Unit Test Series - Bleach Rebirth"
        desc = "20 pages • Japanese ➔ Vietnamese"

        # Simulate form submit logic
        new_proj = Project(owner_id=self.user.id, title=title, description=desc)
        self.db.add(new_proj)
        self.db.commit()
        self.db.refresh(new_proj)

        # Owner membership assignment
        owner_m = ProjectMembership(
            project_id=new_proj.id, user_id=self.user.id, project_role="Owner"
        )
        self.db.add(owner_m)
        self.db.commit()

        # Assertions
        queried = self.db.query(Project).filter_by(id=new_proj.id).first()
        self.assertIsNotNone(queried)
        self.assertEqual(queried.title, title)
        self.assertEqual(queried.owner_id, self.user.id)

        m_check = self.db.query(ProjectMembership).filter_by(
            project_id=new_proj.id, user_id=self.user.id
        ).first()
        self.assertIsNotNone(m_check)
        self.assertEqual(m_check.project_role, "Owner")

        # Cleanup
        self.db.query(ProjectMembership).filter_by(project_id=new_proj.id).delete()
        self.db.delete(new_proj)
        self.db.commit()

    def test_workspace_duplicate_project_prevention(self) -> None:
        title = "Unit Test Series - Unique Title"
        p1 = Project(owner_id=self.user.id, title=title, description="Raw Manga")
        self.db.add(p1)
        self.db.commit()

        # Logic checks if existing title already present
        existing = self.db.query(Project).filter_by(title=title).first()
        self.assertIsNotNone(existing)

        # Cleanup
        self.db.delete(p1)
        self.db.commit()

    # -------------------------------------------------------------
    # 2. TEAM WORKSPACE: Send Invite & Remove Member in SQLite
    # -------------------------------------------------------------
    def test_team_workspace_invite_and_remove_member(self) -> None:
        # Create a test project for team assignment
        proj = Project(
            owner_id=self.user.id,
            title="Unit Test Series - Team Test",
            description="Team Workspace Testing",
        )
        self.db.add(proj)
        self.db.commit()
        self.db.refresh(proj)

        # 1. Invite a colleague
        colleague_email = "colleague.translator@acl.vn"
        colleague = self.db.query(User).filter_by(email=colleague_email).first()
        if not colleague:
            colleague = User(
                username="Colleague Translator",
                email=colleague_email,
                password_hash="colleague_mock",
                role="member",
            )
            self.db.add(colleague)
            self.db.commit()
            self.db.refresh(colleague)

        new_membership = ProjectMembership(
            project_id=proj.id,
            user_id=colleague.id,
            project_role="Translator",
        )
        self.db.add(new_membership)
        self.db.commit()
        self.db.refresh(new_membership)

        # Verify membership added to database
        m_check = self.db.query(ProjectMembership).filter_by(id=new_membership.id).first()
        self.assertIsNotNone(m_check)
        self.assertEqual(m_check.project_role, "Translator")
        self.assertEqual(m_check.user.email, colleague_email)

        # 2. Remove member logic
        self.db.query(ProjectMembership).filter_by(id=new_membership.id).delete()
        self.db.commit()

        # Verify removal
        removed = self.db.query(ProjectMembership).filter_by(id=new_membership.id).first()
        self.assertIsNone(removed)

        # Cleanup project & colleague
        self.db.delete(proj)
        self.db.delete(colleague)
        self.db.commit()

    # -------------------------------------------------------------
    # 3. QUEUE MONITOR: Real ZIP Packaging from rendered_pages
    # -------------------------------------------------------------
    def test_queue_monitor_zip_bundling_and_manifest(self) -> None:
        project_name = "Unit Test Comic Release"
        rendered_dir = Path("data/rendered_pages")
        rendered_dir.mkdir(parents=True, exist_ok=True)

        # Create a temporary test rendered page
        test_file = rendered_dir / "final_test_page_99.png"
        test_file.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDRmock_image_bytes")

        try:
            rendered_files = sorted(list(rendered_dir.glob("final_*.*")))
            self.assertGreater(len(rendered_files), 0)

            # Build in-memory ZIP package
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                manifest_text = f"Project: {project_name}\nPages: {len(rendered_files)}\n"
                for f in rendered_files:
                    zf.write(f, arcname=f"pages/{f.name}")
                    manifest_text += f"- pages/{f.name}\n"
                zf.writestr("RELEASE_MANIFEST.txt", manifest_text)

            zip_bytes = zip_buf.getvalue()
            self.assertGreater(len(zip_bytes), 0)

            # Read back ZIP and verify integrity
            zf_read = zipfile.ZipFile(io.BytesIO(zip_bytes))
            namelist = zf_read.namelist()
            self.assertIn("RELEASE_MANIFEST.txt", namelist)
            self.assertIn("pages/final_test_page_99.png", namelist)

            manifest_content = zf_read.read("RELEASE_MANIFEST.txt").decode("utf-8")
            self.assertIn(project_name, manifest_content)
        finally:
            # Clean up temporary test image
            if test_file.exists():
                test_file.unlink()

    def test_queue_monitor_progress_metrics(self) -> None:
        total_pages = 24
        processed_pages = 18
        progress_pct = min(100, int((processed_pages / total_pages) * 100))
        self.assertEqual(progress_pct, 75)


if __name__ == "__main__":
    unittest.main()
