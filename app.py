"""ACL - Automated Comic Localization (Streamlit Native Application)."""

from __future__ import annotations

import streamlit as st

from backend.database import init_db
from utils.auth_session import current_user, initialize_auth_state, is_authenticated, logout

# 1. Initialize SQLite Database Tables on Launch
init_db()
initialize_auth_state()

# 2. Page Configuration
st.set_page_config(
    page_title="ACL - Automated Comic Localization",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 3. Global CSS (Sora, Plus Jakarta Sans, JetBrains Mono, Exact Stitch Tokens)
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #1C1A17;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Sora', sans-serif !important;
        color: #1C1A17;
    }
    
    .stApp {
        background-color: #F4F7F2 !important;
    }

    /* Clean Streamlit header & default elements */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    footer {
        display: none !important;
    }
    
    /* Primary Pill Buttons matching Stitch */
    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button[kind="primary"],
    div.stFormSubmitButton > button {
        background-color: #25326F !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 999px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.2s ease-in-out !important;
    }
    div.stButton > button[kind="primary"]:hover,
    div.stFormSubmitButton > button[kind="primary"]:hover,
    div.stFormSubmitButton > button:hover {
        background-color: #1B2856 !important;
        box-shadow: 0 4px 14px rgba(37, 50, 111, 0.35) !important;
        transform: translateY(-1px) !important;
    }
</style>
""", unsafe_allow_html=True)

# 4. Multi-Page Definition
login_page = st.Page("pages/0_Login.py", title="Sign In", icon="🔐", default=True, url_path="login")
register_page = st.Page("pages/0_Register.py", title="Create Account", icon="📝", url_path="register")
forgot_pw_page = st.Page("pages/0_Forgot_Password.py", title="Forgot Password", icon="🔑", url_path="forgot-password")

workspace_page = st.Page("pages/1_Workspace.py", title="Projects Workspace", icon="📁", url_path="workspace")
team_page = st.Page("pages/2_Team_Workspace.py", title="Team Workspace", icon="👥", url_path="team-workspace")
chapter_page = st.Page("pages/3_Chapter_Studio.py", title="Chapter Studio", icon="☁️", url_path="chapter-studio")
review_page = st.Page("pages/4_Review_Studio.py", title="Review Studio", icon="🔍", url_path="review-studio")
typesetting_page = st.Page("pages/5_Typesetting.py", title="Typesetting", icon="✍️", url_path="typesetting")
queue_page = st.Page("pages/6_Queue_Monitor.py", title="Queue Monitor", icon="⏱️", url_path="queue-monitor")
settings_page = st.Page("pages/7_Settings.py", title="Personal Settings", icon="⚙️", url_path="settings")

# 5. Dynamic Authentication Routing
user = current_user()

if is_authenticated() and user is not None:
    with st.sidebar:
        with st.container(border=True):
            st.markdown("### 📚 ACL Studio")
            st.markdown(f"**{user.full_name}**")
            st.caption(f"{user.email}")
            st.markdown(f":blue-background[**{user.role.upper()}**]")
        
        if st.button("Log out", key="sidebar_logout_btn", use_container_width=True):
            logout()
            st.rerun()

    nav = st.navigation({
        "Localization Studio": [workspace_page, team_page, chapter_page, review_page, typesetting_page, queue_page],
        "Configuration": [settings_page],
    }, position="sidebar")
else:
    nav = st.navigation([login_page, register_page, forgot_pw_page], position="hidden")

nav.run()
