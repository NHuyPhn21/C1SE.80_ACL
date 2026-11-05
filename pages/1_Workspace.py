"""Dynamic project Workspace backed by SQLite (100% Streamlit Native, 100% Matching Stitch UI)."""

import base64
from html import escape
import os
from pathlib import Path
import socket
import streamlit as st

from backend.database import SessionLocal
from backend.models import ComicPage
from services.workspace_service import WorkspaceService, WorkspaceServiceError
from utils.auth_session import logout, require_auth
from utils.page_navigation import render_page_navigation

user = require_auth()
render_page_navigation()

try:
    user_id = int(user.id)
except (ValueError, TypeError):
    st.error("Invalid user account. Please log in again.")
    st.stop()

workspace_service = WorkspaceService()

# 1. Đọc thông số phần cứng thật (không số giả)
hostname = "Local-Node"
try:
    hostname = socket.gethostname()
except Exception:
    pass

user_initials = (user.full_name[:2] if user.full_name else "PH").upper()
user_display_name = user.full_name or "Phanvanquann26"

# 2. Tính toán dung lượng lưu trữ thực tế từ thư mục data/
BASE_DIR = Path(__file__).resolve().parents[1]
data_dir = BASE_DIR / "data"
total_bytes = 0
if data_dir.exists():
    for f in data_dir.rglob("*"):
        if f.is_file():
            total_bytes += f.stat().st_size
storage_mb = round(total_bytes / (1024 * 1024), 1)
storage_display = f"{storage_mb} MB" if storage_mb < 1024 else f"{round(storage_mb / 1024, 1)} GB"
storage_pct = round((total_bytes / (10 * 1024 * 1024 * 1024)) * 100, 1)

# 3. Đọc dữ liệu In Queue thật từ SQLite
in_queue_count = 0
try:
    with SessionLocal() as db:
        in_queue_count = db.query(ComicPage).filter(ComicPage.status.in_(["PENDING", "PROCESSING"])).count()
except Exception:
    in_queue_count = 0

# 4. Avatar file check (ảnh đại diện nếu có)
avatar_data_uri = None
for ext in (".png", ".jpg", ".jpeg"):
    candidate = BASE_DIR / "data" / "avatars" / f"user_{user.id}{ext}"
    if candidate.exists():
        mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
        b64 = base64.b64encode(candidate.read_bytes()).decode("ascii")
        avatar_data_uri = f"data:{mime};base64,{b64}"
        break

# 5. CSS cục bộ chuyên nghiệp (Khôi phục 100% Giao diện chuẩn, Khối Topbar độc lập, Đồng đều thẳng hàng)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background-color: #F8F9FA !important;
        color: #1A1D1F !important;
    }
    
    [data-testid="stMainBlockContainer"] {
        padding: 1rem 2.5rem 3.5rem 2.5rem !important;
        max-width: 1400px !important;
    }

    /* KHỐI TOP NAVBAR RIÊNG BIỆT: Nổi bật trên nền canvas, viền bo tròn, shadow mềm */
    div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 20px !important;
        padding: 0.65rem 1.4rem !important;
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.04) !important;
        margin-bottom: 2.25rem !important;
    }

    /* Đảm bảo tất cả các cột trong Top Navbar căn giữa hoàn hảo */
    div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type [data-testid="stHorizontalBlock"] {
        align-items: center !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type [data-testid="stColumn"] {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type [data-testid="stColumn"]:first-child {
        justify-content: flex-start !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type [data-testid="stColumn"]:last-child {
        justify-content: flex-end !important;
    }

    /* 1. Breadcrumb: Chiều cao chuẩn 38px */
    .top-breadcrumb-box {
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
        font-size: 0.95rem !important;
        height: 38px !important;
        white-space: nowrap !important;
    }
    .top-breadcrumb-bold {
        font-weight: 800;
        color: #1A1D1F;
    }
    .top-breadcrumb-slash {
        color: #94A3B8;
    }
    .top-breadcrumb-current {
        color: #64748B;
        font-weight: 500;
    }
    
    /* 2. Search Bar: Chiều cao chuẩn 38px, bo tròn pill */
    .top-search-wrapper {
        width: 100% !important;
    }
    .top-search-wrapper div[data-testid="stTextInput"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    .top-search-wrapper div[data-testid="stTextInputRootElement"] {
        height: 38px !important;
        border-radius: 9999px !important;
    }
    .top-search-wrapper div[data-testid="stTextInputRootElement"] input {
        height: 38px !important;
        background-color: #F1F5F9 !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 9999px !important;
        padding: 0 18px !important;
        font-size: 0.85rem !important;
        color: #334155 !important;
        box-sizing: border-box !important;
    }
    .top-search-wrapper div[data-testid="stTextInputRootElement"] input:focus {
        border-color: #2563EB !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15) !important;
    }

    /* 3. Node status badge: Chiều cao chuẩn 38px */
    .node-status-ready {
        height: 38px !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 6px !important;
        background: #EFF6FF !important;
        color: #1E40AF !important;
        border: 1px solid #DBEAFE !important;
        border-radius: 9999px !important;
        padding: 0 14px !important;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        white-space: nowrap !important;
        box-sizing: border-box !important;
    }

    /* 4. Icon Circles (Bell & Slider): Chiều cao chuẩn 38px */
    .top-nav-icons-wrap {
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        height: 38px !important;
    }
    .icon-box-circle {
        width: 38px !important;
        height: 38px !important;
        border-radius: 50% !important;
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: relative !important;
        font-size: 14px !important;
        box-sizing: border-box !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
    }
    .icon-box-circle:hover {
        background-color: #F8FAFC !important;
        border-color: #CBD5E1 !important;
    }
    .icon-red-dot {
        position: absolute;
        top: 6px;
        right: 6px;
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: #EF4444;
    }

    /* 5. Nút Kích Hoạt Avatar Capsule [ (PH) ⌵ ]: Chuẩn 100% Ảnh Mockup */
    .top-avatar-popover {
        display: flex !important;
        justify-content: flex-end !important;
        align-items: center !important;
        height: 38px !important;
    }
    .top-avatar-popover div[data-testid="stPopover"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    .top-avatar-popover [data-testid="stPopover"] button,
    .top-avatar-popover div[data-testid="stPopover"] button,
    div[data-testid="stPopoverButton"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #1C274C !important;
        border-radius: 9999px !important;
        padding: 2px 10px 2px 4px !important;
        height: 38px !important;
        min-height: 38px !important;
        max-height: 38px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 6px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
        box-sizing: border-box !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
    }
    .top-avatar-popover [data-testid="stPopover"] button:hover {
        background-color: #F8FAFC !important;
        border-color: #0F172A !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1) !important;
    }
    /* Logo avatar tròn xanh đen bên trong nút capsule */
    .top-avatar-popover [data-testid="stPopover"] button p,
    .top-avatar-popover [data-testid="stPopover"] button span,
    .top-avatar-popover [data-testid="stPopover"] button [data-testid="stMarkdownContainer"] p {
        background-color: #1C274C !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 11px !important;
        border-radius: 50% !important;
        width: 28px !important;
        height: 28px !important;
        min-width: 28px !important;
        min-height: 28px !important;
        max-width: 28px !important;
        max-height: 28px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 28px !important;
    }
    .top-avatar-popover [data-testid="stPopover"] button svg {
        color: #1C274C !important;
        fill: #1C274C !important;
        width: 14px !important;
        height: 14px !important;
        margin-left: 2px !important;
    }

    /* Popover dropdown container matching Image 2 */
    div[data-testid="stPopoverBody"] {
        padding: 1.25rem 1.15rem !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12) !important;
        border: 1px solid #E2E8F0 !important;
        min-width: 270px !important;
    }

    /* User Menu Links in English */
    div[data-testid="stPopoverBody"] div.stPageLink {
        margin-bottom: 4px !important;
    }
    div[data-testid="stPopoverBody"] div.stPageLink a {
        border-radius: 8px !important;
        padding: 8px 10px !important;
        color: #475569 !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
        transition: all 0.15s ease !important;
        text-decoration: none !important;
        background: transparent !important;
    }
    div[data-testid="stPopoverBody"] div.stPageLink a:hover {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }
    div[data-testid="stPopoverBody"] div.stPageLink a p,
    div[data-testid="stPopoverBody"] div.stPageLink a span {
        color: #475569 !important;
        font-weight: 500 !important;
    }
    div[data-testid="stPopoverBody"] div.stPageLink a:hover p,
    div[data-testid="stPopoverBody"] div.stPageLink a:hover span {
        color: #0F172A !important;
    }

    /* Sign out button matching Image 2 */
    div[data-testid="stPopoverBody"] div[data-testid="stButton"] > button {
        background-color: transparent !important;
        border: none !important;
        color: #DC2626 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 8px 10px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        gap: 10px !important;
        border-radius: 8px !important;
        width: 100% !important;
        transition: all 0.15s ease !important;
    }
    div[data-testid="stPopoverBody"] div[data-testid="stButton"] > button:hover {
        background-color: #FEF2F2 !important;
        color: #B91C1C !important;
    }
    div[data-testid="stPopoverBody"] div[data-testid="stButton"] > button p {
        color: #DC2626 !important;
        font-weight: 600 !important;
    }

    /* Main Page Header */
    .main-page-title {
        font-size: 2.15rem;
        font-weight: 800;
        color: #111827;
        margin: 0;
        letter-spacing: -0.03em;
    }
    .main-page-sub {
        color: #64748B;
        font-size: 0.95rem;
        margin-top: 4px;
        margin-bottom: 1.75rem;
    }

    /* + Create New Project button (Navy Pill 100% chuẩn Ảnh 2) */
    .create-project-btn-wrap div[data-testid="stButton"] > button {
        background-color: #1C274C !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 9999px !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        padding: 0.65rem 1.45rem !important;
        box-shadow: 0 4px 14px rgba(28, 39, 76, 0.22) !important;
        transition: all 0.2s ease !important;
    }
    .create-project-btn-wrap div[data-testid="stButton"] > button:hover {
        background-color: #0F172A !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 18px rgba(28, 39, 76, 0.35) !important;
    }

    /* Clean Project Card (Exact Image 2) */
    .clean-project-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 1.35rem 1.45rem 1.15rem 1.45rem;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        margin-bottom: 0.5rem;
    }
    .clean-project-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
        border-color: #CBD5E1;
    }
    .card-top-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4px;
    }
    .card-title-text {
        font-size: 1.25rem;
        font-weight: 800;
        color: #0F172A;
    }
    .card-id-pill {
        background: #F1F5F9;
        color: #64748B;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 3px 9px;
        border-radius: 9999px;
        border: 1px solid #E2E8F0;
    }
    .card-meta-desc {
        font-size: 0.85rem;
        color: #64748B;
        margin-bottom: 14px;
    }
    .card-badge-status {
        display: inline-block;
        background: #EEF2FF;
        color: #4F46E5;
        border: 1px solid #E0E7FF;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 3px 12px;
        border-radius: 9999px;
        margin-bottom: 16px;
    }
    .card-progress-labels {
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        color: #64748B;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .card-progress-track {
        height: 5px;
        border-radius: 9999px;
        background: #E2E8F0;
        overflow: hidden;
        margin-bottom: 14px;
    }
    .card-progress-fill {
        height: 100%;
        border-radius: inherit;
        background: #2563EB;
    }
    .card-footer-box {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-top: 10px;
        border-top: 1px solid #F1F5F9;
    }
    .card-user-meta {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .avatar-mini-circle {
        width: 26px;
        height: 26px;
        border-radius: 50%;
        background: #1C274C;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
        font-weight: 800;
    }
    .team-badge-text {
        font-size: 0.8rem;
        color: #64748B;
        font-weight: 600;
    }

    /* Open Chapter Studio Button inside card column */
    .card-action-btn div[data-testid="stButton"] > button {
        background: transparent !important;
        border: 1px solid #E2E8F0 !important;
        color: #1C274C !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        border-radius: 9999px !important;
        padding: 6px 14px !important;
        transition: all 0.15s ease !important;
    }
    .card-action-btn div[data-testid="stButton"] > button:hover {
        background: #1C274C !important;
        color: #FFFFFF !important;
        border-color: #1C274C !important;
    }

    /* 3 Summary Metric Cards at Bottom (Image 2) */
    .metric-row-wrap {
        margin-top: 4rem;
        padding-top: 1.5rem;
        border-top: 1px solid #EAEAEA;
    }
    .bottom-metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.25rem 1.4rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.02);
    }
    .metric-title {
        font-size: 0.8rem;
        font-weight: 700;
        color: #64748B;
        margin-bottom: 4px;
    }
    .metric-num {
        font-size: 1.75rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.02em;
    }
    .metric-sub-green {
        font-size: 0.78rem;
        font-weight: 700;
        color: #16A34A;
        margin-top: 2px;
    }
    .metric-sub-gray {
        font-size: 0.78rem;
        color: #64748B;
        margin-top: 2px;
    }
    .metric-icon-box {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }

    /* Modal dialog button */
    div[data-testid="stDialog"] div[data-testid="stFormSubmitButton"] > button {
        background-color: #1C274C !important;
        color: #FFFFFF !important;
        border-radius: 9999px !important;
        font-weight: 700 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 6. KHỐI TOP NAVBAR RIÊNG BIỆT (Bordered Card Container chuẩn 1 khối độc lập, các mục thẳng hàng 38px)
with st.container(border=True):
    nav_col_left, nav_col_search, nav_col_node, nav_col_icons, nav_col_user = st.columns(
        [2.2, 3.2, 2.2, 0.9, 0.8], vertical_alignment="center"
    )

    with nav_col_left:
        st.markdown(
            """
            <div class="top-breadcrumb-box">
                <span class="top-breadcrumb-bold">ACL Studio</span>
                <span class="top-breadcrumb-slash">/</span>
                <span class="top-breadcrumb-current">Projects</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with nav_col_search:
        st.markdown('<div class="top-search-wrapper">', unsafe_allow_html=True)
        search_keyword = st.text_input(
            "Search batches or series",
            placeholder="🔍 Filter batches or series...",
            label_visibility="collapsed",
            key="top_navbar_search_input",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with nav_col_node:
        st.markdown(
            f"""
            <div class="node-status-ready">
                <span>⚙</span>
                <span>Node: {hostname} (Ready)</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with nav_col_icons:
        st.markdown(
            """
            <div class="top-nav-icons-wrap">
                <div class="icon-box-circle">
                    <span>🔔</span>
                    <span class="icon-red-dot"></span>
                </div>
                <div class="icon-box-circle">
                    <span>🎛️</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with nav_col_user:
        st.markdown('<div class="top-avatar-popover">', unsafe_allow_html=True)
        with st.popover(label=f"{user_initials}", use_container_width=False):
            if avatar_data_uri:
                avatar_html = f'<img src="{avatar_data_uri}" style="width:44px; height:44px; border-radius:50%; object-fit:cover; flex-shrink:0; border:1px solid #E2E8F0;" />'
            else:
                avatar_html = f'<div style="width:44px; height:44px; border-radius:50%; background:#1C274C; color:#FFFFFF; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:16px; flex-shrink:0;">{user_initials}</div>'

            st.markdown(
                f"""
                <div style="display:flex; align-items:center; gap:12px; padding:4px 0 10px 0;">
                    {avatar_html}
                    <div>
                        <div style="font-weight:700; font-size:15px; color:#111827; line-height:1.2;">{escape(user_display_name)}</div>
                        <div style="font-size:12px; color:#64748B; margin:2px 0 4px 0;">{escape(user.email or '')}</div>
                        <div>
                            <span style="background:#EFF6FF; color:#2563EB; font-size:11px; font-weight:700; padding:2px 8px; border-radius:9999px; display:inline-flex; align-items:center; gap:4px;">
                                <span style="width:5px; height:5px; border-radius:50%; background:#2563EB;"></span>
                                Lead Editor
                            </span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.page_link("pages/3_Settings.py", label="Personal Settings", icon="👤")
            st.page_link("pages/1_Team_Workspace.py", label="Team Workspace", icon="👥")
            st.divider()
            if st.button("🚪 Sign out", key="popover_signout_btn", use_container_width=True):
                logout()
                st.switch_page("pages/0_Login.py")
        st.markdown("</div>", unsafe_allow_html=True)


# 7. Modal Dialog Tạo Dự Án Mới
@st.dialog("Create New Project")
def create_project_dialog() -> None:
    with st.form("create_project_modal_form"):
        title = st.text_input("Series Title / Manga Name *", placeholder="e.g. Chainsaw Man — Chapter 150")
        description = st.text_area(
            "Project Notes", placeholder="Language pair: JP ➔ VI, font guidelines, resolution..."
        )
        submitted = st.form_submit_button("Confirm & Create", use_container_width=True)
    if submitted:
        if not title.strip():
            st.error("Please enter a project title.")
            return
        try:
            new_p_id = workspace_service.create_project(user_id, title.strip(), description.strip())
            st.session_state["current_project_id"] = new_p_id
            st.session_state["current_project_title"] = title.strip()
            st.query_params["project_id"] = str(new_p_id)
            st.query_params["project"] = title.strip()
            st.success(f"Project '{title.strip()}' created successfully!")
            st.rerun()
        except WorkspaceServiceError as exc:
            st.error(f"Creation error: {exc}")


# 8. Tiêu đề Trang & Nút Tạo Dự Án (Navy Pill Chuẩn Ảnh 2)
head_left, head_right = st.columns([3.8, 1.3], vertical_alignment="center")
with head_left:
    st.markdown('<h1 class="main-page-title">Projects</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="main-page-sub">Manage your ongoing comic localization series and translation pipelines.</p>',
        unsafe_allow_html=True,
    )
with head_right:
    st.markdown('<div class="create-project-btn-wrap">', unsafe_allow_html=True)
    if st.button("＋ Create New Project", key="btn_create_project_top", use_container_width=True):
        create_project_dialog()
    st.markdown("</div>", unsafe_allow_html=True)

# 9. Truy vấn danh sách dự án thật từ SQLite
projects = workspace_service.list_projects(user_id)

display_projects = projects
if search_keyword.strip():
    kw = search_keyword.strip().lower()
    display_projects = [p for p in display_projects if kw in p.title.lower() or kw in p.description.lower()]

# 10. Lưới Thẻ Truyện (Exact Project Cards từ Ảnh 2)
if not display_projects:
    st.info("No projects found matching the current search.")
    if st.button("Create project now", key="btn_empty_create"):
        create_project_dialog()
else:
    for start in range(0, len(display_projects), 3):
        row_projects = display_projects[start : start + 3]
        columns = st.columns(3, gap="large")
        for idx_col, project in enumerate(row_projects):
            with columns[idx_col]:
                desc_text = project.description if project.description else "0 pages • Japanese ➔ Vietnamese"
                status_text = "Ready for Upload" if project.total_pages == 0 else ("Completed" if project.progress_percent == 100 else "Processing")
                st.markdown(
                    f"""
                    <div class="clean-project-card">
                        <div class="card-top-row">
                            <span class="card-title-text">{escape(project.title)}</span>
                            <span class="card-id-pill">#{project.id:02d}</span>
                        </div>
                        <div class="card-meta-desc">{escape(desc_text)}</div>
                        <div class="card-badge-status">{status_text}</div>
                        <div class="card-progress-labels">
                            <span>Progress: {status_text}</span>
                            <span>{project.progress_percent}%</span>
                        </div>
                        <div class="card-progress-track">
                            <div class="card-progress-fill" style="width:{project.progress_percent}%;"></div>
                        </div>
                        <div class="card-footer-box">
                            <div class="card-user-meta">
                                <div class="avatar-mini-circle">{user_initials}</div>
                                <span class="team-badge-text">1 team 👥</span>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown('<div class="card-action-btn">', unsafe_allow_html=True)
                if st.button(
                    "Open Chapter Studio ➔",
                    key=f"btn_open_proj_{project.id}",
                    use_container_width=True,
                ):
                    st.session_state["current_project_id"] = project.id
                    st.session_state["current_project_title"] = project.title
                    st.query_params["project_id"] = str(project.id)
                    st.query_params["project"] = project.title
                    st.switch_page("pages/2_Chapter_Studio.py")
                st.markdown("</div>", unsafe_allow_html=True)

# 11. Hàng 3 Thẻ Metric Thống Kê ở Dưới Cùng (Chuẩn xác 100% theo Ảnh 2)
st.markdown('<div class="metric-row-wrap">', unsafe_allow_html=True)
stat_c1, stat_c2, stat_c3 = st.columns(3, gap="large")

with stat_c1:
    st.markdown(
        f"""
        <div class="bottom-metric-card">
            <div>
                <div class="metric-title">Active Projects</div>
                <div class="metric-num">{len(projects)}</div>
                <div class="metric-sub-green">+1 this week</div>
            </div>
            <div class="metric-icon-box">📁</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with stat_c2:
    st.markdown(
        f"""
        <div class="bottom-metric-card">
            <div>
                <div class="metric-title">In Queue</div>
                <div class="metric-num">{in_queue_count}</div>
                <div class="metric-sub-gray">pages pending OCR</div>
            </div>
            <div class="metric-icon-box">⌛</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with stat_c3:
    st.markdown(
        f"""
        <div class="bottom-metric-card">
            <div>
                <div class="metric-title">Storage Allocation</div>
                <div class="metric-num">{storage_display}</div>
                <div class="metric-sub-gray">/ 10 GB ({storage_pct}%)</div>
            </div>
            <div class="metric-icon-box">☁️</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
st.markdown("</div>", unsafe_allow_html=True)
