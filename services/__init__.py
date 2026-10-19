"""Frontend service adapters."""

from services.auth_service import AuthServiceError, get_auth_service
from services.quota_service import get_quota_service

__all__ = ["AuthServiceError", "get_auth_service", "get_quota_service"]
