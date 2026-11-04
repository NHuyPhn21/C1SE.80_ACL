"""Dynamic project Workspace backed by SQLite (100% Streamlit Native, Zero Iframe)."""

from html import escape
import os
import socket
import psutil
import streamlit as st

from services.workspace_service import WorkspaceService, WorkspaceServiceError
from utils.auth_session import logout, require_auth
from utils.page_navigation import render_page_navigation

user = require_auth()
render_page_navigation()

try:
    user_id = int(user.id)
except (ValueError, TypeError):
    st.error("Tài khoản người dùng không hợp lệ. Vui lòng đăng nhập lại.")
    st.stop()

workspace_service = WorkspaceService()

# 1. Đọc thông số phần cứng thật (không fallback số giả)
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

# 2. CSS cục bộ (100% tự chứa, không phụ thuộc Tailwind CDN bên ngoài)
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
    
    .project-card-box {
        background: #FFFFFF;
        border: 1px solid #EAEAEA;
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 4px 16px rgba(20, 25, 35, 0.03);
        margin-bottom: 0.75rem;
    }
    .project-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 0.5rem;
    }
    .project-card-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1A1D1F;
        margin: 0;
    }
    .project-card-id {
        background: #F1F5F9;
        color: #475569;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .project-card-desc {
        color: #6C7275;
        font-size: 0.85rem;
        margin: 0.5rem 0 1rem;
        min-height: 38px;
        line-height: 1.4;
    }
    .progress-bar-track {
        height: 7px;
        border-radius: 999px;
        background: #E8EAED;
        overflow: hidden;
        margin-top: 4px;
    }
    .progress-bar-fill {
        height: 100%;
        border-radius: inherit;
        background: #2563EB;
    }
    
    div.stButton > button {
        border-radius: 9999px !important;
        font-weight: 700 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 3. Header Top Bar với Logo Minimalist & Hardware Node Badge
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


@st.dialog("Tạo Dự Án Mới")
def create_project_dialog() -> None:
    with st.form("create_project_form"):
        title = st.text_input("Tên dự án / Bộ truyện *", placeholder="Ví dụ: Chainsaw Man Chapter 150")
        description = st.text_area(
            "Mô tả dự án", placeholder="Cặp ngôn ngữ: JP ➔ VI, ghi chú dịch thuật hoặc phạm vi xử lý..."
        )
        submitted = st.form_submit_button("Xác nhận tạo dự án", use_container_width=True)
    if submitted:
        if not title.strip():
            st.error("Vui lòng nhập tên dự án.")
            return
        try:
            new_p = workspace_service.create_project(user_id, title.strip(), description.strip())
            st.session_state["current_project_id"] = new_p.id
            st.session_state["current_project_title"] = new_p.title
            st.query_params["project_id"] = str(new_p.id)
            st.query_params["project"] = new_p.title
            st.success(f"Tạo dự án '{new_p.title}' thành công!")
            st.rerun()
        except WorkspaceServiceError as exc:
            st.error(f"Lỗi khi tạo dự án: {exc}")


# 4. Tiêu đề Workspace và các nút tác vụ Native
title_col, action_col, logout_col = st.columns([2.8, 1.2, 0.6])
with title_col:
    st.caption("ACL Studio / Projects")
    st.markdown('<h1 style="font-size:2rem; font-weight:800; margin:0; color:#1A1D1F;">Projects Workspace</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#6C7275; margin:0.25rem 0 1.25rem;">Quản lý các dự án dịch truyện manga thời gian thực từ database SQLite.</p>',
        unsafe_allow_html=True,
    )

with action_col:
    st.write("")
    if st.button("➕ Tạo Dự Án Mới", use_container_width=True):
        create_project_dialog()

with logout_col:
    st.write("")
    if st.button("Đăng xuất", use_container_width=True):
        logout()
        st.switch_page("pages/0_Login.py")

# 5. Danh sách thẻ truyện (Truy vấn thật 100% từ SQLite)
projects = workspace_service.list_projects(user_id)

if not projects:
    with st.container(border=True):
        st.subheader("Chưa có dự án nào")
        st.write("Bấm **Tạo Dự Án Mới** ở góc trên để bắt đầu tải trang manga và khởi chạy quy trình AI.")
else:
    for start in range(0, len(projects), 3):
        columns = st.columns(3, gap="medium")
        for column, project in zip(columns, projects[start : start + 3]):
            with column:
                desc_display = project.description if project.description else "Dự án dịch truyện tự động."
                st.markdown(
                    f"""
                    <div class="project-card-box">
                      <div class="project-card-header">
                        <h3 class="project-card-title">{escape(project.title)}</h3>
                        <span class="project-card-id">#{project.id:02d}</span>
                      </div>
                      <div class="project-card-desc">{escape(desc_display)}</div>
                      <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px; color:#6C7275;">
                        <span>{project.completed_pages}/{project.total_pages} trang hoàn thành</span>
                        <strong style="color:#1C274C;">{project.progress_percent}%</strong>
                      </div>
                      <div class="progress-bar-track">
                        <div class="progress-bar-fill" style="width:{project.progress_percent}%;"></div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    "Mở Chapter Studio ➔",
                    key=f"open_project_{project.id}",
                    use_container_width=True,
                ):
                    # Thống nhất đồng bộ định danh project trên toàn bộ app
                    st.session_state["current_project_id"] = project.id
                    st.session_state["current_project_title"] = project.title
                    st.query_params["project_id"] = str(project.id)
                    st.query_params["project"] = project.title
                    st.switch_page("pages/2_Chapter_Studio.py")

# 6. Thẻ thống kê tổng kết
st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)
total_pages = sum(p.total_pages for p in projects)
completed_pages = sum(p.completed_pages for p in projects)
metric_col1, metric_col2, metric_col3 = st.columns(3)
metric_col1.metric("Tổng Dự Án", len(projects))
metric_col2.metric("Tổng Số Trang Manga", total_pages)
metric_col3.metric("Số Trang Đã Hoàn Tất", completed_pages)
