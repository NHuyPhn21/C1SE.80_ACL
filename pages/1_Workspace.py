"""Workspace page: Project management, series dashboard, and member role assignment."""

import streamlit as st

from utils.auth_session import logout, require_auth


user = require_auth()

header, actions = st.columns([5, 1])
with header:
    st.title("Projects Workspace")
    st.caption(f"Signed in as **{user.full_name}** ({user.email}) • Role: `{user.role.upper()}`")
with actions:
    if st.button("Log out", type="secondary", use_container_width=True):
        logout()
        st.switch_page("pages/0_Login.py")

st.markdown("---")

col_title, col_btn = st.columns([4, 1])
with col_title:
    st.subheader("Your Localization Projects")
with col_btn:
    if st.button("+ Create New Project", type="primary", use_container_width=True):
        st.session_state["show_create_modal"] = True

# Projects Grid
p1, p2, p3 = st.columns(3)

with p1:
    with st.container(border=True):
        st.markdown("### Shonen Weekly #112")
        st.caption("24 pages • Japanese ➔ Vietnamese")
        st.markdown("Status: :orange[**In review**]")
        st.markdown("Team: `PH`, `PQ`, `TH`")
        if st.button("Open Review Studio", key="proj_1", use_container_width=True):
            st.switch_page("pages/3_Review_Studio.py")

with p2:
    with st.container(border=True):
        st.markdown("### One Piece — Ch. 1115")
        st.caption("19 pages • Japanese ➔ Vietnamese")
        st.markdown("Status: :blue[**Inpainting**]")
        st.markdown("Team: `PH`, `QN`")
        if st.button("Open Chapter Studio", key="proj_2", use_container_width=True):
            st.switch_page("pages/2_Chapter_Studio.py")

with p3:
    with st.container(border=True):
        st.markdown("### Jujutsu Kaisen — Special")
        st.caption("32 pages • English ➔ Vietnamese")
        st.markdown("Status: :green[**Completed**]")
        st.markdown("Team: `All members`")
        if st.button("View Queue & Export", key="proj_3", use_container_width=True):
            st.switch_page("pages/5_Queue_Monitor.py")

st.markdown("---")
st.subheader("Quick Navigation")
nav1, nav2, nav3, nav4 = st.columns(4)
with nav1:
    if st.button("☁️ Chapter Studio", use_container_width=True):
        st.switch_page("pages/2_Chapter_Studio.py")
with nav2:
    if st.button("🔍 Review Studio", use_container_width=True):
        st.switch_page("pages/3_Review_Studio.py")
with nav3:
    if st.button("✍️ Typesetting", use_container_width=True):
        st.switch_page("pages/4_Typesetting.py")
with nav4:
    if st.button("⏱️ Queue Monitor", use_container_width=True):
        st.switch_page("pages/5_Queue_Monitor.py")
