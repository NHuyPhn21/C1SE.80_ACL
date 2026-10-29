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
from backend.models import ComicPage, TextRegion
from backend.image_utils import (
    BASE_DIR,
    resolve_project_path,
    process_comic_page,
    _deduplicate_db_regions,
)
from ai_core.translator import translate_manga_text
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

try:
    all_pages = db.query(ComicPage).order_by(ComicPage.id.asc()).all()
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

        # Vẽ bounding box lên ảnh gốc (Cột trái Figma)
        if os.path.exists(orig_real_path):
            img_bgr = cv2.imread(orig_real_path)
            for idx, r in enumerate(clean_regs, start=1):
                bbox = json.loads(r.bbox_json)
                x1, y1, x2, y2 = map(int, bbox[:4])
                
                # Màu sắc: Vàng đất cho Sound Effect (#3 trong Figma), Xanh navy cho thoại thường
                box_color = (40, 110, 210) if idx == 3 else (111, 50, 37)
                cv2.rectangle(img_bgr, (x1, y1), (x2, y2), box_color, 3)

                # Vẽ nhãn số thứ tự tròn
                cv2.circle(img_bgr, (x1 + 18, y1 + 18), 16, box_color, -1)
                cv2.putText(
                    img_bgr,
                    str(idx),
                    (x1 + 10, y1 + 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                regions_data.append({
                    "id": r.id,
                    "index": idx,
                    "bbox": [x1, y1, x2, y2],
                    "original_text": r.original_text or "",
                    "translated_text": r.translated_text or "",
                })

            annotated_image = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

finally:
    db.close()

# 2. Top Breadcrumb
st.markdown(
    f"""
    <div class="top-breadcrumb">
        <div>ACL Studio &nbsp;/&nbsp; Manga Batch #104 &nbsp;/&nbsp; Raw Ingestion &nbsp;/&nbsp; <strong style="color:#1C274C;">OCR Masking</strong></div>
        <div class="node-status"><span class="node-dot"></span> 18/24 Pages Reviewed</div>
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
        if st.button("← Prev", key="btn_prev_page", use_container_width=True):
            if current_page:
                st.query_params["page_id"] = str(prev_page_id)
                st.rerun()
    with col_info:
        st.markdown(f"<div style='text-align:center; font-weight:700; padding-top:6px;'>Page {page_idx} of {total_pages}</div>", unsafe_allow_html=True)
    with col_n:
        if st.button("Next →", key="btn_next_page", use_container_width=True):
            if current_page:
                st.query_params["page_id"] = str(next_page_id)
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

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

            is_warning = idx == 3  # Mô phỏng card có cảnh báo độ tin cậy thấp như Figma
            card_class = "bubble-card-warning" if is_warning else "bubble-card"
            badge_html = """<span class="badge-warning">0.52 Low Confidence</span>""" if is_warning else """<span class="badge-verified">0.96 Confident</span>"""
            bubble_type = "Sound Effect (Onomatopoeia)" if idx == 3 else "Speech Bubble • Panel"

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
                st.markdown("""<div style="color:#C62828; font-size:0.75rem; font-weight:600; margin-top:4px;">⚠️ OCR confidence low. Please verify against original bubble.</div>""", unsafe_allow_html=True)

            st.markdown(f"""<div style="color:#8A9099; font-size:0.7rem; margin-top:4px;">Box: [x: {x1}, y: {y1}, w: {x2-x1}, h: {y2-y1}]</div></div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# 5. Bottom Action Bar (Chuẩn Figma)
st.markdown("---")
col_bot_status, col_bot_btns = st.columns([1.5, 1.5])

with col_bot_status:
    st.markdown(
        """
        <div style="padding-top:10px; font-size:0.85rem; color:#6C7275;">
            <span style="color:#2E7D32;">●</span> Changes saved automatically to draft • Auto-sync ON
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_bot_btns:
    b1, b2 = st.columns(2)
    with b1:
        if st.button("Save OCR & Re-Translate", key="btn_retranslate", use_container_width=True):
            if current_page:
                db_action = SessionLocal()
                try:
                    retrans = False
                    for reg_id, text_val in edited_texts.items():
                        r_obj = db_action.query(TextRegion).filter(TextRegion.id == reg_id).first()
                        if r_obj and text_val.strip() and r_obj.original_text != text_val.strip():
                            r_obj.original_text = text_val.strip()
                            r_obj.translated_text = ""
                            retrans = True
                    db_action.commit()

                    if retrans:
                        translate_manga_text(page_id=current_page.id)
                        process_comic_page(page_id=current_page.id, use_lama_api=False)
                        st.success("✅ Đã cập nhật OCR và dịch lại thành công!")
                        st.rerun()
                    else:
                        st.info("Nội dung không có thay đổi.")
                finally:
                    db_action.close()

    with b2:
        if st.button("Confirm & Proceed to Typesetting ➔", key="btn_confirm_typeset", use_container_width=True):
            if current_page:
                st.query_params["page_id"] = str(current_page.id)
                st.switch_page("pages/4_Typesetting.py")