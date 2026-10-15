"""ACL application entry point and dynamic page router."""

import streamlit as st

from utils.auth_session import current_user, is_authenticated, logout


authenticated = is_authenticated()

st.set_page_config(
    page_title="ACL - Automated Comic Localization",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded" if authenticated else "collapsed",
)

st.markdown(
    """
    <style>
        #MainMenu, footer, [data-testid="stToolbar"],
        [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
            display: none !important;
        }
        html, body, [data-testid="stAppViewContainer"], .stApp {
            background: #f7faf5;
        }
        [data-testid="stElementContainer"] {
            width: 100% !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if authenticated:
    user = current_user()
    if user is not None:
        with st.sidebar:
            st.markdown(
                f"""
                <div style="padding: 12px; background: #ffffff; border: 1px solid #e4dfd6; border-radius: 12px; margin-bottom: 12px;">
                    <div style="font-weight: 700; color: #25326f; font-size: 15px;">📚 ACL Studio</div>
                    <div style="font-size: 13px; color: #1c1a17; margin-top: 4px; font-weight: 600;">{user.full_name}</div>
                    <div style="font-size: 11px; color: #71689f;">{user.email}</div>
                    <span style="display: inline-block; background: #e7eaf5; color: #25326f; padding: 2px 8px; border-radius: 999px; font-size: 10px; font-weight: 600; margin-top: 6px;">
                        {user.role.upper()}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Log out", key="sidebar_logout_btn", type="secondary", use_container_width=True):
                logout()
                st.switch_page("pages/0_Login.py")

    pages = {
        "Localization Studio": [
            st.Page("pages/1_Workspace.py", title="Projects Workspace", icon="📁", url_path="workspace", default=True),
            st.Page("pages/2_Chapter_Studio.py", title="Chapter Studio", icon="☁️", url_path="chapter-studio"),
            st.Page("pages/3_Review_Studio.py", title="Review Studio", icon="🔍", url_path="review-studio"),
            st.Page("pages/4_Typesetting.py", title="Typesetting", icon="✍️", url_path="typesetting"),
            st.Page("pages/5_Queue_Monitor.py", title="Queue Monitor", icon="⏱️", url_path="queue-monitor"),
        ],
        "Configuration": [
            st.Page("pages/6_Settings.py", title="Personal Settings", icon="⚙️", url_path="settings"),
        ],
    }
    navigation = st.navigation(pages, position="sidebar")
else:
    # Unauthenticated state: Lock and hide all internal studio pages
    pages = [
        st.Page("pages/0_Login.py", title="Log in", url_path="login", default=True),
        st.Page("pages/0_Register.py", title="Register", url_path="register"),
    ]
    navigation = st.navigation(pages, position="hidden")

navigation.run()