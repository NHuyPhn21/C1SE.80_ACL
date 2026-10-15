"""Personal Settings page: Cloud LLM API Key, Custom Glossary, and System Logs."""

import streamlit as st

from utils.auth_session import require_auth


user = require_auth()

st.title("Personal Settings")
st.caption(f"Manage API credentials, project glossary, and system diagnostics • Signed in as **{user.full_name}**")

st.markdown("---")

tab_api, tab_glossary, tab_logs = st.tabs(["API Key Config", "Custom Glossary", "System Logs"])

with tab_api:
    st.subheader("Cloud LLM API Key")
    st.caption("Used by the translation client. Stored encrypted, never exposed directly.")
    
    col_prov, col_key = st.columns([1, 2])
    with col_prov:
        provider = st.selectbox("Provider", options=["Gemini 1.5 Pro", "OpenAI GPT-4o"], index=0)
    with col_key:
        api_key = st.text_input("API Key", type="password", value="AIzaSyDummyKeyPlaceholderForSecurity")
        
    st.success("✓ Key is valid • Last checked 2 hours ago")
    if st.button("Save API Key", type="primary"):
        st.toast("API Key encrypted and saved securely.")

with tab_glossary:
    st.subheader("Custom Glossary")
    st.caption("Enforced in every translation request sent to the Cloud LLM.")
    
    glossary_data = [
        {"Source Term": "先輩", "Target Term": "Senpai", "Notes": "Keep honorific as-is; do not translate literally."},
        {"Source Term": "Konoha", "Target Term": "Konoha", "Notes": "Proper noun — keep untranslated."},
        {"Source Term": "鬼", "Target Term": "Oni", "Notes": "Keep Japanese term; add footnote on first appearance."},
        {"Source Term": "Nakama", "Target Term": "Nakama", "Notes": "Keep pirate comrade term intact."},
    ]
    st.dataframe(glossary_data, use_container_width=True)
    
    with st.expander("+ Add New Glossary Term"):
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Source Term (Japanese)", placeholder="e.g. 先輩")
        with c2:
            st.text_input("Target Term (Vietnamese)", placeholder="e.g. Senpai")
        st.text_area("Translator Guidance / Notes", placeholder="Usage notes for the LLM...")
        if st.button("Save Term", type="primary"):
            st.toast("Term added to project glossary!")

with tab_logs:
    st.subheader("Real-Time System Logs")
    st.caption("Errors and warnings from background workers, CUDA VRAM, and OCR pipeline.")
    
    col_filter, col_btn = st.columns([4, 1])
    with col_filter:
        st.selectbox("Log Level Filter", options=["All levels", "ERROR only", "WARNING only", "INFO only"])
    with col_btn:
        st.button("Refresh Logs", use_container_width=True)
        
    log_text = """[12:04:02] INFO    Queue worker started (pid 8421)
[12:04:15] INFO    Page 014.png queued for OCR – project "Shonen Weekly #112"
[12:06:40] WARNING Cloud LLM API quota at 92% – consider upgrading plan
[12:07:02] ERROR   Inpainting failed for page 014.png – CUDA out of memory
[12:07:03] INFO    Retrying page 014.png with reduced batch size
[12:07:19] INFO    Page 014.png completed – moved to Review Studio
[12:11:52] WARNING OCR confidence below 0.6 on 3 text regions – flagged for manual review"""

    st.code(log_text, language="log")
