"""Workspace page."""

import streamlit as st

from utils.auth_session import logout, require_auth


user = require_auth()

header, actions = st.columns([5, 1])
with header:
    st.title("Workspace")
    st.caption(f"Signed in as {user.full_name} ({user.email})")
with actions:
    if st.button("Log out", type="secondary", use_container_width=True):
        logout()
        st.switch_page("pages/0_Login.py")
