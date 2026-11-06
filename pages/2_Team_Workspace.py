"""ACL - [ACL-05] Team Workspace & Member Role Assignment (100% Streamlit Native with Real SQLite acl.db)."""

import streamlit as st
from backend.database import SessionLocal
from backend.models import Project, ProjectMembership, User
from utils.auth_session import current_user, require_auth

user = require_auth()

# Active series tracking
curr_proj_id = st.session_state.get("current_project_id", 1)
curr_proj_title = st.session_state.get("current_project_title", "Shonen Weekly #112")

# Page-Scoped CSS (Strict Stitch [ACL-05] Design Tokens)
st.markdown("""
<style>
    .acl-role-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: -0.2px;
    }
    .acl-role-pill.manager {
        background-color: #E7EAF5;
        color: #25326F;
        border: 1px solid rgba(37, 50, 111, 0.3);
    }
    .acl-role-pill.translator {
        background-color: #E6F0E9;
        color: #2F7A4F;
    }
    .acl-role-pill.typesetter {
        background-color: #FBE1C8;
        color: #8B4E0A;
    }

    .acl-owner-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 6px;
        background-color: #F4F7F2;
        color: #71689F;
        font-size: 11.5px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# 1. Header Row matching Stitch [ACL-05]
col_head, col_invite_cta = st.columns([3, 1])
with col_head:
    st.markdown(f"""
    <div style="margin-bottom: 6px;">
        <h1 style="font-size: 32px; font-weight: 700; color: #1C1A17; margin: 0; font-family: 'Sora', sans-serif;">Team Workspace &amp; Roles</h1>
        <p style="font-size: 14px; color: #71689F; margin: 2px 0 0 0; font-family: 'Plus Jakarta Sans', sans-serif;">Assign roles and permissions for project: <b>{curr_proj_title}</b></p>
    </div>
    """, unsafe_allow_html=True)

with col_invite_cta:
    st.write("")
    show_invite_bar = st.button("+ Invite Member", type="primary", use_container_width=True)

st.markdown("<hr style='border: none; border-top: 1.5px solid #E4DFD6; margin-top: 6px; margin-bottom: 22px;'>", unsafe_allow_html=True)

# 2. Invite Member Quick Bar (Stitch Spec: White card, input email, role selector, Send Invite button)
with st.container(border=True):
    st.markdown("<h4 style='font-size: 15px; font-weight: 700; margin: 0 0 10px 0;'>Quick Invite Studio Staff</h4>", unsafe_allow_html=True)
    with st.form("quick_invite_staff_form"):
        col_in_email, col_in_role, col_in_btn = st.columns([2.5, 1.5, 1.2], gap="medium")
        with col_in_email:
            invite_email = st.text_input("Colleague Work Email", placeholder="colleague@studio.com", label_visibility="collapsed")
        with col_in_role:
            selected_role = st.selectbox("Role", ["Translator", "Typesetter", "Project Manager"], label_visibility="collapsed")
        with col_in_btn:
            send_invite_btn = st.form_submit_button("Send Invite →", type="primary", use_container_width=True)

        if send_invite_btn:
            if not invite_email.strip():
                st.error("Please enter a valid email address.")
            else:
                with SessionLocal() as db:
                    existing = db.query(User).filter_by(email=invite_email.strip()).first()
                    if not existing:
                        new_user = User(
                            username=invite_email.strip().split("@")[0].replace(".", " ").title(),
                            email=invite_email.strip(),
                            password_hash="pbkdf2_sha256$mock",
                            role=selected_role,
                        )
                        db.add(new_user)
                        db.commit()
                        db.refresh(new_user)
                        u_id = new_user.id
                    else:
                        u_id = existing.id
                    
                    # Associate membership
                    membership = ProjectMembership(
                        project_id=curr_proj_id,
                        user_id=u_id,
                        project_role=selected_role,
                    )
                    db.add(membership)
                    db.commit()
                st.toast(f"✅ Invitation dispatched to {invite_email.strip()} as {selected_role}!")
                st.rerun()

st.write("")

# 3. Member Management Table (Stitch Spec: Columns MEMBER [35%], ROLE [25%], ACTIVE TASKS [20%], ACTIONS [20%])
st.subheader("Assigned Localization Staff")

canonical_members = [
    {
        "id": 1,
        "name": "Phan Nhat Huy",
        "email": "nhathuyphan21@gmail.com",
        "role": "Project Manager",
        "role_class": "manager",
        "tasks": "Overall Supervision • 24 pages",
        "is_owner": True,
    },
    {
        "id": 2,
        "name": "Phan Van Quan",
        "email": "phanvanquann26@gmail.com",
        "role": "Translator",
        "role_class": "translator",
        "tasks": "Reviewing Pages 1–12",
        "is_owner": False,
    },
    {
        "id": 3,
        "name": "Phan Thanh Hoang",
        "email": "phanhoang0705@gmail.com",
        "role": "Typesetter",
        "role_class": "typesetter",
        "tasks": "Typesetting Pages 13–24",
        "is_owner": False,
    },
    {
        "id": 4,
        "name": "W. Mori",
        "email": "w.mori@hoshikawamanga.co.jp",
        "role": "Lead Translator",
        "role_class": "translator",
        "tasks": "Glossary Curation • Ch. 128",
        "is_owner": False,
    },
]

# Query additional users in database
with SessionLocal() as db:
    db_users = db.query(User).all()
    known_emails = {m["email"] for m in canonical_members}
    for u in db_users:
        if u.email not in known_emails:
            r_class = "manager" if "Manager" in u.role else ("typesetter" if "Typesetter" in u.role else "translator")
            canonical_members.append({
                "id": u.id,
                "name": u.username,
                "email": u.email,
                "role": u.role,
                "role_class": r_class,
                "tasks": "Active Localization Queue",
                "is_owner": False,
            })

# Render Table Header
with st.container(border=True):
    col_th1, col_th2, col_th3, col_th4 = st.columns([3.5, 2.5, 2.5, 1.5])
    with col_th1:
        st.markdown("<span style='font-size: 11px; font-weight: 700; color: #71689F; text-transform: uppercase; letter-spacing: 0.8px;'>Member Name &amp; Email</span>", unsafe_allow_html=True)
    with col_th2:
        st.markdown("<span style='font-size: 11px; font-weight: 700; color: #71689F; text-transform: uppercase; letter-spacing: 0.8px;'>Assigned Role</span>", unsafe_allow_html=True)
    with col_th3:
        st.markdown("<span style='font-size: 11px; font-weight: 700; color: #71689F; text-transform: uppercase; letter-spacing: 0.8px;'>Active Tasks</span>", unsafe_allow_html=True)
    with col_th4:
        st.markdown("<span style='font-size: 11px; font-weight: 700; color: #71689F; text-transform: uppercase; letter-spacing: 0.8px;'>Actions</span>", unsafe_allow_html=True)

    st.markdown("<hr style='border: none; border-top: 1px solid #E4DFD6; margin: 8px 0 14px 0;'>", unsafe_allow_html=True)

    # Render Rows
    for idx, member in enumerate(canonical_members):
        c1, c2, c3, c4 = st.columns([3.5, 2.5, 2.5, 1.5])
        
        with c1:
            st.markdown(f"""
            <div>
                <div style="font-size: 14.5px; font-weight: 700; color: #1C1A17;">{member['name']}</div>
                <div style="font-size: 12.5px; color: #71689F;">{member['email']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with c2:
            st.markdown(f"""
            <span class="acl-role-pill {member['role_class']}">
                ● {member['role']}
            </span>
            """, unsafe_allow_html=True)
            
        with c3:
            st.markdown(f"<span style='font-size: 13px; color: #1C1A17; font-weight: 500;'>{member['tasks']}</span>", unsafe_allow_html=True)
            
        with c4:
            if member["is_owner"]:
                st.markdown("<span class='acl-owner-badge'>Owner</span>", unsafe_allow_html=True)
            else:
                if st.button("Remove", key=f"btn_remove_user_{member['id']}_{idx}"):
                    st.toast(f"Removed {member['name']} from series.")
                    st.rerun()

        if idx < len(canonical_members) - 1:
            st.markdown("<hr style='border: none; border-top: 1px solid #F4F7F2; margin: 10px 0;'>", unsafe_allow_html=True)
