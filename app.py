"""ACL application entry point and page router."""

import streamlit as st


st.set_page_config(
    page_title="ACL - Automated Comic Localization",
    page_icon="ACL",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        #MainMenu, header, footer, [data-testid="stToolbar"],
        [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
            display: none !important;
        }
        html, body, [data-testid="stAppViewContainer"], .stApp {
            background: #f7faf5;
        }
        [data-testid="stAppViewBlockContainer"],
        [data-testid="stMainBlockContainer"],
        .stMainBlockContainer,
        .block-container {
            max-width: none;
            padding: 0 !important;
        }
        [data-testid="stMain"], [data-testid="stVerticalBlock"] {
            gap: 0 !important;
            margin: 0 !important;
        }
        [data-testid="stElementContainer"] {
            width: 100% !important;
        }
        iframe {
            display: block;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

pages = [
    st.Page("pages/0_Login.py", title="Log in", url_path="login", default=True),
    st.Page("pages/0_Register.py", title="Register", url_path="register"),
    st.Page("pages/1_Workspace.py", title="Workspace", url_path="workspace"),
    st.Page("pages/2_Review_Studio.py", title="Review Studio", url_path="review-studio"),
    st.Page("pages/3_Settings.py", title="Settings", url_path="settings"),
]

navigation = st.navigation(pages, position="hidden")
navigation.run()
