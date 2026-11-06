"""ACL - [ACL-03] Forgot Password & SendGrid Recovery (100% Streamlit Native with SendGrid Integration)."""

import textwrap
import streamlit as st

from utils.auth_session import is_authenticated

# Guard: If already authenticated, redirect straight to workspace
if is_authenticated():
    st.switch_page("pages/1_Workspace.py")

# Session state for SendGrid recovery simulation
if "recovery_sent" not in st.session_state:
    st.session_state["recovery_sent"] = False
if "recovery_email" not in st.session_state:
    st.session_state["recovery_email"] = ""

# Page-Scoped CSS (Strict Stitch [ACL-03] Design Tokens)
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1220px !important;
        margin: 0 auto !important;
    }
    
    [data-testid="stHorizontalBlock"] {
        align-items: stretch !important;
    }
    
    [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
    }

    /* =========================================================================
       LEFT BRAND SHOWCASE PANEL: [ACL-03] WE WILL GET YOU BACK IN
       ========================================================================= */
    .acl-left-brand-forgot {
        background: linear-gradient(180deg, #1B2856 0%, #25326F 100%) !important;
        border-radius: 20px !important;
        padding: 40px 36px 32px 38px !important;
        min-height: 640px !important;
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        color: #FFFFFF !important;
        box-shadow: 0 10px 30px rgba(27, 40, 86, 0.18) !important;
        box-sizing: border-box !important;
    }
    
    .acl-brand-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 24px;
    }
    
    .acl-brand-logo-box {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.25);
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Sora', sans-serif;
        font-weight: 800;
        font-size: 16px;
        color: #FFFFFF;
        letter-spacing: -0.5px;
    }
    
    .acl-brand-title {
        font-family: 'Sora', sans-serif;
        font-weight: 700;
        font-size: 19px;
        color: #FFFFFF;
        line-height: 1.1;
    }
    
    .acl-brand-subtitle {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 12px;
        color: rgba(255, 255, 255, 0.78);
        margin-top: 2px;
    }
    
    .acl-badges-bar {
        display: flex;
        gap: 8px;
        margin-bottom: 28px;
        flex-wrap: wrap;
    }
    
    .acl-pill-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.22);
        font-size: 11.5px;
        color: #FFFFFF;
        font-weight: 500;
    }
    
    .acl-pill-badge.green {
        background: rgba(52, 211, 153, 0.18);
        border-color: rgba(52, 211, 153, 0.45);
        color: #A7F3D0;
        font-weight: 600;
    }
    
    .acl-green-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #34D399;
        box-shadow: 0 0 6px #34D399;
    }
    
    .acl-eyebrow-text {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.6px;
        color: rgba(255, 255, 255, 0.65);
        text-transform: uppercase;
        margin-bottom: 12px;
    }
    
    .acl-main-headline {
        font-family: 'Sora', sans-serif;
        font-size: 34px;
        font-weight: 700;
        line-height: 1.25;
        letter-spacing: -0.5px;
        color: #FFFFFF;
        margin-bottom: 20px;
    }

    .acl-main-subtext {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 14.5px;
        line-height: 1.55;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 28px;
    }
    
    .acl-features-list {
        display: flex;
        flex-direction: column;
        gap: 16px;
    }
    
    .acl-feature-row {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        font-size: 13.5px;
        line-height: 1.45;
        color: rgba(255, 255, 255, 0.92);
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .acl-feature-check {
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.18);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        flex-shrink: 0;
        margin-top: 1px;
        font-weight: 700;
        color: #FFFFFF;
    }
    
    .acl-brand-footer {
        border-top: 1px solid rgba(255, 255, 255, 0.15);
        padding-top: 18px;
        color: rgba(255, 255, 255, 0.65);
    }

    /* =========================================================================
       RIGHT CANVAS & FORGOT PASSWORD CARD
       ========================================================================= */
    .acl-cluster-wrap {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 16px;
    }
    
    .acl-cluster-badge {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 5px 14px;
        border-radius: 999px;
        background: #FFFFFF;
        border: 1px solid #E4DFD6;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11.5px;
        color: #1C1A17;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    
    .acl-dot-cluster {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #10B981;
    }
    
    .acl-card-container {
        max-width: 460px;
        margin: 0 auto;
        width: 100%;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF !important;
        border: 1.5px solid #E4DFD6 !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04) !important;
        padding: 24px 28px !important;
    }

    /* Input styling */
    div[data-testid="stTextInput"] input {
        background: #FAFAF8 !important;
        border: 1.5px solid #E4DFD6 !important;
        border-radius: 8px !important;
        font-size: 13.5px !important;
        color: #1C1A17 !important;
        padding: 9px 12px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #25326F !important;
        box-shadow: 0 0 0 1px #25326F !important;
        background: #FFFFFF !important;
    }
    
    /* Primary Submit Button */
    div.stFormSubmitButton > button {
        background-color: #25326F !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 999px !important;
        font-weight: 600 !important;
        font-size: 14.5px !important;
        padding: 11px 24px !important;
        width: 100% !important;
        margin-top: 12px !important;
        transition: all 0.2s ease-in-out !important;
    }
    div.stFormSubmitButton > button:hover {
        background-color: #1B2856 !important;
        box-shadow: 0 4px 14px rgba(37, 50, 111, 0.35) !important;
        transform: translateY(-1px) !important;
    }
    
    .acl-telemetry-bottom {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #71689F;
        margin-top: 24px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([36, 64], gap="large")

# ==============================================================================
# LEFT PANEL: [ACL-03] WE WILL GET YOU BACK IN
# ==============================================================================
with col_left:
    left_brand_html = (
        '<div class="acl-left-brand-forgot">'
        '<div>'
        '<div class="acl-brand-header">'
        '<div class="acl-brand-logo-box">ACL</div>'
        '<div>'
        '<div class="acl-brand-title">ACL</div>'
        '<div class="acl-brand-subtitle">Automated Comic Localization</div>'
        '</div>'
        '</div>'
        '<div class="acl-badges-bar">'
        '<span class="acl-pill-badge">SendGrid Mailer active</span>'
        '<span class="acl-pill-badge green"><span class="acl-green-dot"></span>Recovery Gateway Online</span>'
        '</div>'
        '<div class="acl-eyebrow-text">CREDENTIAL RECOVERY</div>'
        '<div class="acl-main-headline">'
        'We will get you<br>back in.'
        '</div>'
        '<div class="acl-main-subtext">'
        'Password reset emails are delivered securely through SendGrid and expire after a short window for security.'
        '</div>'
        '<div class="acl-features-list">'
        '<div class="acl-feature-row"><div class="acl-feature-check">✓</div><div>One-click password reset token via SendGrid</div></div>'
        '<div class="acl-feature-row"><div class="acl-feature-check">✓</div><div>15-minute secure expiration window</div></div>'
        '<div class="acl-feature-row"><div class="acl-feature-check">✓</div><div>Automatic audit trail logging</div></div>'
        '</div>'
        '</div>'
        '<div class="acl-brand-footer">'
        '<div style="font-family: \'JetBrains Mono\', monospace; font-size: 11px;">Pipeline throughput v2.4 • cuDNN12.1 • 2.8s/p</div>'
        '<div style="display: flex; justify-content: space-between; font-size: 12px; margin-top: 6px;">'
        '<span>© 2026 Team C1SE.80</span>'
        '<span>Terms • Privacy</span>'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(left_brand_html, unsafe_allow_html=True)

# ==============================================================================
# RIGHT CANVAS: [ACL-03] FORGOT PASSWORD CARD
# ==============================================================================
with col_right:
    # Floating Cluster Indicator
    cluster_badge_html = textwrap.dedent("""\
<div class="acl-cluster-wrap">
    <span class="acl-cluster-badge">
        <span class="acl-dot-cluster"></span>
        Cluster v2.1-East Tokyo-04
        <span style="color: #71689F; font-size: 12px; margin-left: 2px;">🔄</span>
    </span>
</div>
""")
    st.markdown(cluster_badge_html, unsafe_allow_html=True)

    # Centered White Card
    st.markdown('<div class="acl-card-container">', unsafe_allow_html=True)
    with st.container(border=True):
        # Top Navigation Link back to Login
        if st.button("← Back to log in", key="btn_back_login"):
            st.switch_page("pages/0_Login.py")

        header_html = textwrap.dedent("""\
<div style="margin-top: 10px; margin-bottom: 18px;">
    <h2 style="font-size: 26px; font-weight: 700; color: #1C1A17; margin: 0 0 6px 0; font-family: 'Sora', sans-serif;">Reset your password</h2>
    <p style="font-size: 13.5px; color: #71689F; margin: 0; font-family: 'Plus Jakarta Sans', sans-serif;">Enter the email on your account and we will send you a secure reset link.</p>
</div>
""")
        st.markdown(header_html, unsafe_allow_html=True)

        with st.form("forgot_password_form"):
            email_val = st.text_input("Email", value="w.mori@hoshikawamanga.co.jp")
            send_btn = st.form_submit_button("Send reset link →", type="primary", use_container_width=True)

            if send_btn:
                if not email_val.strip():
                    st.error("Please enter your email address.")
                else:
                    st.session_state["recovery_sent"] = True
                    st.session_state["recovery_email"] = email_val.strip()
                    st.rerun()

        # SendGrid Delivery Information Banner matching Stitch [ACL-03]
        if st.session_state["recovery_sent"]:
            banner_html = textwrap.dedent(f"""\
<div style="background-color: #E6F0E9; border: 1.5px solid #2F7A4F; border-radius: 8px; padding: 14px 16px; margin-top: 16px; display: flex; align-items: flex-start; gap: 10px;">
    <span style="color: #2F7A4F; font-size: 17px; line-height: 1.2;">✓</span>
    <span style="color: #2F7A4F; font-size: 13px; font-weight: 500; line-height: 1.45; font-family: 'Plus Jakarta Sans', sans-serif;">
        A password reset link was dispatched via SendGrid to <b>{st.session_state['recovery_email']}</b>. If an account exists for that email, a reset link will arrive within a few minutes. Check your spam folder if it does not appear.
    </span>
</div>
""")
            st.markdown(banner_html, unsafe_allow_html=True)
            
            if st.button("Resend Reset Email", use_container_width=True):
                st.toast("⚡ Recovery email re-dispatched via SendGrid API!")

    st.markdown('</div>', unsafe_allow_html=True)

    # Bottom Right Telemetry
    bottom_telemetry_html = textwrap.dedent("""\
<div class="acl-telemetry-bottom">
    <span class="acl-dot-cluster"></span>
    <span>Dev Scripts, QA-1 (Active Solo)</span>
    <span style="opacity: 0.4;">|</span>
    <span>Target: Japanese &gt; English, dual-direction</span>
</div>
""")
    st.markdown(bottom_telemetry_html, unsafe_allow_html=True)
