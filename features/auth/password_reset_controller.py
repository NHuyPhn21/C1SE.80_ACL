"""Coordinate password-reset UI, token validation, and delivery."""

from __future__ import annotations

import os
from urllib.parse import quote

import streamlit as st

from components.auth import render_password_reset_ui
from services.auth_service import AuthServiceError, get_auth_service
from services.password_reset_mailer import (
    PasswordResetDeliveryError,
    ensure_password_reset_delivery_ready,
    send_password_reset_email,
)


SENT_KEY = "auth.password_reset.sent"
ERROR_KEY = "auth.password_reset.error"
COMPLETE_KEY = "auth.password_reset.complete"


def render_password_reset_page() -> None:
    token = str(st.query_params.get("token", "")).strip()
    service = get_auth_service()
    token_valid = service.verify_password_reset_token(token) if token else False

    action = render_password_reset_ui(
        has_token=bool(token),
        token_valid=token_valid,
        sent=bool(st.session_state.get(SENT_KEY, False)),
        completed=bool(st.session_state.get(COMPLETE_KEY, False)),
        error=st.session_state.pop(ERROR_KEY, None),
    )
    if not action:
        return

    kind = action.get("kind")
    if kind == "navigate_login":
        _clear_reset_state()
        st.query_params.clear()
        st.switch_page("pages/0_Login.py")
    elif kind == "request_reset":
        _request_reset(str(action.get("email", "")).strip())
    elif kind == "reset_password":
        _reset_password(
            token,
            str(action.get("password", "")),
            str(action.get("confirmPassword", "")),
        )


def _request_reset(email: str) -> None:
    st.session_state.pop(SENT_KEY, None)
    try:
        ensure_password_reset_delivery_ready()
        token = get_auth_service().request_password_reset(email)
    except (AuthServiceError, PasswordResetDeliveryError) as exc:
        st.session_state[ERROR_KEY] = str(exc)
        st.rerun()
        return

    if token:
        link = _reset_link(token)
        try:
            send_password_reset_email(email, link)
        except PasswordResetDeliveryError as exc:
            get_auth_service().discard_password_reset_token(token)
            st.session_state[ERROR_KEY] = str(exc)
            st.rerun()
            return

    # Use the same response for registered and unknown addresses.
    st.session_state[SENT_KEY] = True
    st.rerun()


def _reset_password(token: str, password: str, confirmation: str) -> None:
    if password != confirmation:
        st.session_state[ERROR_KEY] = "Passwords do not match. Please try again."
        st.rerun()
        return
    try:
        get_auth_service().reset_password(token, password)
    except AuthServiceError as exc:
        st.session_state[ERROR_KEY] = str(exc)
        st.rerun()
        return

    st.session_state[COMPLETE_KEY] = True
    st.session_state.pop(SENT_KEY, None)
    st.rerun()


def _reset_link(token: str) -> str:
    base_url = os.getenv("APP_BASE_URL", "http://localhost:8501").strip().rstrip("/")
    return f"{base_url}/forgot-password?token={quote(token, safe='')}"


def _clear_reset_state() -> None:
    for key in (SENT_KEY, ERROR_KEY, COMPLETE_KEY):
        st.session_state.pop(key, None)

