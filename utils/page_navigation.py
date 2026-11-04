"""Native Streamlit navigation controls for pages rendered in HTML components."""

import streamlit as st


def render_page_navigation() -> None:
    """Render same-tab navigation links above the embedded page content."""
    st.markdown(
        """
        <style>
        [data-testid="acl-native-navigation"] {
            display: flex;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            background: #ffffff;
            border-bottom: 1px solid #e7e1dc;
        }
        [data-testid="acl-native-navigation"] a {
            color: #25326f;
            font-size: 0.75rem;
            font-weight: 600;
        }
        </style>
        <div data-testid="acl-native-navigation">
        """,
        unsafe_allow_html=True,
    )
    columns = st.columns(7)
    links = (
        ("Workspace", "pages/1_Workspace.py"),
        ("Team Roles", "pages/1_Team_Workspace.py"),
        ("Chapter Studio", "pages/2_Chapter_Studio.py"),
        ("Review Studio", "pages/2_Review_Studio.py"),
        ("Typesetting", "pages/4_Typesetting.py"),
        ("Queue Monitor", "pages/5_Queue_Monitor.py"),
        ("Settings", "pages/3_Settings.py"),
    )
    for column, (label, page) in zip(columns, links):
        with column:
            st.page_link(page, label=label)
    st.markdown("</div>", unsafe_allow_html=True)