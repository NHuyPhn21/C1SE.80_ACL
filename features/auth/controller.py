"""Coordinate auth UI actions, service calls, session state, and navigation."""

from typing import Any

import streamlit as st

from components.auth import render_auth_ui
from services.auth_service import AuthServiceError, get_auth_service
from utils.auth_session import (
    establish_session,
    is_authenticated,
    pop_auth_error,
    set_auth_error,
)


def render_auth_page(initial_view: str) -> None:
    if st.query_params.get("logout") == "1":
        from utils.auth_session import logout
        logout()

    if is_authenticated() and not st.session_state.get("auth.logged_out"):
        st.switch_page("pages/1_Workspace.py")
        return

    action = render_auth_ui(initial_view=initial_view, error=pop_auth_error())
    if not action:
        return

    kind = action.get("kind")
    if kind == "navigate":
        _navigate(str(action.get("view", "login")))
    elif kind == "login":
        _login(action)
    elif kind == "register":
        _register(action)


def _login(action: dict[str, Any]) -> None:
    email = str(action.get("email", "")).strip()
    password = str(action.get("password", ""))
    remember_me = bool(action.get("rememberMe", False))

    try:
        result = get_auth_service().login(email, password, remember_me)
    except AuthServiceError as exc:
        _show_error(str(exc))
        return

    establish_session(result, remember_me=remember_me)
    st.switch_page("pages/1_Workspace.py")


def _register(action: dict[str, Any]) -> None:
    full_name = str(action.get("fullName", "")).strip()
    email = str(action.get("email", "")).strip()
    password = str(action.get("password", ""))
    confirm_password = str(action.get("confirmPassword", ""))

    if password != confirm_password:
        _show_error("Passwords do not match. Please re-enter your password.")
        return
    if not bool(action.get("acceptedTerms", False)):
        _show_error("Please accept the Terms of Service and Privacy Policy.")
        return

    try:
        result = get_auth_service().register(full_name, email, password)
    except AuthServiceError as exc:
        _show_error(str(exc))
        return

    establish_session(result)
    st.switch_page("pages/1_Workspace.py")


def _navigate(view: str) -> None:
    page = "pages/0_Register.py" if view == "register" else "pages/0_Login.py"
    st.switch_page(page)


def _show_error(message: str) -> None:
    set_auth_error(message)
    st.rerun()
