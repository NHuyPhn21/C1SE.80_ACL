"""Provider quota models shared by services and Streamlit pages."""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum


class QuotaLevel(StrEnum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EXHAUSTED = "exhausted"


@dataclass(frozen=True)
class QuotaStatus:
    provider: str
    metric: str
    used: int
    limit: int
    unit: str = "requests"
    reset_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.limit <= 0:
            raise ValueError("Quota limit must be greater than zero")
        if self.used < 0:
            raise ValueError("Quota usage cannot be negative")

    @property
    def remaining(self) -> int:
        return max(self.limit - self.used, 0)

    @property
    def usage_ratio(self) -> float:
        return min(self.used / self.limit, 1.0)

    @property
    def usage_percent(self) -> int:
        return round(self.usage_ratio * 100)

    @property
    def level(self) -> QuotaLevel:
        if self.used >= self.limit:
            return QuotaLevel.EXHAUSTED
        if self.usage_ratio >= 0.95:
            return QuotaLevel.CRITICAL
        if self.usage_ratio >= 0.80:
            return QuotaLevel.WARNING
        return QuotaLevel.NORMAL

    @property
    def is_available(self) -> bool:
        return self.remaining > 0

    @property
    def seconds_until_reset(self) -> int | None:
        if self.reset_at is None:
            return None
        reset_at = self.reset_at
        if reset_at.tzinfo is None:
            reset_at = reset_at.replace(tzinfo=UTC)
        return max(round((reset_at - datetime.now(UTC)).total_seconds()), 0)


@dataclass(frozen=True)
class QuotaDecision:
    allowed: bool
    reason: str | None = None
    retry_after: int | None = None
