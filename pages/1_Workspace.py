"""ACL - [ACL-04] & [ACL-04-MODAL] Project Workspace Dashboard & Modal (100% Streamlit Native)."""

import streamlit as st
from backend.database import SessionLocal
from backend.models import Chapter, ComicPage, Project, ProjectMembership, User
from services.workspace_service import WorkspaceService, WorkspaceServiceError
from utils.auth_session import current_user, require_auth

# Guard: Ensure authenticated user
user = require_auth()

# Page-Scoped CSS (Strict Stitch [ACL-04] & [ACL-04-MODAL] Tokens)
st.markdown("""
<style>
    .acl-workspace-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
        padding-bottom: 16px;
        border-bottom: 1.5px solid #E4DFD6;
    }
    
    .acl-user-badge {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .acl-avatar-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: #25326F;
        color: #FFFFFF;
        font-family: 'Sora', sans-serif;
        font-weight: 700;
        font-size: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 8px rgba(37, 50, 111, 0.25);
    }
    
    /* Project Card Surfaces */
    .acl-series-card {
        background: #FFFFFF;
        border: 1.5px solid #E4DFD6;
        border-radius: 16px;
        padding: 22px 20px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .acl-series-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(37, 50, 111, 0.08);
        border-color: #25326F;
    }
    
    /* Status Badges */
    .acl-status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: -0.2px;
    }
    .acl-status-pill.review {
        background-color: #E6F0E9;
        color: #2F7A4F;
    }
    .acl-status-pill.inpainting {
        background-color: #E7EAF5;
        color: #25326F;
    }
    .acl-status-pill.completed {
        background-color: #E6F0E9;
        color: #2F7A4F;
    }
    
    /* Overlapping Team Avatar Stack */
    .acl-avatar-stack {
        display: flex;
        align-items: center;
        margin-top: 14px;
        margin-bottom: 18px;
    }
    .acl-stack-avatar {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        border: 2px solid #FFFFFF;
        font-size: 10px;
        font-weight: 700;
        font-family: 'Plus Jakarta Sans', sans-serif;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-left: -7px;
        color: #FFFFFF;
    }
    .acl-stack-avatar:first-child {
        margin-left: 0;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# [ACL-04-MODAL] MODAL DIALOG OVERLAY (MATCHING STITCH SPEC)
# ==============================================================================
@st.dialog("Create New Project")
def show_create_project_modal():
    st.markdown("""
    <p style="font-size: 13.5px; color: #71689F; margin-top: -8px; margin-bottom: 18px; font-family: 'Plus Jakarta Sans', sans-serif;">
        Set up a new comic series or chapter bundle for your localization team.
    </p>
    """, unsafe_allow_html=True)
    
    with st.form("modal_create_project_form"):
        modal_title = st.text_input("Project / Series Name", placeholder="e.g. Shonen Weekly #112")
        modal_desc = st.text_area("Description", placeholder="Enter chapter notes, release target date, or source notes...", height=85)
        
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            src_lang = st.selectbox("Source Language", ["Japanese (Raw Manga)", "Korean (Webtoon)", "English (Raw Scan)"])
        with col_l2:
            tgt_lang = st.selectbox("Target Language", ["Vietnamese (Artisanal Localization)", "English (Standard Edition)"])
            
        col_cancel, col_create = st.columns([1, 1.3])
        with col_cancel:
            cancel = st.form_submit_button("Cancel", use_container_width=True)
        with col_create:
            create_btn = st.form_submit_button("Create Project →", type="primary", use_container_width=True)
            
        if create_btn:
            if not modal_title.strip():
                st.error("Please enter a project / series title.")
            else:
                ws = WorkspaceService()
                try:
                    desc_text = f"{modal_desc.strip() or 'Weekly Localization'} • {src_lang} ➔ {tgt_lang}"
                    with SessionLocal() as db:
                        db_u = db.query(User).filter_by(email=user.email).first()
                        active_uid = db_u.id if db_u else 1
                    created = ws.create_project(user_id=active_uid, title=modal_title.strip(), description=desc_text)
                    st.success(f"Project '{created.title}' created successfully!")
                    st.rerun()
                except WorkspaceServiceError as e:
                    st.error(str(e))
        if cancel:
            st.rerun()

# 1. Header Row matching Stitch [ACL-04]
user_initials = "".join([part[0].upper() for part in user.full_name.split()][:2]) or "PH"

col_head_left, col_head_right = st.columns([3, 1])
with col_head_left:
    st.markdown("""
    <div style="margin-bottom: 8px;">
        <h1 style="font-size: 32px; font-weight: 700; color: #1C1A17; margin: 0; font-family: 'Sora', sans-serif;">Projects</h1>
        <p style="font-size: 14px; color: #71689F; margin: 2px 0 0 0; font-family: 'Plus Jakarta Sans', sans-serif;">Manage your ongoing comic localization series.</p>
    </div>
    """, unsafe_allow_html=True)

with col_head_right:
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-end; align-items: center; gap: 12px; margin-top: 6px;">
        <div style="text-align: right;">
            <div style="font-size: 13.5px; font-weight: 700; color: #1C1A17;">{user.full_name}</div>
            <div style="font-size: 11.5px; color: #71689F;">{user.role}</div>
        </div>
        <div class="acl-avatar-circle">{user_initials}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border: none; border-top: 1.5px solid #E4DFD6; margin-top: 8px; margin-bottom: 20px;'>", unsafe_allow_html=True)

# 2. Action & Filter Bar
col_search, col_filter, col_add_btn = st.columns([2.2, 1, 1.2], gap="medium")
with col_search:
    search_query = st.text_input("Search Projects", placeholder="Search series title...", label_visibility="collapsed")
with col_filter:
    filter_status = st.selectbox("Filter Status", ["All Projects", "In review", "Inpainting", "Completed"], label_visibility="collapsed")
with col_add_btn:
    if st.button("+ Create New Project", type="primary", use_container_width=True):
        show_create_project_modal()

st.write("")

# 3. [ACL-04] Comic Projects 3-Column Grid
# Canonical Stitch Demo Cards Data
demo_series_cards = [
    {
        "id": 1,
        "title": "Shonen Weekly #112",
        "subtitle": "24 pages • Japanese ➔ Vietnamese",
        "status": "In review",
        "status_class": "review",
        "avatars": [
            {"init": "MH", "bg": "#25326F"},
            {"init": "TH", "bg": "#3B4B1F"},
            {"init": "QN", "bg": "#71689F"},
        ],
        "action_label": "Open Chapter Studio →",
        "action_target": "pages/3_Chapter_Studio.py",
        "action_color": "primary",
    },
    {
        "id": 2,
        "title": "One Piece — Chapter 1115",
        "subtitle": "19 pages • Japanese ➔ Vietnamese",
        "status": "Inpainting",
        "status_class": "inpainting",
        "avatars": [
            {"init": "LH", "bg": "#25326F"},
            {"init": "PH", "bg": "#3B4B1F"},
        ],
        "action_label": "View Queue →",
        "action_target": "pages/6_Queue_Monitor.py",
        "action_color": "primary",
    },
    {
        "id": 3,
        "title": "Jujutsu Kaisen — Special",
        "subtitle": "32 pages • English ➔ Vietnamese",
        "status": "Completed",
        "status_class": "completed",
        "avatars": [
            {"init": "MH", "bg": "#25326F"},
            {"init": "PH", "bg": "#3B4B1F"},
            {"init": "TH", "bg": "#71689F"},
            {"init": "QN", "bg": "#2F7A4F"},
        ],
        "action_label": "Download ZIP →",
        "action_target": "pages/6_Queue_Monitor.py",
        "action_color": "primary",
    },
]

# Query additional user-created projects from SQLite acl.db
with SessionLocal() as db:
    all_db_projects = db.query(Project).order_by(Project.id.desc()).all()
    db_titles = {c["title"] for c in demo_series_cards}
    for p in all_db_projects:
        if p.title not in db_titles:
            demo_series_cards.append({
                "id": p.id,
                "title": p.title,
                "subtitle": p.description or "Standard Comic Localization Workflow",
                "status": "In review",
                "status_class": "review",
                "avatars": [{"init": "WM", "bg": "#25326F"}, {"init": "PQ", "bg": "#3B4B1F"}],
                "action_label": "Open Chapter Studio →",
                "action_target": "pages/3_Chapter_Studio.py",
                "action_color": "primary",
            })

# Apply Search & Filter
filtered_cards = demo_series_cards
if search_query.strip():
    filtered_cards = [c for c in filtered_cards if search_query.strip().lower() in c["title"].lower()]
if filter_status != "All Projects":
    filtered_cards = [c for c in filtered_cards if c["status"] == filter_status]

# Render in 3-column rows matching Stitch layout
for row_idx in range(0, len(filtered_cards), 3):
    row_slice = filtered_cards[row_idx:row_idx+3]
    cols = st.columns(3, gap="large")
    
    for c_idx, card in enumerate(row_slice):
        with cols[c_idx]:
            with st.container(border=True):
                badge_bg = "#E6F0E9" if card["status_class"] in ["review", "completed"] else "#E7EAF5"
                badge_fg = "#2F7A4F" if card["status_class"] in ["review", "completed"] else "#25326F"
                
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                    <span class="acl-status-pill" style="background: {badge_bg}; color: {badge_fg};">
                        ● {card['status']}
                    </span>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #71689F;">
                        SERIES-0{card['id']}
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
                # Card Title & Subtitle
                st.markdown(f"""
                <div style="margin-bottom: 14px;">
                    <h3 style="font-size: 18px; font-weight: 700; color: #1C1A17; margin: 0 0 4px 0; font-family: 'Sora', sans-serif;">{card['title']}</h3>
                    <p style="font-size: 13px; color: #71689F; margin: 0; font-family: 'Plus Jakarta Sans', sans-serif;">{card['subtitle']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Team Avatar Stack
                avatar_html = '<div class="acl-avatar-stack">'
                for av in card["avatars"]:
                    avatar_html += f'<div class="acl-stack-avatar" style="background-color: {av["bg"]};">{av["init"]}</div>'
                avatar_html += f'<span style="font-size: 11.5px; color: #71689F; margin-left: 10px; font-family: \'Plus Jakarta Sans\', sans-serif;">{len(card["avatars"])} assigned</span>'
                avatar_html += '</div>'
                st.markdown(avatar_html, unsafe_allow_html=True)
                
                st.markdown("<hr style='border: none; border-top: 1px solid #E4DFD6; margin: 12px 0 16px 0;'>", unsafe_allow_html=True)
                
                # Card Action Button
                if st.button(card["action_label"], key=f"btn_card_{card['id']}_{row_idx}_{c_idx}", type=card["action_color"], use_container_width=True):
                    st.session_state["current_project_id"] = card["id"]
                    st.session_state["current_project_title"] = card["title"]
                    st.switch_page(card["action_target"])
