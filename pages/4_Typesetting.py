"""Live Typesetting Editor page: Typography and Speech Bubble Formatting."""

import streamlit as st

from utils.auth_session import require_auth


user = require_auth()

st.title("Live Typesetting Editor")
st.caption(f"Adjust typography, alignment, and formatting on inpainted pages • Signed in as **{user.full_name}**")

st.markdown("---")

col_canvas, col_controls = st.columns([3, 2])

with col_canvas:
    st.subheader("Inpainted Comic Page Preview")
    st.info("Original Japanese text cleanly removed via LaMa inpainting.")
    st.container(border=True).markdown(
        """
        <div style="background: #ffffff; border: 2px dashed #25326f; border-radius: 8px; height: 440px; display: flex; align-items: center; justify-content: center; text-align: center; padding: 20px;">
            <div>
                <h4 style="color: #25326f;">LaMa Inpainted Canvas</h4>
                <div style="border: 2px solid #25326f; border-radius: 16px; padding: 12px 20px; background: #f4f7f2; display: inline-block; margin-top: 20px;">
                    <p style="font-size: 16px; font-weight: bold; margin: 0; color: #1c1a17;">
                        "Thầy ơi, xin hãy đợi em với!"
                    </p>
                </div>
                <p style="color: #71689f; font-size: 12px; margin-top: 10px;">[Selected Bubble #1]</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_controls:
    st.subheader("Typography Settings (Bubble #1)")
    
    st.text_area("Vietnamese Translated Text", value="Thầy ơi, xin hãy đợi em với!", height=80)
    
    font_col1, font_col2 = st.columns(2)
    with font_col1:
        font_family = st.selectbox("Font Family", options=["CC Wild Words", "Anime Ace", "Plus Jakarta Sans"])
    with font_col2:
        font_size = st.number_input("Font Size (px)", min_value=8, max_value=48, value=14, step=1)
        
    align = st.radio("Text Alignment", options=["Left", "Center", "Right"], horizontal=True, index=1)
    line_spacing = st.slider("Line Spacing", min_value=1.0, max_value=2.0, value=1.3, step=0.1)
    
    st.checkbox("Apply font styling to all bubbles on this page", value=False)
    
    if st.button("Reset to Default", type="secondary"):
        st.toast("Styles reset to auto-fit default.")

st.markdown("---")
if st.button("Mark as Complete & Next Page →", type="primary", use_container_width=True):
    st.success("Page typography marked as complete!")
    st.switch_page("pages/5_Queue_Monitor.py")
