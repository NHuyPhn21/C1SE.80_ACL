"""Authentication state and route guards backed by Streamlit session state."""

from datetime import UTC, datetime, timedelta
import json
import os
from pathlib import Path

import streamlit as st

from models.auth import AuthResult, AuthTokens, User
from services.auth_service import AuthServiceError, get_auth_service

SESSION_FILE = Path(__file__).resolve().parents[1] / "data" / ".auth_session.json"

AUTHENTICATED = "auth.authenticated"
USER = "auth.user"
ACCESS_TOKEN = "auth.access_token"
REFRESH_TOKEN = "auth.refresh_token"
EXPIRES_AT = "auth.expires_at"
REMEMBER_ME = "auth.remember_me"
ERROR = "auth.error"

_AUTH_KEYS = (
    AUTHENTICATED,
    USER,
    ACCESS_TOKEN,
    REFRESH_TOKEN,
    EXPIRES_AT,
    REMEMBER_ME,
    ERROR,
)


def _save_persistent_session(user_dict: dict, tokens: AuthTokens, remember_me: bool) -> None:
    try:
        SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "authenticated": True,
            "user": user_dict,
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "expires_in": tokens.expires_in,
            "remember_me": remember_me,
            "saved_at": datetime.now(UTC).isoformat(),
        }
        SESSION_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except Exception:
        pass


def _clear_persistent_session() -> None:
    try:
        if SESSION_FILE.exists():
            SESSION_FILE.unlink(missing_ok=True)
    except Exception:
        pass


def _load_persistent_session() -> bool:
    try:
        if not SESSION_FILE.exists():
            return False
        content = SESSION_FILE.read_text(encoding="utf-8")
        data = json.loads(content)
        if not data.get("authenticated") or not data.get("user"):
            return False

        user_email = data["user"].get("email")
        if not user_email:
            return False

        # Verify against SQLite users table if using sqlite backend
        from backend.database import SessionLocal
        from backend.models import User as DbUser

        db = SessionLocal()
        try:
            db_u = db.query(DbUser).filter_by(email=user_email).first()
            if not db_u:
                _clear_persistent_session()
                return False
        finally:
            db.close()

        initialize_auth_state()
        st.session_state[AUTHENTICATED] = True
        st.session_state[USER] = data["user"]
        st.session_state[REMEMBER_ME] = bool(data.get("remember_me", False))
        tokens = AuthTokens(
            access_token=str(data.get("access_token") or "local_access_token"),
            refresh_token=data.get("refresh_token"),
            expires_in=data.get("expires_in") or 3600,
        )
        _store_tokens(tokens)
        return True
    except Exception:
        return False


def initialize_auth_state() -> None:
    st.session_state.setdefault(AUTHENTICATED, False)
    st.session_state.setdefault(USER, None)
    st.session_state.setdefault(ACCESS_TOKEN, None)
    st.session_state.setdefault(REFRESH_TOKEN, None)
    st.session_state.setdefault(EXPIRES_AT, None)
    st.session_state.setdefault(REMEMBER_ME, False)


def establish_session(result: AuthResult, remember_me: bool = False) -> None:
    initialize_auth_state()
    st.session_state[AUTHENTICATED] = True
    user_payload = result.user.to_session()
    st.session_state[USER] = user_payload
    st.session_state[REMEMBER_ME] = remember_me
    st.session_state["auth.logged_out"] = False
    _store_tokens(result.tokens)
    st.session_state.pop(ERROR, None)
    _save_persistent_session(user_payload, result.tokens, remember_me)


def is_authenticated() -> bool:
    initialize_auth_state()
    if not st.session_state[AUTHENTICATED]:
        if not st.session_state.get("auth.logged_out", False):
            if _load_persistent_session():
                return _refresh_if_needed()
        return False
    return _refresh_if_needed()


def current_user() -> User | None:
    if not is_authenticated():
        return None
    payload = st.session_state.get(USER)
    if not isinstance(payload, dict):
        clear_session()
        return None
    try:
        return User.from_mapping(payload)
    except (KeyError, TypeError, ValueError):
        clear_session()
        return None


def require_auth() -> User:
    if st.query_params.get("logout"):
        logout()
        st.query_params.pop("logout", None)
        st.switch_page("pages/0_Login.py")
        st.stop()

    user = current_user()
    if user is None:
        if not st.session_state.get("auth.logged_out", False):
            if _load_persistent_session():
                user = current_user()

    if user is None:
        mode = os.getenv("AUTH_BACKEND_MODE", "sqlite").strip().lower()
        if mode == "mock" and not st.session_state.get("auth.logged_out", False):
            try:
                auth_svc = get_auth_service()
                res = auth_svc.login("phanvanquann26@gmail.com", "password123", remember_me=True)
                establish_session(res, remember_me=True)
                user = current_user()
            except Exception:
                pass

        if user is None:
            st.switch_page("pages/0_Login.py")
            st.stop()
    return user


def logout() -> None:
    initialize_auth_state()
    access_token = st.session_state.get(ACCESS_TOKEN)
    try:
        if access_token:
            get_auth_service().logout(str(access_token))
    except AuthServiceError:
        # Local logout must still succeed if the backend is unavailable.
        pass
    finally:
        clear_session()
        _clear_persistent_session()
        st.session_state["auth.logged_out"] = True


def clear_session() -> None:
    for key in _AUTH_KEYS:
        st.session_state.pop(key, None)
    initialize_auth_state()


def set_auth_error(message: str) -> None:
    st.session_state[ERROR] = message


def pop_auth_error() -> str | None:
    error = st.session_state.pop(ERROR, None)
    return str(error) if error else None


def _refresh_if_needed() -> bool:
    expires_at = st.session_state.get(EXPIRES_AT)
    if not isinstance(expires_at, datetime):
        return bool(st.session_state.get(ACCESS_TOKEN))
    if datetime.now(UTC) < expires_at - timedelta(seconds=30):
        return True

    refresh_token = st.session_state.get(REFRESH_TOKEN)
    if not refresh_token:
        clear_session()
        return False

    try:
        tokens = get_auth_service().refresh(str(refresh_token))
    except AuthServiceError:
        clear_session()
        return False
    _store_tokens(tokens)
    return True


def _store_tokens(tokens: AuthTokens) -> None:
    st.session_state[ACCESS_TOKEN] = tokens.access_token
    if tokens.refresh_token:
        st.session_state[REFRESH_TOKEN] = tokens.refresh_token
    st.session_state[EXPIRES_AT] = (
        datetime.now(UTC) + timedelta(seconds=tokens.expires_in)
        if tokens.expires_in
        else None
    )
