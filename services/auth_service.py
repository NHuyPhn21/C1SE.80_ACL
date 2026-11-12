"""Replaceable authentication adapters for mock and HTTP backends."""

from __future__ import annotations

import os
import secrets
import hashlib
import hmac
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from typing import Any, Mapping

import requests
from dotenv import load_dotenv

from models.auth import AuthResult, AuthTokens, User
from models.api_error import ApiError
from services.error_handler import from_exception, from_http_response
from backend.database import SessionLocal, init_db
from backend.models import PasswordResetToken
from backend.models import User as DatabaseUser


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
    forgot_password_path: str = "/auth/forgot-password"
    verify_reset_token_path: str = "/auth/verify-reset-token"
    reset_password_path: str = "/auth/reset-password"
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
            forgot_password_path=_environment_path(
                "AUTH_FORGOT_PASSWORD_PATH", "/auth/forgot-password"
            ),
            verify_reset_token_path=_environment_path(
                "AUTH_VERIFY_RESET_TOKEN_PATH", "/auth/verify-reset-token"
            ),
            reset_password_path=_environment_path(
                "AUTH_RESET_PASSWORD_PATH", "/auth/reset-password"
            ),
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

    @abstractmethod
    def request_password_reset(self, email: str) -> str | None:
        """Request a reset and optionally return a local-development token."""
        raise NotImplementedError

    @abstractmethod
    def verify_password_reset_token(self, token: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def reset_password(self, token: str, new_password: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def discard_password_reset_token(self, token: str) -> None:
        """Invalidate a reset token when delivery cannot be completed."""
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

    def request_password_reset(self, email: str) -> str | None:
        _validate_email(email)
        payload = self._request(
            "POST", self.config.forgot_password_path, json={"email": email.strip()}
        )
        data = payload.get("data", payload)
        if isinstance(data, Mapping):
            token = data.get("reset_token") or data.get("token")
            return str(token) if token else None
        return None

    def verify_password_reset_token(self, token: str) -> bool:
        if not token:
            return False
        try:
            payload = self._request(
                "POST", self.config.verify_reset_token_path, json={"token": token}
            )
        except AuthServiceError:
            return False
        data = payload.get("data", payload)
        return bool(data.get("valid", True)) if isinstance(data, Mapping) else False

    def reset_password(self, token: str, new_password: str) -> None:
        _validate_password(new_password)
        if not token:
            raise AuthServiceError("This password reset link is invalid or has expired.")
        self._request(
            "POST",
            self.config.reset_password_path,
            json={"token": token, "new_password": new_password},
            allow_empty=True,
        )

    def discard_password_reset_token(self, token: str) -> None:
        # API backends own token delivery and invalidation.
        del token

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

    def __init__(self) -> None:
        self._reset_tokens: set[str] = set()

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

    def request_password_reset(self, email: str) -> str | None:
        _validate_email(email)
        token = secrets.token_urlsafe(32)
        self._reset_tokens.add(token)
        return token

    def verify_password_reset_token(self, token: str) -> bool:
        return token in self._reset_tokens

    def reset_password(self, token: str, new_password: str) -> None:
        _validate_password(new_password)
        if token not in self._reset_tokens:
            raise AuthServiceError("This password reset link is invalid or has expired.")
        self._reset_tokens.remove(token)

    def discard_password_reset_token(self, token: str) -> None:
        self._reset_tokens.discard(token)


class SqliteAuthService(AuthService):
    """Authenticate local Streamlit users against the ``users`` table."""

    def __init__(self, session_factory=SessionLocal, *, initialize_database: bool = True) -> None:
        if initialize_database:
            init_db()
        self.session_factory = session_factory

    def login(self, email: str, password: str, remember_me: bool) -> AuthResult:
        del remember_me
        _validate_credentials(email, password)
        normalized_email = email.strip().lower()
        db = self.session_factory()
        try:
            user = (
                db.query(DatabaseUser)
                .filter(DatabaseUser.email.ilike(normalized_email))
                .first()
            )
            if user is None or not verify_password(password, user.password_hash):
                raise AuthServiceError("Invalid email or password.")
            return _database_result(user)
        finally:
            db.close()

    def register(self, full_name: str, email: str, password: str) -> AuthResult:
        _validate_credentials(email, password)
        normalized_email = email.strip().lower()
        normalized_name = full_name.strip()
        if not normalized_name:
            raise AuthServiceError("Full name is required.")

        db = self.session_factory()
        try:
            existing = (
                db.query(DatabaseUser)
                .filter(DatabaseUser.email.ilike(normalized_email))
                .first()
            )
            if existing is not None:
                raise AuthServiceError("This email address is already registered.")

            user = DatabaseUser(
                username=normalized_name,
                email=normalized_email,
                password_hash=hash_password(password),
                role="USER",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return _database_result(user)
        except AuthServiceError:
            db.rollback()
            raise
        except Exception as exc:
            db.rollback()
            raise AuthServiceError("Unable to create the account.") from exc
        finally:
            db.close()

    def logout(self, access_token: str) -> None:
        del access_token

    def refresh(self, refresh_token: str) -> AuthTokens:
        if not refresh_token:
            raise AuthServiceError("Your session has expired. Please sign in again.")
        return _local_tokens()

    def request_password_reset(self, email: str) -> str | None:
        _validate_email(email)
        normalized_email = email.strip().lower()
        db = self.session_factory()
        try:
            user = (
                db.query(DatabaseUser)
                .filter(DatabaseUser.email.ilike(normalized_email))
                .first()
            )
            if user is None:
                return None

            now = _utc_now()
            db.query(PasswordResetToken).filter(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.used_at.is_(None),
            ).update({PasswordResetToken.used_at: now}, synchronize_session=False)

            token = secrets.token_urlsafe(32)
            db.add(
                PasswordResetToken(
                    user_id=user.id,
                    token_hash=_hash_reset_token(token),
                    expires_at=now + timedelta(minutes=15),
                )
            )
            db.commit()
            return token
        except Exception as exc:
            db.rollback()
            raise AuthServiceError("Unable to create a password reset request.") from exc
        finally:
            db.close()

    def verify_password_reset_token(self, token: str) -> bool:
        if not token:
            return False
        db = self.session_factory()
        try:
            reset = self._active_reset_token(db, token)
            return reset is not None
        finally:
            db.close()

    def reset_password(self, token: str, new_password: str) -> None:
        _validate_password(new_password)
        db = self.session_factory()
        try:
            reset = self._active_reset_token(db, token)
            if reset is None:
                raise AuthServiceError(
                    "This password reset link is invalid or has expired."
                )

            now = _utc_now()
            reset.user.password_hash = hash_password(new_password)
            db.query(PasswordResetToken).filter(
                PasswordResetToken.user_id == reset.user_id,
                PasswordResetToken.used_at.is_(None),
            ).update({PasswordResetToken.used_at: now}, synchronize_session=False)
            db.commit()
        except AuthServiceError:
            db.rollback()
            raise
        except Exception as exc:
            db.rollback()
            raise AuthServiceError("Unable to reset the password.") from exc
        finally:
            db.close()

    def discard_password_reset_token(self, token: str) -> None:
        if not token:
            return
        db = self.session_factory()
        try:
            reset = (
                db.query(PasswordResetToken)
                .filter(
                    PasswordResetToken.token_hash == _hash_reset_token(token),
                    PasswordResetToken.used_at.is_(None),
                )
                .first()
            )
            if reset is not None:
                reset.used_at = _utc_now()
                db.commit()
        except Exception as exc:
            db.rollback()
            raise AuthServiceError("Unable to invalidate the reset request.") from exc
        finally:
            db.close()

    @staticmethod
    def _active_reset_token(db: Any, token: str) -> PasswordResetToken | None:
        return (
            db.query(PasswordResetToken)
            .filter(
                PasswordResetToken.token_hash == _hash_reset_token(token),
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > _utc_now(),
            )
            .first()
        )


@lru_cache(maxsize=1)
def get_auth_service() -> AuthService:
    """Return the configured adapter without coupling pages to its transport."""
    mode = os.getenv("AUTH_BACKEND_MODE", "sqlite").strip().lower()
    if mode == "sqlite":
        return SqliteAuthService()
    if mode == "mock":
        return MockAuthService()
    if mode != "api":
        raise AuthServiceError(
            "AUTH_BACKEND_MODE must be 'sqlite', 'mock', or 'api'."
        )

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
    _validate_email(email)
    _validate_password(password)


def _validate_email(email: str) -> None:
    if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
        raise AuthServiceError("Please enter a valid email address.")


def _validate_password(password: str) -> None:
    if len(password) < 8:
        raise AuthServiceError("Password must contain at least 8 characters.")


def _hash_reset_token(token: str) -> str:
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        token.encode("utf-8"),
        b"acl-reset-token",
        120_000,
    )
    return digest.hex()


def _utc_now() -> datetime:
    """Return naive UTC for SQLite DateTime compatibility."""
    return datetime.now(UTC).replace(tzinfo=None)


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


def hash_password(password: str, *, iterations: int = 310_000) -> str:
    """Create a salted PBKDF2-SHA256 password hash using only the standard library."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded_hash: str) -> bool:
    try:
        algorithm, iterations_text, salt_hex, expected_hex = encoded_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            bytes.fromhex(salt_hex),
            int(iterations_text),
        )
        return hmac.compare_digest(actual, bytes.fromhex(expected_hex))
    except (TypeError, ValueError):
        return False


def _database_result(user: DatabaseUser) -> AuthResult:
    return AuthResult(
        user=User(
            id=str(user.id),
            email=user.email,
            full_name=user.username,
            role=user.role.lower(),
        ),
        tokens=_local_tokens(),
    )


def _local_tokens() -> AuthTokens:
    return AuthTokens(
        access_token=f"local_access_{secrets.token_urlsafe(24)}",
        refresh_token=f"local_refresh_{secrets.token_urlsafe(24)}",
        expires_in=3600,
    )
