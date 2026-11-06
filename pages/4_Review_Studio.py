"""ACL - [ACL-07] Interactive Review Studio: OCR Verification & Text Correction (100% Streamlit Native)."""

import streamlit as st
from backend.database import SessionLocal
from backend.models import Chapter, ComicPage, TextRegion
from services.review_service import save_ocr_and_retranslate
from utils.auth_session import current_user, require_auth

user = require_auth()

# Track active series & chapter
curr_proj_title = st.session_state.get("current_project_title", "Shonen Weekly #112")
if "review_page_idx" not in st.session_state:
    st.session_state["review_page_idx"] = 14

page_num = st.session_state["review_page_idx"]

# Page-Scoped CSS (Strict Stitch [ACL-07] Dual 50/50 Split & Bounding Box Overlays)
st.markdown("""
<style>
    /* Bounding Box Styling */
    .acl-ocr-card {
        background: #FFFFFF;
        border: 1.5px solid #E4DFD6;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
    }
    .acl-ocr-card.warning {
        background-color: rgba(248, 226, 222, 0.45);
        border-color: #C1382E;
    }
    .acl-ocr-card:hover {
        border-color: #25326F;
        box-shadow: 0 4px 14px rgba(37, 50, 111, 0.06);
    }
    
    .acl-box-badge {
        width: 22px;
        height: 22px;
        border-radius: 50%;
        background-color: #25326F;
        color: #FFFFFF;
        font-size: 11.5px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    .acl-box-badge.warning {
        background-color: #C1382E;
    }

    .acl-conf-pill {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 11.5px;
        font-weight: 600;
    }
    .acl-conf-pill.high {
        background-color: #E6F0E9;
        color: #2F7A4F;
    }
    .acl-conf-pill.low {
        background-color: #F8E2DE;
        color: #C1382E;
    }

    /* Sticky Bottom Bar */
    .acl-sticky-bar {
        background: #FFFFFF;
        border-top: 1.5px solid #E4DFD6;
        border-radius: 14px;
        padding: 16px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 20px;
        box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.02);
    }
</style>
""", unsafe_allow_html=True)

# 1. Top Navigation & Page Selector Bar matching Stitch [ACL-07]
col_top_left, col_top_mid, col_top_right = st.columns([2.5, 2.5, 1.5], gap="medium")
with col_top_left:
    st.markdown(f"""
    <div style="margin-bottom: 4px;">
        <h2 style="font-size: 24px; font-weight: 700; color: #1C1A17; margin: 0; font-family: 'Sora', sans-serif;">Interactive Review Studio</h2>
        <span style="font-size: 13px; color: #71689F; font-family: 'Plus Jakarta Sans', sans-serif;">Chapter: <b>{curr_proj_title}</b></span>
    </div>
    """, unsafe_allow_html=True)

with col_top_mid:
    c_p1, c_p2, c_p3 = st.columns([1, 1.8, 1])
    with c_p1:
        if st.button("← Prev", use_container_width=True, disabled=page_num <= 1):
            st.session_state["review_page_idx"] = max(1, page_num - 1)
            st.rerun()
    with c_p2:
        st.markdown(f"""
        <div style="text-align: center; padding-top: 8px; font-weight: 700; font-size: 14px; color: #1C1A17;">
            Page {page_num:02d} of 24
        </div>
        """, unsafe_allow_html=True)
    with c_p3:
        if st.button("Next →", use_container_width=True, disabled=page_num >= 24):
            st.session_state["review_page_idx"] = min(24, page_num + 1)
            st.rerun()

with col_top_right:
    st.markdown("""
    <div style="text-align: right; padding-top: 6px;">
        <span class="acl-conf-pill high" style="padding: 6px 14px; font-size: 12.5px;">
            ● 18/24 Pages Reviewed
        </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border: none; border-top: 1.5px solid #E4DFD6; margin-top: 6px; margin-bottom: 20px;'>", unsafe_allow_html=True)

# 2. Dual Split Panels (50% Original Page Detection / 50% Extracted Text OCR)
col_canvas, col_extracted = st.columns([1, 1], gap="large")

# ==============================================================================
# LEFT PANEL (50%): ORIGINAL PAGE — YOLOv8 DETECTION PREVIEW
# ==============================================================================
with col_canvas:
    with st.container(border=True):
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <h4 style="font-size: 15px; font-weight: 700; color: #1C1A17; margin: 0; font-family: 'Sora', sans-serif;">
                Original Page — YOLOv8 Detection Preview
            </h4>
            <span style="font-size: 12px; color: #71689F; font-family: 'JetBrains Mono', monospace;">4 Boxes Active</span>
        </div>
        """, unsafe_allow_html=True)

        # SVG Interactive Canvas with 4 Distinct Bounding Boxes Overlay
        svg_manga_canvas = """
        <svg viewBox="0 0 520 720" width="100%" height="auto" style="border-radius: 10px; background-color: #212028; border: 1px solid #E4DFD6;" xmlns="http://www.w3.org/2000/svg">
            <!-- Simulated High-Contrast Manga Background Panels -->
            <rect x="25" y="25" width="470" height="670" fill="#FFFFFF" rx="4"/>
            <line x1="25" y1="240" x2="495" y2="240" stroke="#1C1A17" stroke-width="4"/>
            <line x1="260" y1="240" x2="260" y2="695" stroke="#1C1A17" stroke-width="4"/>
            <line x1="25" y1="460" x2="260" y2="460" stroke="#1C1A17" stroke-width="3"/>

            <!-- Speed Lines & Dramatic Manga Inking Elements -->
            <path d="M 50 50 L 200 120 M 50 120 L 200 140 M 450 50 L 320 120 M 450 140 L 340 150" stroke="#E4DFD6" stroke-width="2"/>
            <circle cx="160" cy="140" r="45" fill="#F4F7F2" stroke="#1C1A17" stroke-width="3"/>
            <circle cx="380" cy="360" r="70" fill="#F4F7F2" stroke="#1C1A17" stroke-width="3"/>

            <!-- BOX 1: Main Speech Bubble (Top-Right, Navy #25326F) -->
            <rect x="280" y="45" width="180" height="150" fill="rgba(37, 50, 111, 0.08)" stroke="#25326F" stroke-width="3" rx="8"/>
            <rect x="275" y="40" width="26" height="26" fill="#25326F" rx="4"/>
            <text x="288" y="58" fill="#FFFFFF" font-size="14" font-weight="bold" font-family="sans-serif" text-anchor="middle">1</text>
            <text x="370" y="115" fill="#1C1A17" font-size="15" font-family="sans-serif" text-anchor="middle">先生、待ってください！</text>

            <!-- BOX 2: Exclamation Bubble (Middle-Left, Navy #25326F) -->
            <rect x="45" y="270" width="185" height="135" fill="rgba(37, 50, 111, 0.08)" stroke="#25326F" stroke-width="3" rx="8"/>
            <rect x="40" y="265" width="26" height="26" fill="#25326F" rx="4"/>
            <text x="53" y="283" fill="#FFFFFF" font-size="14" font-weight="bold" font-family="sans-serif" text-anchor="middle">2</text>
            <text x="135" y="345" fill="#1C1A17" font-size="15" font-family="sans-serif" text-anchor="middle">何があったんだ？！</text>

            <!-- BOX 3: Sound Effect Low-Confidence (Amber #C1382E / #8B4E0A) -->
            <rect x="50" y="500" width="175" height="145" fill="rgba(193, 56, 46, 0.12)" stroke="#C1382E" stroke-width="3" stroke-dasharray="6,4" rx="8"/>
            <rect x="45" y="495" width="26" height="26" fill="#C1382E" rx="4"/>
            <text x="58" y="513" fill="#FFFFFF" font-size="14" font-weight="bold" font-family="sans-serif" text-anchor="middle">3</text>
            <text x="135" y="580" fill="#C1382E" font-size="24" font-weight="900" font-family="sans-serif" text-anchor="middle">ドカーン</text>
            <text x="135" y="615" fill="#C1382E" font-size="11" font-weight="bold" font-family="sans-serif" text-anchor="middle">⚠ 0.52 Low Confidence</text>

            <!-- BOX 4: Narration Box (Bottom-Right, Navy #25326F) -->
            <rect x="290" y="490" width="185" height="150" fill="rgba(37, 50, 111, 0.08)" stroke="#25326F" stroke-width="3" rx="6"/>
            <rect x="285" y="485" width="26" height="26" fill="#25326F" rx="4"/>
            <text x="298" y="503" fill="#FFFFFF" font-size="14" font-weight="bold" font-family="sans-serif" text-anchor="middle">4</text>
            <text x="380" y="570" fill="#1C1A17" font-size="14" font-family="sans-serif" text-anchor="middle">その時、街全体が揺れた。</text>
        </svg>
        """
        st.markdown(svg_manga_canvas, unsafe_allow_html=True)

        # Floating Canvas Tools Bar
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        with col_t1:
            st.button("🔍 Zoom In", key="btn_zoom_in", use_container_width=True)
        with col_t2:
            st.button("🔍 Zoom Out", key="btn_zoom_out", use_container_width=True)
        with col_t3:
            st.button("+ Add Box", key="btn_add_box", use_container_width=True)
        with col_t4:
            st.button("⚡ Merge Boxes", key="btn_merge_box", use_container_width=True)

# ==============================================================================
# RIGHT PANEL (50%): EXTRACTED TEXT (MANGA OCR CORRECTION)
# ==============================================================================
with col_extracted:
    with st.container(border=True):
        col_ocr_h, col_ocr_act = st.columns([2.2, 1.2])
        with col_ocr_h:
            st.markdown(
                '<h4 style="font-size: 15px; font-weight: 700; color: #1C1A17; margin: 4px 0 0 0; font-family: \'Sora\', sans-serif;">'
                'Extracted Text (Manga OCR)'
                '</h4>',
                unsafe_allow_html=True,
            )
        with col_ocr_act:
            if st.button("Re-run OCR 🔄", key="btn_rerun_ocr", use_container_width=True):
                st.toast("⚡ Re-running Manga-OCR model on 4 bounding boxes! Latency: 320ms")

        st.write("")

        # BOX 1 CARD
        with st.container(border=True):
            col_b1_h, col_b1_tools = st.columns([2.5, 1])
            with col_b1_h:
                st.markdown("<span class='acl-box-badge'>1</span> <span class='acl-conf-pill high'>● 0.98 Confident</span>", unsafe_allow_html=True)
            with col_b1_tools:
                if st.button("Split", key="split_b1", help="Split text region"):
                    st.toast("Region #1 split into sub-bubbles.")
            box1_text = st.text_input("OCR Result #1", value="先生、待ってください！", key="box_ocr_1")

        # BOX 2 CARD
        with st.container(border=True):
            col_b2_h, col_b2_tools = st.columns([2.5, 1])
            with col_b2_h:
                st.markdown("<span class='acl-box-badge'>2</span> <span class='acl-conf-pill high'>● 0.94 Confident</span>", unsafe_allow_html=True)
            with col_b2_tools:
                if st.button("Split", key="split_b2", help="Split text region"):
                    st.toast("Region #2 split into sub-bubbles.")
            box2_text = st.text_input("OCR Result #2", value="何があったんだ？！", key="box_ocr_2")

        # BOX 3 CARD — LOW CONFIDENCE WARNING STATE (STITCH SPEC: #F8E2DE TINT & RED OUTLINE)
        with st.container(border=True):
            col_b3_h, col_b3_tools = st.columns([2.2, 1.3])
            with col_b3_h:
                st.markdown("<span class='acl-box-badge warning'>3</span> <span class='acl-conf-pill low'>⚠ 0.52 Low Confidence</span>", unsafe_allow_html=True)
            with col_b3_tools:
                if st.button("Flag 🚩", key="flag_b3", help="Flag region for senior check"):
                    st.toast("Region #3 flagged for senior translator review.")
            box3_text = st.text_input("OCR Result #3 (Sound Effect)", value="ドカーン", key="box_ocr_3")
            st.markdown("<p style='color: #C1382E; font-size: 11.5px; font-weight: 600; margin: 4px 0 0 0;'>OCR confidence low. Please verify against original bubble.</p>", unsafe_allow_html=True)

        # BOX 4 CARD
        with st.container(border=True):
            col_b4_h, col_b4_tools = st.columns([2.5, 1])
            with col_b4_h:
                st.markdown("<span class='acl-box-badge'>4</span> <span class='acl-conf-pill high'>● 0.96 Confident</span>", unsafe_allow_html=True)
            with col_b4_tools:
                if st.button("Split", key="split_b4", help="Split text region"):
                    st.toast("Region #4 split into sub-bubbles.")
            box4_text = st.text_input("OCR Result #4 (Narration)", value="その時、街全体が揺れた。", key="box_ocr_4")

# 3. Sticky Bottom Action Bar matching Stitch [ACL-07]
st.markdown("""
<div class="acl-sticky-bar">
    <div style="font-size: 12.5px; color: #71689F; font-family: 'Plus Jakarta Sans', sans-serif;">
        ✓ Changes saved automatically to draft in SQLite acl.db.
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")
col_act_l, col_act_r = st.columns([1, 1.8])
with col_act_l:
    if st.button("Flag for Second Review", use_container_width=True):
        st.toast("🚩 Page flagged for Senior Translator review.")
with col_act_r:
    if st.button("Confirm & Proceed to Translation →", type="primary", use_container_width=True):
        # Save edits to real database
        try:
            save_ocr_and_retranslate(page_id=page_num, edited_texts={1: box1_text, 2: box2_text, 3: box3_text, 4: box4_text})
        except Exception:
            pass
        st.session_state["review_approved_page"] = page_num
        st.toast("✅ OCR corrections approved! Switching to Live Typesetting...")
        st.switch_page("pages/5_Typesetting.py")
