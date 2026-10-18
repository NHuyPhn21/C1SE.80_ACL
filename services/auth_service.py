"""Replaceable authentication adapters for mock and HTTP backends."""

from __future__ import annotations

import os
import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Mapping

import requests
from dotenv import load_dotenv

from models.auth import AuthResult, AuthTokens, User
from models.api_error import ApiError
from services.error_handler import from_exception, from_http_response


load_dotenv()


class AuthServiceError(RuntimeError):
    """A user-safe authentication failure."""

    def __init__(self, message: str, api_error: ApiError | None = None) -> None:
        super().__init__(message)
        self.api_error = api_error


@dataclass(frozen=True)
class AuthApiConfig:
    base_url: str
    login_path: str = "/auth/login"
    register_path: str = "/auth/register"
    refresh_path: str = "/auth/refresh"
    logout_path: str = "/auth/logout"
    timeout: float = 10.0
    login_identifier_field: str = "email"
    register_name_field: str = "username"

    @classmethod
    def from_environment(cls) -> "AuthApiConfig":
        base_url = os.getenv("AUTH_API_BASE_URL", "").strip()
        if not base_url:
            raise AuthServiceError(
                "AUTH_API_BASE_URL is required when AUTH_BACKEND_MODE=api."
            )

        try:
            timeout = float(os.getenv("AUTH_API_TIMEOUT", "10"))
        except ValueError as exc:
            raise AuthServiceError("AUTH_API_TIMEOUT must be a number.") from exc
        if timeout <= 0:
            raise AuthServiceError("AUTH_API_TIMEOUT must be greater than zero.")

        return cls(
            base_url=base_url.rstrip("/"),
            login_path=_environment_path("AUTH_LOGIN_PATH", "/auth/login"),
            register_path=_environment_path("AUTH_REGISTER_PATH", "/auth/register"),
            refresh_path=_environment_path("AUTH_REFRESH_PATH", "/auth/refresh"),
            logout_path=_environment_path("AUTH_LOGOUT_PATH", "/auth/logout"),
            timeout=timeout,
            login_identifier_field=_environment_field(
                "AUTH_LOGIN_IDENTIFIER_FIELD", "email"
            ),
            register_name_field=_environment_field(
                "AUTH_REGISTER_NAME_FIELD", "username"
            ),
        )


class AuthService(ABC):
    @abstractmethod
    def login(self, email: str, password: str, remember_me: bool) -> AuthResult:
        raise NotImplementedError

    @abstractmethod
    def register(self, full_name: str, email: str, password: str) -> AuthResult:
        raise NotImplementedError

    @abstractmethod
    def logout(self, access_token: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def refresh(self, refresh_token: str) -> AuthTokens:
        raise NotImplementedError


class HttpAuthService(AuthService):
    """HTTP adapter for the configured backend authentication contract."""

    def __init__(
        self,
        config: AuthApiConfig,
        client: requests.Session | None = None,
    ) -> None:
        self.config = config
        self.client = client or requests.Session()

    def login(self, email: str, password: str, remember_me: bool) -> AuthResult:
        payload = self._request(
            "POST",
            self.config.login_path,
            json={
                self.config.login_identifier_field: email,
                "password": password,
                "remember_me": remember_me,
            },
        )
        return self._auth_result(payload)

    def register(self, full_name: str, email: str, password: str) -> AuthResult:
        payload = self._request(
            "POST",
            self.config.register_path,
            json={
                self.config.register_name_field: full_name,
                "email": email,
                "password": password,
            },
        )
        return self._auth_result(payload)

    def logout(self, access_token: str) -> None:
        self._request(
            "POST", self.config.logout_path, access_token=access_token, allow_empty=True
        )

    def refresh(self, refresh_token: str) -> AuthTokens:
        payload = self._request(
            "POST",
            self.config.refresh_path,
            json={"refresh_token": refresh_token},
        )
        data = payload.get("data", payload)
        if not isinstance(data, Mapping):
            raise AuthServiceError("Invalid token response from authentication server.")
        token_payload = data.get("tokens", data)
        if not isinstance(token_payload, Mapping):
            raise AuthServiceError("Invalid token response from authentication server.")
        try:
            return AuthTokens.from_mapping(token_payload)
        except (KeyError, TypeError, ValueError) as exc:
            raise AuthServiceError(
                "Invalid token response from authentication server."
            ) from exc

    def _auth_result(self, payload: Mapping[str, Any]) -> AuthResult:
        try:
            return AuthResult.from_mapping(payload)
        except (KeyError, TypeError, ValueError) as exc:
            raise AuthServiceError(
                "Invalid response from authentication server."
            ) from exc

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Mapping[str, Any] | None = None,
        access_token: str | None = None,
        allow_empty: bool = False,
    ) -> Mapping[str, Any]:
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        try:
            response = self.client.request(
                method,
                f"{self.config.base_url}{path}",
                json=json,
                headers=headers,
                timeout=self.config.timeout,
            )
        except requests.RequestException as exc:
            error = from_exception(exc)
            raise AuthServiceError(error.message, api_error=error) from exc

        if not response.ok:
            error = from_http_response(response)
            raise AuthServiceError(error.message, api_error=error)
        payload = _response_payload(response, allow_empty=allow_empty)
        return payload


class MockAuthService(AuthService):
    """Development adapter used until the backend endpoints are available."""

    def login(self, email: str, password: str, remember_me: bool) -> AuthResult:
        del remember_me
        _validate_credentials(email, password)
        return _mock_result(email=email)

    def register(self, full_name: str, email: str, password: str) -> AuthResult:
        _validate_credentials(email, password)
        return _mock_result(email=email, full_name=full_name)

    def logout(self, access_token: str) -> None:
        del access_token

    def refresh(self, refresh_token: str) -> AuthTokens:
        if not refresh_token:
            raise AuthServiceError("Your session has expired. Please sign in again.")
        return _mock_tokens()


@lru_cache(maxsize=1)
def get_auth_service() -> AuthService:
    """Return the configured adapter without coupling pages to its transport."""
    mode = os.getenv("AUTH_BACKEND_MODE", "mock").strip().lower()
    if mode == "mock":
        return MockAuthService()
    if mode != "api":
        raise AuthServiceError("AUTH_BACKEND_MODE must be either 'mock' or 'api'.")

    return HttpAuthService(config=AuthApiConfig.from_environment())


def _response_payload(
    response: requests.Response, *, allow_empty: bool = False
) -> Mapping[str, Any]:
    if not response.content:
        if allow_empty or response.ok:
            return {}
        raise AuthServiceError("Authentication server returned an empty response.")
    try:
        payload = response.json()
    except requests.ValueError as exc:
        raise AuthServiceError(
            "Authentication server returned an invalid response."
        ) from exc
    if not isinstance(payload, Mapping):
        raise AuthServiceError("Authentication server returned an invalid response.")
    return payload


def _environment_path(name: str, default: str) -> str:
    value = os.getenv(name, default).strip() or default
    return value if value.startswith("/") else f"/{value}"


def _environment_field(name: str, default: str) -> str:
    value = os.getenv(name, default).strip()
    if not value:
        raise AuthServiceError(f"{name} cannot be empty.")
    return value


def _validate_credentials(email: str, password: str) -> None:
    if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
        raise AuthServiceError("Please enter a valid email address.")
    if len(password) < 8:
        raise AuthServiceError("Password must contain at least 8 characters.")


def _mock_result(email: str, full_name: str | None = None) -> AuthResult:
    return AuthResult(
        user=User(
            id=f"mock:{email.lower()}",
            email=email.lower(),
            full_name=full_name or email.split("@", 1)[0].replace(".", " ").title(),
            role="editor",
        ),
        tokens=_mock_tokens(),
    )


def _mock_tokens() -> AuthTokens:
    return AuthTokens(
        access_token=f"mock_access_{secrets.token_urlsafe(24)}",
        refresh_token=f"mock_refresh_{secrets.token_urlsafe(24)}",
        expires_in=3600,
    )
