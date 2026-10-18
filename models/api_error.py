"""Normalized API errors consumed by the Streamlit frontend."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping


class ApiErrorCode(StrEnum):
    NETWORK = "NETWORK_ERROR"
    TIMEOUT = "TIMEOUT"
    VALIDATION = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    RATE_LIMITED = "RATE_LIMITED"
    SERVER = "SERVER_ERROR"
    INVALID_RESPONSE = "INVALID_RESPONSE"
    UNKNOWN = "UNKNOWN_ERROR"


@dataclass(frozen=True)
class ApiError:
    code: ApiErrorCode
    message: str
    status_code: int | None = None
    retryable: bool = False
    retry_after: int | None = None
    field_errors: Mapping[str, str] = field(default_factory=dict)

    @property
    def retry_message(self) -> str | None:
        if self.retry_after is not None:
            return f"Try again in {self.retry_after} seconds."
        if self.retryable:
            return "Please try again in a moment."
        return None


class FrontendApiError(RuntimeError):
    """Exception carrying a safe, display-ready API error."""

    def __init__(self, error: ApiError) -> None:
        super().__init__(error.message)
        self.error = error
