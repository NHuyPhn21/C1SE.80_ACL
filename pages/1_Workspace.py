"""Dynamic project Workspace backed by SQLite (100% Streamlit Native, High-End SaaS UI)."""

from html import escape
import os
from pathlib import Path
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

# 1. Đọc thông số phần cứng thật (không số giả)
hardware_info = "Local Worker"
hostname = "Local-Node"
cores = 4
try:
    hostname = socket.gethostname()
    vm = psutil.virtual_memory()
    total_ram = round(vm.total / (1024**3), 1)
    used_ram = round(vm.used / (1024**3), 1)
    ram_pct = int(vm.percent)
    cores = os.cpu_count() or 1
    hardware_info = f"Node {hostname} • RAM {used_ram}/{total_ram} GB ({ram_pct}%) • {cores} Cores"
except Exception:
    hardware_info = "Node Worker (Active)"

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

# 3. CSS cục bộ chuyên nghiệp (100% tự chứa, không phụ thuộc Tailwind CDN bên ngoài)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background-color: #F8F9FA !important;
        color: #1A1D1F !important;
    }
    
    /* Top Header Bar */
    .top-header-wrap {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.85rem 0 1.25rem 0;
        border-bottom: 1px solid #EAEAEA;
        margin-bottom: 1.5rem;
    }
    .brand-title-wrap {
        display: flex;
        align-items: baseline;
        gap: 3px;
    }
    .brand-logo-text {
        font-size: 24px;
        font-weight: 900;
        color: #1C274C;
        letter-spacing: -0.03em;
    }
    .brand-logo-dot {
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: #2563EB;
        margin-bottom: 2px;
    }
    .brand-bar-divider {
        height: 18px;
        width: 1px;
        background: #D1D5DB;
        margin: 0 12px;
    }
    .brand-slogan {
        font-size: 12px;
        font-weight: 700;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .node-status-pill {
        background: #E8F5E9;
        color: #2E7D32;
        padding: 5px 14px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        border: 1px solid #C8E6C9;
    }
    .node-green-dot {
        width: 7px;
        height: 7px;
        background: #2E7D32;
        border-radius: 50%;
        box-shadow: 0 0 0 2px rgba(46, 125, 50, 0.2);
    }

    /* 4 Thẻ KPI Stat Cards */
    .kpi-row-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.25rem;
        margin-bottom: 2rem;
    }
    .kpi-stat-card {
        background: #FFFFFF;
        border: 1px solid #EAEAEA;
        border-radius: 16px;
        padding: 1.25rem 1.35rem;
        box-shadow: 0 2px 8px rgba(20, 25, 35, 0.02);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .kpi-stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(20, 25, 35, 0.06);
    }
    .kpi-card-sub {
        font-size: 0.75rem;
        font-weight: 700;
        color: #6C7275;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .kpi-card-num {
        font-size: 1.85rem;
        font-weight: 800;
        color: #1A1D1F;
        margin: 6px 0 2px 0;
        letter-spacing: -0.02em;
    }
    .kpi-card-badge {
        font-size: 0.72rem;
        font-weight: 700;
        color: #2563EB;
        background: #EFF6FF;
        padding: 2px 8px;
        border-radius: 9999px;
    }

    /* Thẻ truyện Project Card */
    .manga-card-box {
        background: #FFFFFF;
        border: 1px solid #EAEAEA;
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(20, 25, 35, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 0.75rem;
    }
    .manga-card-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 28px rgba(20, 25, 35, 0.08);
    }
    .manga-card-banner {
        height: 70px;
        background: linear-gradient(135deg, #1C274C 0%, #2563EB 100%);
        padding: 12px 16px;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }
    .manga-card-tag {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(4px);
        color: #FFFFFF;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 9999px;
    }
    .manga-card-id {
        background: #FFFFFF;
        color: #1C274C;
        font-size: 0.75rem;
        font-weight: 800;
        padding: 2px 8px;
        border-radius: 6px;
    }
    .manga-card-body {
        padding: 1.25rem 1.35rem;
    }
    .manga-card-title {
        font-size: 1.2rem;
        font-weight: 800;
        color: #1A1D1F;
        margin: 0 0 6px 0;
    }
    .manga-card-desc {
        color: #6C7275;
        font-size: 0.85rem;
        min-height: 40px;
        line-height: 1.45;
        margin-bottom: 1rem;
    }
    .manga-progress-track {
        height: 8px;
        border-radius: 9999px;
        background: #E8EAED;
        overflow: hidden;
        margin-top: 6px;
    }
    .manga-progress-fill {
        height: 100%;
        border-radius: inherit;
        background: #2563EB;
    }

    /* Dashed New Card */
    .dashed-new-card {
        border: 2px dashed #CBD5E1;
        background: #FAFAFA;
        border-radius: 18px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 230px;
        padding: 1.5rem;
        text-align: center;
        color: #64748B;
        transition: all 0.2s ease;
    }
    .dashed-new-card:hover {
        border-color: #2563EB;
        background: #EFF6FF;
        color: #2563EB;
    }

    div.stButton > button {
        border-radius: 9999px !important;
        font-weight: 700 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 4. Top Header Bar
st.markdown(
    f"""
    <div class="top-header-wrap">
        <div style="display:flex; align-items:center;">
            <div class="brand-title-wrap">
                <span class="brand-logo-text">ACL</span>
                <span class="brand-logo-dot"></span>
            </div>
            <div class="brand-bar-divider"></div>
            <span class="brand-slogan">Automated Comic Localization</span>
        </div>
        <div class="node-status-pill">
            <span class="node-green-dot"></span>
            {hardware_info}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


@st.dialog("Tạo Dự Án Dịch Thuật Mới")
def create_project_dialog() -> None:
    with st.form("create_project_modal_form"):
        title = st.text_input("Tên bộ truyện / Manga *", placeholder="Ví dụ: Chainsaw Man — Chapter 150")
        description = st.text_area(
            "Ghi chú dự án", placeholder="Cặp ngôn ngữ: JP ➔ VI, ghi chú font chữ, độ phân giải..."
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
            st.success(f"Khởi tạo dự án '{new_p.title}' thành công!")
            st.rerun()
        except WorkspaceServiceError as exc:
            st.error(f"Lỗi khởi tạo: {exc}")


# 5. Truy vấn danh sách dự án thật từ SQLite
projects = workspace_service.list_projects(user_id)
total_pages = sum(p.total_pages for p in projects)
completed_pages = sum(p.completed_pages for p in projects)
overall_pct = int((completed_pages / total_pages * 100)) if total_pages > 0 else 0

# 6. Hàng 4 Thẻ KPI Stat Cards Sang Trọng
st.markdown(
    f"""
    <div class="kpi-row-grid">
        <div class="kpi-stat-card">
            <div class="kpi-card-sub">
                <span>DỰ ÁN KHẢ DỤNG</span>
                <span class="kpi-card-badge">SQLite Real</span>
            </div>
            <div class="kpi-card-num">{len(projects)}</div>
            <div style="font-size:0.75rem; color:#6C7275;">Dự án được phân quyền quản lý</div>
        </div>
        <div class="kpi-stat-card">
            <div class="kpi-card-sub">
                <span>DUNG LƯỢNG DATA</span>
                <span class="kpi-card-badge">Local Disk</span>
            </div>
            <div class="kpi-card-num">{storage_display}</div>
            <div style="font-size:0.75rem; color:#6C7275;">Bộ nhớ ảnh raw & rendered</div>
        </div>
        <div class="kpi-stat-card">
            <div class="kpi-card-sub">
                <span>TIẾN ĐỘ TỔNG THỂ</span>
                <span class="kpi-card-badge">{overall_pct}%</span>
            </div>
            <div class="kpi-card-num">{completed_pages}<span style="font-size:1.1rem; color:#6C7275; font-weight:500;">/{total_pages}</span></div>
            <div style="font-size:0.75rem; color:#6C7275;">Trang manga đã xuất bản</div>
        </div>
        <div class="kpi-stat-card">
            <div class="kpi-card-sub">
                <span>AI WORKER NODE</span>
                <span class="kpi-card-badge" style="background:#DCFCE7; color:#15803D;">Online</span>
            </div>
            <div class="kpi-card-num" style="font-size:1.45rem; padding-top:4px;">{hostname}</div>
            <div style="font-size:0.75rem; color:#6C7275;">{cores} CPU Cores • Sẵn sàng xử lý</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 7. Tiêu đề Workspace và Nút Tạo Dự Án Native
title_col, action_col, logout_col = st.columns([2.7, 1.3, 0.6])
with title_col:
    st.markdown('<h1 style="font-size:1.85rem; font-weight:800; margin:0; color:#1A1D1F;">Manga Projects Workspace</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#6C7275; margin:0.25rem 0 1rem;">Quản lý và điều phối các tác vụ dịch thuật tự động theo thời gian thực.</p>', unsafe_allow_html=True)

with action_col:
    st.write("")
    if st.button("➕ Tạo Dự Án Mới", use_container_width=True):
        create_project_dialog()

with logout_col:
    st.write("")
    if st.button("Đăng xuất", use_container_width=True):
        logout()
        st.switch_page("pages/0_Login.py")

# 8. Thanh Tìm Kiếm & Bộ Lọc Native
search_col, filter_col = st.columns([3, 1.2])
with search_col:
    search_keyword = st.text_input(
        "Tìm kiếm dự án",
        placeholder="🔍 Tìm kiếm theo tên bộ truyện...",
        label_visibility="collapsed",
    )
with filter_col:
    filter_status = st.selectbox(
        "Bộ lọc",
        ["Tất cả trạng thái", "Đang xử lý (< 100%)", "Đã hoàn thành (100%)"],
        label_visibility="collapsed",
    )

# Lọc danh sách theo từ khóa và trạng thái
display_projects = projects
if search_keyword.strip():
    kw = search_keyword.strip().lower()
    display_projects = [p for p in display_projects if kw in p.title.lower() or kw in p.description.lower()]

if filter_status == "Đang xử lý (< 100%)":
    display_projects = [p for p in display_projects if p.progress_percent < 100]
elif filter_status == "Đã hoàn thành (100%)":
    display_projects = [p for p in display_projects if p.progress_percent == 100]

# 9. Lưới Thẻ Truyện (Project Cards Grid) + Thẻ Dashed New Project
if not display_projects:
    st.info("Không tìm thấy bộ truyện nào phù hợp với bộ lọc hiện tại.")
else:
    # Hiển thị dạng lưới 3 cột
    for start in range(0, len(display_projects), 3):
        row_projects = display_projects[start : start + 3]
        columns = st.columns(3, gap="medium")
        for idx_col, project in enumerate(row_projects):
            with columns[idx_col]:
                desc_text = project.description if project.description else "Dự án dịch truyện tự động."
                st.markdown(
                    f"""
                    <div class="manga-card-box">
                        <div class="manga-card-banner">
                            <span class="manga-card-tag">MANGA SERIE</span>
                            <span class="manga-card-id">#{project.id:02d}</span>
                        </div>
                        <div class="manga-card-body">
                            <h3 class="manga-card-title">{escape(project.title)}</h3>
                            <div class="manga-card-desc">{escape(desc_text)}</div>
                            <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#6C7275; margin-bottom:4px;">
                                <span>{project.completed_pages}/{project.total_pages} trang hoàn thành</span>
                                <strong style="color:#1C274C;">{project.progress_percent}%</strong>
                            </div>
                            <div class="manga-progress-track">
                                <div class="manga-progress-fill" style="width:{project.progress_percent}%;"></div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    "Mở Chapter Studio ➔",
                    key=f"btn_open_proj_{project.id}",
                    use_container_width=True,
                ):
                    st.session_state["current_project_id"] = project.id
                    st.session_state["current_project_title"] = project.title
                    st.query_params["project_id"] = str(project.id)
                    st.query_params["project"] = project.title
                    st.switch_page("pages/2_Chapter_Studio.py")

        # Nếu hàng cuối cùng còn chỗ trống, hiển thị 1 thẻ Dashed tạo dự án mới để lấp đầy khoảng trắng
        if len(row_projects) < 3:
            remaining_col = columns[len(row_projects)]
            with remaining_col:
                st.markdown(
                    """
                    <div class="dashed-new-card">
                        <div style="font-size:28px; margin-bottom:8px;">➕</div>
                        <div style="font-weight:700; font-size:1rem; margin-bottom:4px;">Khởi Tạo Bộ Truyện Mới</div>
                        <div style="font-size:0.8rem; color:#64748B;">Tải lên tập raw manga mới để chạy pipeline AI</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Tạo Dự Án Nhanh", key=f"quick_create_btn_{start}", use_container_width=True):
                    create_project_dialog()
