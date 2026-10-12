"""Replaceable authentication adapters for mock and HTTP backends."""

from __future__ import annotations

import os
import secrets
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Any, Mapping

import requests

from models.auth import AuthResult, AuthTokens, User


class AuthServiceError(RuntimeError):
    """A user-safe authentication failure."""


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
    """HTTP adapter matching the future backend authentication contract."""

    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = requests.Session()

    def login(self, email: str, password: str, remember_me: bool) -> AuthResult:
        payload = self._request(
            "POST",
            "/auth/login",
            json={
                "email": email,
                "password": password,
                "remember_me": remember_me,
            },
        )
        return self._auth_result(payload)

    def register(self, full_name: str, email: str, password: str) -> AuthResult:
        payload = self._request(
            "POST",
            "/auth/register",
            json={"full_name": full_name, "email": email, "password": password},
        )
        return self._auth_result(payload)

    def logout(self, access_token: str) -> None:
        self._request("POST", "/auth/logout", access_token=access_token)

    def refresh(self, refresh_token: str) -> AuthTokens:
        payload = self._request(
            "POST", "/auth/refresh", json={"refresh_token": refresh_token}
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
    ) -> Mapping[str, Any]:
        headers = {"Accept": "application/json"}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        try:
            response = self.client.request(
                method,
                f"{self.base_url}{path}",
                json=json,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise AuthServiceError(
                "Authentication service is unavailable. Please try again."
            ) from exc

        payload = _response_payload(response)
        if not response.ok:
            message = payload.get("message") or payload.get("detail")
            raise AuthServiceError(
                str(message or "Authentication request was rejected.")
            )
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

    base_url = os.getenv("AUTH_API_BASE_URL", "").strip()
    if not base_url:
        raise AuthServiceError(
            "AUTH_API_BASE_URL is required when AUTH_BACKEND_MODE=api."
        )
    return HttpAuthService(base_url=base_url)


def _response_payload(response: requests.Response) -> Mapping[str, Any]:
    if not response.content:
        return {}
    try:
        payload = response.json()
    except requests.ValueError as exc:
        raise AuthServiceError(
            "Authentication server returned an invalid response."
        ) from exc
    if not isinstance(payload, Mapping):
        raise AuthServiceError("Authentication server returned an invalid response.")
    return payload


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
