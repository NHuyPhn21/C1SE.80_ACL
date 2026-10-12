"""Frontend service adapters."""

from services.auth_service import AuthServiceError, get_auth_service

__all__ = ["AuthServiceError", "get_auth_service"]
