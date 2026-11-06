"""ACL - [ACL-08] Live Typesetting Editor: Speech Bubble Typography Studio (100% Streamlit Native)."""

import streamlit as st
from utils.auth_session import current_user, require_auth

user = require_auth()

curr_proj_title = st.session_state.get("current_project_title", "Shonen Weekly #112")
page_idx = st.session_state.get("review_approved_page", 14)

# Typography state
if "typeset_font" not in st.session_state:
    st.session_state["typeset_font"] = "CC Wild Words"
if "typeset_size" not in st.session_state:
    st.session_state["typeset_size"] = 14
if "typeset_align" not in st.session_state:
    st.session_state["typeset_align"] = "Center"
if "typeset_text" not in st.session_state:
    st.session_state["typeset_text"] = "Thầy ơi, xin hãy đợi em với!"
if "typeset_bold" not in st.session_state:
    st.session_state["typeset_bold"] = True
if "typeset_italic" not in st.session_state:
    st.session_state["typeset_italic"] = False
if "typeset_caps" not in st.session_state:
    st.session_state["typeset_caps"] = False

# Page-Scoped CSS (Strict Stitch [ACL-08] Inpainted Canvas & Typography Controls)
st.markdown("""
<style>
    .acl-bubble-selected {
        border: 2px solid #25326F !important;
        position: relative;
    }
    .acl-bubble-handle {
        width: 8px;
        height: 8px;
        background-color: #25326F;
        border: 1px solid #FFFFFF;
        position: absolute;
    }
</style>
""", unsafe_allow_html=True)

# 1. Header Bar matching Stitch [ACL-08]
col_head, col_pages_nav = st.columns([3, 1.5])
with col_head:
    st.markdown(f"""
    <div style="margin-bottom: 6px;">
        <h2 style="font-size: 24px; font-weight: 700; color: #1C1A17; margin: 0; font-family: 'Sora', sans-serif;">Live Typesetting Editor</h2>
        <span style="font-size: 13.5px; color: #71689F; font-family: 'Plus Jakarta Sans', sans-serif;">Project: <b>{curr_proj_title} — Page {page_idx:02d}</b></span>
    </div>
    """, unsafe_allow_html=True)

with col_pages_nav:
    st.markdown(f"""
    <div style="text-align: right; padding-top: 8px; font-weight: 700; font-size: 13.5px; color: #25326F;">
        Page {page_idx:02d} of 24 • Typesetting Active
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border: none; border-top: 1.5px solid #E4DFD6; margin-top: 6px; margin-bottom: 20px;'>", unsafe_allow_html=True)

# 2. Workspace Split (60% Canvas / 40% Inspector Controls)
col_canvas, col_controls = st.columns([6, 4], gap="large")

# ==============================================================================
# LEFT PANEL (60%): INPAINTED CANVAS & LIVE TEXT OVERLAY
# ==============================================================================
with col_canvas:
    with st.container(border=True):
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <h4 style="font-size: 15px; font-weight: 700; color: #1C1A17; margin: 0; font-family: 'Sora', sans-serif;">
                Inpainted Canvas &amp; Live Text Overlay
            </h4>
            <span style="font-size: 12px; color: #2F7A4F; font-weight: 600;">LaMa Clean-Plate Active ✓</span>
        </div>
        """, unsafe_allow_html=True)

        align_anchor = "middle" if st.session_state["typeset_align"] == "Center" else ("start" if st.session_state["typeset_align"] == "Left" else "end")
        align_x = 370 if st.session_state["typeset_align"] == "Center" else (290 if st.session_state["typeset_align"] == "Left" else 450)
        fw = "bold" if st.session_state["typeset_bold"] else "normal"
        fs = "italic" if st.session_state["typeset_italic"] else "normal"
        disp_txt = st.session_state["typeset_text"].upper() if st.session_state["typeset_caps"] else st.session_state["typeset_text"]

        # SVG Clean-Plate Canvas with Inpainted Balloons & Vietnamese Text
        svg_typeset_canvas = f"""
        <svg viewBox="0 0 520 720" width="100%" height="auto" style="border-radius: 10px; background-color: #F8F8F6; border: 1.5px solid #E4DFD6;" xmlns="http://www.w3.org/2000/svg">
            <!-- Comic Panels Layout -->
            <rect x="25" y="25" width="470" height="670" fill="#FFFFFF" stroke="#1C1A17" stroke-width="3" rx="4"/>
            <line x1="25" y1="240" x2="495" y2="240" stroke="#1C1A17" stroke-width="4"/>
            <line x1="260" y1="240" x2="260" y2="695" stroke="#1C1A17" stroke-width="4"/>

            <!-- Panel Artwork Placeholder -->
            <rect x="35" y="35" width="220" height="195" fill="#F4F7F2"/>
            <circle cx="140" cy="130" r="50" fill="#E4DFD6"/>

            <!-- ACTIVE SPEECH BUBBLE #1 (Selected with 2px navy outline & 4 corner resize handles) -->
            <rect x="280" y="45" width="180" height="150" fill="#FFFFFF" stroke="#25326F" stroke-width="2.5" rx="10"/>
            <rect x="277" y="42" width="6" height="6" fill="#25326F"/>
            <rect x="457" y="42" width="6" height="6" fill="#25326F"/>
            <rect x="277" y="192" width="6" height="6" fill="#25326F"/>
            <rect x="457" y="192" width="6" height="6" fill="#25326F"/>
            <rect x="280" y="45" width="22" height="20" fill="#25326F" rx="3"/>
            <text x="291" y="60" fill="#FFFFFF" font-size="12" font-weight="bold" font-family="sans-serif" text-anchor="middle">1</text>
            <text x="{align_x}" y="125" fill="#1C1A17" font-size="{st.session_state['typeset_size']}" font-weight="{fw}" font-style="{fs}" font-family="'Plus Jakarta Sans', sans-serif" text-anchor="{align_anchor}">
                {disp_txt}
            </text>

            <!-- BUBBLE #2 (Unselected, subtle dashed border) -->
            <rect x="45" y="270" width="185" height="135" fill="#FFFFFF" stroke="#71689F" stroke-dasharray="4,4" stroke-width="1.5" rx="8"/>
            <text x="55" y="285" fill="#71689F" font-size="11" font-weight="bold">#2</text>
            <text x="135" y="340" fill="#1C1A17" font-size="14" font-family="sans-serif" text-anchor="middle">Chuyện gì đã xảy ra vậy?!</text>

            <!-- BUBBLE #3 (Sound Effect clean-plate inpainting) -->
            <rect x="50" y="500" width="175" height="145" fill="#FFFFFF" stroke="#71689F" stroke-dasharray="4,4" stroke-width="1.5" rx="8"/>
            <text x="60" y="515" fill="#71689F" font-size="11" font-weight="bold">#3</text>
            <text x="135" y="580" fill="#C1382E" font-size="22" font-weight="bold" font-family="sans-serif" text-anchor="middle">BÙM !</text>

            <!-- BUBBLE #4 (Narration in Vietnamese) -->
            <rect x="290" y="490" width="185" height="150" fill="#FFFFFF" stroke="#71689F" stroke-dasharray="4,4" stroke-width="1.5" rx="6"/>
            <text x="300" y="505" fill="#71689F" font-size="11" font-weight="bold">#4</text>
            <text x="380" y="570" fill="#1C1A17" font-size="13.5" font-family="sans-serif" text-anchor="middle">Ngay lúc đó, toàn thành phố rung chuyển.</text>
        </svg>
        """
        st.markdown(svg_typeset_canvas, unsafe_allow_html=True)

# ==============================================================================
# RIGHT PANEL (40%): TYPOGRAPHY INSPECTOR & CONTROLS
# ==============================================================================
with col_controls:
    with st.container(border=True):
        st.markdown("""
        <div style="margin-bottom: 14px;">
            <h4 style="font-size: 17px; font-weight: 700; color: #1C1A17; margin: 0; font-family: 'Sora', sans-serif;">
                Typography Settings
            </h4>
            <span style="font-size: 12px; color: #71689F; font-family: 'Plus Jakarta Sans', sans-serif;">Editing Bubble #1 (Active Selection)</span>
        </div>
        """, unsafe_allow_html=True)

        # Control 1 — Translated Vietnamese Text
        st.markdown("<span style='font-size: 12.5px; font-weight: 600; color: #1C1A17;'>Translated Vietnamese Text</span>", unsafe_allow_html=True)
        new_text = st.text_area(
            "Dialogue Content",
            value=st.session_state["typeset_text"],
            height=75,
            label_visibility="collapsed",
        )
        if new_text != st.session_state["typeset_text"]:
            st.session_state["typeset_text"] = new_text
            st.rerun()

        # Control 2 — Font Family & Size
        col_f1, col_f2 = st.columns([1.5, 1])
        with col_f1:
            font_sel = st.selectbox(
                "Font Family",
                ["CC Wild Words (Manga Standard)", "Anime Ace v3 (Bold Shonen)", "Plus Jakarta Sans (Editorial)"],
            )
        with col_f2:
            size_val = st.number_input("Font Size", min_value=10, max_value=32, value=st.session_state["typeset_size"], step=1)
            if size_val != st.session_state["typeset_size"]:
                st.session_state["typeset_size"] = size_val
                st.rerun()

        # Control 3 — Text Alignment Toggle Group
        st.markdown("<span style='font-size: 12.5px; font-weight: 600; color: #1C1A17;'>Text Alignment</span>", unsafe_allow_html=True)
        col_a1, col_a2, col_a3 = st.columns(3)
        with col_a1:
            if st.button("Left", key="align_l", type="primary" if st.session_state["typeset_align"] == "Left" else "secondary", use_container_width=True):
                st.session_state["typeset_align"] = "Left"
                st.rerun()
        with col_a2:
            if st.button("Center", key="align_c", type="primary" if st.session_state["typeset_align"] == "Center" else "secondary", use_container_width=True):
                st.session_state["typeset_align"] = "Center"
                st.rerun()
        with col_a3:
            if st.button("Right", key="align_r", type="primary" if st.session_state["typeset_align"] == "Right" else "secondary", use_container_width=True):
                st.session_state["typeset_align"] = "Right"
                st.rerun()

        # Control 4 — Line Spacing & Kerning
        line_h = st.slider("Line Spacing (Leading)", min_value=1.0, max_value=2.0, value=1.2, step=0.05)

        # Control 5 — Text Style & Case
        st.markdown("<span style='font-size: 12.5px; font-weight: 600; color: #1C1A17;'>Text Style</span>", unsafe_allow_html=True)
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            if st.button("Bold [B]", key="btn_toggle_b", type="primary" if st.session_state["typeset_bold"] else "secondary", use_container_width=True):
                st.session_state["typeset_bold"] = not st.session_state["typeset_bold"]
                st.rerun()
        with col_s2:
            if st.button("Italic [I]", key="btn_toggle_i", type="primary" if st.session_state["typeset_italic"] else "secondary", use_container_width=True):
                st.session_state["typeset_italic"] = not st.session_state["typeset_italic"]
                st.rerun()
        with col_s3:
            if st.button("ALL CAPS [TT]", key="btn_toggle_c", type="primary" if st.session_state["typeset_caps"] else "secondary", use_container_width=True):
                st.session_state["typeset_caps"] = not st.session_state["typeset_caps"]
                st.rerun()

        # Global Option
        st.checkbox("Apply this font style to all bubbles on this page", value=True)
        
        # Reset Button (Functional Streamlit Native)
        if st.button("Reset to Auto-Fit Default ↺", key="btn_reset_typeset", use_container_width=True):
            st.session_state["typeset_size"] = 14
            st.session_state["typeset_align"] = "Center"
            st.session_state["typeset_bold"] = True
            st.session_state["typeset_italic"] = False
            st.session_state["typeset_caps"] = False
            st.toast("Typography reset to standard manga preset.")
            st.rerun()

# 3. Bottom Action Bar matching Stitch [ACL-08]
st.markdown("""
<div class="acl-sticky-bar" style="margin-top: 24px;">
    <div style="font-size: 13px; color: #71689F; font-family: 'Plus Jakarta Sans', sans-serif;">
        Bubble 1 of 4 configured • All bounding boxes verified.
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")
col_act_prev, col_act_next = st.columns([1, 1.8])
with col_act_prev:
    if st.button("← Previous Page", use_container_width=True):
        st.switch_page("pages/4_Review_Studio.py")
with col_act_next:
    if st.button("Mark Page Complete & Next Page →", type="primary", use_container_width=True):
        st.session_state["review_page_idx"] = min(24, page_idx + 1)
        st.toast(f"✅ Page {page_idx} marked Complete! Moving to Queue Monitor...")
        st.switch_page("pages/6_Queue_Monitor.py")
