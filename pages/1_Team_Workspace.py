"""Database-backed Team Workspace and project role assignment (100% Streamlit Native, Zero Iframe)."""

from html import escape
import os
import socket
import psutil
import streamlit as st

from services.team_service import TeamService, TeamServiceError
from services.workspace_service import WorkspaceService
from utils.auth_session import logout, require_auth
from utils.page_navigation import render_page_navigation

user = require_auth()
render_page_navigation()

try:
    current_user_id = int(user.id)
except (ValueError, TypeError):
    st.error("Tài khoản người dùng không hợp lệ. Vui lòng đăng nhập lại.")
    st.stop()

team_service = TeamService()
workspace_service = WorkspaceService()

# 1. Thống nhất xác định Project xuyên suốt giữa các trang
user_projects = []
try:
    user_projects = workspace_service.list_projects(current_user_id)
except Exception:
    pass

default_proj_title = user_projects[0].title if user_projects else "Local Manga"
project_title = st.query_params.get("project", st.session_state.get("current_project_title", default_proj_title))

project = team_service.get_or_create_project(project_title, current_user_id)
st.session_state["current_project_id"] = project.id
st.session_state["current_project_title"] = project.title
st.query_params["project_id"] = str(project.id)
st.query_params["project"] = project.title

# 2. Đọc thông số phần cứng thật
hardware_info = "Local Worker"
try:
    hostname = socket.gethostname()
    vm = psutil.virtual_memory()
    total_ram = round(vm.total / (1024**3), 1)
    used_ram = round(vm.used / (1024**3), 1)
    ram_pct = int(vm.percent)
    cores = os.cpu_count() or 1
    hardware_info = f"Node {hostname} (RAM {used_ram}/{total_ram} GB • {ram_pct}% • {cores} Cores)"
except Exception:
    hardware_info = "Node Worker (Active)"

# 3. CSS cục bộ (100% tự chứa, không phụ thuộc Tailwind CDN bên ngoài)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background-color: #F8F9FA !important;
        color: #1A1D1F !important;
    }
    
    .workspace-top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 0 1.25rem 0;
        border-bottom: 1px solid #EAEAEA;
        margin-bottom: 1.5rem;
    }
    
    .brand-wrap {
        display: flex;
        align-items: baseline;
        gap: 4px;
    }
    .brand-title {
        font-size: 22px;
        font-weight: 900;
        color: #1C274C;
        letter-spacing: -0.03em;
    }
    .brand-dot {
        display: inline-block;
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: #2563EB;
        margin-bottom: 2px;
    }
    .brand-divider {
        height: 18px;
        width: 1px;
        background: #D1D5DB;
        margin: 0 12px;
    }
    .brand-sub {
        font-size: 12px;
        font-weight: 700;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .node-pill {
        background: #E8F5E9;
        color: #2E7D32;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .node-dot {
        width: 7px;
        height: 7px;
        background: #2E7D32;
        border-radius: 50%;
    }
    
    .role-badge {
        background: #E8EDFB;
        color: #1C274C;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
    }
    .role-badge-owner {
        background: #FEF3C7;
        color: #92400E;
    }
    
    div.stButton > button {
        border-radius: 9999px !important;
        font-weight: 700 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 4. Top Bar Header
st.markdown(
    f"""
    <div class="workspace-top-bar">
        <div style="display:flex; align-items:center;">
            <div class="brand-wrap">
                <span class="brand-title">ACL</span>
                <span class="brand-dot"></span>
            </div>
            <div class="brand-divider"></div>
            <span class="brand-sub">Automated Comic Localization</span>
        </div>
        <div class="node-pill">
            <span class="node-dot"></span>
            {hardware_info}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 5. Tiêu đề và thông tin dự án
st.caption(f"ACL Studio / Projects / {project.title} / Team Workspace")
header_col, logout_col = st.columns([4, 0.8])
with header_col:
    st.markdown(
        f"""
        <h1 style="font-size:2rem; font-weight:800; margin:0; color:#1A1D1F;">Nhóm &amp; Phân Quyền Thành Viên</h1>
        <p style="color:#6C7275; margin:0.25rem 0 1.25rem;">Quản lý các thành viên tham gia dự án <strong>{escape(project.title)}</strong> trong database SQLite.</p>
        """,
        unsafe_allow_html=True,
    )
with logout_col:
    st.write("")
    if st.button("Đăng xuất", use_container_width=True):
        logout()
        st.switch_page("pages/0_Login.py")

# 6. Form Mời Thành Viên Native
with st.container(border=True):
    st.markdown("#### ➕ Mời Thành Viên Mới")
    email_col, role_col, submit_col = st.columns([2.5, 1.5, 1])
    with email_col:
        invite_email = st.text_input(
            "Email đồng nghiệp",
            placeholder="colleague@studio.com",
            label_visibility="collapsed",
            key="team_invite_email_input",
        )
    with role_col:
        invite_role = st.selectbox(
            "Vai trò",
            ["Translator", "Typesetter", "Project Manager"],
            label_visibility="collapsed",
            key="team_invite_role_select",
        )
    with submit_col:
        if st.button("Gửi Lời Mời", use_container_width=True):
            if not invite_email.strip():
                st.error("Vui lòng nhập địa chỉ email đồng nghiệp.")
            else:
                try:
                    invited = team_service.invite_member(project.id, invite_email.strip(), invite_role)
                    st.success(f"Đã thêm {invited.name} với vai trò {invited.role} thành công!")
                    st.rerun()
                except TeamServiceError as exc:
                    st.error(f"Lỗi khi mời thành viên: {exc}")

# 7. Thống kê số lượng thành viên
members = team_service.list_members(project.id)
m_col1, m_col2, m_col3 = st.columns(3)
m_col1.metric("Tổng Số Thành Viên", len(members))
m_col2.metric("Số Lượng Vai Trò", len({m.role for m in members}))
m_col3.metric("Quyền Truy Cập", "Private Team")

# 8. Danh sách thành viên dự án
with st.container(border=True):
    list_head_col, filter_col = st.columns([3, 1.2])
    with list_head_col:
        st.markdown("### Danh Sách Thành Viên Dự Án")
    with filter_col:
        filter_role = st.selectbox(
            "Lọc theo vai trò",
            ["Tất cả", "Translator", "Typesetter", "Project Manager", "Owner"],
            label_visibility="collapsed",
        )

    filtered_members = members
    if filter_role != "Tất cả":
        if filter_role == "Owner":
            filtered_members = [m for m in members if m.is_owner]
        else:
            filtered_members = [m for m in members if m.role == filter_role]

    if not filtered_members:
        st.info("Không có thành viên nào phù hợp với bộ lọc đã chọn.")
    else:
        for member in filtered_members:
            owner_badge_class = " role-badge-owner" if member.is_owner else ""
            owner_text = " (Chủ sở hữu)" if member.is_owner else ""

            with st.container():
                info_col, role_col, action_col = st.columns([2.5, 1.2, 0.8])
                with info_col:
                    first_letter = escape(member.name[:1].upper()) if member.name else "U"
                    st.markdown(
                        f"""
                        <div style="display:flex; align-items:center; gap:12px; padding:4px 0;">
                            <div style="width:36px; height:36px; border-radius:50%; background:#E2E8F0; color:#1C274C; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:13px;">
                                {first_letter}
                            </div>
                            <div>
                                <div style="font-weight:700; color:#1A1D1F; font-size:0.95rem;">{escape(member.name)}</div>
                                <div style="color:#6C7275; font-size:0.8rem;">{escape(member.email)}</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with role_col:
                    st.markdown(
                        f'<div style="padding-top:8px;"><span class="role-badge{owner_badge_class}">{escape(member.role)}{owner_text}</span></div>',
                        unsafe_allow_html=True,
                    )
                with action_col:
                    if not member.is_owner:
                        st.write("")
                        if st.button("Xóa", key=f"del_mem_{member.user_id}", use_container_width=True):
                            try:
                                team_service.remove_member(project.id, member.user_id)
                                st.success(f"Đã gỡ {member.name} khỏi dự án.")
                                st.rerun()
                            except TeamServiceError as exc:
                                st.error(f"Lỗi khi xóa thành viên: {exc}")
                    else:
                        st.markdown("<div style='padding-top:10px; color:#94A3B8; font-size:0.8rem; text-align:center;'>—</div>", unsafe_allow_html=True)
