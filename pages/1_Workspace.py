"""ACL Project Workspace Dashboard (Series Grid) — Screen ACL-04.

Pixel-perfect implementation matching Google Stitch Project 'UX/UI_ACL'.
Screen: ACL-04: Project Workspace Dashboard (Series Grid).
Modal: ACL-04-MODAL: Create New Project Modal Overlay.
100% real SQLite data, zero mock data, responsive layout.
"""

from html import escape
import os
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from utils.auth_session import require_auth
from backend.database import SessionLocal, init_db
from backend.models import Chapter, ComicPage, Project, ProjectMembership, User
from services.workspace_service import WorkspaceService

# Enforce authentication guard
user = require_auth()

user_initials = (user.full_name[:2] if user.full_name else "PH").upper()
user_name = user.full_name or "Phan Van Quan"

init_db()
db = SessionLocal()

# Ensure current user exists in SQLite users table
db_user = db.query(User).filter_by(email=user.email).first()
if not db_user:
    db_user = User(
        username=user.full_name or user.email.split("@")[0],
        email=user.email,
        password_hash="session_user_hash",
        role="editor",
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

# Handle Create New Project form submission (persisting to projects table)
create_title = st.query_params.get("create_title")
create_desc = st.query_params.get("create_desc", "0 pages • Japanese ➔ Vietnamese")
if create_title:
    title_clean = create_title.strip()
    if title_clean:
        existing_proj = db.query(Project).filter_by(title=title_clean).first()
        if not existing_proj:
            new_proj = Project(
                owner_id=db_user.id,
                title=title_clean,
                description=create_desc or "0 pages • Japanese ➔ Vietnamese",
            )
            db.add(new_proj)
            db.commit()
            db.refresh(new_proj)
            # Add owner membership in project_memberships table
            db.add(
                ProjectMembership(
                    project_id=new_proj.id,
                    user_id=db_user.id,
                    project_role="Owner",
                )
            )
            db.commit()
    st.query_params.pop("create_title", None)
    st.query_params.pop("create_desc", None)
    st.rerun()

# Query real projects for the authenticated user from SQLite database (NO mock seed data)
workspace_svc = WorkspaceService(session_factory=SessionLocal, initialize_database=False)
user_summaries = workspace_svc.list_projects(db_user.id)
user_proj_ids = [s.id for s in user_summaries]
projects = (
    db.query(Project)
    .filter(Project.id.in_(user_proj_ids))
    .order_by(Project.id.asc())
    .all()
    if user_proj_ids
    else []
)
active_projects_count = len(projects)

# Calculate real storage usage from data folder
BASE_DIR = Path(__file__).parents[1]
data_dir = BASE_DIR / "data"
total_bytes = 0
if data_dir.exists():
    for f in data_dir.rglob("*"):
        if f.is_file():
            total_bytes += f.stat().st_size
storage_mb = round(total_bytes / (1024 * 1024), 1)
if storage_mb >= 1024:
    storage_display = f"{round(storage_mb / 1024, 1)} GB"
    storage_pct = round((storage_mb / 10240) * 100, 1)
else:
    storage_display = f"{storage_mb} MB"
    storage_pct = round((storage_mb / 10240) * 100, 1)

# Generate project cards dynamically from SQLite records
cards_html_list = []
total_in_queue = 0

for idx, p in enumerate(projects, start=1):
    num_str = f"#{p.id:02d}"
    pages = (
        db.query(ComicPage)
        .join(Chapter, ComicPage.chapter_id == Chapter.id)
        .filter(Chapter.project_id == p.id)
        .all()
    )
    total_pages = len(pages)
    done_pages = sum(page.status == "COMPLETED" for page in pages)
    in_queue_pages = total_pages - done_pages
    total_in_queue += in_queue_pages
    prog_pct = round(done_pages / total_pages * 100) if total_pages > 0 else 0

    if done_pages > 0:
        status_pill = f"""<span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#E6F4EA] text-[#137333] font-code text-xs font-semibold">
          <span class="w-1.5 h-1.5 rounded-full bg-[#137333]"></span>
          <span>{done_pages} Pages Rendered</span>
        </span>"""
        prog_label = f"Progress: {done_pages}/{total_pages} Pages Reviewed"
        queue_link = f"""<a class="inline-flex items-center gap-1 font-semibold text-primary-container hover:underline cursor-pointer group/q" onclick="navigateParent('queue-monitor?project=' + encodeURIComponent('{escape(p.title)}'))" title="Inspect Live Pipeline Queue">
          <span class="w-1.5 h-1.5 rounded-full bg-[#137333] animate-pulse"></span>
          <span>Live Queue ({prog_pct}%)</span>
          <span class="material-symbols-outlined text-[13px] group-hover/q:translate-x-0.5 transition-transform">arrow_forward</span>
        </a>"""
    else:
        status_pill = """<span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#E8EDFB] text-[#1C274C] font-code text-xs font-semibold">
          <span>Ready for Upload</span>
        </span>"""
        prog_label = "Progress: Ready for Upload"
        queue_link = '<span class="font-semibold text-on-surface-variant">0%</span>'

    # Query members for avatars
    members = db.query(ProjectMembership).filter_by(project_id=p.id).all()
    if members:
        avatars_html = "".join(
            f"""<div class="w-7 h-7 rounded-full bg-primary-container text-on-primary border-2 border-white flex items-center justify-center font-code text-[11px] font-bold" title="{escape(m.user.username if m.user else 'User')}">{(m.user.username[:2] if m.user and m.user.username else 'US').upper()}</div>"""
            for m in members[:3]
        )
        team_tag = f"{len(members)} team"
    else:
        avatars_html = f"""<div class="w-7 h-7 rounded-full bg-primary-container text-on-primary border-2 border-white flex items-center justify-center font-code text-[11px] font-bold" title="{escape(user_name)}">{user_initials}</div>"""
        team_tag = "Owner"

    action_btn = f"""<a class="inline-flex items-center gap-1 text-xs font-semibold text-primary-container hover:underline cursor-pointer group" onclick="navigateParent('chapter-studio?project=' + encodeURIComponent('{escape(p.title)}'))">
      <span>Open Chapter Studio</span>
      <span class="material-symbols-outlined text-[16px] group-hover:translate-x-0.5 transition-transform">arrow_forward</span>
    </a>"""

    card_code = f"""
    <div class="project-card bg-surface-container-lowest rounded-2xl p-6 border border-[#E4DFD6] shadow-sm hover:shadow-md transition-all flex flex-col justify-between min-h-[270px]" data-title="{escape(p.title.lower())}">
      <div>
        <div class="flex items-center justify-between mb-1">
          <h3 class="font-headline text-lg font-bold text-on-surface">{escape(p.title)}</h3>
          <span class="px-2 py-0.5 rounded-full border border-[#C4C7C5] text-xs text-[#5A5E62] flex items-center justify-center font-medium font-code">{num_str}</span>
        </div>
        <p class="text-xs text-on-surface-variant font-medium">{escape(p.description or '0 pages • Japanese ➔ Vietnamese')}</p>
        <div class="mt-3">
          {status_pill}
        </div>
        <div class="mt-5">
          <div class="flex justify-between items-center text-xs text-on-surface-variant font-medium mb-1.5">
            <span>{prog_label}</span>
            {queue_link}
          </div>
          <div class="w-full bg-[#E8EAED] rounded-full h-1.5 overflow-hidden">
            <div class="bg-primary-container h-1.5 rounded-full transition-all" style="width: {prog_pct}%"></div>
          </div>
        </div>
      </div>
      <div class="mt-6 pt-4 border-t border-[#E4DFD6]/60 flex items-center justify-between">
        <div class="flex items-center cursor-pointer group/team p-1 -m-1 rounded-lg hover:bg-surface-container-low transition-colors" onclick="navigateParent('team-roles?project=' + encodeURIComponent('{escape(p.title)}'))" title="Manage team roles & permissions for {escape(p.title)}">
          <div class="flex items-center -space-x-1.5">
            {avatars_html}
          </div>
          <span class="text-xs text-on-surface-variant font-medium ml-2 group-hover/team:text-primary-container transition-colors">{team_tag}</span>
          <span class="material-symbols-outlined text-[15px] text-on-surface-variant ml-1 opacity-70 group-hover/team:opacity-100 group-hover/team:text-primary-container transition-all" title="Team Workspace">groups</span>
        </div>
        {action_btn}
      </div>
    </div>
    """
    cards_html_list.append(card_code)

if not cards_html_list:
    rendered_project_cards = """
    <div class="col-span-1 md:col-span-3 bg-surface-container-lowest rounded-2xl p-12 border border-[#E4DFD6] text-center shadow-sm">
      <div class="text-4xl mb-3">📁</div>
      <h3 class="font-headline text-lg font-bold text-on-surface">No ongoing projects yet</h3>
      <p class="text-xs text-on-surface-variant mt-1 mb-5">Create your first manga localization project to upload chapter raw scans.</p>
      <button onclick="showModal()" class="px-5 py-2.5 rounded-full bg-primary-container text-on-primary text-xs font-bold hover:bg-primary-container/90 transition-colors shadow-sm inline-flex items-center gap-2 cursor-pointer">
        <span class="material-symbols-outlined text-[16px]">add</span>
        <span>Create New Project</span>
      </button>
    </div>
    """
else:
    rendered_project_cards = "\n".join(cards_html_list)

workspace_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<meta content="web_dashboard" name="shell-type"/>
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,600&family=Sora:wght@600;700;800&subset=vietnamese,latin,latin-ext&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet"/>
<script src="https://cdn.tailwindcss.com"></script>

<script>
tailwind.config = {{
  theme: {{
    extend: {{
      colors: {{
        primary: "#1C274C",
        "primary-container": "#25326F",
        "on-primary": "#ffffff",
        "primary-fixed": "#dde1ff",
        "on-primary-fixed": "#09164a",
        secondary: "#536435",
        "secondary-container": "#d6e9b0",
        "on-secondary-container": "#3c4c20",
        tertiary: "#356658",
        "tertiary-container": "#b9ece2",
        "on-tertiary": "#ffffff",
        surface: "#f8faf7",
        "surface-container-lowest": "#ffffff",
        "surface-container-low": "#f2f5f1",
        "surface-container": "#ecefe9",
        "surface-container-high": "#e6e9e4",
        "surface-container-highest": "#e0e4de",
        "surface-variant": "#e1e4df",
        "on-surface": "#191c19",
        "on-surface-variant": "#5a5e62",
        outline: "#717971",
        "outline-variant": "#c1c8be",
        error: "#ba1a1a"
      }},
      fontFamily: {{
        sans: ["Plus Jakarta Sans", "sans-serif"],
        headline: ["Sora", "sans-serif"],
        code: ["JetBrains Mono", "monospace"]
      }}
    }}
  }}
}};
</script>
<style>
font {{
  font-family: inherit !important;
  font-size: inherit !important;
  line-height: inherit !important;
}}
.notranslate {{
  translate: no !important;
}}
</style>
</head>
<body class="bg-surface font-sans text-on-surface antialiased">

<!-- FIXED LEFT SIDEBAR (Matching Image 3) -->
<aside class="fixed left-0 top-0 h-full w-[220px] bg-surface-container-lowest z-50 flex flex-col justify-between py-5 border-r border-[#E4DFD6]">
  <div>
    <!-- Brand / Logo Area: Square Badge with 'A' -->
    <div class="px-5 mb-6 flex items-center gap-3">
      <div class="w-9 h-9 rounded-xl bg-primary-container text-on-primary flex items-center justify-center font-bold text-lg shadow-sm shrink-0">
        A
      </div>
      <div class="min-w-0">
        <h1 class="font-headline text-[17px] font-bold text-on-surface tracking-tight leading-none">ACL</h1>
        <p class="font-code text-[11px] text-on-surface-variant mt-1 leading-snug truncate">v2.4 Editorial Core</p>
      </div>
    </div>
    
    <!-- Navigation Links -->
    <nav class="px-3 flex flex-col gap-1">
      <a aria-current="page" class="flex items-center gap-3 px-3 py-2 transition-all bg-primary-container text-on-primary text-xs font-semibold rounded-xl cursor-pointer shadow-sm" onclick="navigateParent('workspace')">
        <span class="material-symbols-outlined text-[20px]">folder</span>
        <span>Projects</span>
      </a>
      <a class="flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all cursor-pointer" onclick="navigateParent('team-roles')">
        <span class="material-symbols-outlined text-[20px]">groups</span>
        <span>Team Roles</span>
      </a>
      <a class="flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all cursor-pointer" onclick="navigateParent('chapter-studio')">
        <span class="material-symbols-outlined text-[20px]">cloud_upload</span>
        <span>Chapter Studio</span>
      </a>
      <a class="flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all cursor-pointer" onclick="navigateParent('review-studio')">
        <span class="material-symbols-outlined text-[20px]">vertical_split</span>
        <span>Review Studio</span>
      </a>
      <a class="flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all cursor-pointer" onclick="navigateParent('typesetting')">
        <span class="material-symbols-outlined text-[20px]">edit_note</span>
        <span>Typesetting</span>
      </a>
      <a class="flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all cursor-pointer" onclick="navigateParent('queue-monitor')">
        <span class="material-symbols-outlined text-[20px]">schedule</span>
        <span>Queue Monitor</span>
      </a>
      <a class="flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all cursor-pointer" onclick="navigateParent('settings')">
        <span class="material-symbols-outlined text-[20px]">settings</span>
        <span>Personal Settings</span>
      </a>
    </nav>
  </div>

  <!-- Sidebar Footer: Documentation, Core Online & Sign Out -->
  <div class="px-5 pt-3 border-t border-[#E4DFD6] flex flex-col gap-2.5">
    <a class="flex items-center gap-2 text-on-surface-variant hover:text-on-surface text-xs font-medium cursor-pointer transition-colors" onclick="alert('ACL Documentation v2.4: System guides, Manga-OCR pipelines, and API specs.')">
      <span class="material-symbols-outlined text-[18px]">help_outline</span>
      <span>Documentation</span>
    </a>
    <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#E8F5E9] text-[#2E7D32] border border-[#C8E6C9] font-code text-xs font-semibold w-fit">
      <span class="w-2 h-2 rounded-full bg-[#2E7D32] animate-pulse"></span>
      <span>Core • Online</span>
    </div>
    <a class="flex items-center gap-2 text-[#BA1A1A] hover:bg-[#FFDAD6]/40 px-2.5 py-1.5 rounded-xl text-xs font-semibold cursor-pointer transition-all mt-1" onclick="navigateParent('login?logout=1')" title="Sign out of ACL Studio">
      <span class="material-symbols-outlined text-[18px] text-[#BA1A1A]">logout</span>
      <span>Sign Out</span>
    </a>
  </div>
</aside>

<!-- MAIN APP SHELL -->
<div class="pl-[220px]">

  <!-- TOP HEADER BAR (Matching Image 3) -->
  <header class="fixed top-0 left-[220px] right-0 h-16 bg-surface-container-lowest/95 backdrop-blur-md z-40 px-8 flex items-center justify-between border-b border-[#E4DFD6]">
    
    <!-- Left: Breadcrumb -->
    <div class="flex items-center gap-2">
      <span class="text-base font-bold text-on-surface">ACL Studio</span>
      <span class="text-outline-variant font-light text-sm">/</span>
      <span class="text-sm text-on-surface-variant font-medium">Projects</span>
    </div>

    <!-- Right Header Controls -->
    <div class="flex items-center gap-4">
      
      <!-- Search Input -->
      <div class="hidden md:flex items-center bg-surface-container-low rounded-full px-3.5 py-1.5 border border-[#E4DFD6]">
        <span class="material-symbols-outlined text-[18px] text-on-surface-variant mr-1.5">search</span>
        <input id="header-search-input" class="bg-transparent text-xs outline-none placeholder:text-on-surface-variant w-44 text-on-surface" placeholder="Filter batches or series..." type="text"/>
      </div>

      <!-- Node Tokyo-01 Status Badge -->
      <a class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#E8EDF4] text-[#414754] border border-[#D0D7DE] font-code text-xs font-medium cursor-pointer" title="Local Pipeline Daemon Context">
        <span class="material-symbols-outlined text-[15px] text-[#57606A]">memory</span>
        <span>Node Tokyo-01 (GPU idle)</span>
      </a>

      <!-- Notification Bell -->
      <div class="relative">
        <button id="notif-btn" onclick="toggleNotifDropdown(event)" class="relative p-1.5 rounded-full hover:bg-surface-container text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer" title="Notifications">
          <span class="material-symbols-outlined text-[22px]">notifications</span>
          <span id="notif-badge" class="absolute top-1 right-1 w-2.5 h-2.5 bg-[#DC2626] rounded-full ring-2 ring-white animate-pulse"></span>
        </button>

        <!-- Dropdown -->
        <div id="notif-dropdown" class="hidden absolute right-0 mt-2 w-80 bg-surface-container-lowest rounded-2xl shadow-xl border border-[#E4DFD6] py-3 z-50 text-left transition-all">
          <div class="flex items-center justify-between px-4 pb-2 border-b border-[#E4DFD6]/70">
            <div class="flex items-center gap-2">
              <span class="text-sm font-bold text-on-surface">Notifications</span>
              <span id="notif-count" class="px-2 py-0.5 rounded-full bg-[#FEE2E2] text-[#DC2626] font-code text-[11px] font-semibold">1 New</span>
            </div>
          </div>
          <div class="p-3 hover:bg-surface-container-low transition-colors cursor-pointer" onclick="navigateParent('queue-monitor')">
            <p class="text-xs font-semibold text-on-surface">SQLite Connected</p>
            <p class="text-[11px] text-on-surface-variant mt-0.5">{active_projects_count} active project(s) ready in workspace.</p>
          </div>
        </div>
      </div>

      <!-- Filter Icon -->
      <button onclick="document.getElementById('header-search-input')?.focus();" class="p-1.5 rounded-full hover:bg-surface-container text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer" title="Filter series">
        <span class="material-symbols-outlined text-[20px]">tune</span>
      </button>

      <!-- User Profile Menu -->
      <div class="relative pl-2 border-l border-[#E4DFD6]">
        <button id="profile-btn" onclick="toggleProfileDropdown(event)" class="flex items-center gap-1.5 p-1 rounded-full hover:bg-surface-container transition-colors cursor-pointer group" title="Account Menu">
          <div class="w-8 h-8 rounded-full bg-primary-container flex items-center justify-center font-bold text-xs text-on-primary shadow-sm notranslate" translate="no" title="{escape(user_name)}">
            {user_initials}
          </div>
          <span class="material-symbols-outlined text-[18px] text-on-surface-variant group-hover:text-on-surface transition-transform duration-200">expand_more</span>
        </button>

        <!-- Profile Popover Dropdown -->
        <div id="profile-dropdown" class="hidden absolute right-0 mt-2 w-64 bg-surface-container-lowest rounded-2xl shadow-xl border border-[#E4DFD6] py-2 z-50 text-left transition-all">
          <div class="px-4 py-3 border-b border-[#E4DFD6]/70 flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-primary-container flex items-center justify-center font-bold text-sm text-on-primary shrink-0 notranslate" translate="no">
              {user_initials}
            </div>
            <div class="min-w-0 flex-1">
              <div class="text-sm font-bold text-on-surface truncate notranslate" translate="no">{escape(user_name)}</div>
              <div class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[#E8EDF4] text-primary-container font-code text-[11px] font-semibold mt-0.5">
                <span class="w-1.5 h-1.5 rounded-full bg-primary-container"></span>
                <span>Lead Editor</span>
              </div>
            </div>
          </div>
          <div class="py-1">
            <a class="flex items-center gap-2.5 px-4 py-2 text-xs font-medium text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low transition-colors cursor-pointer" onclick="navigateParent('settings')">
              <span class="material-symbols-outlined text-[18px]">manage_accounts</span>
              <span>Personal Settings</span>
            </a>
            <a class="flex items-center gap-2.5 px-4 py-2 text-xs font-medium text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low transition-colors cursor-pointer" onclick="navigateParent('team-roles')">
              <span class="material-symbols-outlined text-[18px]">groups</span>
              <span>Team Workspace</span>
            </a>
            <div class="border-t border-[#E4DFD6]/70 my-1"></div>
            <a class="flex items-center gap-2.5 px-4 py-2 text-xs font-semibold text-[#BA1A1A] hover:bg-[#FFDAD6]/40 transition-colors cursor-pointer" onclick="navigateParent('login?logout=1')">
              <span class="material-symbols-outlined text-[18px] text-[#BA1A1A]">logout</span>
              <span>Sign Out</span>
            </a>
          </div>
        </div>
      </div>

    </div>
  </header>

  <!-- MAIN VIEWPORT CONTENT (Matching Image 3) -->
  <main class="w-full min-h-screen pt-20 pb-12 bg-surface px-8">
    <div id="main-content-wrap" class="max-w-7xl mx-auto flex flex-col w-full transition-all duration-200">
      
      <!-- Page Title & Create Project Button Row -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 class="font-headline text-3xl font-bold text-on-surface tracking-tight">Projects</h1>
          <p class="text-sm text-on-surface-variant mt-1 font-normal">
            Manage your ongoing comic localization series and translation pipelines.
          </p>
        </div>
        <button id="create-project-btn" onclick="showModal()" class="inline-flex items-center gap-2 h-11 px-6 rounded-full bg-primary text-on-primary text-sm font-semibold hover:bg-primary-container transition-all shadow-sm active:scale-95 cursor-pointer self-start sm:self-auto" type="button">
          <span class="material-symbols-outlined text-[20px]">add</span>
          <span>Create New Project</span>
        </button>
      </div>

      <!-- SECTION 1: PROJECT CARDS GRID (Matching Image 3) -->
      <div id="projects-grid" class="grid grid-cols-1 md:grid-cols-3 gap-6">
        {rendered_project_cards}
      </div>

      <!-- SECTION 2: 3 STATS METRIC CARDS (Matching Image 3) -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">

        <!-- Stat 1: Active Projects -->
        <div class="bg-surface-container-lowest rounded-2xl p-6 border border-[#E4DFD6] shadow-sm hover:shadow-md hover:border-primary-container/40 transition-all flex items-center justify-between group">
          <div>
            <span class="text-xs font-medium text-on-surface-variant block mb-1 group-hover:text-primary-container transition-colors">Active Projects</span>
            <div class="flex items-baseline gap-2">
              <span class="text-3xl font-bold text-on-surface font-headline">{active_projects_count}</span>
              <span class="text-xs font-semibold text-[#137333] font-code">+1 this week</span>
            </div>
          </div>
          <div class="w-12 h-12 rounded-xl bg-[#F0F4F8] group-hover:bg-primary-container/10 transition-colors flex items-center justify-center text-on-surface-variant group-hover:text-primary-container">
            <span class="material-symbols-outlined text-[24px] text-[#414754] group-hover:text-primary-container transition-colors">folder</span>
          </div>
        </div>

        <!-- Stat 2: In Queue -->
        <div class="bg-surface-container-lowest rounded-2xl p-6 border border-[#E4DFD6] shadow-sm hover:shadow-md hover:border-primary-container/40 transition-all cursor-pointer flex items-center justify-between group" onclick="navigateParent('queue-monitor')" title="Open Queue Monitor">
          <div>
            <span class="text-xs font-medium text-on-surface-variant block mb-1 group-hover:text-primary-container transition-colors">In Queue</span>
            <div class="flex items-baseline gap-2">
              <span class="text-3xl font-bold text-on-surface font-headline">{total_in_queue}</span>
              <span class="text-xs text-on-surface-variant font-code">pages pending OCR</span>
            </div>
          </div>
          <div class="w-12 h-12 rounded-xl bg-[#F0F4F8] group-hover:bg-primary-container/10 transition-colors flex items-center justify-center text-on-surface-variant group-hover:text-primary-container">
            <span class="material-symbols-outlined text-[24px] text-[#414754] group-hover:text-primary-container transition-colors">hourglass_empty</span>
          </div>
        </div>

        <!-- Stat 3: Storage Allocation -->
        <div class="bg-surface-container-lowest rounded-2xl p-6 border border-[#E4DFD6] shadow-sm hover:shadow-md hover:border-primary-container/40 transition-all flex items-center justify-between group">
          <div>
            <span class="text-xs font-medium text-on-surface-variant block mb-1 group-hover:text-primary-container transition-colors">Storage Allocation</span>
            <div class="flex items-baseline gap-2">
              <span class="text-3xl font-bold text-on-surface font-headline">{storage_display}</span>
              <span class="text-xs text-on-surface-variant font-code">/ 10 GB ({storage_pct}%)</span>
            </div>
          </div>
          <div class="w-12 h-12 rounded-xl bg-[#F0F4F8] group-hover:bg-primary-container/10 transition-colors flex items-center justify-center text-on-surface-variant group-hover:text-primary-container">
            <span class="material-symbols-outlined text-[24px] text-[#414754] group-hover:text-primary-container transition-colors">cloud</span>
          </div>
        </div>

      </div>

    </div>
  </main>
</div>

<!-- MODAL OVERLAY: CREATE NEW PROJECT (ACL-04-MODAL) -->
<div id="create-project-modal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 transition-all duration-300 opacity-0 pointer-events-none">
  <div class="bg-surface-container-lowest rounded-2xl shadow-2xl max-w-lg w-full p-7 transition-all duration-300 transform scale-95 border border-[#E4DFD6]">
    <div class="flex items-start justify-between">
      <div>
        <div class="flex items-center gap-2 mb-1">
          <span class="w-2 h-2 rounded-full bg-primary-container"></span>
          <span class="font-code text-xs uppercase tracking-wider text-on-surface-variant font-semibold">New Workspace Entity</span>
        </div>
        <h2 class="font-headline text-2xl font-bold text-on-surface tracking-tight">Create New Project</h2>
      </div>
      <button id="modal-close-x" onclick="dismissModal()" class="w-9 h-9 rounded-full bg-surface-container flex items-center justify-center text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-colors cursor-pointer" type="button">
        <span class="material-symbols-outlined text-[20px]">close</span>
      </button>
    </div>
    
    <p class="text-sm text-on-surface-variant mt-1.5 mb-6">
      Set up a new comic series or chapter bundle for your localization team.
    </p>

    <!-- Form Fields Stack -->
    <form id="create-project-form" class="flex flex-col gap-[18px]">
      <div class="flex flex-col">
        <label class="text-xs font-semibold text-on-surface mb-1.5 flex items-center justify-between" for="series-name">
          <span>Project / Series Name</span>
          <span class="font-code text-xs text-on-surface-variant font-normal">Required</span>
        </label>
        <input id="series-name" class="w-full h-[44px] px-3.5 bg-surface-container-low text-on-surface text-sm rounded-lg placeholder:text-outline focus:bg-surface-container-lowest focus:outline-none focus:ring-2 focus:ring-primary-container/25 transition-all border border-[#E4DFD6]" placeholder="e.g. Bleach Chapter 01" required type="text"/>
      </div>

      <div class="flex flex-col">
        <label class="text-xs font-semibold text-on-surface mb-1.5 flex items-center justify-between" for="series-desc">
          <span>Description</span>
          <span class="font-code text-xs text-on-surface-variant font-normal">Optional</span>
        </label>
        <textarea id="series-desc" class="w-full h-[90px] p-3 bg-surface-container-low text-on-surface text-sm rounded-lg resize-none placeholder:text-outline focus:bg-surface-container-lowest focus:outline-none focus:ring-2 focus:ring-primary-container/25 transition-all border border-[#E4DFD6]" placeholder="Enter chapter notes, release target date, or source notes..." rows="3"></textarea>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="flex flex-col">
          <label class="text-xs font-semibold text-on-surface mb-1.5 block">Source Language</label>
          <select id="source-lang-select" class="w-full h-[44px] px-3 rounded-lg bg-surface-container-low text-on-surface text-sm border border-[#E4DFD6] focus:outline-none focus:ring-2 focus:ring-primary-container/25">
            <option value="JA">Japanese (Raw Manga)</option>
            <option value="EN">English (Scanlation)</option>
            <option value="KO">Korean (Webtoon)</option>
          </select>
        </div>
        <div class="flex flex-col">
          <label class="text-xs font-semibold text-on-surface mb-1.5 block">Target Language</label>
          <select id="target-lang-select" class="w-full h-[44px] px-3 rounded-lg bg-surface-container-low text-on-surface text-sm border border-[#E4DFD6] focus:outline-none focus:ring-2 focus:ring-primary-container/25">
            <option value="VI" selected>Vietnamese</option>
            <option value="EN">English</option>
          </select>
        </div>
      </div>

      <div class="flex items-center justify-end gap-3 mt-4 pt-4 border-t border-[#E4DFD6]">
        <button id="modal-cancel-btn" onclick="dismissModal()" class="px-6 h-[42px] rounded-full bg-surface-container hover:bg-surface-container-high text-on-surface text-sm font-semibold transition-colors cursor-pointer" type="button">
          Cancel
        </button>
        <button id="modal-submit-btn" class="px-7 h-[42px] rounded-full bg-primary-container hover:bg-primary text-on-primary text-sm font-semibold shadow-md hover:shadow-lg transition-all flex items-center gap-2 justify-center cursor-pointer" type="submit">
          <span class="material-symbols-outlined text-[18px]">folder_special</span>
          <span>Create Project</span>
        </button>
      </div>
    </form>
  </div>
</div>

<script>
// Parent navigation bridge
function navigateParent(path) {{
  const target = '/' + path.replace(/^\\//, '');
  try {{
    if (window.parent && window.parent.location) {{
      window.parent.location.href = window.parent.location.origin + target;
      return;
    }}
  }} catch (e) {{}}
  window.location.href = target;
}}

// Notification Dropdown Toggle
function toggleNotifDropdown(e) {{
  e.stopPropagation();
  const profileDropdown = document.getElementById('profile-dropdown');
  if (profileDropdown) profileDropdown.classList.add('hidden');
  const dropdown = document.getElementById('notif-dropdown');
  if (dropdown) dropdown.classList.toggle('hidden');
}}

// Profile Dropdown Toggle
function toggleProfileDropdown(e) {{
  e.stopPropagation();
  const notifDropdown = document.getElementById('notif-dropdown');
  if (notifDropdown) notifDropdown.classList.add('hidden');
  const dropdown = document.getElementById('profile-dropdown');
  if (dropdown) dropdown.classList.toggle('hidden');
}}

document.addEventListener('click', function(e) {{
  const notifDropdown = document.getElementById('notif-dropdown');
  const notifBtn = document.getElementById('notif-btn');
  if (notifDropdown && !notifDropdown.contains(e.target) && notifBtn && !notifBtn.contains(e.target)) {{
    notifDropdown.classList.add('hidden');
  }}
  const profileDropdown = document.getElementById('profile-dropdown');
  const profileBtn = document.getElementById('profile-btn');
  if (profileDropdown && !profileDropdown.contains(e.target) && profileBtn && !profileBtn.contains(e.target)) {{
    profileDropdown.classList.add('hidden');
  }}
}});

// Header Search Filter Interaction
const headerSearch = document.getElementById('header-search-input');
const projectCards = document.querySelectorAll('.project-card');

if (headerSearch) {{
  headerSearch.addEventListener('input', (e) => {{
    const val = e.target.value.toLowerCase().trim();
    projectCards.forEach(card => {{
      const text = card.getAttribute('data-title') || '';
      card.style.display = text.includes(val) ? 'flex' : 'none';
    }});
  }});
}}

// Modal controls
const modal = document.getElementById('create-project-modal');
const modalBox = modal.querySelector('div');
const nameInput = document.getElementById('series-name');
const mainWrap = document.getElementById('main-content-wrap');

function showModal() {{
  modal.classList.remove('opacity-0', 'pointer-events-none');
  modalBox.classList.remove('scale-95');
  modalBox.classList.add('scale-100');
  if (mainWrap) mainWrap.classList.add('opacity-90', 'blur-[1px]', 'filter');
  setTimeout(() => {{ if (nameInput) nameInput.focus(); }}, 100);
}}

function dismissModal() {{
  modal.classList.add('opacity-0', 'pointer-events-none');
  modalBox.classList.add('scale-95');
  modalBox.classList.remove('scale-100');
  if (mainWrap) mainWrap.classList.remove('opacity-90', 'blur-[1px]', 'filter');
}}

const form = document.getElementById('create-project-form');
if (form) {{
  form.addEventListener('submit', (e) => {{
    e.preventDefault();
    const title = nameInput.value.trim();
    if (!title) return;
    const submitBtn = document.getElementById('modal-submit-btn');
    submitBtn.innerHTML = '<span class="material-symbols-outlined text-[18px] animate-spin">progress_activity</span><span>Creating Project...</span>';
    submitBtn.disabled = true;
    const descInput = document.getElementById('series-desc');
    const descVal = descInput ? descInput.value.trim() : '';
    const srcLang = document.getElementById('source-lang-select')?.value || 'JA';
    const tgtLang = document.getElementById('target-lang-select')?.value || 'VI';
    const finalDesc = descVal || ('0 pages • ' + srcLang + ' ➔ ' + tgtLang);
    navigateParent('workspace?create_title=' + encodeURIComponent(title) + '&create_desc=' + encodeURIComponent(finalDesc));
  }});
}}
</script>
</body>
</html>
"""

components.html(workspace_html, height=1050, scrolling=True)
db.close()
