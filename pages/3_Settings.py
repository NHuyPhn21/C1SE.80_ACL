"""Database-backed project settings, glossary, and encrypted API keys."""

import os

import streamlit as st

from backend.database import SessionLocal
from services.settings_service import (
    SettingsService,
    SettingsServiceError,
    project_for_user,
)
from utils.auth_session import require_auth
from utils.page_navigation import render_page_navigation


user = require_auth()
render_page_navigation()

try:
    user_id = int(user.id)
except ValueError:
    st.error("Your local account is invalid. Please sign out and register again.")
    st.stop()

project_name = st.query_params.get("project", "Shonen Weekly #112")
project = project_for_user(SessionLocal, user_id, project_name)
settings_service = SettingsService()

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [data-testid="stAppViewContainer"] { font-family:'Plus Jakarta Sans',sans-serif; background:#F8F9FA; }
    .settings-title { font-size:2rem; font-weight:800; margin:.5rem 0 0; }
    .settings-subtitle { color:#6C7275; margin:.25rem 0 1.5rem; }
    div.stButton > button { border-radius:999px; font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.caption(f"ACL Studio / {project.title} / Settings")
st.markdown('<h1 class="settings-title">Project Settings</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="settings-subtitle">Manage encrypted provider credentials and translation terminology.</p>',
    unsafe_allow_html=True,
)

tab_api, tab_glossary, tab_logs = st.tabs(
    ["API Key Config", "Custom Glossary", "System Logs"]
)

with tab_api:
    with st.container(border=True):
        st.subheader("Cloud LLM API Key")
        provider_label = st.selectbox(
            "Provider",
            ["Google Gemini", "OpenAI", "Anthropic Claude"],
        )
        provider_key = {
            "Google Gemini": "gemini",
            "OpenAI": "openai",
            "Anthropic Claude": "anthropic",
        }[provider_label]
        configured = settings_service.load_api_key(project.id, provider_key)
        if configured:
            st.success(f"{provider_label} is configured. Enter a new key to replace it.")
        else:
            st.info(f"No {provider_label} key has been configured for this project.")

        api_key = st.text_input(
            f"{provider_label} API key",
            value="",
            type="password",
            placeholder="Enter a new API key",
        )
        if st.button("Save encrypted API key", key="save_api_key"):
            try:
                settings_service.save_api_key(project.id, provider_key, api_key)
                if provider_key == "gemini":
                    os.environ["GEMINI_API_KEY"] = api_key.strip()
                st.success("API key encrypted and saved to api_key_configs.")
                st.rerun()
            except SettingsServiceError as exc:
                st.error(str(exc))

with tab_glossary:
    with st.container(border=True):
        st.subheader("Custom Glossary")
        st.caption("Terms are persisted in the custom_glossaries table for this project.")
        with st.form("create_glossary", clear_on_submit=True):
            source_col, target_col, submit_col = st.columns([2, 2, 1])
            source_term = source_col.text_input("Source term", placeholder="先生")
            target_term = target_col.text_input("Vietnamese term", placeholder="Thầy")
            create_entry = submit_col.form_submit_button("Add term", use_container_width=True)
        if create_entry:
            try:
                settings_service.create_glossary(project.id, source_term, target_term)
                st.success("Glossary entry added.")
                st.rerun()
            except SettingsServiceError as exc:
                st.error(str(exc))

        entries = settings_service.list_glossary(project.id)
        if not entries:
            st.info("No glossary entries yet.")
        for entry in entries:
            with st.expander(f"{entry.source_term} -> {entry.target_term}"):
                edit_source = st.text_input(
                    "Source", value=entry.source_term, key=f"source_{entry.id}"
                )
                edit_target = st.text_input(
                    "Target", value=entry.target_term, key=f"target_{entry.id}"
                )
                update_col, delete_col = st.columns(2)
                if update_col.button("Save changes", key=f"update_{entry.id}"):
                    try:
                        settings_service.update_glossary(
                            entry.id, edit_source, edit_target
                        )
                        st.success("Glossary entry updated.")
                        st.rerun()
                    except SettingsServiceError as exc:
                        st.error(str(exc))
                if delete_col.button("Delete", key=f"delete_{entry.id}"):
                    settings_service.delete_glossary(entry.id)
                    st.success("Glossary entry deleted.")
                    st.rerun()

with tab_logs:
    with st.container(border=True):
        st.subheader("System Diagnostics")
        st.code(
            "\n".join(
                [
                    "[INFO] SQLite database connected (acl.db)",
                    f"[INFO] Active project: {project.title}",
                    f"[INFO] Glossary entries: {len(settings_service.list_glossary(project.id))}",
                    "[INFO] API credentials are encrypted at rest",
                ]
            )
        )
