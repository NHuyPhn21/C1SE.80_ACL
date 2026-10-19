"""Streamlit presentation helpers for quota and API error states."""

from datetime import datetime

import streamlit as st

from models.api_error import ApiError
from models.quota import QuotaLevel, QuotaStatus


def render_api_error(error: ApiError) -> None:
    st.error(error.message)
    if error.retry_message:
        st.caption(error.retry_message)
    for field, message in error.field_errors.items():
        st.caption(f"{field}: {message}")


def render_quota_dashboard(quotas: list[QuotaStatus]) -> None:
    for quota in quotas:
        with st.container(border=True):
            title, usage, remaining = st.columns([2, 1, 1])
            title.subheader(quota.provider)
            title.caption(quota.metric)
            usage.metric("Used", f"{quota.used:,} {quota.unit}")
            remaining.metric("Remaining", f"{quota.remaining:,} {quota.unit}")
            st.progress(quota.usage_ratio, text=f"{quota.usage_percent}% used")
            _render_quota_notice(quota)


def _render_quota_notice(quota: QuotaStatus) -> None:
    reset_text = _format_reset(quota.reset_at)
    if quota.level == QuotaLevel.EXHAUSTED:
        st.error(f"Quota exhausted. New requests are blocked.{reset_text}")
    elif quota.level == QuotaLevel.CRITICAL:
        st.error(f"Quota is almost exhausted.{reset_text}")
    elif quota.level == QuotaLevel.WARNING:
        st.warning(f"Quota usage is above 80%.{reset_text}")
    else:
        st.success(f"Quota is healthy.{reset_text}")


def _format_reset(reset_at: datetime | None) -> str:
    if reset_at is None:
        return ""
    return f" Resets at {reset_at.astimezone().strftime('%d/%m/%Y %H:%M %Z')}."
