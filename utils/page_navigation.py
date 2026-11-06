"""ACL Page Navigation Utility (100% Native Streamlit — Zero iFrame).

Provides breadcrumb and navigation context across all studio pages.
"""

from __future__ import annotations

import streamlit as st


def render_page_navigation(active_item: str = "") -> None:
    """Render consistent page context and breadcrumbs without iFrames."""
    # Active navigation is managed natively via st.navigation in app.py.
    # This helper stores active state and provides optional breadcrumb context.
    if active_item:
        st.session_state["active_nav_item"] = active_item
