"""Replaceable quota service with frontend mock data until an API exists."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta
from functools import lru_cache

from dotenv import load_dotenv

from models.quota import QuotaDecision, QuotaStatus


load_dotenv()


class QuotaService(ABC):
    @abstractmethod
    def list_quotas(self) -> list[QuotaStatus]:
        raise NotImplementedError

    def can_execute(self, provider: str | None = None) -> QuotaDecision:
        quotas = self.list_quotas()
        relevant = [
            quota
            for quota in quotas
            if provider is None or quota.provider.casefold() == provider.casefold()
        ]
        if not relevant:
            target = provider or "provider"
            return QuotaDecision(
                allowed=False,
                reason=f"Quota status is unavailable for {target}.",
            )
        exhausted = [quota for quota in relevant if not quota.is_available]
        if not exhausted:
            return QuotaDecision(allowed=True)

        blocked = exhausted[0]
        return QuotaDecision(
            allowed=False,
            reason=f"{blocked.provider} {blocked.metric} quota has been exhausted.",
            retry_after=blocked.seconds_until_reset,
        )


class MockQuotaService(QuotaService):
    """Preview quota state; replace with an HTTP adapter when backend is ready."""

    def list_quotas(self) -> list[QuotaStatus]:
        return [
            QuotaStatus(
                provider="Gemini",
                metric="Daily requests",
                used=_env_int("QUOTA_MOCK_GEMINI_USED", 920),
                limit=_env_int("QUOTA_MOCK_GEMINI_LIMIT", 1000),
                unit="requests",
                reset_at=_next_utc_midnight(),
            ),
            QuotaStatus(
                provider="OpenAI",
                metric="Monthly tokens",
                used=_env_int("QUOTA_MOCK_OPENAI_USED", 72_000),
                limit=_env_int("QUOTA_MOCK_OPENAI_LIMIT", 100_000),
                unit="tokens",
                reset_at=_next_month_start(),
            ),
        ]


@lru_cache(maxsize=1)
def get_quota_service() -> QuotaService:
    mode = os.getenv("QUOTA_BACKEND_MODE", "mock").strip().lower()
    if mode != "mock":
        raise RuntimeError(
            "Quota API is not available yet. Set QUOTA_BACKEND_MODE=mock."
        )
    return MockQuotaService()


def _env_int(name: str, default: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if value < 0:
        raise ValueError(f"{name} cannot be negative")
    return value


def _next_utc_midnight() -> datetime:
    now = datetime.now(UTC)
    tomorrow = now + timedelta(days=1)
    return tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)


def _next_month_start() -> datetime:
    now = datetime.now(UTC)
    if now.month == 12:
        return datetime(now.year + 1, 1, 1, tzinfo=UTC)
    return datetime(now.year, now.month + 1, 1, tzinfo=UTC)
