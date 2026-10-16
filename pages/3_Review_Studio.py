"""Interactive Review Studio page: Dual-panel OCR inspection and text correction."""

import streamlit as st

from utils.auth_session import require_auth


user = require_auth()

st.title("Interactive Review Studio")
st.caption(f"Inspect YOLOv8 detection bounding boxes and correct Manga OCR text • Signed in as **{user.full_name}**")

st.markdown("---")

# Navigation header
col_nav_l, col_nav_c, col_nav_r = st.columns([1, 2, 1])
with col_nav_l:
    if st.button("← Previous Page", use_container_width=True):
        st.toast("Navigating to previous page")
with col_nav_c:
    st.markdown("<p style='text-align: center; font-weight: bold;'>Page 14 of 24 (Shonen Weekly #112)</p>", unsafe_allow_html=True)
with col_nav_r:
    if st.button("Next Page →", use_container_width=True):
        st.toast("Navigating to next page")

# Dual 50/50 split layout
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Original Page (YOLOv8 Detection)")
    st.info("Raw comic scan preview with detected text bounding boxes.")
    st.container(border=True).markdown(
        """
        <div style="background: #1c1a17; color: white; border-radius: 8px; height: 420px; display: flex; align-items: center; justify-content: center; text-align: center; padding: 20px;">
            <div>
                <h4>Manga Page Preview</h4>
                <p style="color: #71689f;">[Box 1: x=340, y=120, w=180, h=90] ➔ 先生、待って！</p>
                <p style="color: #71689f;">[Box 2: x=110, y=410, w=220, h=110] ➔ 何があったんだ？！</p>
                <p style="color: #71689f;">[Box 3: x=240, y=650, w=150, h=80] ➔ ドカーン</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_right:
    st.subheader("Extracted Text (Manga OCR Correction)")
    st.caption("Edit recognition errors directly before triggering translation.")
    
    with st.container(border=True):
        st.markdown("**Box #1** (Confidence: :green[0.98])")
        st.text_input("Raw Japanese text", value="先生、待ってください！", key="box_1")
    
    with st.container(border=True):
        st.markdown("**Box #2** (Confidence: :green[0.94])")
        st.text_input("Raw Japanese text", value="何があったんだ？！", key="box_2")
    
    with st.container(border=True):
        st.markdown("**Box #3** (Confidence: :orange[0.58 - Low])")
        st.text_input("Raw Japanese text (Flagged for review)", value="ドカーン", key="box_3")

st.markdown("---")
col_act_l, col_act_r = st.columns([3, 1])
with col_act_r:
    if st.button("Confirm & Proceed to Translation →", type="primary", use_container_width=True):
        st.success("Page verified! Proceeding to translation.")
        st.switch_page("pages/4_Typesetting.py")
