"""Chapter Studio page: Batch Image Upload and AI Pipeline Configuration."""

import streamlit as st

from utils.auth_session import require_auth


user = require_auth()

st.title("Chapter Studio")
st.caption(f"Batch image upload and AI pipeline configuration • Signed in as **{user.full_name}**")

st.markdown("---")

# Section 1: Drag & drop batch upload
st.subheader("1. Upload Comic Pages (Batch Upload)")
uploaded_files = st.file_uploader(
    "Drag & drop comic pages here (JPG, PNG)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    help="Supports batch uploading up to 50 pages per chapter.",
)

if uploaded_files:
    st.success(f"✓ {len(uploaded_files)} pages uploaded and staged.")
    with st.expander("View uploaded files list", expanded=False):
        for idx, file in enumerate(uploaded_files, start=1):
            st.write(f"Page {idx:03d}: `{file.name}` ({file.size / 1024:.1f} KB)")

# Section 2: Language pair configuration
st.subheader("2. AI Pipeline Configuration")
col_src, col_tgt = st.columns(2)
with col_src:
    source_lang = st.selectbox(
        "Source Language",
        options=["Japanese (Raw Manga)", "English"],
        index=0,
        help="Language of raw speech bubbles (used by Manga OCR).",
    )
with col_tgt:
    target_lang = st.selectbox(
        "Target Language",
        options=["Vietnamese"],
        index=0,
        help="Target language for translation and typesetting.",
    )

# Section 3: Launch pipeline
st.subheader("3. Pipeline Execution")
st.info(
    "Pipeline Stages: **YOLOv8 Detection** ➔ **Manga OCR** ➔ **Waiting Review** ➔ **LaMa Inpainting** ➔ **Live Typesetting** ➔ **Completed**"
)

if st.button("Start AI Pipeline", type="primary", use_container_width=True):
    if not uploaded_files:
        st.warning("Please upload at least one page before starting the pipeline.")
    else:
        st.success(f"Successfully queued {len(uploaded_files)} pages for processing!")
        st.switch_page("pages/5_Queue_Monitor.py")
