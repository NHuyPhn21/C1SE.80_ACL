"""Settings page."""

import streamlit as st

from utils.auth_session import require_auth


require_auth()
st.title("Settings")
