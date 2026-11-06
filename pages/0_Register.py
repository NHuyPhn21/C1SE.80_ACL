"""ACL - [ACL-02] User Registration (Create New Account) (100% Streamlit Native with Real SQLite & Auth)."""

import textwrap
import streamlit as st

from services.auth_service import AuthServiceError, get_auth_service
from utils.auth_session import establish_session, is_authenticated

# Guard: If already authenticated, redirect straight to workspace
if is_authenticated():
    st.switch_page("pages/1_Workspace.py")

# Session state for registration validation errors
if "reg_error_msg" not in st.session_state:
    st.session_state["reg_error_msg"] = ""

reg_error = st.session_state["reg_error_msg"]
reg_border_color = "#C1382E" if reg_error else "#E4DFD6"
reg_focus_color = "#C1382E" if reg_error else "#25326F"

# Page-Scoped CSS (Strict Stitch [ACL-02] Design Tokens)
st.markdown(f"""
<style>
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1220px !important;
        margin: 0 auto !important;
    }}
    
    [data-testid="stHorizontalBlock"] {{
        align-items: stretch !important;
    }}
    
    [data-testid="column"] {{
        display: flex !important;
        flex-direction: column !important;
    }}

    /* =========================================================================
       LEFT BRAND SHOWCASE PANEL: [ACL-02] BUILD YOUR TEAM WORKSPACE
       ========================================================================= */
    .acl-left-brand-reg {{
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
    }}
    
    .acl-brand-header {{
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 24px;
    }}
    
    .acl-brand-logo-box {{
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
    }}
    
    .acl-brand-title {{
        font-family: 'Sora', sans-serif;
        font-weight: 700;
        font-size: 19px;
        color: #FFFFFF;
        line-height: 1.1;
    }}
    
    .acl-brand-subtitle {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 12px;
        color: rgba(255, 255, 255, 0.78);
        margin-top: 2px;
    }}
    
    .acl-badges-bar {{
        display: flex;
        gap: 8px;
        margin-bottom: 28px;
        flex-wrap: wrap;
    }}
    
    .acl-pill-badge {{
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
    }}
    
    .acl-pill-badge.green {{
        background: rgba(52, 211, 153, 0.18);
        border-color: rgba(52, 211, 153, 0.45);
        color: #A7F3D0;
        font-weight: 600;
    }}
    
    .acl-green-dot {{
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #34D399;
        box-shadow: 0 0 6px #34D399;
    }}
    
    .acl-eyebrow-text {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.6px;
        color: rgba(255, 255, 255, 0.65);
        text-transform: uppercase;
        margin-bottom: 12px;
    }}
    
    .acl-main-headline {{
        font-family: 'Sora', sans-serif;
        font-size: 34px;
        font-weight: 700;
        line-height: 1.25;
        letter-spacing: -0.5px;
        color: #FFFFFF;
        margin-bottom: 28px;
    }}
    
    .acl-features-list {{
        display: flex;
        flex-direction: column;
        gap: 16px;
    }}
    
    .acl-feature-row {{
        display: flex;
        align-items: flex-start;
        gap: 12px;
        font-size: 13.5px;
        line-height: 1.45;
        color: rgba(255, 255, 255, 0.92);
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    
    .acl-feature-check {{
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
    }}
    
    .acl-brand-footer {{
        border-top: 1px solid rgba(255, 255, 255, 0.15);
        padding-top: 18px;
        color: rgba(255, 255, 255, 0.65);
    }}

    /* =========================================================================
       RIGHT CANVAS & REGISTRATION CARD
       ========================================================================= */
    .acl-cluster-wrap {{
        display: flex;
        justify-content: flex-end;
        margin-bottom: 16px;
    }}
    
    .acl-cluster-badge {{
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
    }}
    
    .acl-dot-cluster {{
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #10B981;
    }}
    
    .acl-card-container {{
        max-width: 480px;
        margin: 0 auto;
        width: 100%;
    }}
    
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: #FFFFFF !important;
        border: 1.5px solid #E4DFD6 !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04) !important;
        padding: 24px 28px !important;
    }}

    /* Tab styling */
    .acl-tabs-header {{
        display: flex;
        gap: 24px;
        border-bottom: 1.5px solid #E4DFD6;
        padding-bottom: 10px;
        margin-bottom: 18px;
    }}
    .acl-tab-link {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        text-decoration: none;
    }}
    .acl-tab-link.active {{
        color: #25326F;
        border-bottom: 2.5px solid #25326F;
        padding-bottom: 10px;
        margin-bottom: -11.5px;
    }}
    .acl-tab-link.inactive {{
        color: #71689F;
    }}

    /* Input styling with dynamic error state */
    div[data-testid="stTextInput"] input {{
        background: #FAFAF8 !important;
        border: 1.5px solid {reg_border_color} !important;
        border-radius: 8px !important;
        font-size: 13.5px !important;
        color: #1C1A17 !important;
        padding: 9px 12px !important;
    }}
    div[data-testid="stTextInput"] input:focus {{
        border-color: {reg_focus_color} !important;
        box-shadow: 0 0 0 1px {reg_focus_color} !important;
        background: #FFFFFF !important;
    }}
    
    /* Primary Submit Button */
    div.stFormSubmitButton > button {{
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
    }}
    div.stFormSubmitButton > button:hover {{
        background-color: #1B2856 !important;
        box-shadow: 0 4px 14px rgba(37, 50, 111, 0.35) !important;
        transform: translateY(-1px) !important;
    }}
    
    .acl-telemetry-bottom {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #71689F;
        margin-top: 24px;
        text-align: center;
    }}
</style>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([36, 64], gap="large")

# ==============================================================================
# LEFT PANEL: [ACL-02] BUILD YOUR TEAM WORKSPACE
# ==============================================================================
with col_left:
    left_brand_html = (
        '<div class="acl-left-brand-reg">'
        '<div>'
        '<div class="acl-brand-header">'
        '<div class="acl-brand-logo-box">ACL</div>'
        '<div>'
        '<div class="acl-brand-title">ACL</div>'
        '<div class="acl-brand-subtitle">Automated Comic Localization</div>'
        '</div>'
        '</div>'
        '<div class="acl-badges-bar">'
        '<span class="acl-pill-badge">Team Workspace active</span>'
        '<span class="acl-pill-badge green"><span class="acl-green-dot"></span>Registration Open</span>'
        '</div>'
        '<div class="acl-eyebrow-text">COLLABORATIVE WORKBENCH</div>'
        '<div class="acl-main-headline">'
        'Build your team<br>workspace.'
        '</div>'
        '<div class="acl-features-list">'
        '<div class="acl-feature-row"><div class="acl-feature-check">✓</div><div>Create a Project per series you localize</div></div>'
        '<div class="acl-feature-row"><div class="acl-feature-check">✓</div><div>Invite Translators and Typesetters by role</div></div>'
        '<div class="acl-feature-row"><div class="acl-feature-check">✓</div><div>Keep terminology consistent with a shared glossary</div></div>'
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
# RIGHT CANVAS: [ACL-02] USER REGISTRATION CARD
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
        # Tabs bar with Log in link back to 0_Login.py
        c_t1, c_t2, c_sp = st.columns([1, 1, 2])
        with c_t1:
            if st.button("Log in", key="tab_nav_login", use_container_width=True):
                st.switch_page("pages/0_Login.py")
        with c_t2:
            st.button("Register", key="tab_nav_reg_active", type="primary", use_container_width=True)

        register_header_html = textwrap.dedent("""\
<div style="margin-top: 12px; margin-bottom: 16px;">
    <h2 style="font-size: 24px; font-weight: 700; color: #1C1A17; margin: 0 0 4px 0; font-family: 'Sora', sans-serif;">Create your account</h2>
    <p style="font-size: 13.5px; color: #71689F; margin: 0; font-family: 'Plus Jakarta Sans', sans-serif;">You will be able to create or join a Project after signing up.</p>
</div>
""")
        st.markdown(register_header_html, unsafe_allow_html=True)

        # Validation error banner if present
        if reg_error:
            err_alert_html = f"""\
<div style="background-color: #F8E2DE; border: 1.5px solid #C1382E; border-radius: 8px; padding: 10px 14px; margin-bottom: 14px; display: flex; align-items: center; gap: 8px;">
    <span style="color: #C1382E; font-size: 16px;">⚠️</span>
    <span style="color: #C1382E; font-size: 12.5px; font-weight: 600; font-family: 'Plus Jakarta Sans', sans-serif;">{reg_error}</span>
</div>
"""
            st.markdown(err_alert_html, unsafe_allow_html=True)

        with st.form("acl_02_registration_form"):
            reg_name = st.text_input("Full name", placeholder="Phan Thanh Hoang")
            reg_email = st.text_input("Work email", placeholder="you@studio.com")
            
            st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-top: 10px; margin-bottom: 4px;">
                <span style="font-size: 13px; font-weight: 600; color: #1C1A17;">Password</span>
                <span style="font-size: 11px; color: #71689F; font-family: 'JetBrains Mono', monospace;">Min. 8 characters</span>
            </div>
            """, unsafe_allow_html=True)
            reg_pwd = st.text_input("Password", type="password", placeholder="At least 8 characters", label_visibility="collapsed")
            
            st.markdown("""
            <div style="margin-top: 10px; margin-bottom: 4px;">
                <span style="font-size: 13px; font-weight: 600; color: #1C1A17;">Confirm password</span>
            </div>
            """, unsafe_allow_html=True)
            reg_cpwd = st.text_input("Confirm password", type="password", placeholder="Repeat password", label_visibility="collapsed")
            
            terms = st.checkbox("I agree to the Terms of Service and Privacy Policy", value=True)

            reg_submit = st.form_submit_button("Create Account →", type="primary", use_container_width=True)

            if reg_submit:
                if not reg_name.strip() or not reg_email.strip():
                    st.session_state["reg_error_msg"] = "Please provide your full name and work email."
                    st.rerun()
                elif reg_pwd != reg_cpwd:
                    # ACL-02-ERR State: Passwords mismatch
                    st.session_state["reg_error_msg"] = "Passwords do not match. Please re-enter identical passwords."
                    st.rerun()
                elif len(reg_pwd) < 8:
                    st.session_state["reg_error_msg"] = "Password must be at least 8 characters long."
                    st.rerun()
                elif not terms:
                    st.session_state["reg_error_msg"] = "Please accept the Terms of Service and Privacy Policy."
                    st.rerun()
                else:
                    auth_service = get_auth_service()
                    try:
                        result = auth_service.register(full_name=reg_name.strip(), email=reg_email.strip(), password=reg_pwd)
                        establish_session(result, remember_me=True)
                        st.session_state["reg_error_msg"] = ""
                        st.success(f"Account created successfully for {result.user.full_name}!")
                        st.rerun()
                    except AuthServiceError as err:
                        st.session_state["reg_error_msg"] = str(err)
                        st.rerun()

        col_lg_txt, col_lg_btn = st.columns([2, 1])
        with col_lg_txt:
            st.markdown(
                '<div style="text-align: right; padding-top: 8px; font-size: 13px; color: #71689F;">'
                'Already have an account?'
                '</div>',
                unsafe_allow_html=True,
            )
        with col_lg_btn:
            if st.button("Log in →", key="btn_switch_login_from_reg", use_container_width=True):
                st.switch_page("pages/0_Login.py")

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
