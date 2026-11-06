"""ACL - [ACL-01] & [ACL-01-ERR] User Sign In — Default & Error States (100% Streamlit Native)."""

import textwrap
import streamlit as st

from services.auth_service import AuthServiceError, get_auth_service
from utils.auth_session import establish_session, is_authenticated

# Guard: If already authenticated, redirect straight to workspace
if is_authenticated():
    st.switch_page("pages/1_Workspace.py")

# Session state initialization for error simulation & tracking
if "auth_failed" not in st.session_state:
    st.session_state["auth_failed"] = False
if "auth_error_msg" not in st.session_state:
    st.session_state["auth_error_msg"] = ""

# Dynamic border & input styling based on error state
error_active = st.session_state["auth_failed"]
input_border_color = "#C1382E" if error_active else "#E4DFD6"
input_focus_color = "#C1382E" if error_active else "#25326F"

# Page-Scoped CSS (Strict Stitch [ACL-01] & [ACL-01-ERR] Design Tokens)
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
       LEFT BRAND SHOWCASE PANEL (DEEP NAVY GRADIENT)
       ========================================================================= */
    .acl-left-brand {{
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
        font-size: 32px;
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
       RIGHT CANVAS & FORM CARD
       ========================================================================= */
    .acl-cluster-wrap {{
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 12px;
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
        max-width: 460px;
        margin: 0 auto;
        width: 100%;
    }}
    
    /* Native Card Container Border Wrapper */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: #FFFFFF !important;
        border: 1.5px solid #E4DFD6 !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04) !important;
        padding: 24px 28px !important;
    }}

    /* Top Tabs pill bar */
    .acl-tabs-bar {{
        display: flex;
        border-bottom: 1.5px solid #E4DFD6;
        margin-bottom: 20px;
        gap: 24px;
    }}
    .acl-tab-item {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 14px;
        font-weight: 600;
        padding-bottom: 8px;
        text-decoration: none;
        cursor: pointer;
    }}
    .acl-tab-item.active {{
        color: #25326F;
        border-bottom: 2.5px solid #25326F;
        margin-bottom: -2px;
    }}
    .acl-tab-item.inactive {{
        color: #71689F;
    }}

    /* Input styling with dynamic error state */
    div[data-testid="stTextInput"] input {{
        background: #FAFAF8 !important;
        border: 1.5px solid {input_border_color} !important;
        border-radius: 8px !important;
        font-size: 13.5px !important;
        color: #1C1A17 !important;
        padding: 9px 12px !important;
    }}
    div[data-testid="stTextInput"] input:focus {{
        border-color: {input_focus_color} !important;
        box-shadow: 0 0 0 1px {input_focus_color} !important;
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
    
    /* Bottom Telemetry */
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
# LEFT PANEL: EXACT STITCH BRAND SHOWCASE (NO INDENTATION PITFALLS)
# ==============================================================================
with col_left:
    left_brand_html = (
        '<div class="acl-left-brand">'
        '<div>'
        '<div class="acl-brand-header">'
        '<div class="acl-brand-logo-box">ACL</div>'
        '<div>'
        '<div class="acl-brand-title">ACL</div>'
        '<div class="acl-brand-subtitle">Automated Comic Localization</div>'
        '</div>'
        '</div>'
        '<div class="acl-badges-bar">'
        '<span class="acl-pill-badge">Daily pipeline active</span>'
        '<span class="acl-pill-badge green"><span class="acl-green-dot"></span>3 Engines Online</span>'
        '</div>'
        '<div class="acl-eyebrow-text">PRODUCTION WORKBENCH</div>'
        '<div class="acl-main-headline">'
        'One pipeline,<br>from raw scan to<br>typeset page.'
        '</div>'
        '<div class="acl-features-list">'
        '<div class="acl-feature-row"><div class="acl-feature-check">✓</div><div>Detection, OCR, translation and typesetting in one pipeline</div></div>'
        '<div class="acl-feature-row"><div class="acl-feature-check">✓</div><div>Dual OCR for Japanese and English source pages</div></div>'
        '<div class="acl-feature-row"><div class="acl-feature-check">✓</div><div>Team workspace with role-based review</div></div>'
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
# RIGHT CANVAS: LOGIN / REGISTRATION CARD & CLUSTER STATUS
# ==============================================================================
with col_right:
    # Cluster Status Badge (top-right, full width)
    st.markdown(
        '<div class="acl-cluster-wrap">'
        '<span class="acl-cluster-badge">'
        '<span class="acl-dot-cluster"></span>'
        'Cluster v2.1-East Tokyo-04'
        '<span style="color: #71689F; font-size: 12px; margin-left: 2px;">&#x1F504;</span>'
        '</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Centered White Card
    st.markdown('<div class="acl-card-container">', unsafe_allow_html=True)
    with st.container(border=True):
        tab_login, tab_register = st.tabs(["Log in", "Register"])

        # ======================================================================
        # TAB 1: [ACL-01] DEFAULT OR [ACL-01-ERR] ERROR STATE
        # ======================================================================
        with tab_login:
            st.markdown(
                '<div style="margin-bottom: 16px;">'
                '<h2 style="font-size: 24px; font-weight: 700; color: #1C1A17; margin: 0 0 4px 0; font-family: \'Sora\', sans-serif;">Welcome back</h2>'
                '<p style="font-size: 13.5px; color: #71689F; margin: 0; font-family: \'Plus Jakarta Sans\', sans-serif;">Sign in to continue to your workspace.</p>'
                '</div>',
                unsafe_allow_html=True,
            )

            # High-Visibility Authentication Error Alert Banner matching Stitch [ACL-01-ERR]
            if error_active:
                st.markdown(
                    '<div style="background-color: #F8E2DE; border: 1.5px solid #C1382E; border-radius: 8px; padding: 12px 14px; margin-bottom: 16px; display: flex; align-items: center; gap: 10px;">'
                    '<span style="color: #C1382E; font-size: 17px; line-height: 1;">⚠️</span>'
                    '<span style="color: #C1382E; font-size: 13px; font-weight: 600; font-family: \'Plus Jakarta Sans\', sans-serif;">Invalid email or password. Please check your credentials and try again.</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )

            with st.form("stitch_login_form"):
                default_email = "wrong.account@studio.com" if error_active else "w.mori@hoshikawamanga.co.jp"
                default_pw = "WrongPassword999!" if error_active else "DoublePassLorem2024!"

                email = st.text_input("Email", value=default_email)
                if error_active:
                    st.markdown(
                        "<p style='color: #C1382E; font-size: 11.5px; font-weight: 600; margin-top: -10px; margin-bottom: 6px;'>Please check this email address.</p>",
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    '<div style="display: flex; justify-content: space-between; align-items: baseline; margin-top: 10px; margin-bottom: 4px;">'
                    '<span style="font-size: 13px; font-weight: 600; color: #1C1A17;">Password</span>'
                    '<span style="font-size: 11px; color: #71689F; font-family: \'JetBrains Mono\', monospace;">Min. 8 characters</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                password = st.text_input("Password", type="password", value=default_pw, label_visibility="collapsed")
                if error_active:
                    st.markdown(
                        "<p style='color: #C1382E; font-size: 11.5px; font-weight: 600; margin-top: -10px; margin-bottom: 6px;'>Incorrect password entered.</p>",
                        unsafe_allow_html=True,
                    )

                remember_me = st.checkbox("Remember me", value=True)
                submit = st.form_submit_button("Log In →", type="primary", use_container_width=True)

                if submit:
                    auth_service = get_auth_service()
                    try:
                        result = auth_service.login(email=email.strip(), password=password, remember_me=remember_me)
                        establish_session(result, remember_me=remember_me)
                        st.session_state["auth_failed"] = False
                        st.session_state["auth_error_msg"] = ""
                        st.success(f"Authenticated as {result.user.full_name} ({result.user.role})")
                        st.rerun()
                    except AuthServiceError as err:
                        st.session_state["auth_failed"] = True
                        st.session_state["auth_error_msg"] = str(err)
                        st.rerun()

            st.write("")
            col_fp_left, col_fp_right = st.columns([1.2, 1])
            with col_fp_left:
                st.markdown(
                    '<div style="padding-top: 8px; font-size: 13px; color: #71689F;">'
                    "Don't have an account? "
                    '<span style="color: #25326F; font-weight: 700;">Select Register</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )
            with col_fp_right:
                if st.button("Forgot password? →", key="btn_forgot_pw", use_container_width=True):
                    st.switch_page("pages/0_Forgot_Password.py")

        # ======================================================================
        # TAB 2: [ACL-02] USER REGISTRATION (CREATE NEW ACCOUNT)
        # ======================================================================
        with tab_register:
            st.markdown(
                '<div style="margin-bottom: 16px;">'
                '<h2 style="font-size: 24px; font-weight: 700; color: #1C1A17; margin: 0 0 4px 0; font-family: \'Sora\', sans-serif;">Create your account</h2>'
                '<p style="font-size: 13.5px; color: #71689F; margin: 0; font-family: \'Plus Jakarta Sans\', sans-serif;">You will be able to create or join a Project after signing up.</p>'
                '</div>',
                unsafe_allow_html=True,
            )

            with st.form("stitch_register_form"):
                reg_name = st.text_input("Full Name", placeholder="Phan Thanh Hoang")
                reg_email = st.text_input("Work Email", placeholder="you@studio.com")
                reg_pwd = st.text_input("Password", type="password", placeholder="At least 8 characters")
                reg_cpwd = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
                terms = st.checkbox("I agree to the Terms of Service and Privacy Policy", value=True)

                reg_submit = st.form_submit_button("Create Account →", type="primary", use_container_width=True)

                if reg_submit:
                    if not reg_name.strip() or not reg_email.strip():
                        st.error("Please fill in your name and email.")
                    elif reg_pwd != reg_cpwd:
                        st.markdown(
                            '<div style="background-color: #F8E2DE; border: 1.5px solid #C1382E; border-radius: 8px; padding: 10px 14px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">'
                            '<span style="color: #C1382E;">⚠️</span>'
                            '<span style="color: #C1382E; font-size: 12.5px; font-weight: 600;">Passwords do not match. Please re-enter identical passwords.</span>'
                            '</div>',
                            unsafe_allow_html=True,
                        )
                    elif len(reg_pwd) < 8:
                        st.error("Password must be at least 8 characters.")
                    elif not terms:
                        st.error("Please agree to the Terms of Service and Privacy Policy.")
                    else:
                        auth_service = get_auth_service()
                        try:
                            result = auth_service.register(full_name=reg_name.strip(), email=reg_email.strip(), password=reg_pwd)
                            establish_session(result, remember_me=True)
                            st.session_state["auth_failed"] = False
                            st.success(f"Account created successfully for {result.user.full_name}!")
                            st.rerun()
                        except AuthServiceError as err:
                            st.markdown(
                                '<div style="background-color: #F8E2DE; border: 1.5px solid #C1382E; border-radius: 8px; padding: 10px 14px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">'
                                '<span style="color: #C1382E;">⚠️</span>'
                                f'<span style="color: #C1382E; font-size: 12.5px; font-weight: 600;">{str(err)}</span>'
                                '</div>',
                                unsafe_allow_html=True,
                            )

            st.markdown(
                '<div style="text-align: center; margin-top: 18px; font-size: 13px; color: #71689F;">'
                'Already have an account? '
                '<span style="color: #25326F; font-weight: 700;">Select Log in tab above</span>'
                '</div>',
                unsafe_allow_html=True,
            )

    st.markdown('</div>', unsafe_allow_html=True)

    # Bottom Right Telemetry
    st.markdown(
        '<div class="acl-telemetry-bottom">'
        '<span class="acl-dot-cluster"></span>'
        '<span>Dev Scripts, QA-1 (Active Solo)</span>'
        '<span style="opacity: 0.4;">|</span>'
        '<span>Target: Japanese &gt; English, dual-direction</span>'
        '</div>',
        unsafe_allow_html=True,
    )
