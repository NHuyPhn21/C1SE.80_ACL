"""Native Streamlit navigation controls for sidebar matching 100% Google Stitch design (Pure White Sidebar & Navy Active Pill)."""

import streamlit as st


def render_page_navigation() -> None:
    """Render sleek left sidebar navigation matching 100% original Stitch design."""
    st.markdown(
        """
        <style>
        /* Hide default Streamlit auto-generated page list */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        
        /* Custom Sidebar: Pure White Background matching Image 2 */
        [data-testid="stSidebar"] {
            display: block !important;
            visibility: visible !important;
            transform: none !important;
            background-color: #FFFFFF !important;
            border-right: 1px solid #EAEAEA !important;
            width: 250px !important;
            min-width: 250px !important;
        }
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 0.35rem !important;
            padding-left: 0.85rem !important;
            padding-right: 0.85rem !important;
            background-color: #FFFFFF !important;
        }
        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }
        
        /* Brand Header xích lên phía trên gọn gàng và tinh tế */
        .sidebar-brand-box {
            padding: 0.25rem 0.5rem 1rem 0.5rem !important;
            margin-top: -0.25rem !important;
        }
        .sidebar-brand-logo {
            display: flex;
            align-items: baseline;
            gap: 3px;
        }
        .sidebar-brand-title {
            font-size: 25px;
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
            color: #64748B;
            margin-top: 2px;
        }
        
        /* Style native page links in sidebar */
        [data-testid="stSidebar"] div.stPageLink {
            margin-bottom: 4px !important;
        }
        [data-testid="stSidebar"] div.stPageLink a {
            border-radius: 9999px !important;
            padding: 8px 16px !important;
            font-weight: 600 !important;
            font-size: 13.5px !important;
            color: #475569 !important;
            background-color: transparent !important;
            transition: all 0.15s ease !important;
            text-decoration: none !important;
            display: flex !important;
            align-items: center !important;
            gap: 10px !important;
        }
        [data-testid="stSidebar"] div.stPageLink a p,
        [data-testid="stSidebar"] div.stPageLink a span {
            color: #475569 !important;
            font-weight: 600 !important;
        }
        [data-testid="stSidebar"] div.stPageLink a:hover {
            background-color: #F1F5F9 !important;
            color: #1C274C !important;
        }
        [data-testid="stSidebar"] div.stPageLink a:hover p,
        [data-testid="stSidebar"] div.stPageLink a:hover span {
            color: #1C274C !important;
        }

        /* Active highlight for Workspace (Projects): Solid Navy Pill with White Text */
        [data-testid="stSidebar"] a[href*="Workspace"]:not([href*="Team"]) {
            background-color: #1C274C !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 14px rgba(28, 39, 76, 0.2) !important;
        }
        [data-testid="stSidebar"] a[href*="Workspace"]:not([href*="Team"]) p,
        [data-testid="stSidebar"] a[href*="Workspace"]:not([href*="Team"]) span {
            color: #FFFFFF !important;
            font-weight: 700 !important;
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
