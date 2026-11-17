
import os
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base
from backend.models import ApiUsage, Project, User
from services.settings_service import SettingsService, SettingsServiceError


class ApiQuotaTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "quota_test.db"

        self.engine = create_engine(
            f"sqlite:///{db_path.as_posix()}",
            connect_args={
                "check_same_thread": False,
                "timeout": 10,
            },
        )
        Base.metadata.create_all(self.engine)

        self.session_factory = sessionmaker(bind=self.engine)

        db = self.session_factory()
        try:
            user = User(
                username="Quota Tester",
                email="quota@example.com",
                password_hash="test",
            )
            db.add(user)
            db.flush()

            project = Project(
                owner_id=user.id,
                title="Quota Test Project",
            )
            db.add(project)
            db.commit()

            self.project_id = project.id
        finally:
            db.close()

        self.service = SettingsService(
            self.session_factory,
            encryption_secret="test-secret",
            initialize_database=False,
        )

        self.quota_patch = patch.dict(
            os.environ,
            {"ACL_MONTHLY_QUOTA": "2"},
        )
        self.quota_patch.start()

    def tearDown(self):
        self.quota_patch.stop()
        self.engine.dispose()
        self.temp_dir.cleanup()

    def test_initial_quota_is_zero(self):
        result = self.service.get_project_quota_usage(
            self.project_id
        )

        self.assertEqual(result["requests_this_month"], 0)
        self.assertEqual(result["monthly_limit"], 2)
        self.assertEqual(result["remaining"], 2)
        self.assertFalse(result["quota_exceeded"])

    def test_consume_quota_records_usage(self):
        result = self.service.consume_project_quota(
            self.project_id,
            "translate",
        )

        self.assertEqual(result["requests_this_month"], 1)
        self.assertEqual(result["remaining"], 1)

        db = self.session_factory()
        try:
            records = db.query(ApiUsage).all()
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].action, "translate")
        finally:
            db.close()

    def test_quota_limit_blocks_third_request(self):
        self.service.consume_project_quota(
            self.project_id,
            "translate",
        )
        self.service.consume_project_quota(
            self.project_id,
            "queue_start",
        )

        with self.assertRaises(SettingsServiceError):
            self.service.consume_project_quota(
                self.project_id,
                "translate",
            )

        result = self.service.get_project_quota_usage(
            self.project_id
        )

        self.assertEqual(result["requests_this_month"], 2)
        self.assertEqual(result["remaining"], 0)
        self.assertTrue(result["quota_exceeded"])

    def test_previous_month_does_not_count(self):
        previous_month = (
            datetime.now(UTC).replace(tzinfo=None)
            - timedelta(days=40)
        )

        db = self.session_factory()
        try:
            db.add(
                ApiUsage(
                    project_id=self.project_id,
                    action="translate",
                    created_at=previous_month,
                )
            )
            db.commit()
        finally:
            db.close()

        result = self.service.get_project_quota_usage(
            self.project_id
        )

        self.assertEqual(result["requests_this_month"], 0)

    def test_invalid_action_does_not_consume_quota(self):
        with self.assertRaises(ValueError):
            self.service.consume_project_quota(
                self.project_id,
                "invalid_action",
            )

        result = self.service.get_project_quota_usage(
            self.project_id
        )
        self.assertEqual(result["requests_this_month"], 0)

    def test_concurrent_requests_do_not_exceed_limit(self):
        def consume():
            try:
                self.service.consume_project_quota(
                    self.project_id,
                    "translate",
                )
                return "accepted"
            except SettingsServiceError:
                return "rejected"

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(
                lambda _: consume(),
                range(5),
            ))

        self.assertEqual(results.count("accepted"), 2)
        self.assertEqual(results.count("rejected"), 3)

        usage = self.service.get_project_quota_usage(
            self.project_id
        )
        self.assertEqual(usage["requests_this_month"], 2)


if __name__ == "__main__":
    unittest.main()
