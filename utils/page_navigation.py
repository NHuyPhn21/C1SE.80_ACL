"""Native Streamlit navigation controls for sidebar matching Stitch UX/UI design (100% Native)."""

import streamlit as st


def render_page_navigation() -> None:
    """Render sleek left sidebar navigation matching Stitch design using native Streamlit."""
    st.markdown(
        """
        <style>
        /* Hide default Streamlit auto-generated page list */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        
        /* Custom Sidebar Background and Width */
        [data-testid="stSidebar"] {
            display: block !important;
            visibility: visible !important;
            transform: none !important;
            background-color: #FFFFFF !important;
            border-right: 1px solid #EAEAEA !important;
            width: 250px !important;
            min-width: 250px !important;
        }
        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.25rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        .sidebar-brand-box {
            padding: 0.5rem 0.5rem 1.75rem 0.5rem;
        }
        .sidebar-brand-logo {
            display: flex;
            align-items: baseline;
            gap: 3px;
        }
        .sidebar-brand-title {
            font-size: 26px;
            font-weight: 900;
            color: #1C274C;
            letter-spacing: -0.03em;
        }
        .sidebar-brand-dot {
            display: inline-block;
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background-color: #2563EB;
            margin-bottom: 2px;
        }
        .sidebar-brand-sub {
            font-size: 11px;
            font-weight: 600;
            color: #6C7275;
            margin-top: 3px;
        }
        
        /* Style native page links in sidebar to match Stitch pills */
        [data-testid="stSidebar"] div.stPageLink {
            margin-bottom: 6px;
        }
        [data-testid="stSidebar"] div.stPageLink a {
            border-radius: 9999px !important;
            padding: 10px 18px !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            color: #475569 !important;
            transition: all 0.15s ease !important;
            text-decoration: none !important;
            display: flex !important;
            align-items: center !important;
            gap: 12px !important;
        }
        [data-testid="stSidebar"] div.stPageLink a:hover {
            background-color: #F1F5F9 !important;
            color: #1C274C !important;
        }
        [data-testid="stSidebar"] div.stPageLink a[aria-current="page"] {
            background-color: #1C274C !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 14px rgba(28, 39, 76, 0.18) !important;
        }
        [data-testid="stSidebar"] div.stPageLink a[aria-current="page"] p,
        [data-testid="stSidebar"] div.stPageLink a[aria-current="page"] span {
            color: #FFFFFF !important;
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
