"""ACL Typesetting Studio — Clean Native Streamlit + Real-Time Re-rendering."""

import json
import os
from pathlib import Path
from PIL import Image
import streamlit as st

from utils.auth_session import require_auth
from backend.database import SessionLocal
from backend.models import ComicPage, TextRegion
from backend.image_utils import (
    BASE_DIR,
    resolve_project_path,
    process_comic_page,
    _deduplicate_db_regions,
)
from utils.page_navigation import render_page_navigation

user = require_auth()
render_page_navigation()

project_name = st.query_params.get("project", "Shonen Weekly #112")

# Tùy biến CSS giao diện đồng bộ Figma
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #F8F9FA !important;
        color: #1A1D1F !important;
    }

    .top-breadcrumb {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-top: 0.5rem;
        padding-bottom: 0.75rem;
        font-size: 0.85rem;
        color: #6C7275;
    }
    .node-status {
        background-color: #E8F5E9;
        color: #2E7D32;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .node-dot {
        width: 8px;
        height: 8px;
        background-color: #2E7D32;
        border-radius: 50%;
    }

    .panel-card {
        background: #FFFFFF;
        border: 1px solid #EAEAEA;
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.02);
    }

    .inspector-box {
        background: #FAFAFA;
        border: 1px solid #EAEAEA;
        border-radius: 12px;
        padding: 14px 16px;
        margin-top: 10px;
    }

    /* Primary Buttons */
    div.stButton > button:first-child {
        border-radius: 9999px !important;
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 1. Truy vấn thông tin trang từ SQLite
db = SessionLocal()
all_pages = []
current_page = None
page_idx = 1
total_pages = 1

try:
    all_pages = db.query(ComicPage).order_by(ComicPage.id.asc()).all()
    req_page_id = st.query_params.get("page_id")

    if req_page_id and str(req_page_id).isdigit():
        current_page = db.query(ComicPage).filter(ComicPage.id == int(req_page_id)).first()

    if not current_page and all_pages:
        current_page = all_pages[-1]

    if current_page and all_pages:
        page_ids = [p.id for p in all_pages]
        if current_page.id in page_ids:
            idx_pos = page_ids.index(current_page.id)
            page_idx = idx_pos + 1
            prev_page_id = page_ids[max(0, idx_pos - 1)]
            next_page_id = page_ids[min(len(page_ids) - 1, idx_pos + 1)]
        total_pages = len(all_pages)

    rendered_img_path = ""
    orig_img_path = ""
    regions_list = []
    page_filename = "Unknown"

    if current_page:
        orig_real = resolve_project_path(current_page.original_path)
        page_filename = os.path.basename(orig_real)
        orig_img_path = orig_real

        # Tìm ảnh đã render tiếng Việt
        cand_path = BASE_DIR / "data" / "rendered_pages" / f"final_{page_filename}"
        if current_page.rendered_path and os.path.exists(resolve_project_path(current_page.rendered_path)):
            rendered_img_path = resolve_project_path(current_page.rendered_path)
        elif cand_path.exists():
            rendered_img_path = str(cand_path)
        else:
            rendered_img_path = orig_real

        raw_regs = db.query(TextRegion).filter(TextRegion.page_id == current_page.id).all()
        clean_regs = _deduplicate_db_regions(raw_regs) if raw_regs else []
        if not clean_regs and raw_regs:
            clean_regs = raw_regs

        for idx, r in enumerate(clean_regs, start=1):
            regions_list.append({
                "id": r.id,
                "index": idx,
                "original_text": r.original_text or "",
                "translated_text": r.translated_text or "",
            })

finally:
    db.close()

# 2. Top Breadcrumb
st.markdown(
    f"""
    <div class="top-breadcrumb">
        <div>ACL Studio &nbsp;/&nbsp; Manga Batch #104 &nbsp;/&nbsp; Post-Processing &nbsp;/&nbsp; <strong style="color:#1C274C;">Live Typesetting Studio</strong></div>
        <div class="node-status"><span class="node-dot"></span> Collision Avoidance Matrix: Active</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 3. Main Header & Pagination Strip
c_head, c_nav = st.columns([1.8, 1.2])
with c_head:
    st.markdown(
        f"""
        <div style="margin-bottom:1rem;">
            <h1 style="font-size:1.85rem; font-weight:800; margin:0; letter-spacing:-0.02em;">Live Typesetting Studio</h1>
            <p style="color:#6C7275; font-size:0.875rem; margin-top:4px;">{project_name} — final_{page_filename} (Page ID: #{current_page.id if current_page else 0})</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c_nav:
    st.markdown("<div style='padding-top:0.5rem;'>", unsafe_allow_html=True)
    col_p, col_info, col_n = st.columns([1, 1.5, 1])
    with col_p:
        if st.button("← Prev", key="btn_prev_ts", use_container_width=True):
            if current_page:
                st.query_params["page_id"] = str(prev_page_id)
                st.rerun()
    with col_info:
        st.markdown(f"<div style='text-align:center; font-weight:700; padding-top:6px;'>Page {page_idx} of {total_pages}</div>", unsafe_allow_html=True)
    with col_n:
        if st.button("Next →", key="btn_next_ts", use_container_width=True):
            if current_page:
                st.query_params["page_id"] = str(next_page_id)
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# 4. Workspace Split: Cột trái (Canvas xem ảnh) & Cột phải (Inspector chỉnh chữ)
col_canvas, col_inspector = st.columns([1.1, 0.9], gap="large")

with col_canvas:
    st.markdown(
        """
        <div class="panel-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div style="font-weight:700; font-size:0.95rem;">🖼️ Rendered Output Canvas</div>
                <div style="color:#6C7275; font-size:0.8rem; font-weight:600;">Engine: Telea + HLcomic1</div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    # Chế độ so sánh ảnh gốc
    show_original = st.toggle("So sánh với bản tiếng Nhật gốc", value=False)
    target_img_to_show = orig_img_path if (show_original and os.path.exists(orig_img_path)) else rendered_img_path

    if target_img_to_show and os.path.exists(target_img_to_show):
        st.image(target_img_to_show, use_container_width=True)
    else:
        st.info("Chưa có ảnh kết quả.")
    st.markdown("</div>", unsafe_allow_html=True)

with col_inspector:
    st.markdown(
        """
        <div class="panel-card">
            <div style="font-weight:700; font-size:0.95rem; margin-bottom:4px;">✏️ Typography & Dialogue Inspector</div>
            <p style="color:#6C7275; font-size:0.8rem; margin:0 0 12px 0;">Chọn bóng thoại cần sửa lại câu chữ tiếng Việt và bấm vẽ lại.</p>
        """,
        unsafe_allow_html=True,
    )

    if not regions_list:
        st.info("Trang này chưa có dữ liệu bóng thoại.")
    else:
        bubble_options = {
            f"Bóng thoại #{item['index']} — {item['translated_text'][:25]}...": item
            for item in regions_list
        }
        selected_bubble_label = st.selectbox(
            "Chọn bóng thoại trên trang:",
            options=list(bubble_options.keys()),
            key="sel_bubble",
        )
        selected_item = bubble_options[selected_bubble_label]

        st.markdown(
            f"""
            <div class="inspector-box">
                <div style="font-size:0.75rem; color:#6C7275; font-weight:700; text-transform:uppercase;">Tiếng Nhật gốc (Manga OCR)</div>
                <div style="padding:8px 0; font-size:0.9rem; font-weight:600; color:#1C274C;">{selected_item['original_text']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='margin-top:10px;'>", unsafe_allow_html=True)
        new_vi_text = st.text_area(
            "Lời thoại tiếng Việt (Có thể chỉnh sửa):",
            value=selected_item["translated_text"],
            height=120,
            key=f"vi_input_{selected_item['id']}",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Nút Re-render ảnh tức thì
        if st.button("⚡ Lưu & Vẽ lại trang (Re-Render Now)", use_container_width=True):
            if current_page:
                db_action = SessionLocal()
                try:
                    r_target = db_action.query(TextRegion).filter(TextRegion.id == selected_item["id"]).first()
                    if r_target:
                        r_target.translated_text = new_vi_text.strip()
                        db_action.commit()

                    # Kích hoạt inpainting và căn chữ lại
                    updated_final = process_comic_page(page_id=current_page.id, use_lama_api=False)
                    p_obj = db_action.query(ComicPage).filter(ComicPage.id == current_page.id).first()
                    if p_obj and updated_final:
                        p_obj.rendered_path = str(Path(updated_final).relative_to(BASE_DIR)).replace("\\", "/")
                        p_obj.status = "COMPLETED"
                        db_action.commit()

                    st.success("✅ Đã cập nhật câu thoại và vẽ lại trang thành công!")
                    st.rerun()
                finally:
                    db_action.close()

    st.markdown("</div>", unsafe_allow_html=True)

# 5. Thanh công cụ dưới cùng
st.markdown("---")
col_b1, col_b2, col_b3 = st.columns([1.5, 1, 1])

with col_b1:
    st.caption("Bản dịch được lưu tại thư mục: `data/rendered_pages/`")

with col_b2:
    if st.button("← Quay lại Review OCR", key="btn_back_rev", use_container_width=True):
        if current_page:
            st.query_params["page_id"] = str(current_page.id)
            st.switch_page("pages/2_Review_Studio.py")

with col_b3:
    if st.button("Xem trên Queue Monitor ➔", key="btn_go_queue", use_container_width=True):
        st.switch_page("pages/5_Queue_Monitor.py")