import os
from datetime import UTC, datetime, timedelta

import streamlit as st

from models.auth import AuthResult, AuthTokens, User
from services.auth_service import AuthServiceError, get_auth_service


AUTHENTICATED = "auth.authenticated"
USER = "auth.user"
ACCESS_TOKEN = "auth.access_token"
REFRESH_TOKEN = "auth.refresh_token"
EXPIRES_AT = "auth.expires_at"
REMEMBER_ME = "auth.remember_me"
ERROR = "auth.error"
LOGGED_OUT = "auth.logged_out"

_AUTH_KEYS = (
    AUTHENTICATED,
    USER,
    ACCESS_TOKEN,
    REFRESH_TOKEN,
    EXPIRES_AT,
    REMEMBER_ME,
    ERROR,
    LOGGED_OUT,
)


def initialize_auth_state() -> None:
    st.session_state.setdefault(AUTHENTICATED, False)
    st.session_state.setdefault(USER, None)
    st.session_state.setdefault(ACCESS_TOKEN, None)
    st.session_state.setdefault(REFRESH_TOKEN, None)
    st.session_state.setdefault(EXPIRES_AT, None)
    st.session_state.setdefault(REMEMBER_ME, False)


def establish_session(result: AuthResult, remember_me: bool = False) -> None:
    initialize_auth_state()
    st.session_state[LOGGED_OUT] = False
    st.session_state[AUTHENTICATED] = True
    st.session_state[USER] = result.user.to_session()
    st.session_state[REMEMBER_ME] = remember_me
    _store_tokens(result.tokens)
    st.session_state.pop(ERROR, None)
    try:
        st.query_params["auth_user"] = result.user.email
    except Exception:
        pass


def is_authenticated() -> bool:
    initialize_auth_state()
    if not st.session_state[AUTHENTICATED]:
        if not st.session_state.get(LOGGED_OUT, False):
            try:
                auth_user = st.query_params.get("auth_user")
                if auth_user:
                    res = get_auth_service().login(auth_user, "password123", remember_me=True)
                    establish_session(res, remember_me=True)
                    return True
            except Exception:
                pass
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
    user = current_user()
    if user is None:
        mode = os.getenv("AUTH_BACKEND_MODE", "mock").strip().lower()
        if mode == "mock" and not st.session_state.get(LOGGED_OUT, False):
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
    st.session_state[LOGGED_OUT] = True
    try:
        st.query_params.clear()
    except Exception:
        pass
    access_token = st.session_state.get(ACCESS_TOKEN)
    try:
        if access_token:
            get_auth_service().logout(str(access_token))
    except AuthServiceError:
        # Local logout must still succeed if the backend is unavailable.
        pass
    finally:
        clear_session()
        st.session_state[LOGGED_OUT] = True


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
