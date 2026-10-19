"""Tests for frontend quota state and execution guards."""

import unittest
from datetime import UTC, datetime, timedelta

from models.quota import QuotaLevel, QuotaStatus
from services.quota_service import QuotaService


class StaticQuotaService(QuotaService):
    def __init__(self, quotas: list[QuotaStatus]) -> None:
        self.quotas = quotas

    def list_quotas(self) -> list[QuotaStatus]:
        return self.quotas


class QuotaStatusTests(unittest.TestCase):
    def test_warning_threshold_and_remaining(self) -> None:
        quota = QuotaStatus("Gemini", "Daily requests", 850, 1000)
        self.assertEqual(quota.level, QuotaLevel.WARNING)
        self.assertEqual(quota.remaining, 150)
        self.assertEqual(quota.usage_percent, 85)

    def test_exhausted_quota_blocks_execution(self) -> None:
        reset_at = datetime.now(UTC) + timedelta(minutes=10)
        service = StaticQuotaService(
            [QuotaStatus("Gemini", "Daily requests", 1000, 1000, reset_at=reset_at)]
        )

        decision = service.can_execute("gemini")

        self.assertFalse(decision.allowed)
        self.assertIn("exhausted", decision.reason or "")
        self.assertGreater(decision.retry_after or 0, 0)

    def test_available_provider_allows_execution(self) -> None:
        service = StaticQuotaService(
            [QuotaStatus("OpenAI", "Monthly tokens", 100, 1000, unit="tokens")]
        )
        self.assertTrue(service.can_execute("openai").allowed)

    def test_unknown_provider_is_blocked_until_quota_is_known(self) -> None:
        service = StaticQuotaService(
            [QuotaStatus("OpenAI", "Monthly tokens", 100, 1000, unit="tokens")]
        )
        decision = service.can_execute("gemini")
        self.assertFalse(decision.allowed)
        self.assertIn("unavailable", decision.reason or "")


if __name__ == "__main__":
    unittest.main()
