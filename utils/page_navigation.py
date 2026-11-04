"""Native Streamlit navigation controls for sidebar matching Login brand & Stitch UX/UI design (100% Native)."""

import streamlit as st


def render_page_navigation() -> None:
    """Render sleek left sidebar navigation matching Login brand navy theme using native Streamlit."""
    st.markdown(
        """
        <style>
        /* Hide default Streamlit auto-generated page list */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        
        /* Custom Sidebar: Deep Navy Background synced with Login Brand Panel (#25326f) */
        [data-testid="stSidebar"] {
            display: block !important;
            visibility: visible !important;
            transform: none !important;
            background-color: #25326F !important;
            border-right: 1px solid rgba(255, 255, 255, 0.12) !important;
            width: 250px !important;
            min-width: 250px !important;
        }
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.5rem !important;
            padding-left: 1.1rem !important;
            padding-right: 1.1rem !important;
            background-color: #25326F !important;
        }
        [data-testid="stSidebarCollapseButton"] button,
        [data-testid="stSidebarCollapseButton"] svg {
            color: rgba(255, 255, 255, 0.7) !important;
            fill: rgba(255, 255, 255, 0.7) !important;
        }
        [data-testid="stSidebarCollapseButton"] button:hover {
            color: #FFFFFF !important;
            background: rgba(255, 255, 255, 0.15) !important;
        }
        
        /* Brand Header in Sidebar matching Login Screen */
        .sidebar-brand-box {
            padding: 0.5rem 0.5rem 2rem 0.5rem;
        }
        .sidebar-brand-logo {
            display: flex;
            align-items: baseline;
            gap: 4px;
        }
        .sidebar-brand-title {
            font-size: 28px;
            font-weight: 900;
            color: #FFFFFF;
            letter-spacing: -0.03em;
        }
        .sidebar-brand-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #38BDF8;
            margin-bottom: 2px;
            box-shadow: 0 0 10px #38BDF8;
        }
        .sidebar-brand-sub {
            font-size: 11px;
            font-weight: 500;
            color: rgba(255, 255, 255, 0.75);
            margin-top: 4px;
            letter-spacing: 0.02em;
        }
        
        /* Style native page links in sidebar */
        [data-testid="stSidebar"] div.stPageLink {
            margin-bottom: 8px;
        }
        [data-testid="stSidebar"] div.stPageLink a {
            border-radius: 9999px !important;
            padding: 10px 18px !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            color: rgba(255, 255, 255, 0.82) !important;
            background-color: transparent !important;
            transition: all 0.18s ease !important;
            text-decoration: none !important;
            display: flex !important;
            align-items: center !important;
            gap: 12px !important;
        }
        [data-testid="stSidebar"] div.stPageLink a p,
        [data-testid="stSidebar"] div.stPageLink a span {
            color: rgba(255, 255, 255, 0.82) !important;
        }
        [data-testid="stSidebar"] div.stPageLink a:hover {
            background-color: rgba(255, 255, 255, 0.14) !important;
            color: #FFFFFF !important;
        }
        [data-testid="stSidebar"] div.stPageLink a:hover p,
        [data-testid="stSidebar"] div.stPageLink a:hover span {
            color: #FFFFFF !important;
        }

        /* Active highlight for each page: Solid White Pill with Navy Text */
        [data-testid="stSidebar"] a[href*="Workspace"]:not([href*="Team"]),
        [data-testid="stSidebar"] a[href*="Team_Workspace"],
        [data-testid="stSidebar"] a[href*="Chapter_Studio"],
        [data-testid="stSidebar"] a[href*="Review_Studio"],
        [data-testid="stSidebar"] a[href*="Typesetting"],
        [data-testid="stSidebar"] a[href*="Queue_Monitor"],
        [data-testid="stSidebar"] a[href*="Settings"] {
            /* Fallback link styles */
        }

        /* Specific active style injected per page, e.g., Projects on Workspace */
        .active-nav-pill a {
            background-color: #FFFFFF !important;
            color: #25326F !important;
            font-weight: 800 !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25) !important;
        }
        .active-nav-pill a p,
        .active-nav-pill a span {
            color: #25326F !important;
            font-weight: 800 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand-box">
                <div class="sidebar-brand-logo">
                    <span class="sidebar-brand-title">ACL</span>
                    <span class="sidebar-brand-dot"></span>
                </div>
                <div class="sidebar-brand-sub">Automated Comic Localization</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.page_link("pages/1_Workspace.py", label="Projects", icon="📁")
        st.page_link("pages/1_Team_Workspace.py", label="Team Roles", icon="👥")
        st.page_link("pages/2_Chapter_Studio.py", label="Chapter Studio", icon="☁️")
        st.page_link("pages/2_Review_Studio.py", label="Review Studio", icon="📖")
        st.page_link("pages/4_Typesetting.py", label="Typesetting", icon="✏️")
        st.page_link("pages/5_Queue_Monitor.py", label="Queue Monitor", icon="🕒")
        st.page_link("pages/3_Settings.py", label="Personal Settings", icon="⚙️")
