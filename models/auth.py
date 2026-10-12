"""Typed authentication data exchanged between the UI and auth services."""

from dataclasses import asdict, dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class User:
    id: str
    email: str
    full_name: str
    role: str = "member"

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "User":
        return cls(
            id=str(payload.get("id") or payload.get("user_id") or payload["email"]),
            email=str(payload["email"]),
            full_name=str(
                payload.get("full_name")
                or payload.get("fullName")
                or payload.get("name")
                or payload["email"].split("@", 1)[0]
            ),
            role=str(payload.get("role") or "member"),
        )

    def to_session(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AuthTokens:
    access_token: str
    refresh_token: str | None = None
    expires_in: int | None = None

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "AuthTokens":
        return cls(
            access_token=str(payload.get("access_token") or payload["accessToken"]),
            refresh_token=payload.get("refresh_token") or payload.get("refreshToken"),
            expires_in=_optional_int(
                payload.get("expires_in") or payload.get("expiresIn")
            ),
        )


@dataclass(frozen=True)
class AuthResult:
    user: User
    tokens: AuthTokens

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "AuthResult":
        data = payload.get("data", payload)
        if not isinstance(data, Mapping):
            raise ValueError("Authentication response must be a JSON object")

        user_payload = data.get("user")
        if not isinstance(user_payload, Mapping):
            raise ValueError("Authentication response is missing user data")

        token_payload = data.get("tokens", data)
        if not isinstance(token_payload, Mapping):
            raise ValueError("Authentication response is missing token data")

        return cls(
            user=User.from_mapping(user_payload),
            tokens=AuthTokens.from_mapping(token_payload),
        )


def _optional_int(value: Any) -> int | None:
    return int(value) if value is not None else None
