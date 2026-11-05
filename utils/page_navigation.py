"""Native Streamlit navigation controls for sidebar matching 100% Google Stitch design (Pure White Sidebar & Navy Active Pill)."""

import streamlit as st


def render_page_navigation(active_item: str = "") -> None:
    """Render sleek left sidebar navigation matching 100% original Stitch design."""
    # Build active item CSS selectors
    active_css = """
        /* Automatic Streamlit active link support */
        [data-testid="stSidebar"] div.stPageLink a[aria-current="page"] {
            background-color: #1C274C !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 14px rgba(28, 39, 76, 0.2) !important;
        }
        [data-testid="stSidebar"] div.stPageLink a[aria-current="page"] p,
        [data-testid="stSidebar"] div.stPageLink a[aria-current="page"] span {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }
    """

    href_map = {
        "Projects": 'a[href*="Workspace"]:not([href*="Team"])',
        "Team Roles": 'a[href*="Team_Workspace"]',
        "Chapter Studio": 'a[href*="Chapter_Studio"]',
        "Review Studio": 'a[href*="Review_Studio"]',
        "Typesetting": 'a[href*="Typesetting"]',
        "Queue Monitor": 'a[href*="Queue_Monitor"]',
        "Personal Settings": 'a[href*="Settings"]',
    }

    if active_item and active_item in href_map:
        sel = href_map[active_item]
        active_css += f"""
        [data-testid="stSidebar"] {sel} {{
            background-color: #1C274C !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 14px rgba(28, 39, 76, 0.2) !important;
        }}
        [data-testid="stSidebar"] {sel} p,
        [data-testid="stSidebar"] {sel} span {{
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }}
        """
    elif not active_item:
        # Default fallback to Projects if no explicit active_item
        active_css += """
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
        """

    st.markdown(
        f"""
        <style>
        /* Hide default Streamlit auto-generated page list */
        [data-testid="stSidebarNav"] {{
            display: none !important;
        }}
        
        /* Custom Sidebar: Pure White Background matching Image 1, 2, 3 */
        [data-testid="stSidebar"] {{
            display: block !important;
            visibility: visible !important;
            transform: none !important;
            background-color: #FFFFFF !important;
            border-right: 1px solid #EAEAEA !important;
            width: 250px !important;
            min-width: 250px !important;
        }}
        
        /* Ẩn header mặc định và thu gọn đỉnh để nâng logo lên ngang bằng Top Navbar */
        [data-testid="stSidebarHeader"] {{
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
        }}
        [data-testid="stSidebarUserContent"] {{
            padding-top: 0 !important;
            margin-top: 0 !important;
        }}
        [data-testid="stSidebar"] > div:first-child {{
            padding-top: 1.15rem !important;
            padding-left: 0.85rem !important;
            padding-right: 0.85rem !important;
            background-color: #FFFFFF !important;
        }}
        [data-testid="stSidebarCollapsedControl"] {{
            display: none !important;
        }}
        
        /* Brand Header xích lên ngang bằng thanh Topbar chuẩn Figma */
        .sidebar-brand-box {{
            padding: 0.25rem 0.5rem 1.25rem 0.5rem !important;
            margin-top: 0 !important;
            margin-bottom: 0.2rem !important;
        }}
        .sidebar-brand-logo {{
            display: flex;
            align-items: baseline;
            gap: 3px;
        }}
        .sidebar-brand-title {{
            font-size: 25px;
            font-weight: 900;
            color: #1C274C;
            letter-spacing: -0.03em;
        }}
        .sidebar-brand-dot {{
            display: inline-block;
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background-color: #2563EB;
            margin-bottom: 2px;
        }}
        .sidebar-brand-sub {{
            font-size: 11px;
            font-weight: 600;
            color: #64748B;
            margin-top: 2px;
        }}
        
        /* Style native page links in sidebar */
        [data-testid="stSidebar"] div.stPageLink {{
            margin-bottom: 4px !important;
        }}
        [data-testid="stSidebar"] div.stPageLink a {{
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
        }}
        [data-testid="stSidebar"] div.stPageLink a p,
        [data-testid="stSidebar"] div.stPageLink a span {{
            color: #475569 !important;
            font-weight: 600 !important;
        }}
        [data-testid="stSidebar"] div.stPageLink a:hover {{
            background-color: #F1F5F9 !important;
            color: #1C274C !important;
        }}
        [data-testid="stSidebar"] div.stPageLink a:hover p,
        [data-testid="stSidebar"] div.stPageLink a:hover span {{
            color: #1C274C !important;
        }}

        {active_css}
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

