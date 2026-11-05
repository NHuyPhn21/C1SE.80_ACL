"""ACL Interactive Review Studio — Figma Design Implemented (Native Streamlit + SQLite)."""

import json
import os
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import streamlit as st

from utils.auth_session import require_auth
from backend.database import SessionLocal
from backend.models import Chapter, ComicPage, Project, TextRegion
from backend.image_utils import (
    resolve_project_path,
    _deduplicate_db_regions,
)
from services.review_service import (
    ReviewServiceError,
    confirm_review_and_translate,
    flag_page_for_second_review,
    save_ocr_draft,
)
from utils.page_navigation import render_page_navigation

user = require_auth()
render_page_navigation()

project_name = st.query_params.get("project", "Shonen Weekly #112")

# CSS chuẩn giao diện Figma
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

    /* Bounding Box Card */
    .bubble-card {
        background: #FAFAFA;
        border: 1px solid #EAEAEA;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 12px;
    }
    .bubble-card-warning {
        background: #FFF9F9;
        border: 1px solid #FFCDD2;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 12px;
    }
    .bubble-card, .bubble-card-warning {
        transition: border-color .2s ease, box-shadow .2s ease, transform .2s ease;
    }
    .bubble-card-selected {
        border: 2px solid #25326F;
        box-shadow: 0 8px 24px rgba(37,50,111,.14);
        transform: translateY(-1px);
    }

    .badge-verified {
        background: #E8F5E9;
        color: #2E7D32;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-warning {
        background: #FFEBEE;
        color: #C62828;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
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
reviewed_pages = 0
idx_pos = 0

try:
    page_query = (
        db.query(ComicPage)
        .join(Chapter, ComicPage.chapter_id == Chapter.id)
        .join(Project, Chapter.project_id == Project.id)
    )
    project_pages = (
        page_query.filter(Project.title == project_name)
        .order_by(ComicPage.id.asc())
        .all()
    )
    all_pages = project_pages or page_query.order_by(ComicPage.id.asc()).all()
    reviewed_pages = sum(
        1 for page in all_pages
        if page.status in {"REVIEWED", "COMPLETED"} or bool(page.rendered_path)
    )
    req_page_id = st.query_params.get("page_id")
    req_page_name = st.query_params.get("page_name")

    if req_page_id and str(req_page_id).isdigit():
        current_page = db.query(ComicPage).filter(ComicPage.id == int(req_page_id)).first()
    elif req_page_name:
        current_page = db.query(ComicPage).filter(ComicPage.original_path.like(f"%{req_page_name}%")).first()

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

    regions_data = []
    annotated_image = None
    orig_real_path = ""

    if current_page:
        orig_real_path = resolve_project_path(current_page.original_path)
        raw_regs = db.query(TextRegion).filter(TextRegion.page_id == current_page.id).all()
        clean_regs = _deduplicate_db_regions(raw_regs) if raw_regs else []
        if not clean_regs and raw_regs:
            clean_regs = raw_regs

        for idx, r in enumerate(clean_regs, start=1):
            bbox = json.loads(r.bbox_json)
            x1, y1, x2, y2 = map(int, bbox[:4])
            regions_data.append({
                    "id": r.id,
                    "index": idx,
                    "bbox": [x1, y1, x2, y2],
                    "original_text": r.original_text or "",
                    "translated_text": r.translated_text or "",
            })

finally:
    db.close()

# 2. Top Breadcrumb
st.markdown(
    f"""
    <div class="top-breadcrumb">
        <div>ACL Studio &nbsp;/&nbsp; Manga Batch #104 &nbsp;/&nbsp; Raw Ingestion &nbsp;/&nbsp; <strong style="color:#1C274C;">OCR Masking</strong></div>
        <div class="node-status"><span class="node-dot"></span> {reviewed_pages}/{total_pages} Pages Reviewed</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 3. Tiêu đề chính & Thanh Pagination
c_head, c_nav = st.columns([1.8, 1.2])
with c_head:
    page_filename = os.path.basename(orig_real_path) if orig_real_path else "Unknown"
    st.markdown(
        f"""
        <div style="margin-bottom:1rem;">
            <h1 style="font-size:1.85rem; font-weight:800; margin:0; letter-spacing:-0.02em;">Interactive Review Studio</h1>
            <p style="color:#6C7275; font-size:0.875rem; margin-top:4px;">{project_name} — {page_filename} (Page ID: #{current_page.id if current_page else 0})</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c_nav:
    st.markdown("<div style='padding-top:0.5rem;'>", unsafe_allow_html=True)
    col_p, col_info, col_n = st.columns([1, 1.5, 1])
    with col_p:
        if st.button(
            "← Prev",
            key="btn_prev_page",
            use_container_width=True,
            disabled=not current_page or idx_pos == 0,
        ):
            if current_page:
                st.query_params["page_id"] = str(prev_page_id)
                st.rerun()
    with col_info:
        st.markdown(f"<div style='text-align:center; font-weight:700; padding-top:6px;'>Page {page_idx} of {total_pages}</div>", unsafe_allow_html=True)
    with col_n:
        if st.button(
            "Next →",
            key="btn_next_page",
            use_container_width=True,
            disabled=not current_page or idx_pos >= total_pages - 1,
        ):
            if current_page:
                st.query_params["page_id"] = str(next_page_id)
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

selected_region_id = regions_data[0]["id"] if regions_data else None
if regions_data:
    selected_region_id = st.radio(
        "Select a detected bubble to highlight",
        options=[item["id"] for item in regions_data],
        format_func=lambda region_id: next(
            f"Bubble #{item['index']}" for item in regions_data if item["id"] == region_id
        ),
        horizontal=True,
        key=f"selected_review_region_{current_page.id if current_page else 0}",
    )

if regions_data and os.path.exists(orig_real_path):
    img_bgr = cv2.imread(orig_real_path)
    for item in regions_data:
        x1, y1, x2, y2 = item["bbox"]
        is_selected = item["id"] == selected_region_id
        box_color = (52, 122, 47) if is_selected else (111, 50, 37)
        thickness = 6 if is_selected else 2
        cv2.rectangle(img_bgr, (x1, y1), (x2, y2), box_color, thickness)
        cv2.circle(img_bgr, (x1 + 18, y1 + 18), 16, box_color, -1)
        cv2.putText(
            img_bgr,
            str(item["index"]),
            (x1 + 10, y1 + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
    annotated_image = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

# 4. Workspace Split: Cột trái (Ảnh YOLOv8) & Cột phải (Danh sách OCR)
col_left, col_right = st.columns([1.1, 0.9], gap="large")

with col_left:
    st.markdown(
        """
        <div class="panel-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div style="font-weight:700; font-size:0.95rem;">🔍 Original Page — Detection Preview</div>
                <div style="background:#E8EDFB; color:#1C274C; padding:4px 10px; border-radius:6px; font-size:0.75rem; font-weight:600;">
                    Model: YOLOv8-Manga v2.1
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )
    if annotated_image is not None:
        st.image(annotated_image, use_container_width=True)
    else:
        st.info("Chưa có ảnh truyện để hiển thị.")
    st.markdown("</div>", unsafe_allow_html=True)

edited_texts = {}

with col_right:
    st.markdown(
        f"""
        <div class="panel-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div style="font-weight:700; font-size:0.95rem;">文A Extracted Text (Manga OCR)</div>
                <div style="color:#6C7275; font-size:0.8rem; font-weight:600;">{len(regions_data)} Bubbles Detected</div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    if not regions_data:
        st.info("Không phát hiện được bóng thoại nào trên trang này.")
    else:
        for item in regions_data:
            idx = item["index"]
            rid = item["id"]
            x1, y1, x2, y2 = item["bbox"]

            is_warning = not bool(item["original_text"].strip())
            card_class = "bubble-card-warning" if is_warning else "bubble-card"
            if rid == selected_region_id:
                card_class += " bubble-card-selected"
            badge_html = """<span class="badge-warning">Needs Transcription</span>""" if is_warning else """<span class="badge-verified">OCR Text Available</span>"""
            bubble_type = "Detected Text Region • Panel"

            st.markdown(
                f"""
                <div class="{card_class}">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                        <div><strong>#{idx}</strong> &nbsp;{bubble_type}</div>
                        {badge_html}
                    </div>
                """,
                unsafe_allow_html=True,
            )

            # Ô nhập liệu chỉnh sửa chữ tiếng Nhật
            new_val = st.text_input(
                label=f"Text for bubble #{idx}",
                value=item["original_text"],
                key=f"ocr_input_{rid}",
                label_visibility="collapsed",
            )
            edited_texts[rid] = new_val

            if item["translated_text"]:
                st.caption(f"🇻🇳 Dịch: *{item['translated_text']}*")

            if is_warning:
                st.markdown("""<div style="color:#C62828; font-size:0.75rem; font-weight:600; margin-top:4px;">⚠️ No OCR text is available. Please transcribe this region from the original page.</div>""", unsafe_allow_html=True)

            st.markdown(f"""<div style="color:#8A9099; font-size:0.7rem; margin-top:4px;">Box: [x: {x1}, y: {y1}, w: {x2-x1}, h: {y2-y1}]</div></div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

draft_changes = 0
draft_error = None
if current_page and edited_texts:
    try:
        draft_changes = save_ocr_draft(current_page.id, edited_texts)
    except ReviewServiceError as exc:
        draft_error = str(exc)

# 5. Bottom Action Bar (Chuẩn Figma)
st.markdown("---")
col_bot_status, col_bot_btns = st.columns([1.5, 1.5])

with col_bot_status:
    if draft_error:
        sync_label = f"Auto-sync failed: {draft_error}"
        sync_color = "#C62828"
    elif draft_changes:
        sync_label = f"{draft_changes} OCR correction(s) saved to draft • Auto-sync ON"
        sync_color = "#2E7D32"
    else:
        sync_label = "OCR draft synchronized with SQLite • Auto-sync ON"
        sync_color = "#2E7D32"
    st.markdown(
        f"""
        <div style="padding-top:10px; font-size:0.85rem; color:#6C7275;">
            <span style="color:{sync_color};">●</span> {sync_label}
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_bot_btns:
    b1, b2 = st.columns(2)
    with b1:
        if st.button("Flag for Second Review", key="btn_second_review", use_container_width=True):
            if current_page:
                try:
                    flag_page_for_second_review(current_page.id)
                    st.warning("Trang đã được đưa vào hàng chờ kiểm duyệt lần hai.")
                    st.rerun()
                except ReviewServiceError as exc:
                    st.error(str(exc))

    with b2:
        if st.button("Confirm & Proceed to Translation ➔", key="btn_confirm_translate", use_container_width=True):
            if current_page:
                try:
                    confirm_review_and_translate(current_page.id, edited_texts)
                    st.query_params["page_id"] = str(current_page.id)
                    st.switch_page("pages/4_Typesetting.py")
                except ReviewServiceError as exc:
                    st.error(str(exc))
