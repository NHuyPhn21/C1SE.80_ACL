"""Queue Monitor & Export page: Real-time asynchronous pipeline tracking."""

import streamlit as st

from utils.auth_session import require_auth


user = require_auth()

st.title("Queue Monitor & Export")
st.caption(f"Track real-time progress of chapter processing queue • Signed in as **{user.full_name}**")

st.markdown("---")

# Progress section
st.subheader("Chapter Progress: Shonen Weekly #112")
st.progress(68, text="16 of 24 pages completed (68%)")

# Detailed tasks table
st.subheader("Queue Status Table")

queue_data = [
    {"Page": "001 - 012", "File": "page_001.png - 012.png", "Stage": "Typesetting", "Status": "Completed"},
    {"Page": "013", "File": "page_013.png", "Stage": "Waiting Review", "Status": "Ready for Review"},
    {"Page": "014", "File": "page_014.png", "Stage": "LaMa Inpainting", "Status": "Processing (Active)"},
    {"Page": "015", "File": "page_015.png", "Stage": "Manga OCR", "Status": "Processing (Active)"},
    {"Page": "016", "File": "page_016.png", "Stage": "YOLOv8 Detection", "Status": "Queued"},
    {"Page": "017 - 024", "File": "page_017.png - 024.png", "Stage": "Async FIFO", "Status": "Waiting Worker"},
]

st.dataframe(queue_data, use_container_width=True)

st.markdown("---")
st.subheader("Export Localized Chapter")
st.info("Export is available once all pages reach Completed status.")

col_down_l, col_down_r = st.columns([3, 1])
with col_down_r:
    st.download_button(
        label="Download ZIP (Draft)",
        data=b"ACL ZIP Archive Placeholder",
        file_name="Shonen_Weekly_112_Vietnamese.zip",
        mime="application/zip",
        use_container_width=True,
    )
