"""ACL Queue Monitor & Async Pipeline Tracking — Screen ACL-09 & ACL-09-DONE.

Pixel-perfect implementation of Google Stitch Project 'UX/UI_ACL' (ID: 15081338219515375601).
Screen: ACL-09: Queue Monitor — Real-Time Pipeline Progress Tracker & ZIP Export.
Includes full Vietnamese Unicode font support with fallback metrics to ensure Google Translate never breaks fonts.
100% English UI Labels.
"""

import streamlit as st
import streamlit.components.v1 as components

from utils.auth_session import require_auth


# Enforce authentication guard
user = require_auth()

user_initials = (user.full_name[:2] if user.full_name else "PH").upper()
user_name = user.full_name or "Phan Van Quan"
project_name = st.query_params.get("project", "Shonen Weekly #112")
file_safe_project = project_name.replace(" ", "_").replace("#", "")

# Dynamic project context mapping to ensure 100% data consistency with Workspace (Task 2)
project_lower = project_name.lower()
if "one piece" in project_lower:
    batch_code = "#CH-1115-RAW"
    total_pages = 19
    processed_pages = 14
    progress_pct = 68
    chapter_desc = "Chapter 1115 • Japanese -> Vietnamese"
    est_time = "~1m 45s"
    task_count_all = 19
    task_count_comp = 10
    task_count_inprog = 4
    task_count_queued = 5
elif "jujutsu" in project_lower:
    batch_code = "#CH-SP-RAW"
    total_pages = 32
    processed_pages = 32
    progress_pct = 100
    chapter_desc = "Special Chapter • English -> Vietnamese"
    est_time = "Completed"
    task_count_all = 32
    task_count_comp = 32
    task_count_inprog = 0
    task_count_queued = 0
else:
    # Default: Shonen Weekly #112 (Matches Card 1 in Workspace: 18/24 Pages Reviewed - 75%)
    batch_code = "#CH-112-RAW"
    total_pages = 24
    processed_pages = 18
    progress_pct = 75
    chapter_desc = "Issue #112 • Japanese -> Vietnamese"
    est_time = "~2m 10s"
    task_count_all = 24
    task_count_comp = 12
    task_count_inprog = 4
    task_count_queued = 8

queue_monitor_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<meta content="web_dashboard" name="shell-type"/>
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
<!-- Comprehensive Google Fonts import with explicit Vietnamese & Latin-Ext subsets to prevent font breakage during browser translation -->
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,600&family=Sora:wght@600;700;800&subset=vietnamese,latin,latin-ext&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet"/>

<style>
@layer base {{
  html, body {{
    margin: 0;
    padding: 0;
    background: #fff8f3;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif;
    color: #1d1b18;
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
  }}
  body {{ overscroll-behavior: none; }}
  main > :first-child {{ margin-top: 0 !important; }}
  main > :last-child {{ margin-bottom: 0 !important; }}
}}

/* Google Translate DOM Injection Compatibility Fixes:
   Ensure all translated elements inherit full font family, line-height, and baseline alignment */
font {{
  font-family: inherit !important;
  font-size: inherit !important;
  line-height: inherit !important;
  color: inherit !important;
  letter-spacing: inherit !important;
  vertical-align: baseline !important;
  display: inline !important;
}}

/* Hide native scrollbar while retaining scroll capability */
::-webkit-scrollbar {{ display: none; }}

.material-symbols-outlined {{
  font-family: 'Material Symbols Outlined';
  font-weight: normal;
  font-style: normal;
  font-size: 20px;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
}}

@keyframes moveBg {{
  0% {{ background-position: 0 0; }}
  100% {{ background-position: 2rem 0; }}
}}
.progress-animated {{
  background-image: linear-gradient(45deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent);
  background-size: 1rem 1rem;
  animation: moveBg 2s linear infinite;
}}
</style>

<script src="https://cdn.tailwindcss.com"></script>
<script id="tailwind-config">
tailwind.config = {{
  darkMode: "class",
  theme: {{
    extend: {{
      colors: {{
        "secondary": "#536435",
        "outline-variant": "#c6c5d1",
        "on-secondary-fixed": "#131f00",
        "tertiary-fixed": "#e6deff",
        "on-secondary": "#ffffff",
        "surface-variant": "#e7e1dc",
        "primary-fixed": "#dee1ff",
        "tertiary-fixed-dim": "#cabffc",
        "on-error-container": "#93000a",
        "outline": "#767681",
        "surface-container-high": "#ede7e2",
        "primary-fixed-dim": "#b9c3ff",
        "on-surface": "#1d1b18",
        "error-container": "#ffdad6",
        "on-primary-fixed": "#041453",
        "error": "#ba1a1a",
        "surface-dim": "#dfd9d4",
        "on-background": "#1d1b18",
        "secondary-fixed": "#d6eaaf",
        "secondary-fixed-dim": "#bace95",
        "inverse-on-surface": "#f6f0ea",
        "on-surface-variant": "#454650",
        "inverse-surface": "#32302d",
        "surface": "#fff8f3",
        "on-tertiary-container": "#a399d4",
        "on-primary-container": "#909ce0",
        "surface-tint": "#4e5a99",
        "surface-container": "#f3ede7",
        "background": "#fff8f3",
        "secondary-container": "#d3e7ac",
        "on-tertiary-fixed": "#1c1245",
        "primary": "#0c1b59",
        "on-secondary-fixed-variant": "#3c4c20",
        "surface-container-low": "#f9f2ed",
        "on-tertiary-fixed-variant": "#484073",
        "on-secondary-container": "#576839",
        "tertiary": "#231a4c",
        "tertiary-container": "#383063",
        "on-error": "#ffffff",
        "inverse-primary": "#b9c3ff",
        "surface-container-highest": "#e7e1dc",
        "on-primary": "#ffffff",
        "surface-container-lowest": "#ffffff",
        "primary-container": "#25326f",
        "on-primary-fixed-variant": "#354280",
        "on-tertiary": "#ffffff",
        "surface-bright": "#fff8f3"
      }},
      borderRadius: {{
        "DEFAULT": "0.25rem",
        "lg": "0.5rem",
        "xl": "0.75rem",
        "full": "9999px"
      }},
      spacing: {{
        "space-xs": "0.25rem",
        "space-sm": "0.5rem",
        "space-md": "1rem",
        "space-lg": "1.5rem",
        "space-xl": "2rem",
        "gutter": "1rem",
        "gutter-lg": "1.5rem",
        "margin": "1rem",
        "margin-md": "1.5rem",
        "margin-lg": "2rem"
      }},
      fontFamily: {{
        sans: ["Plus Jakarta Sans", "sans-serif"],
        headline: ["Sora", "sans-serif"],
        code: ["JetBrains Mono", "monospace"],
        "display-lg": ["Sora", "sans-serif"],
        "headline-lg": ["Sora", "sans-serif"],
        "headline-md": ["Sora", "sans-serif"],
        "headline-sm": ["Sora", "sans-serif"],
        "title-md": ["Plus Jakarta Sans", "sans-serif"],
        "body-lg": ["Plus Jakarta Sans", "sans-serif"],
        "body-md": ["Plus Jakarta Sans", "sans-serif"],
        "body-sm": ["Plus Jakarta Sans", "sans-serif"],
        "label-md": ["Plus Jakarta Sans", "sans-serif"],
        "code-md": ["JetBrains Mono", "monospace"],
        "code-sm": ["JetBrains Mono", "monospace"]
      }},
      fontSize: {{
        "display-lg": ["40px", {{ "lineHeight": "48px", "letterSpacing": "-0.02em", "fontWeight": "700" }}],
        "headline-lg": ["32px", {{ "lineHeight": "40px", "letterSpacing": "-0.015em", "fontWeight": "600" }}],
        "headline-md": ["24px", {{ "lineHeight": "32px", "letterSpacing": "-0.01em", "fontWeight": "600" }}],
        "headline-sm": ["18px", {{ "lineHeight": "26px", "fontWeight": "600" }}],
        "title-md": ["16px", {{ "lineHeight": "24px", "fontWeight": "600" }}],
        "body-lg": ["16px", {{ "lineHeight": "24px", "fontWeight": "400" }}],
        "body-md": ["14px", {{ "lineHeight": "20px", "fontWeight": "400" }}],
        "body-sm": ["12px", {{ "lineHeight": "18px", "fontWeight": "400" }}],
        "label-md": ["13px", {{ "lineHeight": "18px", "fontWeight": "500" }}],
        "code-md": ["13px", {{ "lineHeight": "18px", "fontWeight": "500" }}],
        "code-sm": ["11px", {{ "lineHeight": "16px", "fontWeight": "400" }}]
      }}
    }}
  }}
}};
</script>
</head>

<body class="bg-surface font-body-md text-on-surface antialiased">

<!-- FIXED LEFT SIDEBAR -->
<aside class="fixed left-0 top-0 h-full w-[220px] bg-surface-container-lowest z-50 flex flex-col justify-between py-5 border-r border-[#E4DFD6]">
  <div>
    <!-- Brand / Logo Area: Square Badge with 'A' (Mục 1 - Đồng bộ 100% Task 2) -->
    <div class="px-5 mb-6 flex items-center gap-3">
      <div class="w-9 h-9 rounded-xl bg-primary-container text-on-primary flex items-center justify-center font-bold text-lg shadow-sm shrink-0">
        A
      </div>
      <div class="min-w-0">
        <h1 class="font-headline text-[17px] font-bold text-on-surface tracking-tight leading-none">ACL</h1>
        <p class="font-code text-[11px] text-on-surface-variant mt-1 leading-snug truncate">v2.4 Editorial Core</p>
      </div>
    </div>
    
    <!-- Navigation Links (Đồng bộ 100% Task 2) -->
    <nav class="px-3 flex flex-col gap-1">
      <a class="flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all cursor-pointer" onclick="navigateParent('workspace')">
        <span class="material-symbols-outlined text-[20px]">grid_view</span>
        <span>Dashboard</span>
      </a>
      <a class="flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all cursor-pointer" onclick="navigateParent('workspace')">
        <span class="material-symbols-outlined text-[20px]">folder</span>
        <span>Projects</span>
      </a>
      <a class="flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all cursor-pointer" onclick="navigateParent('team-roles?project=' + encodeURIComponent('{project_name}'))">
        <span class="material-symbols-outlined text-[20px]">groups</span>
        <span>Team Roles</span>
      </a>
      <a class="flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all cursor-pointer" onclick="navigateParent('chapter-studio?project=' + encodeURIComponent('{project_name}'))">
        <span class="material-symbols-outlined text-[20px]">cloud_upload</span>
        <span>Chapter Studio</span>
      </a>
      <a class="flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all cursor-pointer" onclick="navigateParent('review-studio?project=' + encodeURIComponent('{project_name}'))">
        <span class="material-symbols-outlined text-[20px]">vertical_split</span>
        <span>Review Studio</span>
      </a>
      <a class="flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all cursor-pointer" onclick="navigateParent('typesetting')">
        <span class="material-symbols-outlined text-[20px]">edit_note</span>
        <span>Typesetting</span>
      </a>
      <a aria-current="page" class="flex items-center gap-3 px-3 py-2 transition-all bg-primary-container text-on-primary text-xs font-semibold rounded-xl cursor-pointer shadow-sm" onclick="navigateParent('queue-monitor?project=' + encodeURIComponent('{project_name}'))">
        <span class="material-symbols-outlined text-[20px]">schedule</span>
        <span>Queue Monitor</span>
      </a>
      <a class="flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all cursor-pointer" onclick="navigateParent('settings')">
        <span class="material-symbols-outlined text-[20px]">settings</span>
        <span>Personal Settings</span>
      </a>
    </nav>
  </div>

  <!-- Sidebar Footer: Documentation & Core Online (Đồng bộ 100% Task 2) -->
  <div class="px-5 pt-3 border-t border-[#E4DFD6] flex flex-col gap-2.5">
    <a class="flex items-center gap-2 text-on-surface-variant hover:text-on-surface text-xs font-medium cursor-pointer transition-colors" onclick="openDocsModal()">
      <span class="material-symbols-outlined text-[18px]">help_outline</span>
      <span>Documentation</span>
    </a>
    <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#E8F5E9] text-[#2E7D32] border border-[#C8E6C9] font-code text-xs font-semibold w-fit">
      <span class="w-2 h-2 rounded-full bg-[#2E7D32] animate-pulse"></span>
      <span>Core • Online</span>
    </div>
  </div>
</aside>

<!-- MAIN APP SHELL -->
<div class="pl-[220px]">

  <!-- TOP HEADER BAR (SaaS Pro with Notification & Profile Dropdown) -->
  <header class="fixed top-0 left-[220px] right-0 h-16 bg-surface-container-lowest/95 backdrop-blur-md z-40 px-8 flex items-center justify-between border-b border-[#E4DFD6]">
    
    <!-- Left: ACL Studio / Projects / {project_name} / Queue Monitor Breadcrumb -->
    <div class="flex items-center gap-2">
      <a class="text-base font-bold text-on-surface hover:text-primary-container transition-colors cursor-pointer" onclick="navigateParent('workspace')">ACL Studio</a>
      <span class="text-outline-variant font-light text-sm">/</span>
      <a class="text-sm text-on-surface-variant font-medium hover:text-on-surface transition-colors cursor-pointer" onclick="navigateParent('workspace')">Projects</a>
      <span class="text-outline-variant font-light text-sm">/</span>
      <a class="text-sm text-on-surface-variant font-medium hover:text-primary-container transition-colors cursor-pointer notranslate" translate="no" onclick="navigateParent('chapter-studio?project=' + encodeURIComponent('{project_name}'))" title="Open Chapter Studio for {project_name}">{project_name}</a>
      <span class="text-outline-variant font-light text-sm">/</span>
      <span id="breadcrumb-tail" class="inline-flex items-center gap-2">
        <span class="text-sm text-primary-container font-semibold">Queue Monitor</span>
      </span>
    </div>

    <!-- Center/Right Header Controls (Đồng bộ 100% Task 2) -->
    <div class="flex items-center gap-4">
      
      <!-- Search Input (Filter tasks or pages... - Đồng bộ Task 2 & Hoạt động 100%) -->
      <div class="hidden md:flex items-center bg-surface-container-low rounded-full px-3.5 py-1.5 border border-[#E4DFD6] relative">
        <span class="material-symbols-outlined text-[18px] text-on-surface-variant mr-1.5">search</span>
        <input id="header-search-input" oninput="searchTaskRows(this.value)" class="bg-transparent text-xs outline-none placeholder:text-on-surface-variant w-44 text-on-surface pr-4" placeholder="Search tasks (e.g. 13, OCR)..." type="text"/>
        <button id="search-clear-btn" onclick="clearSearch()" class="hidden absolute right-2 text-on-surface-variant hover:text-on-surface cursor-pointer p-0.5 rounded-full hover:bg-surface-container" title="Clear search">
          <span class="material-symbols-outlined text-[14px]">close</span>
        </button>
      </div>

      <!-- Node Tokyo-01 (GPU idle) Pill Badge (Click mở GPU Hardware Modal) -->
      <a onclick="openGpuModal()" class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#E8EDF4] hover:bg-[#D8E2EE] text-[#414754] hover:text-[#191C19] border border-[#D0D7DE] font-code text-xs font-medium cursor-pointer transition-colors" title="Click to view Node Tokyo-01 GPU hardware status">
        <span class="material-symbols-outlined text-[15px] text-[#57606A]">memory</span>
        <span>Node Tokyo-01 (GPU idle)</span>
      </a>

      <!-- INTERACTIVE NOTIFICATION BELL WITH RED DOT (Đặc biệt) -->
      <div class="relative">
        <button id="notif-btn" onclick="toggleNotifDropdown(event)" class="relative p-1.5 rounded-full hover:bg-surface-container text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer" title="Notifications">
          <span class="material-symbols-outlined text-[22px]">notifications</span>
          <!-- Active Red Notification Badge -->
          <span id="notif-badge" class="absolute top-1 right-1 w-2.5 h-2.5 bg-[#DC2626] rounded-full ring-2 ring-white animate-pulse"></span>
        </button>

        <!-- Notification Popover Dropdown -->
        <div id="notif-dropdown" class="hidden absolute right-0 mt-2 w-80 bg-surface-container-lowest rounded-2xl shadow-xl border border-[#E4DFD6] py-3 z-50 text-left transition-all">
          <div class="flex items-center justify-between px-4 pb-2 border-b border-[#E4DFD6]/70">
            <div class="flex items-center gap-2">
              <span class="text-sm font-bold text-on-surface">Notifications</span>
              <span id="notif-count" class="px-2 py-0.5 rounded-full bg-[#FEE2E2] text-[#DC2626] font-code text-[11px] font-semibold">3 New</span>
            </div>
            <button onclick="markAllNotifsRead()" class="text-[11px] font-semibold text-primary-container hover:underline cursor-pointer">
              Mark all read
            </button>
          </div>
          <div class="divide-y divide-[#E4DFD6]/40 max-h-72 overflow-y-auto">
            <div class="p-3 hover:bg-surface-container-low transition-colors cursor-pointer" onclick="navigateParent('review-studio?project=' + encodeURIComponent('{project_name}'))">
              <div class="flex items-start gap-2.5">
                <span class="notif-dot w-2 h-2 rounded-full bg-[#DC2626] mt-1.5 shrink-0"></span>
                <div>
                  <p class="text-xs font-semibold text-on-surface">Batch Processing: Page 013 Ready</p>
                  <p class="text-[11px] text-on-surface-variant mt-0.5">OCR extraction completed. Awaiting review.</p>
                  <span class="font-code text-[10px] text-outline mt-1 block">Just now</span>
                </div>
              </div>
            </div>
            <div class="p-3 hover:bg-surface-container-low transition-colors cursor-pointer" onclick="navigateParent('queue-monitor?project=' + encodeURIComponent('{project_name}'))">
              <div class="flex items-start gap-2.5">
                <span class="notif-dot w-2 h-2 rounded-full bg-[#DC2626] mt-1.5 shrink-0"></span>
                <div>
                  <p class="text-xs font-semibold text-on-surface">Worker Pool Active</p>
                  <p class="text-[11px] text-on-surface-variant mt-0.5">4 Python background workers running smoothly.</p>
                  <span class="font-code text-[10px] text-outline mt-1 block">5 mins ago</span>
                </div>
              </div>
            </div>
            <div class="p-3 hover:bg-surface-container-low transition-colors cursor-pointer" onclick="navigateParent('team-roles?project=' + encodeURIComponent('{project_name}'))">
              <div class="flex items-start gap-2.5">
                <span class="notif-dot w-2 h-2 rounded-full bg-[#DC2626] mt-1.5 shrink-0"></span>
                <div>
                  <p class="text-xs font-semibold text-on-surface">RBAC Permissions Active</p>
                  <p class="text-[11px] text-on-surface-variant mt-0.5">Assigned editorial team operating on this project.</p>
                  <span class="font-code text-[10px] text-outline mt-1 block">1 hour ago</span>
                </div>
              </div>
            </div>
          </div>
          <div class="pt-2 px-4 border-t border-[#E4DFD6]/70 text-center">
            <a class="text-xs font-semibold text-primary-container hover:underline cursor-pointer" onclick="switchView('completed')">
              Jump to Chapter Export (ZIP) →
            </a>
          </div>
        </div>
      </div>

      <!-- Filter / Slider Icon (Đồng bộ Task 2) -->
      <button onclick="document.getElementById('header-search-input')?.focus();" class="p-1.5 rounded-full hover:bg-surface-container text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer" title="Focus search filter">
        <span class="material-symbols-outlined text-[20px]">tune</span>
      </button>

      <!-- User Profile Menu (Avatar + Chevron Dropdown matching Demo) -->
      <div class="relative pl-2 border-l border-[#E4DFD6]">
        <button id="profile-btn" onclick="toggleProfileDropdown(event)" class="flex items-center gap-1.5 p-1 rounded-full hover:bg-surface-container transition-colors cursor-pointer group" title="Account Menu">
          <div class="w-8 h-8 rounded-full bg-primary-container flex items-center justify-center font-bold text-xs text-on-primary shadow-sm notranslate" translate="no" title="{user_name}">
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
              <div class="text-sm font-bold text-on-surface truncate notranslate" translate="no">{user_name}</div>
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
            <a class="flex items-center gap-2.5 px-4 py-2 text-xs font-medium text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low transition-colors cursor-pointer" onclick="navigateParent('team-roles?project=' + encodeURIComponent('{project_name}'))">
              <span class="material-symbols-outlined text-[18px]">groups</span>
              <span>Team Workspace</span>
            </a>
            <a class="flex items-center gap-2.5 px-4 py-2 text-xs font-medium text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low transition-colors cursor-pointer" onclick="navigateParent('workspace')">
              <span class="material-symbols-outlined text-[18px]">grid_view</span>
              <span>All Projects</span>
            </a>
          </div>
          <div class="pt-1 border-t border-[#E4DFD6]/70">
            <button onclick="navigateParent('login?logout=1')" class="w-full flex items-center gap-2.5 px-4 py-2 text-xs font-semibold text-[#DC2626] hover:bg-[#FEE2E2]/50 transition-colors cursor-pointer" title="Sign out of ACL">
              <span class="material-symbols-outlined text-[18px]">logout</span>
              <span>Sign out</span>
            </button>
          </div>
        </div>
      </div>

    </div>
  </header>

  <!-- MAIN VIEWPORT CONTENT -->
  <main class="relative pt-16 bg-surface min-h-screen">
    <!-- Floating Toast Notification -->
    <div id="toastNotification" class="fixed top-20 right-8 z-50 flex items-center gap-3 px-4 py-3 bg-surface-container-lowest rounded-xl shadow-lg border border-[#E4DFD6] transition-all duration-300 transform translate-y-[-20px] opacity-0 pointer-events-none">
      <div class="w-7 h-7 rounded-full bg-secondary-container text-secondary flex items-center justify-center shrink-0">
        <span class="material-symbols-outlined text-[18px]">check_circle</span>
      </div>
      <div class="flex flex-col">
        <span class="font-title-md text-xs font-bold text-on-surface" id="toastMessage">Action completed</span>
        <span class="font-code text-[11px] text-on-surface-variant">Queue Monitor Status Synchronized</span>
      </div>
    </div>

    <div class="flex flex-col w-full p-gutter-lg space-y-space-lg max-w-7xl mx-auto">

      <!-- View State Tabs: In-Progress Monitor vs Complete Chapter ZIP Export -->
      <div class="flex items-center justify-between gap-4 border-b border-[#E4DFD6] pb-3">
        <div class="flex items-center gap-2">
          <button onclick="switchView('active')" id="tab-active" class="px-4 py-2 rounded-full font-title-md text-label-md font-semibold bg-primary-container text-on-primary transition-all cursor-pointer">
            Live Pipeline Queue (Active)
          </button>
          <button onclick="switchView('completed')" id="tab-completed" class="px-4 py-2 rounded-full font-title-md text-label-md font-semibold bg-surface-container text-on-surface-variant hover:text-on-surface transition-all cursor-pointer">
            Completed Chapter &amp; ZIP Export
          </button>
        </div>

        <div class="flex items-center gap-2">
          <button onclick="simulateJobProgress()" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface-container text-primary font-label-md text-label-md font-semibold hover:bg-surface-container-high transition-colors cursor-pointer border border-[#E4DFD6]">
            <span class="material-symbols-outlined text-[16px]">play_circle</span>
            <span>Simulate Step</span>
          </button>
        </div>
      </div>

      <!-- SECTION 1: ACTIVE PIPELINE QUEUE VIEW -->
      <div id="view-active" class="space-y-space-lg">
        <!-- 1. TOP HEADER ROW -->
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-space-md">
          <div class="flex flex-col gap-space-xs">
            <div class="flex flex-wrap items-center gap-space-sm">
              <h1 class="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">Queue Monitor</h1>
              <div class="flex items-center gap-1.5 bg-primary-fixed text-primary px-space-sm py-0.5 rounded-full">
                <span class="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></span>
                <span id="worker-pool-badge" class="font-code-sm text-code-sm font-semibold tracking-normal notranslate" translate="no">Worker Pool: 4 Active Workers • FIFO Priority Engine</span>
              </div>
            </div>
            <p class="font-body-md text-body-md text-outline">Real-time task tracking for Python Asynchronous Queue pipeline.</p>
          </div>
          <!-- Action Controls -->
          <div class="flex items-center gap-space-sm flex-wrap">
            <button id="auto-refresh-btn" onclick="toggleAutoRefresh()" class="relative inline-flex items-center bg-surface-container-lowest border border-outline-variant/60 rounded-full px-space-md py-1.5 text-on-surface shadow-sm cursor-pointer hover:bg-surface-container-low transition-all active:scale-95" type="button" title="Click to pause or resume auto-refresh">
              <span id="auto-refresh-dot" class="w-2 h-2 rounded-full bg-secondary mr-2 inline-block animate-ping"></span>
              <span id="auto-refresh-label" class="font-label-md text-label-md">Auto-refresh: <strong>5s</strong></span>
            </button>
            <button id="pause-queue-btn" onclick="togglePauseQueue()" class="inline-flex items-center gap-1.5 px-space-md py-1.5 rounded-full border border-outline-variant/60 bg-surface-container-lowest text-on-surface hover:bg-surface-container-low transition-colors shadow-sm font-label-md text-label-md cursor-pointer" type="button">
              <span id="pause-icon" class="material-symbols-outlined text-[16px] text-on-surface-variant">pause</span>
              <span id="pause-label">Pause Queue</span>
            </button>
            <button id="run-pipeline-btn" onclick="runPipelineManual()" class="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full bg-primary-container text-on-primary hover:bg-primary transition-all shadow-sm font-label-md text-label-md cursor-pointer active:scale-95" type="button">
              <span class="material-symbols-outlined text-[16px]">play_arrow</span>
              <span>Run Pipeline</span>
            </button>
          </div>
        </div>

        <!-- 2. CHAPTER OVERALL PROGRESS CARD -->
        <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 p-space-lg shadow-sm">
          <!-- Row 1: Header & Metrics (Dynamic Context Synchronized with Task 2) -->
          <div class="flex flex-col sm:flex-row sm:items-baseline justify-between gap-space-xs mb-space-sm">
            <div class="flex items-center gap-space-sm flex-wrap">
              <h2 class="font-headline-sm text-headline-sm text-on-surface font-semibold">Active Chapter: <span class="notranslate" translate="no">{project_name}</span></h2>
              <span class="font-code-sm text-code-sm bg-surface-container-high text-on-surface-variant px-space-xs py-0.5 rounded notranslate" translate="no">{batch_code}</span>
            </div>
            <div class="text-left sm:text-right">
              <div class="font-headline-sm text-headline-sm text-primary-container font-bold" id="progress-percentage-label">{processed_pages} / {total_pages} Pages Processed ({progress_pct}%)</div>
              <div class="font-body-sm text-body-sm text-outline">Estimated completion: {est_time}</div>
            </div>
          </div>
          <!-- Row 2: Large Progress Bar -->
          <div class="w-full h-3 bg-surface-container-highest rounded-full overflow-hidden mb-space-lg relative">
            <div class="h-full bg-primary-container rounded-full relative progress-animated" id="progress-bar-fill" style="width: {progress_pct}%;"></div>
          </div>
          <!-- Row 3: 7-Stage Pipeline Visual Stepper (Navigates to Studio / Stages) -->
          <div class="grid grid-cols-2 md:grid-cols-7 gap-space-xs pt-space-xs">
            <div onclick="scrollToQueuedTasks()" class="flex flex-col items-center text-center p-space-xs rounded-lg hover:bg-surface-container-low transition-all cursor-pointer group hover:scale-105 active:scale-95" title="Click to scroll to Ingestion Queue table">
              <div class="w-8 h-8 rounded-full bg-secondary-container text-secondary flex items-center justify-center mb-1.5 shadow-sm group-hover:bg-secondary group-hover:text-on-secondary transition-colors">
                <span class="material-symbols-outlined text-[16px] font-bold">check</span>
              </div>
              <span class="font-label-md text-label-md text-on-surface font-semibold group-hover:text-primary-container">1. Queued</span>
              <span class="font-code-sm text-code-sm text-secondary font-medium">8 in FIFO ↓</span>
            </div>
            <div onclick="navigateParent('chapter-studio?project=' + encodeURIComponent('{project_name}'))" class="flex flex-col items-center text-center p-space-xs rounded-lg hover:bg-surface-container-low transition-all cursor-pointer group hover:scale-105 active:scale-95" title="Click to navigate to Chapter Studio (YOLOv8 Detection)">
              <div class="w-8 h-8 rounded-full bg-secondary-container text-secondary flex items-center justify-center mb-1.5 shadow-sm group-hover:bg-secondary group-hover:text-on-secondary transition-colors">
                <span class="material-symbols-outlined text-[16px] font-bold">check</span>
              </div>
              <span class="font-label-md text-label-md text-on-surface font-semibold group-hover:text-primary-container">2. Detection</span>
              <span class="font-code-sm text-code-sm text-secondary font-medium notranslate" translate="no">YOLOv8 →</span>
            </div>
            <div onclick="navigateParent('review-studio?project=' + encodeURIComponent('{project_name}'))" class="flex flex-col items-center text-center p-space-xs rounded-lg hover:bg-surface-container-low transition-all cursor-pointer group hover:scale-105 active:scale-95" title="Click to navigate to Review Studio (Manga-OCR Extraction)">
              <div class="w-8 h-8 rounded-full bg-secondary-container text-secondary flex items-center justify-center mb-1.5 shadow-sm group-hover:bg-secondary group-hover:text-on-secondary transition-colors">
                <span class="material-symbols-outlined text-[16px] font-bold">check</span>
              </div>
              <span class="font-label-md text-label-md text-on-surface font-semibold group-hover:text-primary-container">3. OCR</span>
              <span class="font-code-sm text-code-sm text-secondary font-medium notranslate" translate="no">Manga OCR →</span>
            </div>
            <div onclick="navigateParent('review-studio?project=' + encodeURIComponent('{project_name}') + '&page=013')" class="flex flex-col items-center text-center p-space-xs rounded-lg bg-primary-fixed/30 hover:bg-primary-fixed/60 transition-all cursor-pointer group border border-primary-container/20 hover:scale-105 active:scale-95" title="Click to open Review Studio for Page 013">
              <div class="relative w-8 h-8 rounded-full bg-primary-container text-on-primary flex items-center justify-center mb-1.5 shadow-sm group-hover:shadow-md">
                <span class="material-symbols-outlined text-[16px]">edit_note</span>
                <span class="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-error border-2 border-surface-container-lowest animate-pulse"></span>
              </div>
              <span class="font-label-md text-label-md text-primary-container font-bold">4. Review</span>
              <span class="font-code-sm text-code-sm px-1.5 py-0.5 rounded-full bg-primary-container text-on-primary font-semibold">1 Active →</span>
            </div>
            <div onclick="navigateParent('review-studio?project=' + encodeURIComponent('{project_name}'))" class="flex flex-col items-center text-center p-space-xs rounded-lg hover:bg-surface-container-low transition-all cursor-pointer group hover:scale-105 active:scale-95" title="Click to inspect Inpainting in Review Studio">
              <div class="w-8 h-8 rounded-full bg-surface-container-high text-on-surface-variant flex items-center justify-center mb-1.5 shadow-sm animate-pulse group-hover:bg-secondary-container group-hover:text-secondary transition-colors">
                <span class="material-symbols-outlined text-[16px] text-tertiary">brush</span>
              </div>
              <span class="font-label-md text-label-md text-on-surface font-semibold group-hover:text-primary-container">5. Inpainting</span>
              <span class="font-code-sm text-code-sm text-on-surface-variant notranslate" translate="no">LaMa GAN →</span>
            </div>
            <div onclick="navigateParent('typesetting?project=' + encodeURIComponent('{project_name}'))" class="flex flex-col items-center text-center p-space-xs rounded-lg hover:bg-surface-container-low transition-all cursor-pointer group hover:scale-105 active:scale-95" title="Click to open Typesetting Studio">
              <div class="w-8 h-8 rounded-full bg-surface-container text-outline flex items-center justify-center mb-1.5 group-hover:bg-primary-fixed group-hover:text-primary transition-colors">
                <span class="material-symbols-outlined text-[16px]">text_fields</span>
              </div>
              <span class="font-label-md text-label-md text-on-surface font-semibold group-hover:text-primary-container">6. Typesetting</span>
              <span class="font-code-sm text-code-sm text-outline">CC Wild Words →</span>
            </div>
            <div onclick="switchView('completed')" class="flex flex-col items-center text-center p-space-xs rounded-lg hover:bg-surface-container-low transition-all cursor-pointer group hover:scale-105 active:scale-95" title="Click to jump to Completed Chapter & ZIP Export">
              <div class="w-8 h-8 rounded-full bg-secondary-container/50 text-secondary flex items-center justify-center mb-1.5 group-hover:bg-secondary group-hover:text-on-secondary transition-colors">
                <span class="material-symbols-outlined text-[16px]">archive</span>
              </div>
              <span class="font-label-md text-label-md text-on-surface font-semibold group-hover:text-primary-container">7. Completed</span>
              <span class="font-code-sm text-code-sm text-secondary font-medium">ZIP Export →</span>
            </div>
          </div>
        </div>

        <!-- 3. HARDWARE & CLUSTER HEALTH MINI-METRICS ROW (Pixel-Perfect Matching Demo) -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-space-md">
          <!-- Metric 1: Worker Node & VRAM (Click to focus live stream) -->
          <div onclick="openGpuModal()" class="bg-surface-container-lowest rounded-2xl border border-outline-variant/50 p-space-md shadow-sm flex flex-col justify-between hover:shadow-md hover:border-primary-container/40 transition-all cursor-pointer group" title="Click to jump to Live Worker Stream Terminal">
            <div class="flex items-center justify-between mb-space-xs">
              <span class="font-code text-xs uppercase tracking-wider text-outline font-semibold">WORKER NODE</span>
              <span class="material-symbols-outlined text-[20px] text-primary-container">dns</span>
            </div>
            <div>
              <div class="font-headline text-lg text-on-surface font-bold notranslate" translate="no">Node Tokyo-01 (Active)</div>
              <div class="font-code text-xs text-on-surface-variant mt-0.5 notranslate" translate="no">VRAM: 15.4 GB / 24.0 GB • CUDA 12.2</div>
            </div>
            <div class="mt-space-sm pt-space-xs border-t border-surface-container-high flex items-center justify-between">
              <div class="w-full bg-surface-container-highest h-1.5 rounded-full mr-space-sm overflow-hidden">
                <div class="bg-primary-container h-full rounded-full" style="width: 64%;"></div>
              </div>
              <span class="font-code text-[11px] bg-secondary-container text-secondary px-space-xs py-0.5 rounded-full whitespace-nowrap font-medium notranslate" translate="no">64% Load • Normal 58°C</span>
            </div>
          </div>

          <!-- Metric 2: Average Latency & Throughput -->
          <div class="bg-surface-container-lowest rounded-2xl border border-outline-variant/50 p-space-md shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
            <div class="flex items-center justify-between mb-space-xs">
              <span class="font-code text-xs uppercase tracking-wider text-outline font-semibold">THROUGHPUT</span>
              <span class="material-symbols-outlined text-[20px] text-primary-container">speed</span>
            </div>
            <div>
              <div class="font-headline text-lg text-on-surface font-bold">14.2s / page avg</div>
              <div class="font-code text-xs text-on-surface-variant mt-0.5">Est. Remaining: ~1m 54s</div>
            </div>
            <div class="mt-space-sm pt-space-xs border-t border-surface-container-high flex items-center justify-between">
              <span class="font-code text-[11px] text-secondary font-medium flex items-center gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-secondary inline-block"></span>
                <span>Manga OCR + LaMa Engine</span>
              </span>
              <span class="font-code text-[11px] text-outline notranslate" translate="no">Optimal</span>
            </div>
          </div>

          <!-- Metric 3: Review Queue (Click to open Review Studio) -->
          <div onclick="navigateParent('review-studio?project=' + encodeURIComponent('{project_name}') + '&page=013')" class="bg-surface-container-lowest rounded-2xl border border-outline-variant/50 p-space-md shadow-sm flex flex-col justify-between hover:shadow-md hover:border-primary-container/40 transition-all cursor-pointer group" title="Click anywhere on card to open Review Studio for Page 013">
            <div class="flex items-center justify-between mb-space-xs">
              <span class="font-code text-xs uppercase tracking-wider text-outline font-semibold">REVIEW QUEUE</span>
              <span class="material-symbols-outlined text-[20px] text-amber-600">flag</span>
            </div>
            <div>
              <div class="font-headline text-lg text-on-surface font-bold flex items-center gap-2">
                <span>1 Page Awaiting Review</span>
                <span class="w-2 h-2 rounded-full bg-error animate-pulse"></span>
              </div>
              <div class="font-code text-xs text-on-surface-variant mt-0.5 notranslate" translate="no">Page 013 flagged for verification</div>
            </div>
            <div class="mt-space-sm pt-space-xs border-t border-surface-container-high flex items-center justify-between">
              <span class="font-code text-[11px] text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full font-semibold border border-amber-200">
                Human-in-the-Loop OCR
              </span>
              <a class="font-code text-[11px] text-primary-container font-bold hover:underline cursor-pointer" onclick="navigateParent('review-studio?project=' + encodeURIComponent('{project_name}'))">Review Now →</a>
            </div>
          </div>
        </div>

        <!-- 4. DETAILED PAGE TASKS TABLE -->
        <div id="detailed-tasks-table" class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 overflow-hidden shadow-sm">
          <div class="p-space-md border-b border-outline-variant/50 flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm bg-surface-container-lowest">
            <div class="flex items-center gap-space-xs overflow-x-auto pb-1 sm:pb-0">
              <button id="task-filter-all" onclick="filterTaskRows('all')" class="px-space-sm py-1 rounded-lg text-primary-container bg-primary-fixed/40 font-title-md text-title-md text-xs font-bold whitespace-nowrap cursor-pointer transition-all" type="button">All Tasks ({task_count_all})</button>
              <button id="task-filter-completed" onclick="filterTaskRows('completed')" class="px-space-sm py-1 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container font-label-md text-label-md whitespace-nowrap transition-colors cursor-pointer" type="button">Completed ({task_count_comp})</button>
              <button id="task-filter-inprogress" onclick="filterTaskRows('inprogress')" class="px-space-sm py-1 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container font-label-md text-label-md whitespace-nowrap transition-colors cursor-pointer" type="button">In Progress ({task_count_inprog})</button>
              <button id="task-filter-queued" onclick="filterTaskRows('queued')" class="px-space-sm py-1 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container font-label-md text-label-md whitespace-nowrap transition-colors cursor-pointer" type="button">Queued ({task_count_queued})</button>
            </div>
            <div class="hidden sm:flex items-center gap-2 text-xs text-on-surface-variant font-medium">
              <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-surface-container-low border border-outline-variant/50">
                <span class="w-1.5 h-1.5 rounded-full bg-[#137333] animate-pulse"></span>
                <span class="font-code text-[11px] text-on-surface">Live Pipeline Active</span>
              </span>
              <button type="button" onclick="focusHeaderSearch()" class="inline-flex items-center gap-1 text-[11px] text-outline hover:text-primary-container transition-colors cursor-pointer" title="Focus master search in Header">
                <span class="material-symbols-outlined text-[14px]">search</span>
                <span>Filter in Header</span>
              </button>
            </div>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-surface-container-low text-on-surface font-title-md text-xs uppercase tracking-wider border-b border-outline-variant/50">
                  <th class="py-3 px-space-md font-bold w-[16%]">Page</th>
                  <th class="py-3 px-space-md font-bold w-[22%]">Filename</th>
                  <th class="py-3 px-space-md font-bold w-[24%]">Current Stage</th>
                  <th class="py-3 px-space-md font-bold w-[22%]">Status Badge</th>
                  <th class="py-3 px-space-md font-bold w-[16%] text-right">Updated</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-outline-variant/40 font-body-sm text-body-sm">
                <tr data-status="completed" class="task-row hover:bg-surface-container-low/60 transition-colors">
                  <td class="py-3.5 px-space-md font-title-md font-semibold text-on-surface">Page 001–012 (Batch A)</td>
                  <td class="py-3.5 px-space-md font-code-sm text-code-sm text-on-surface-variant notranslate" translate="no">page_001.png → page_012.png</td>
                  <td class="py-3.5 px-space-md text-on-surface font-medium">Typesetting Complete</td>
                  <td class="py-3.5 px-space-md">
                    <span class="inline-flex items-center gap-1 bg-secondary-container text-secondary px-space-sm py-0.5 rounded-full font-code-sm text-code-sm font-semibold">
                      <span class="material-symbols-outlined text-[13px]">check_circle</span>
                      <span>Completed</span>
                    </span>
                  </td>
                  <td class="py-3.5 px-space-md text-right font-code-sm text-code-sm text-outline notranslate" translate="no">12:05:30 (4m ago)</td>
                </tr>
                <tr data-status="inprogress" class="task-row hover:bg-surface-container-low/60 transition-colors bg-primary-fixed/10">
                  <td class="py-3.5 px-space-md font-title-md font-semibold text-primary-container flex items-center gap-2">
                    <span class="w-6 h-6 rounded-full border border-primary-container text-primary-container font-code text-xs font-bold inline-flex items-center justify-center">13</span>
                    <span>Page 013</span>
                  </td>
                  <td class="py-3.5 px-space-md font-code text-xs text-on-surface-variant notranslate" translate="no">page_013.png (2.4 MB)</td>
                  <td class="py-3.5 px-space-md text-on-surface font-medium">Human-in-the-Loop OCR</td>
                  <td class="py-3.5 px-space-md">
                    <div class="flex items-center gap-2">
                      <span class="inline-flex items-center gap-1 bg-primary-fixed text-primary px-space-sm py-0.5 rounded-full font-code text-xs font-semibold">
                        <span class="material-symbols-outlined text-[13px]">rate_review</span>
                        <span>Waiting Review</span>
                      </span>
                      <a class="font-code text-xs text-primary-container font-bold hover:underline cursor-pointer" onclick="navigateParent('review-studio?project=' + encodeURIComponent('{project_name}'))">Review Now →</a>
                    </div>
                  </td>
                  <td class="py-3.5 px-space-md text-right font-code text-xs text-primary font-medium notranslate" translate="no">Just now</td>
                </tr>
                <tr data-status="inprogress" class="task-row hover:bg-surface-container-low/60 transition-colors">
                  <td class="py-3.5 px-space-md font-title-md font-semibold text-on-surface flex items-center gap-2">
                    <span class="w-6 h-6 rounded-full border border-[#C4C7C5] text-[#5A5E62] font-code text-xs font-medium inline-flex items-center justify-center">14</span>
                    <span>Page 014</span>
                  </td>
                  <td class="py-3.5 px-space-md font-code text-xs text-on-surface-variant notranslate" translate="no">page_014.png (2.2 MB)</td>
                  <td class="py-3.5 px-space-md text-on-surface font-medium">LaMa Background Inpainting</td>
                  <td class="py-3.5 px-space-md">
                    <div class="flex items-center gap-2">
                      <span class="inline-flex items-center gap-1.5 bg-[#FFF3E0] text-[#E65100] px-space-sm py-0.5 rounded-full font-code text-xs font-semibold border border-[#FFE0B2]">
                        <span class="material-symbols-outlined text-[13px] animate-spin">sync</span>
                        <span>Inpainting</span>
                      </span>
                      <span class="font-code text-[11px] text-outline">Processing (18s)</span>
                    </div>
                  </td>
                  <td class="py-3.5 px-space-md text-right font-code text-xs text-outline notranslate" translate="no">12:08:52</td>
                </tr>
                <tr data-status="inprogress" class="task-row hover:bg-surface-container-low/60 transition-colors">
                  <td class="py-3.5 px-space-md font-title-md font-semibold text-on-surface flex items-center gap-2">
                    <span class="w-6 h-6 rounded-full border border-[#C4C7C5] text-[#5A5E62] font-code text-xs font-medium inline-flex items-center justify-center">15</span>
                    <span>Page 015</span>
                  </td>
                  <td class="py-3.5 px-space-md font-code text-xs text-on-surface-variant notranslate" translate="no">page_015.png (2.8 MB)</td>
                  <td class="py-3.5 px-space-md text-on-surface font-medium">Manga OCR Recognition</td>
                  <td class="py-3.5 px-space-md">
                    <div class="flex items-center gap-2">
                      <span class="inline-flex items-center gap-1.5 bg-[#FFF3E0] text-[#E65100] px-space-sm py-0.5 rounded-full font-code text-xs font-semibold border border-[#FFE0B2]">
                        <span class="material-symbols-outlined text-[13px] animate-spin">sync</span>
                        <span>OCR Extraction</span>
                      </span>
                      <span class="font-code text-[11px] text-outline">Processing (6s)</span>
                    </div>
                  </td>
                  <td class="py-3.5 px-space-md text-right font-code text-xs text-outline notranslate" translate="no">12:09:01</td>
                </tr>
                <tr data-status="inprogress" class="task-row hover:bg-surface-container-low/60 transition-colors">
                  <td class="py-3.5 px-space-md font-title-md font-semibold text-on-surface flex items-center gap-2">
                    <span class="w-6 h-6 rounded-full border border-[#C4C7C5] text-[#5A5E62] font-code text-xs font-medium inline-flex items-center justify-center">16</span>
                    <span>Page 016</span>
                  </td>
                  <td class="py-3.5 px-space-md font-code text-xs text-on-surface-variant notranslate" translate="no">page_016.png (2.1 MB)</td>
                  <td class="py-3.5 px-space-md text-on-surface font-medium">YOLOv8 Speech Bubble Detection</td>
                  <td class="py-3.5 px-space-md">
                    <div class="flex items-center gap-2">
                      <span class="inline-flex items-center gap-1.5 bg-[#FEF3C7] text-[#92400E] px-space-sm py-0.5 rounded-full font-code text-xs font-semibold border border-[#FDE68A]">
                        <span class="material-symbols-outlined text-[13px] animate-spin">autorenew</span>
                        <span>YOLO Detection</span>
                      </span>
                      <span class="font-code text-[11px] text-outline">Starting</span>
                    </div>
                  </td>
                  <td class="py-3.5 px-space-md text-right font-code text-xs text-outline notranslate" translate="no">12:09:10</td>
                </tr>
                <tr data-status="queued" class="task-row hover:bg-surface-container-low/60 transition-colors">
                  <td class="py-3.5 px-space-md font-title-md font-medium text-on-surface-variant">Page 017–024 (8 Pages)</td>
                  <td class="py-3.5 px-space-md font-code-sm text-code-sm text-on-surface-variant notranslate" translate="no">page_017.png → page_024.png</td>
                  <td class="py-3.5 px-space-md text-outline font-normal">FIFO Pipeline Ingestion Queue</td>
                  <td class="py-3.5 px-space-md">
                    <div class="flex items-center gap-1.5">
                      <span class="inline-flex items-center gap-1 bg-surface-container text-on-surface-variant px-space-sm py-0.5 rounded-full font-code-sm text-code-sm">
                        <span class="material-symbols-outlined text-[13px]">hourglass_empty</span>
                        <span>Queued in FIFO</span>
                      </span>
                      <span class="font-body-sm text-body-sm text-outline text-[11px]">Waiting worker</span>
                    </div>
                  </td>
                  <td class="py-3.5 px-space-md text-right font-code-sm text-code-sm text-outline notranslate" translate="no">12:04:00 (Staged)</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 5. FOOTER WORKER STATUS BAR -->
        <div class="flex flex-col sm:flex-row items-center justify-between gap-space-xs text-on-surface-variant py-space-xs px-1">
          <div class="flex items-center gap-space-xs font-code text-xs">
            <span class="w-2 h-2 rounded-full bg-secondary"></span>
            <span>Displaying 6 queue pipeline execution units (24 manga pages total) • Queue ID: <strong class="text-on-surface notranslate" translate="no">q_async_tokyo01_8849b</strong></span>
          </div>
          <a class="font-code text-xs text-primary-container hover:underline flex items-center gap-1 cursor-pointer" onclick="downloadPipelineLog()">
            <span class="material-symbols-outlined text-[14px]">download</span>
            <span>Download JSON / Full Pipeline Log (.LOG)</span>
          </a>
        </div>

        <!-- 6. LIVE WORKER STREAM CONSOLE (DARK TERMINAL - EXACT MATCH TO DEMO) -->
        <div id="worker-stream-terminal" class="rounded-2xl overflow-hidden shadow-lg border border-[#2d3139] bg-[#14161b] text-[#c9d1d9] font-code text-xs mt-4">
          <!-- Terminal Header Bar -->
          <div class="flex items-center justify-between px-5 py-2.5 bg-[#1b1e25] border-b border-[#2d3139]">
            <div class="flex items-center gap-2.5">
              <span class="w-2.5 h-2.5 rounded-full bg-[#3fb950] animate-pulse"></span>
              <span class="font-bold text-white font-code text-xs tracking-wide notranslate" translate="no">Live Worker Stream: worker-tokyo-01-daemon.py</span>
            </div>
            <div class="flex items-center gap-3">
              <span class="inline-flex items-center gap-1.5 text-[11px] text-[#3fb950] font-medium notranslate" translate="no">
                <span class="w-1.5 h-1.5 rounded-full bg-[#3fb950] animate-ping"></span>
                <span>Streaming stdout</span>
              </span>
              <button onclick="copyTerminalLogs()" class="px-2 py-0.5 rounded text-[11px] text-gray-400 hover:text-white hover:bg-white/10 transition-colors cursor-pointer flex items-center gap-1" title="Copy stdout logs">
                <span class="material-symbols-outlined text-[13px]">content_copy</span>
                <span>Copy</span>
              </button>
              <button onclick="clearTerminalLogs()" class="px-2 py-0.5 rounded text-[11px] text-gray-400 hover:text-white hover:bg-white/10 transition-colors cursor-pointer" title="Clear log output">Clear</button>
            </div>
          </div>
          <!-- Terminal Log Body -->
          <div id="terminal-log-body" class="p-4 space-y-1.5 max-h-48 overflow-y-auto font-code text-[11px] leading-relaxed select-text">
            <div class="text-[#8b949e]"><span class="text-[#58a6ff]">[12:05:32.001]</span> <span class="text-[#3fb950] font-bold">INFO</span> [Worker-04] Batch #104 Initialized with 24 assets. GPU allocated: 0 (Device RTX 4090).</div>
            <div class="text-[#8b949e]"><span class="text-[#58a6ff]">[12:05:38.550]</span> <span class="text-[#3fb950] font-bold">INFO</span> [Inpainting] Page 012 LaMa mask inpainting resolved in 1.44s. Output validated (PSNR 38.8dB).</div>
            <div class="text-[#8b949e]"><span class="text-[#58a6ff]">[12:05:30.952]</span> <span class="text-[#3fb950] font-bold">INFO</span> [OCR] Page 013 Manga OCR completed text inference for 32 bounding boxes (Confidence: 0.984).</div>
            <div class="text-[#e3b341]"><span class="text-[#58a6ff]">[12:05:32.405]</span> <span class="text-[#d29922] font-bold">WARN</span> [Inspector] Page 013 flagged for human editorial validation: vertical multi-column punctuation edge case detected in Bubble #4.</div>
            <div class="text-[#8b949e]"><span class="text-[#58a6ff]">[12:05:33.018]</span> <span class="text-[#bc8cff] font-bold">ASYNC</span> [Worker-04] Forking process LaMa-v2.0-fp16 on page_014.png (Bounding mask resolution: 1800x2560).</div>
          </div>
        </div>
      </div>

      <!-- SECTION 2: COMPLETED CHAPTER & ZIP EXPORT VIEW -->
      <div id="view-completed" class="hidden space-y-space-lg">
        <!-- Top Bar / Page Header -->
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-space-md">
          <div>
            <div class="flex items-center gap-space-xs mb-1">
              <span class="font-code-sm text-code-sm text-secondary font-semibold uppercase tracking-wider">Pipeline Execution Complete</span>
              <span class="w-1.5 h-1.5 rounded-full bg-secondary"></span>
              <span class="font-code-sm text-code-sm text-on-surface-variant notranslate" translate="no">Batch ID: {batch_code}</span>
            </div>
            <h1 class="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">Chapter Release Pack</h1>
            <p class="font-body-md text-body-md text-on-surface-variant mt-0.5">All chapter pipeline tasks completed successfully with zero validation errors.</p>
          </div>
          <div class="flex items-center gap-space-sm flex-wrap">
            <div onclick="scrollToCompletedArtifacts()" class="inline-flex items-center gap-1.5 bg-secondary-container/40 hover:bg-secondary-container/70 text-on-secondary-container px-3 py-1.5 rounded-full shadow-sm cursor-pointer transition-all active:scale-95" title="Click to inspect all {total_pages} completed pages">
              <span class="material-symbols-outlined text-[18px] text-secondary">check_circle</span>
              <span class="font-code-sm text-code-sm font-semibold tracking-wide">All {total_pages}/{total_pages} Pages Complete</span>
            </div>
          </div>
        </div>

        <!-- Full-Width Success Announcement Banner -->
        <div class="relative overflow-hidden rounded-2xl bg-secondary-container/30 p-space-lg md:p-8 shadow-sm border border-secondary/20">
          <div class="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div class="flex items-start gap-5">
              <div class="flex-shrink-0 w-14 h-14 rounded-2xl bg-secondary-container flex items-center justify-center text-secondary shadow-sm">
                <span class="material-symbols-outlined text-[36px]">verified</span>
              </div>
              <div class="space-y-1">
                <div class="flex items-center gap-2 flex-wrap">
                  <h2 class="font-headline-md text-headline-md text-on-surface font-bold tracking-tight">Chapter Localization 100% Complete!</h2>
                  <span class="bg-secondary text-on-secondary font-code-sm text-code-sm px-2.5 py-0.5 rounded-full uppercase font-medium">Ready for Release</span>
                </div>
                <p class="font-body-md text-body-md text-on-surface-variant max-w-2xl">
                  All 24 manga spreads have been accurately masked, OCR-scanned, AI-translated, infilled with LaMa GAN, and lettered with strict typographical kerning metrics.
                </p>
                <div class="flex items-center gap-3 pt-1 text-on-surface-variant font-code-sm text-code-sm">
                  <span class="inline-flex items-center gap-1 font-medium text-secondary notranslate" translate="no">
                    <span class="material-symbols-outlined text-[14px]">auto_stories</span>
                    <span class="notranslate" translate="no">{project_name}</span>
                  </span>
                  <span>•</span>
                  <span class="notranslate" translate="no">Job #JOB-9823-C</span>
                  <span>•</span>
                  <span class="inline-flex items-center gap-1 text-secondary">
                    <span class="material-symbols-outlined text-[14px]">bolt</span>
                    <span>Zero OCR Retries</span>
                  </span>
                </div>
              </div>
            </div>

            <!-- Download Button -->
            <div class="flex flex-col items-center lg:items-end flex-shrink-0 pt-2 lg:pt-0">
              <button onclick="downloadZipArchive()" class="group w-full sm:w-auto inline-flex items-center justify-center gap-3 bg-primary-container text-on-primary hover:bg-primary transition-all duration-200 px-8 py-3.5 rounded-full shadow-md hover:shadow-lg active:scale-95 font-title-md text-title-md cursor-pointer" type="button">
                <span class="material-symbols-outlined text-[22px] group-hover:-translate-y-0.5 transition-transform">folder_zip</span>
                <span>Download Chapter (ZIP)</span>
                <span class="bg-primary px-2 py-0.5 rounded-full font-code-sm text-code-sm text-on-primary-fixed notranslate" translate="no">142.8 MB</span>
              </button>
              <div class="flex items-center gap-3 mt-2.5">
                <a class="font-label-md text-label-md text-primary-container hover:text-primary underline underline-offset-2 transition-colors cursor-pointer" onclick="downloadIndividualPngs()">Individual Pages (.PNG)</a>
                <span class="text-outline-variant">•</span>
                <a class="font-label-md text-label-md text-primary-container hover:text-primary underline underline-offset-2 transition-colors cursor-pointer" onclick="downloadIdmlPackage()">InDesign (.IDML) Package</a>
              </div>
              <div class="flex items-center gap-3 mt-3 pt-2.5 border-t border-secondary/20 flex-wrap">
                <button onclick="switchView('active')" class="font-label-md text-label-md font-bold text-primary-container hover:text-primary inline-flex items-center gap-1.5 cursor-pointer bg-white px-3.5 py-1.5 rounded-full border border-primary-container/30 shadow-sm transition-all hover:scale-105 active:scale-95" type="button" title="Return to Live Pipeline Queue table">
                  <span class="material-symbols-outlined text-[16px]">arrow_back</span>
                  <span>Back to Live Queue</span>
                </button>
                <span class="text-outline-variant">•</span>
                <a class="font-label-md text-label-md font-semibold text-on-surface-variant hover:text-on-surface inline-flex items-center gap-1 cursor-pointer" onclick="navigateParent('workspace')">
                  <span class="material-symbols-outlined text-[16px]">grid_view</span>
                  <span>All Projects</span>
                </a>
                <span class="text-outline-variant">•</span>
                <a class="font-label-md text-label-md font-semibold text-on-surface-variant hover:text-on-surface inline-flex items-center gap-1 cursor-pointer" onclick="navigateParent('chapter-studio?project=' + encodeURIComponent('{project_name}'))">
                  <span class="material-symbols-outlined text-[16px]">cloud_upload</span>
                  <span>Chapter Studio</span>
                </a>
              </div>
            </div>
          </div>
        </div>

        <!-- Final Summary Metrics Row -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-gutter-lg">
          <div class="bg-surface-container-lowest rounded-2xl p-space-md shadow-sm border border-[#E4DFD6] flex flex-col justify-between hover:shadow-md transition-shadow">
            <div class="flex items-start justify-between">
              <div>
                <span class="font-code text-xs uppercase tracking-wider font-semibold text-on-surface-variant">Total Pages Localized</span>
                <div class="font-headline-lg text-headline-lg text-on-surface mt-1 font-bold">24 <span class="font-body-md text-body-md font-normal text-on-surface-variant">Pages</span></div>
              </div>
              <div class="w-10 h-10 rounded-full bg-secondary-container/50 text-secondary flex items-center justify-center">
                <span class="material-symbols-outlined text-[22px]">auto_stories</span>
              </div>
            </div>
            <div class="mt-4 pt-3 border-t border-[#E4DFD6] flex items-center gap-1.5 font-body-sm text-body-sm text-secondary font-medium">
              <span class="material-symbols-outlined text-[16px]">check_circle</span>
              <span>100% of staged batch completed without errors</span>
            </div>
          </div>

          <div class="bg-surface-container-lowest rounded-2xl p-space-md shadow-sm border border-[#E4DFD6] flex flex-col justify-between hover:shadow-md transition-shadow">
            <div class="flex items-start justify-between">
              <div>
                <span class="font-code text-xs uppercase tracking-wider font-semibold text-on-surface-variant">Average Processing Time</span>
                <div class="font-headline-lg text-headline-lg text-on-surface mt-1 font-bold">14.2 <span class="font-body-md text-body-md font-normal text-on-surface-variant">sec / page</span></div>
              </div>
              <div class="w-10 h-10 rounded-full bg-primary-fixed text-primary flex items-center justify-center">
                <span class="material-symbols-outlined text-[22px]">speed</span>
              </div>
            </div>
            <div class="mt-4 pt-3 border-t border-[#E4DFD6] flex items-center gap-1.5 font-body-sm text-body-sm text-secondary font-medium">
              <span class="material-symbols-outlined text-[16px]">bolt</span>
              <span>Total elapsed time: 5m 41s</span>
            </div>
          </div>

          <div class="bg-surface-container-lowest rounded-2xl p-space-md shadow-sm border border-[#E4DFD6] flex flex-col justify-between hover:shadow-md transition-shadow">
            <div class="flex items-start justify-between">
              <div>
                <span class="font-code text-xs uppercase tracking-wider font-semibold text-on-surface-variant">Translation &amp; Inpaint Quality</span>
                <div class="font-headline-lg text-headline-lg text-on-surface mt-1 font-bold">99.8% <span class="font-body-md text-body-md font-normal text-on-surface-variant">Accuracy</span></div>
              </div>
              <div class="w-10 h-10 rounded-full bg-secondary-container/50 text-secondary flex items-center justify-center">
                <span class="material-symbols-outlined text-[22px]">verified_user</span>
              </div>
            </div>
            <div class="mt-4 pt-3 border-t border-[#E4DFD6] flex items-center gap-1.5 font-body-sm text-body-sm text-secondary font-medium">
              <span class="material-symbols-outlined text-[16px]">task_alt</span>
              <span>Human verification signoff recorded</span>
            </div>
          </div>
        </div>

        <!-- Completed Chapter Artifacts Table (Matching Demo Image 3) -->
        <div id="completed-artifacts-section" class="bg-surface-container-lowest rounded-2xl border border-outline-variant/50 overflow-hidden shadow-sm mt-6">
          <div class="p-space-md border-b border-outline-variant/50 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <h3 class="font-headline text-base font-bold text-on-surface">Completed Chapter Artifacts</h3>
              <span class="font-code text-xs px-2.5 py-0.5 rounded-full bg-secondary-container text-secondary font-semibold">{total_pages} / {total_pages} Rendered</span>
            </div>
            <button onclick="downloadJsonManifest()" class="font-code text-xs text-primary-container hover:underline flex items-center gap-1 cursor-pointer">
              <span class="material-symbols-outlined text-[15px]">code</span>
              <span>Download JSON Manifest</span>
            </button>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-surface-container-low text-on-surface font-title-md text-xs uppercase tracking-wider border-b border-outline-variant/50">
                  <th class="py-3 px-space-md font-bold w-[16%]">Page</th>
                  <th class="py-3 px-space-md font-bold w-[25%]">Filename</th>
                  <th class="py-3 px-space-md font-bold w-[22%]">Final Stage</th>
                  <th class="py-3 px-space-md font-bold w-[18%]">Status Badge</th>
                  <th class="py-3 px-space-md font-bold w-[19%] text-right">Action &amp; Preview</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-outline-variant/40 font-body-sm text-body-sm">
                <tr class="hover:bg-surface-container-low/60 transition-colors">
                  <td class="py-3.5 px-space-md font-semibold text-on-surface">Page 001–012</td>
                  <td class="py-3.5 px-space-md font-code text-xs text-on-surface-variant notranslate" translate="no">page_001.png → page_012.png (42.1 MB)</td>
                  <td class="py-3.5 px-space-md text-on-surface font-medium flex items-center gap-1.5">
                    <span class="material-symbols-outlined text-[16px] text-secondary">verified</span>
                    <span>Typesetting Done</span>
                  </td>
                  <td class="py-3.5 px-space-md">
                    <span class="inline-flex items-center gap-1 bg-secondary-container text-secondary px-space-sm py-0.5 rounded-full font-code text-xs font-semibold">
                      <span class="material-symbols-outlined text-[13px]">check_circle</span>
                      <span>Completed</span>
                    </span>
                  </td>
                  <td class="py-3.5 px-space-md text-right">
                    <button onclick="openPagePreview('Batch A (Pages 1-12)', 'page_001.png → page_012.png', 'Typesetting Complete', '12 Spreads Verified')" class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-surface-container hover:bg-surface-container-high transition-colors cursor-pointer border border-[#E4DFD6]">
                      <span class="material-symbols-outlined text-[14px]">visibility</span>
                      <span>Preview Page</span>
                    </button>
                  </td>
                </tr>
                <tr class="hover:bg-surface-container-low/60 transition-colors">
                  <td class="py-3.5 px-space-md font-semibold text-on-surface flex items-center gap-2">
                    <span class="w-6 h-6 rounded-full border border-primary-container text-primary-container font-code text-xs font-bold inline-flex items-center justify-center">13</span>
                    <span>Page 013</span>
                  </td>
                  <td class="py-3.5 px-space-md font-code text-xs text-on-surface-variant notranslate" translate="no">page_013.png (300 DPI • 2.4 MB)</td>
                  <td class="py-3.5 px-space-md text-on-surface font-medium flex items-center gap-1.5">
                    <span class="material-symbols-outlined text-[16px] text-secondary">verified</span>
                    <span>Typesetting Done</span>
                  </td>
                  <td class="py-3.5 px-space-md">
                    <span class="inline-flex items-center gap-1 bg-secondary-container text-secondary px-space-sm py-0.5 rounded-full font-code text-xs font-semibold">
                      <span class="material-symbols-outlined text-[13px]">check_circle</span>
                      <span>Completed</span>
                    </span>
                  </td>
                  <td class="py-3.5 px-space-md text-right">
                    <button onclick="openPagePreview('Page 013 (Flagged Spread)', 'page_013.png (2.4 MB)', 'Waiting Editorial Review', 'Awaiting Sign-off')" class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-surface-container hover:bg-surface-container-high transition-colors cursor-pointer border border-[#E4DFD6]">
                      <span class="material-symbols-outlined text-[14px]">visibility</span>
                      <span>Preview Page</span>
                    </button>
                  </td>
                </tr>
                <tr class="hover:bg-surface-container-low/60 transition-colors">
                  <td class="py-3.5 px-space-md font-semibold text-on-surface flex items-center gap-2">
                    <span class="w-6 h-6 rounded-full border border-[#C4C7C5] text-[#5A5E62] font-code text-xs font-medium inline-flex items-center justify-center">14</span>
                    <span>Page 014</span>
                  </td>
                  <td class="py-3.5 px-space-md font-code text-xs text-on-surface-variant notranslate" translate="no">page_014.png (300 DPI • 2.2 MB)</td>
                  <td class="py-3.5 px-space-md text-on-surface font-medium flex items-center gap-1.5">
                    <span class="material-symbols-outlined text-[16px] text-secondary">verified</span>
                    <span>Typesetting Done</span>
                  </td>
                  <td class="py-3.5 px-space-md">
                    <span class="inline-flex items-center gap-1 bg-secondary-container text-secondary px-space-sm py-0.5 rounded-full font-code text-xs font-semibold">
                      <span class="material-symbols-outlined text-[13px]">check_circle</span>
                      <span>Completed</span>
                    </span>
                  </td>
                  <td class="py-3.5 px-space-md text-right">
                    <button onclick="openPagePreview('Page 014 (LaMa GAN Inpainting)', 'page_014.png (2.2 MB)', 'LaMa Inpainting In-Progress', 'Mask Resolution 1800x2560')" class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-surface-container hover:bg-surface-container-high transition-colors cursor-pointer border border-[#E4DFD6]">
                      <span class="material-symbols-outlined text-[14px]">visibility</span>
                      <span>Preview Page</span>
                    </button>
                  </td>
                </tr>
                <tr class="hover:bg-surface-container-low/60 transition-colors">
                  <td class="py-3.5 px-space-md font-semibold text-on-surface">Page 015–024</td>
                  <td class="py-3.5 px-space-md font-code text-xs text-on-surface-variant notranslate" translate="no">page_015.png → page_024.png (37.9 MB)</td>
                  <td class="py-3.5 px-space-md text-on-surface font-medium flex items-center gap-1.5">
                    <span class="material-symbols-outlined text-[16px] text-secondary">verified</span>
                    <span>Typesetting Done</span>
                  </td>
                  <td class="py-3.5 px-space-md">
                    <span class="inline-flex items-center gap-1 bg-secondary-container text-secondary px-space-sm py-0.5 rounded-full font-code text-xs font-semibold">
                      <span class="material-symbols-outlined text-[13px]">check_circle</span>
                      <span>Completed</span>
                    </span>
                  </td>
                  <td class="py-3.5 px-space-md text-right">
                    <button onclick="openPagePreview('Batch B (Pages 15-24)', 'page_015.png → page_024.png', 'Manga OCR & YOLO Detection', 'Queued / Processing')" class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-surface-container hover:bg-surface-container-high transition-colors cursor-pointer border border-[#E4DFD6]">
                      <span class="material-symbols-outlined text-[14px]">visibility</span>
                      <span>Preview Page</span>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Terminal Execution Summary (Dark Box in Completed View - Image 3) -->
        <div class="rounded-2xl overflow-hidden shadow-lg border border-[#2d3139] bg-[#14161b] text-[#c9d1d9] font-code text-xs mt-6">
          <div class="flex items-center justify-between px-5 py-2.5 bg-[#1b1e25] border-b border-[#2d3139]">
            <div class="flex items-center gap-2.5">
              <span class="w-2.5 h-2.5 rounded-full bg-[#3fb950]"></span>
              <span class="font-bold text-white font-code text-xs tracking-wide notranslate" translate="no">Terminal Execution Summary — worker-tokyo-01-daemon.py</span>
            </div>
            <span class="inline-flex items-center gap-1.5 font-code text-[11px] bg-[#238636]/25 text-[#3fb950] border border-[#238636]/40 px-2.5 py-0.5 rounded-full font-semibold notranslate" translate="no"><span class="w-1.5 h-1.5 rounded-full bg-[#3fb950]"></span><span>Process Finished (exit code 0)</span></span>
          </div>
          <div class="p-4 space-y-1.5 font-code text-[11px] leading-relaxed select-text">
            <div class="text-[#8b949e]"><span class="text-[#58a6ff]">[12:14:02.100]</span> <span class="text-[#3fb950] font-bold">INFO</span> All {total_pages} pages localized successfully. Final ZIP package compiled at <span class="text-[#79c0ff]">/exports/{file_safe_project}_full.zip</span></div>
            <div class="text-[#8b949e]"><span class="text-[#58a6ff]">[12:14:03.450]</span> <span class="text-[#3fb950] font-bold">INFO</span> VRAM cleared (23.4 GB released). GPU cluster returned to standby mode.</div>
            <div class="text-[#3fb950] font-bold"><span class="text-[#58a6ff]">[12:14:05.000]</span> SUCCESS Pipeline run completed in 05m 41s with 0 errors. Ready for release.</div>
          </div>
        </div>
      </div>

    </div>
    <!-- PAGE PREVIEW LIGHTBOX MODAL -->
    <div id="preview-modal" style="display: none;" onclick="if (event.target === this) closePagePreview()" class="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 cursor-pointer">
      <div class="bg-surface-container-lowest rounded-2xl shadow-2xl max-w-xl w-full border border-[#E4DFD6] overflow-hidden transform transition-all animate-fadeIn">
        <div class="flex items-center justify-between px-6 py-4 border-b border-[#E4DFD6] bg-surface-container-low">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-primary-container text-on-primary flex items-center justify-center font-bold text-sm">
              <span class="material-symbols-outlined text-[18px]">auto_stories</span>
            </div>
            <div>
              <h3 id="preview-modal-title" class="font-headline text-base font-bold text-on-surface">Page Preview</h3>
              <p id="preview-modal-subtitle" class="font-code text-xs text-on-surface-variant">300 DPI • Print-Ready CMYK Matrix</p>
            </div>
          </div>
          <button onclick="closePagePreview()" class="p-1.5 rounded-full hover:bg-surface-container text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer" title="Close Preview (Esc)">
            <span class="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>
        <div class="p-6 flex flex-col items-center">
          <div class="w-full h-72 rounded-xl bg-[#0f1117] border border-[#2d3139] flex flex-col items-center justify-center p-4 relative overflow-hidden group">
            <div class="absolute inset-0 bg-gradient-to-b from-transparent to-black/70 pointer-events-none"></div>
            <div class="flex flex-col items-center text-center z-10 space-y-2">
              <div class="w-14 h-14 rounded-2xl bg-primary-container/20 border border-primary-container/40 flex items-center justify-center text-primary-container mb-1">
                <span class="material-symbols-outlined text-[32px]">image</span>
              </div>
              <span id="preview-modal-spread-name" class="font-headline text-lg font-bold text-white">page_013.png</span>
              <span id="preview-modal-badge" class="px-3 py-1 rounded-full bg-secondary-container text-secondary font-code text-xs font-semibold">Verified 100% Quality</span>
              <p id="preview-modal-desc" class="font-body-sm text-xs text-gray-300 max-w-sm mt-1">
                PSNR: 39.2 dB • Manga-OCR Confidence: 99.4% • Typography: CC Wild Words
              </p>
            </div>
            <div class="absolute bottom-3 right-3 font-code text-[11px] text-gray-400 bg-black/60 px-2 py-0.5 rounded">
              1800 x 2560 px (300 DPI)
            </div>
          </div>
        </div>
        <div class="px-6 py-3.5 bg-surface-container-low border-t border-[#E4DFD6] flex items-center justify-between">
          <button onclick="closePagePreview()" class="px-4 py-2 rounded-full text-xs font-semibold text-on-surface-variant hover:bg-surface-container transition-colors cursor-pointer">
            Close
          </button>
          <div class="flex items-center gap-2">
            <button onclick="navigateParent('review-studio?project=' + encodeURIComponent('{project_name}') + '&page=013'); closePagePreview();" class="px-4 py-2 rounded-full text-xs font-semibold bg-surface-container hover:bg-surface-container-high text-primary-container transition-colors cursor-pointer border border-[#E4DFD6]">
              Review Studio →
            </button>
            <button onclick="downloadZipArchive(); closePagePreview();" class="px-4 py-2 rounded-full text-xs font-semibold bg-primary-container text-on-primary hover:bg-primary transition-colors cursor-pointer shadow-sm">
              Download Asset (.PNG)
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ACL SYSTEM DOCUMENTATION MODAL -->
    <div id="docs-modal" style="display: none;" onclick="if (event.target === this) closeDocsModal()" class="fixed inset-0 z-50 bg-black/65 backdrop-blur-sm flex items-center justify-center p-4 cursor-pointer">
      <div class="bg-surface-container-lowest rounded-2xl shadow-2xl max-w-lg w-full border border-[#E4DFD6] overflow-hidden transform transition-all animate-fadeIn">
        <div class="flex items-center justify-between px-6 py-4 border-b border-[#E4DFD6] bg-surface-container-low">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-primary-container text-on-primary flex items-center justify-center font-bold text-sm">
              <span class="material-symbols-outlined text-[18px]">help_outline</span>
            </div>
            <div>
              <h3 class="font-headline text-base font-bold text-on-surface">ACL System Documentation</h3>
              <p class="font-code text-[11px] text-on-surface-variant">Version 2.4 Editorial Core • C1SE.80</p>
            </div>
          </div>
          <button onclick="closeDocsModal()" class="p-1.5 rounded-full hover:bg-surface-container text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer">
            <span class="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>
        <div class="p-6 space-y-3.5 font-body-sm text-xs text-on-surface leading-relaxed max-h-96 overflow-y-auto">
          <div class="p-3 bg-surface-container-low rounded-xl border border-[#E4DFD6]">
            <h4 class="font-bold text-on-surface text-sm flex items-center gap-2 mb-1">
              <span class="material-symbols-outlined text-[16px] text-primary-container">route</span>
              <span>7-Stage Pipeline Workflow</span>
            </h4>
            <p class="text-on-surface-variant text-[11px]">
              1. Ingestion → 2. YOLOv8 Bubble Detection → 3. Manga OCR v2.1 Extraction → 4. Human Editorial Review → 5. LaMa GAN Inpainting → 6. Typesetting & Kerning → 7. Print-Ready ZIP Package.
            </p>
          </div>
          <div class="p-3 bg-surface-container-low rounded-xl border border-[#E4DFD6]">
            <h4 class="font-bold text-on-surface text-sm flex items-center gap-2 mb-1">
              <span class="material-symbols-outlined text-[16px] text-secondary">memory</span>
              <span>Worker Node Cluster & Hardware</span>
            </h4>
            <p class="text-on-surface-variant text-[11px]">
              Worker Node Tokyo-01 with NVIDIA CUDA 12.2 (24GB VRAM). Worker daemon handles FIFO queue with automatic task dispatch and PSNR validation threshold of 38.0 dB.
            </p>
          </div>
          <div class="p-3 bg-surface-container-low rounded-xl border border-[#E4DFD6]">
            <h4 class="font-bold text-on-surface text-sm flex items-center gap-2 mb-1">
              <span class="material-symbols-outlined text-[16px] text-amber-600">tune</span>
              <span>Shortcuts & Live Controls</span>
            </h4>
            <p class="text-on-surface-variant text-[11px]">
              • Type in the search box to filter tasks in real-time.<br/>
              • Click any stepper stage (1-7) to filter or jump to the studio.<br/>
              • Click Pause/Resume Queue to freeze worker dispatch without dropping tasks.<br/>
              • Click Copy in Terminal to copy stdout stream logs to clipboard.
            </p>
          </div>
        </div>
        <div class="px-6 py-3 bg-surface-container-low border-t border-[#E4DFD6] flex justify-end">
          <button onclick="closeDocsModal()" class="px-5 py-2 rounded-full text-xs font-semibold bg-primary-container text-on-primary hover:bg-primary transition-colors cursor-pointer shadow-sm">
            Got it
          </button>
        </div>
      </div>
    </div>
    <!-- NODE TOKYO-01 GPU CLUSTER HARDWARE MODAL -->
    <div id="gpu-modal" style="display: none;" onclick="if (event.target === this) closeGpuModal()" class="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 cursor-pointer">
      <div class="bg-surface-container-lowest rounded-2xl shadow-2xl max-w-lg w-full border border-[#E4DFD6] overflow-hidden transform transition-all animate-fadeIn text-left cursor-default" onclick="event.stopPropagation()">
        <!-- Modal Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-[#E4DFD6] bg-surface-container-low">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-primary-container text-on-primary flex items-center justify-center font-bold text-sm shadow-sm">
              <span class="material-symbols-outlined text-[20px]">memory</span>
            </div>
            <div>
              <div class="flex items-center gap-2">
                <h3 class="font-headline text-base font-bold text-on-surface">Node Tokyo-01</h3>
                <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[#E8F5E9] text-[#2E7D32] border border-[#C8E6C9] font-code text-[11px] font-semibold">
                  <span class="w-1.5 h-1.5 rounded-full bg-[#2E7D32] animate-pulse"></span>
                  <span>Active • 58°C</span>
                </span>
              </div>
              <p class="font-code text-[11px] text-on-surface-variant mt-0.5">Primary GPU Cluster Node • Tokyo Datacenter DC-02</p>
            </div>
          </div>
          <button onclick="closeGpuModal()" class="p-1.5 rounded-full hover:bg-surface-container text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer" title="Close (Esc)">
            <span class="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        <!-- Modal Body: Hardware Specs -->
        <div class="p-6 space-y-4">
          <!-- Hardware Card -->
          <div class="p-4 bg-surface-container-low rounded-xl border border-[#E4DFD6] space-y-3">
            <div class="flex items-center justify-between">
              <span class="font-code text-xs uppercase tracking-wider text-outline font-semibold">ACCELERATOR</span>
              <span class="font-code text-xs text-primary-container font-bold">Device #0</span>
            </div>
            <div class="flex items-baseline justify-between">
              <div class="font-headline text-base font-bold text-on-surface">NVIDIA GeForce RTX 4090</div>
              <div class="font-code text-xs font-semibold text-secondary">Ada Lovelace • 16,384 CUDA Cores</div>
            </div>
            <!-- VRAM Progress -->
            <div>
              <div class="flex items-center justify-between font-code text-xs mb-1.5">
                <span class="text-on-surface-variant">VRAM Allocation: <strong>15.4 GB / 24.0 GB</strong></span>
                <span class="text-primary-container font-semibold">64.2% Load</span>
              </div>
              <div class="w-full bg-surface-container-highest h-2 rounded-full overflow-hidden">
                <div class="bg-primary-container h-full rounded-full transition-all duration-500" style="width: 64.2%;"></div>
              </div>
            </div>
          </div>

          <!-- Metrics Grid -->
          <div class="grid grid-cols-2 gap-3 font-code text-xs">
            <div class="p-3 bg-surface-container-low rounded-xl border border-[#E4DFD6]">
              <span class="text-outline text-[11px] block mb-0.5">RUNTIME DRIVER</span>
              <span class="font-bold text-on-surface">CUDA 12.2 / cuDNN 8.9</span>
            </div>
            <div class="p-3 bg-surface-container-low rounded-xl border border-[#E4DFD6]">
              <span class="text-outline text-[11px] block mb-0.5">DAEMON PROCESS</span>
              <span class="font-bold text-secondary flex items-center gap-1">
                <span class="w-2 h-2 rounded-full bg-secondary animate-pulse"></span>
                <span>PID 8421 (Running)</span>
              </span>
            </div>
            <div class="p-3 bg-surface-container-low rounded-xl border border-[#E4DFD6]">
              <span class="text-outline text-[11px] block mb-0.5">CURRENT INFERENCE</span>
              <span class="font-bold text-on-surface">Manga-OCR + LaMa</span>
            </div>
            <div class="p-3 bg-surface-container-low rounded-xl border border-[#E4DFD6]">
              <span class="text-outline text-[11px] block mb-0.5">THERMAL / FAN</span>
              <span class="font-bold text-on-surface">58°C • Fan 42% (Normal)</span>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="px-6 py-3.5 bg-surface-container-low border-t border-[#E4DFD6] flex items-center justify-between">
          <button onclick="closeGpuModal()" class="px-4 py-2 rounded-full text-xs font-semibold text-on-surface-variant hover:bg-surface-container transition-colors cursor-pointer">
            Close
          </button>
          <button onclick="closeGpuModal(); scrollToTerminal();" class="inline-flex items-center gap-1.5 px-4 py-2 rounded-full text-xs font-semibold bg-primary-container text-on-primary hover:bg-primary transition-colors cursor-pointer shadow-sm">
            <span class="material-symbols-outlined text-[16px]">terminal</span>
            <span>View stdout in Terminal →</span>
          </button>
        </div>
      </div>
    </div>
  </main>
</div>

<script>
// Parent navigation bridge for seamless Streamlit router interaction
function navigateParent(path) {{
  const target = '/' + path.replace(/^\//, '');
  try {{
    if (window.parent && window.parent.location) {{
      window.parent.location.href = window.parent.location.origin + target;
      return;
    }}
  }} catch (e) {{
    console.warn("Cross-origin frame navigation fallback triggered:", e);
  }}
  window.location.href = target;
}}

// Interactive Toast Notification
function showToast(message) {{
  const toast = document.getElementById('toastNotification');
  const msgEl = document.getElementById('toastMessage');
  if (!toast || !msgEl) return;
  msgEl.textContent = message;
  toast.classList.remove('opacity-0', 'translate-y-[-20px]', 'pointer-events-none');
  toast.classList.add('opacity-100', 'translate-y-0');
  setTimeout(() => {{
    toast.classList.remove('opacity-100', 'translate-y-0');
    toast.classList.add('opacity-0', 'translate-y-[-20px]', 'pointer-events-none');
  }}, 3200);
}}

// Interactive Notification Dropdown Toggle
function toggleNotifDropdown(e) {{
  e.stopPropagation();
  const profileDropdown = document.getElementById('profile-dropdown');
  if (profileDropdown) profileDropdown.classList.add('hidden');
  const dropdown = document.getElementById('notif-dropdown');
  if (dropdown) dropdown.classList.toggle('hidden');
}}

// Interactive Profile Dropdown Toggle
function toggleProfileDropdown(e) {{
  e.stopPropagation();
  const notifDropdown = document.getElementById('notif-dropdown');
  if (notifDropdown) notifDropdown.classList.add('hidden');
  const dropdown = document.getElementById('profile-dropdown');
  if (dropdown) dropdown.classList.toggle('hidden');
}}

function markAllNotifsRead() {{
  const badge = document.getElementById('notif-badge');
  const count = document.getElementById('notif-count');
  if (badge) badge.classList.add('hidden');
  if (count) {{
    count.innerText = '0 New';
    count.classList.remove('bg-[#FEE2E2]', 'text-[#DC2626]');
    count.classList.add('bg-surface-container', 'text-on-surface-variant');
  }}
  const dots = document.querySelectorAll('.notif-dot');
  dots.forEach(d => d.classList.add('opacity-0'));
  showToast("All notifications marked as read");
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

// Interactive Pause / Resume Queue
let isPaused = false;
function togglePauseQueue() {{
  isPaused = !isPaused;
  const badge = document.getElementById('worker-pool-badge');
  const icon = document.getElementById('pause-icon');
  const label = document.getElementById('pause-label');
  if (isPaused) {{
    if (badge) badge.innerText = 'Worker Pool: Paused • Queue Frozen by Operator';
    if (icon) icon.innerText = 'play_arrow';
    if (label) label.innerText = 'Resume Queue';
    showToast('Queue pipeline paused. Workers idle.');
  }} else {{
    if (badge) badge.innerText = 'Worker Pool: 4 Active Workers • FIFO Priority Engine';
    if (icon) icon.innerText = 'pause';
    if (label) label.innerText = 'Pause Queue';
    showToast('Queue pipeline resumed. Workers processing.');
  }}
}}

// Filter task rows by status (All, Completed, In Progress, Queued)
let currentFilter = 'all';
function filterTaskRows(status) {{
  currentFilter = status;
  const rows = document.querySelectorAll('.task-row');
  rows.forEach(r => {{
    const rStatus = r.getAttribute('data-status');
    if (status === 'all' || rStatus === status) {{
      r.style.display = '';
    }} else {{
      r.style.display = 'none';
    }}
  }});

  // Update button active styles
  const btnAll = document.getElementById('task-filter-all');
  const btnComp = document.getElementById('task-filter-completed');
  const btnInprog = document.getElementById('task-filter-inprogress');
  const btnQueued = document.getElementById('task-filter-queued');

  const btns = [
    {{ el: btnAll, active: status === 'all' }},
    {{ el: btnComp, active: status === 'completed' }},
    {{ el: btnInprog, active: status === 'inprogress' }},
    {{ el: btnQueued, active: status === 'queued' }}
  ];

  btns.forEach(b => {{
    if (!b.el) return;
    if (b.active) {{
      b.el.className = 'px-space-sm py-1 rounded-lg text-primary-container bg-primary-fixed/40 font-title-md text-title-md text-xs font-bold whitespace-nowrap cursor-pointer transition-all';
    }} else {{
      b.el.className = 'px-space-sm py-1 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container font-label-md text-label-md whitespace-nowrap transition-colors cursor-pointer';
    }}
  }});
}}

// Search filter inside task table - Comprehensive Live Filter (Master Header Search)
function searchTaskRows(query) {{
  const rawTerm = (query || '').trim();
  const term = rawTerm.toLowerCase();

  // Sync to master header search input if called programmatically
  const headerSearch = document.getElementById('header-search-input');
  if (headerSearch && headerSearch.value !== query) headerSearch.value = query;
  
  // Toggle clear button
  const clearBtn = document.getElementById('search-clear-btn');
  if (clearBtn) {{
    if (term) clearBtn.classList.remove('hidden');
    else clearBtn.classList.add('hidden');
  }}

  // Auto-switch to active queue view if currently in completed tab so results are immediately visible
  if (term) {{
    const viewActive = document.getElementById('view-active');
    if (viewActive && viewActive.classList.contains('hidden') && typeof switchView === 'function') {{
      switchView('active');
    }}
  }}

  // Smart normalization (e.g., 'page 13' -> matches 'page 013')
  const altTerm = term.replace(/page\s+(\d)\b/i, 'page 00$1').replace(/page\s+(\d{2})\b/i, 'page 0$1');

  const rows = document.querySelectorAll('.task-row');
  let matchCount = 0;

  rows.forEach(r => {{
    const text = r.innerText.toLowerCase();
    // When actively searching, search globally across all tasks regardless of previous tab filter
    const matchesFilter = !term ? (currentFilter === 'all' || r.getAttribute('data-status') === currentFilter) : true;
    const matchesSearch = !term || text.includes(term) || (altTerm && text.includes(altTerm));

    if (matchesFilter && matchesSearch) {{
      r.style.display = '';
      matchCount++;
    }} else {{
      r.style.display = 'none';
    }}
  }});

  // Reset tab filter button styles to 'All' when actively searching
  if (term) {{
    const btnAll = document.getElementById('task-filter-all');
    const btnComp = document.getElementById('task-filter-completed');
    const btnInprog = document.getElementById('task-filter-inprogress');
    const btnQueued = document.getElementById('task-filter-queued');
    if (btnAll) btnAll.className = 'px-space-sm py-1 rounded-lg text-primary-container bg-primary-fixed/40 font-title-md text-title-md text-xs font-bold whitespace-nowrap cursor-pointer transition-all';
    [btnComp, btnInprog, btnQueued].forEach(b => {{
      if (b) b.className = 'px-space-sm py-1 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container font-label-md text-label-md whitespace-nowrap transition-colors cursor-pointer';
    }});
    currentFilter = 'all';
  }}

  // Empty State handling: If 0 results, show helpful feedback
  let emptyRow = document.getElementById('task-search-empty-row');
  const tbody = document.querySelector('tbody.divide-y');
  if (!emptyRow && tbody) {{
    emptyRow = document.createElement('tr');
    emptyRow.id = 'task-search-empty-row';
    emptyRow.className = 'hidden';
    emptyRow.innerHTML = '<td colspan="5" class="py-10 text-center text-on-surface-variant font-body-md bg-surface-container-low/30 rounded-xl"><div class="flex flex-col items-center justify-center gap-2"><span class="material-symbols-outlined text-[32px] text-outline">search_off</span><span class="font-bold text-on-surface text-sm">No tasks found matching your filter</span><span id="no-match-term-desc" class="font-code text-xs text-outline"></span><button onclick="clearSearch()" class="mt-2 inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-surface-container hover:bg-surface-container-high transition-colors text-primary-container border border-[#E4DFD6] cursor-pointer"><span class="material-symbols-outlined text-[14px]">refresh</span><span>Reset Search</span></button></div></td>';
    tbody.appendChild(emptyRow);
  }}

  if (emptyRow) {{
    if (term && matchCount === 0) {{
      emptyRow.classList.remove('hidden');
      const desc = document.getElementById('no-match-term-desc');
      if (desc) desc.innerText = `No results found for "${{rawTerm}}". Try searching 'OCR', 'Page 013', 'Inpainting', or 'Completed'.`;
    }} else {{
      emptyRow.classList.add('hidden');
    }}
  }}
}}

function clearSearch() {{
  const hInp = document.getElementById('header-search-input');
  if (hInp) hInp.value = '';
  searchTaskRows('');
  if (hInp) hInp.focus();
}}

// Interactive Run Pipeline Manual Trigger
function runPipelineManual() {{
  showToast('Dispatched immediate batch execution to Node Tokyo-01');
  appendTerminalLog('INFO', `[Manual-Trigger] Operator initiated forced cycle on ${{encodeURIComponent('{project_name}')}}. Allocating GPU stream.`);
}}

function clearTerminalLogs() {{
  const el = document.getElementById('terminal-log-body');
  if (el) {{
    el.innerHTML = '<div class="text-[#8b949e] italic">// Log buffer cleared by operator</div>';
    showToast('Terminal log buffer cleared');
  }}
}}

function appendTerminalLog(level, msg) {{
  const el = document.getElementById('terminal-log-body');
  if (!el) return;
  const now = new Date();
  const timeStr = now.toTimeString().split(' ')[0] + '.' + String(now.getMilliseconds()).padStart(3, '0');
  const div = document.createElement('div');
  let colorClass = 'text-[#3fb950] font-bold';
  if (level === 'WARN') colorClass = 'text-[#d29922] font-bold';
  if (level === 'ASYNC') colorClass = 'text-[#bc8cff] font-bold';
  div.innerHTML = `<span class="text-[#58a6ff]">[${{timeStr}}]</span> <span class="${{colorClass}}">${{level}}</span> ${{msg}}`;
  el.appendChild(div);
  el.scrollTop = el.scrollHeight;
}}

function downloadJsonManifest() {{
  const manifest = {{
    project: "{project_name}",
    batch_id: "{batch_code.replace('#', '')}",
    total_pages: {total_pages},
    stages_completed: ["Detection", "OCR", "Translation", "Inpainting", "Typesetting"],
    export_format: "Print-Ready 300 DPI PNGs",
    checksum_sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    generated_at: new Date().toISOString()
  }};
  const blob = new Blob([JSON.stringify(manifest, null, 2)], {{ type: 'application/json' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = '{file_safe_project}_manifest.json';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('Downloaded JSON manifest metadata');
}}

// Tab switcher between Active Queue and Completed ZIP export (with dynamic breadcrumb trail)
function switchView(viewName) {{
  const viewActive = document.getElementById('view-active');
  const viewCompleted = document.getElementById('view-completed');
  const tabActive = document.getElementById('tab-active');
  const tabCompleted = document.getElementById('tab-completed');
  const bTail = document.getElementById('breadcrumb-tail');

  if (viewName === 'completed') {{
    viewActive.classList.add('hidden');
    viewCompleted.classList.remove('hidden');
    tabCompleted.classList.add('bg-primary-container', 'text-on-primary');
    tabCompleted.classList.remove('bg-surface-container', 'text-on-surface-variant');
    tabActive.classList.remove('bg-primary-container', 'text-on-primary');
    tabActive.classList.add('bg-surface-container', 'text-on-surface-variant');

    if (bTail) {{
      bTail.innerHTML = '<a class="text-sm text-on-surface-variant font-medium hover:text-primary-container transition-colors cursor-pointer" onclick="switchView(&quot;active&quot;)" title="Return to Active Queue">Queue Monitor</a><span class="text-outline-variant font-light text-sm">/</span><span class="text-sm text-primary-container font-semibold">Completed Chapter</span>';
    }}
  }} else {{
    viewCompleted.classList.add('hidden');
    viewActive.classList.remove('hidden');
    tabActive.classList.add('bg-primary-container', 'text-on-primary');
    tabActive.classList.remove('bg-surface-container', 'text-on-surface-variant');
    tabCompleted.classList.remove('bg-primary-container', 'text-on-primary');
    tabCompleted.classList.add('bg-surface-container', 'text-on-surface-variant');

    if (bTail) {{
      bTail.innerHTML = '<span class="text-sm text-primary-container font-semibold">Queue Monitor</span>';
    }}
  }}
}}

// Focus header search with gentle visual pulse
function focusHeaderSearch() {{
  const inp = document.getElementById('header-search-input');
  if (inp) {{
    inp.focus();
    const parent = inp.closest('.rounded-full');
    if (parent) {{
      parent.classList.add('ring-2', 'ring-primary-container', 'shadow-md');
      setTimeout(() => parent.classList.remove('ring-2', 'ring-primary-container', 'shadow-md'), 1600);
    }}
  }}
}}

// Progress simulation (Dynamic Context Synchronized with Task 2)
let simPercent = {progress_pct};
let totalProjectPages = {total_pages};
function simulateJobProgress() {{
  if (isPaused) {{
    showToast('Queue is currently paused. Click Resume first.');
    return;
  }}
  simPercent = Math.min(100, simPercent + 8);
  const bar = document.getElementById('progress-bar-fill');
  const label = document.getElementById('progress-percentage-label');
  const pages = Math.min(totalProjectPages, Math.round((simPercent / 100) * totalProjectPages));
  if (bar) bar.style.width = simPercent + '%';
  if (label) label.innerText = `${{pages}} / ${{totalProjectPages}} Pages Processed (${{simPercent}}%)`;

  showToast(`Simulated step: ${{pages}}/${{totalProjectPages}} Pages processed (${{simPercent}}%)`);
  appendTerminalLog('INFO', `[Worker-04] Page 0${{pages}} pipeline inference completed. PSNR: 39.1dB • VRAM allocated: 15.4 GB`);

  if (simPercent >= 100) {{
    setTimeout(() => {{
      switchView('completed');
      showToast('Pipeline execution finished! Chapter release ready for ZIP export.');
    }}, 600);
  }}
}}

// Download ZIP action
function downloadZipArchive() {{
  const blob = new Blob(["ACL Production Chapter Export: {project_name}\\nLocalizer: ACL v2.4\\nPages: 24/24\\nLanguage: JA -> VI\\nStatus: Verified Complete"], {{ type: 'application/zip' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = '{file_safe_project}_Vietnamese_Export.zip';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('Downloaded chapter release ZIP package ({file_safe_project})');
}}

// Download log action
function downloadPipelineLog() {{
  const logContent = `[ACL-PIPELINE-LOG] Project: {project_name}
Timestamp: 2026-10-20T14:20:00Z
Job ID: #JOB-9823-C
Batch ID: {batch_code}
Total Pages: {total_pages}
Pipeline Stages:
1. Ingestion: Complete ({total_pages}/{total_pages})
2. YOLOv8 Text Detection: Complete ({total_pages}/{total_pages}) - mAP 0.942
3. Manga OCR v2.1: Complete ({total_pages}/{total_pages}) - Zero retries
4. Human Interactive Review: Signed off by Lead Editor
5. LaMa GAN Inpainting: Complete ({total_pages}/{total_pages})
6. Typography & Typesetting: Complete ({total_pages}/{total_pages}) - CC Wild Words
7. Package Bundle: Success
Exit status: SUCCESS (0 errors)
Worker: Python AsyncIO Worker #acl-worker-8421
`;
  const blob = new Blob([logContent], {{ type: 'text/plain' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'acl_pipeline_{file_safe_project}.log';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('Exported pipeline execution log');
}}

// Interactive Auto-Refresh Toggle
let isAutoRefreshActive = true;
let autoRefreshTimer = null;
function toggleAutoRefresh() {{
  isAutoRefreshActive = !isAutoRefreshActive;
  const dot = document.getElementById('auto-refresh-dot');
  const label = document.getElementById('auto-refresh-label');
  if (isAutoRefreshActive) {{
    if (dot) {{
      dot.className = 'w-2 h-2 rounded-full bg-secondary mr-2 inline-block animate-ping';
    }}
    if (label) {{
      label.innerHTML = 'Auto-refresh: <strong>5s</strong>';
    }}
    showToast('Auto-refresh active (5s interval)');
    startAutoRefreshLoop();
  }} else {{
    if (dot) {{
      dot.className = 'w-2 h-2 rounded-full bg-outline mr-2 inline-block';
    }}
    if (label) {{
      label.innerHTML = 'Auto-refresh: <strong>Paused</strong>';
    }}
    showToast('Auto-refresh paused by operator');
    if (autoRefreshTimer) clearInterval(autoRefreshTimer);
  }}
}}

function startAutoRefreshLoop() {{
  if (autoRefreshTimer) clearInterval(autoRefreshTimer);
  autoRefreshTimer = setInterval(() => {{
    if (isAutoRefreshActive && !isPaused) {{
      // Update updated timestamps slightly
      const timeStamps = document.querySelectorAll('.task-row td:last-child');
      if (timeStamps.length > 0) {{
        // Subtle indicator that pulse happened
        const dot = document.getElementById('auto-refresh-dot');
        if (dot) {{
          dot.classList.add('scale-150');
          setTimeout(() => dot.classList.remove('scale-150'), 300);
        }}
      }}
    }}
  }}, 5000);
}}
startAutoRefreshLoop();






// Toggleable filterTaskRows: click active filter again to return to 'all'

function toggleFilterTaskRows(status) {{

  if (currentFilter === status && status !== 'all') {{

    filterTaskRows('all');

    showToast('Reset filter: Showing all 24 tasks');

  }} else {{

    filterTaskRows(status);

  }}

}}



function scrollToCompletedArtifacts() {{
  const el = document.getElementById('completed-artifacts-section');
  if (el) {{
    el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
  }}
  showToast('Verified: All {total_pages}/{total_pages} pages rendered with zero pipeline errors');
}}

function scrollToQueuedTasks() {{
  const viewCompleted = document.getElementById('view-completed');
  if (viewCompleted && !viewCompleted.classList.contains('hidden')) {{
    switchView('active');
  }}
  filterTaskRows('queued');
  const table = document.getElementById('detailed-tasks-table');
  if (table) {{
    table.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
  }}
  showToast('Viewing 8 Queued tasks waiting in FIFO pipeline');
}}



// Scroll smoothly to Terminal console
function scrollToTerminal() {{
  const viewCompleted = document.getElementById('view-completed');
  if (viewCompleted && !viewCompleted.classList.contains('hidden')) {{
    switchView('active');
  }}
  const el = document.getElementById('worker-stream-terminal');
  if (el) {{
    el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
    el.classList.add('ring-2', 'ring-primary-container');
    setTimeout(() => el.classList.remove('ring-2', 'ring-primary-container'), 2400);
    showToast('Node Tokyo-01: GPU cluster healthy (Active daemon streaming)');
  }}
}}

// Copy terminal logs to clipboard
function copyTerminalLogs() {{
  const el = document.getElementById('terminal-log-body');
  if (el) {{
    const text = el.innerText;
    try {{
      navigator.clipboard.writeText(text);
      showToast('Copied stdout logs to clipboard');
    }} catch (e) {{
      showToast('Terminal stdout buffer ready (selected)');
    }}
  }}
}}


// GPU Hardware Status Modal
function openGpuModal() {{
  const modal = document.getElementById('gpu-modal');
  if (modal) modal.style.display = 'flex';
}}

function closeGpuModal() {{
  const modal = document.getElementById('gpu-modal');
  if (modal) modal.style.display = 'none';
}}







// Page Preview Modal Lightbox
function openPagePreview(title, fileName, stage, status) {{
  const modal = document.getElementById('preview-modal');
  const titleEl = document.getElementById('preview-modal-title');
  const subEl = document.getElementById('preview-modal-subtitle');
  const nameEl = document.getElementById('preview-modal-spread-name');
  const badgeEl = document.getElementById('preview-modal-badge');
  const descEl = document.getElementById('preview-modal-desc');

  if (titleEl) titleEl.innerText = title;
  if (subEl) subEl.innerText = `${{fileName}} • 300 DPI Print Matrix`;
  if (nameEl) nameEl.innerText = fileName;
  if (badgeEl) badgeEl.innerText = status;
  if (descEl) descEl.innerText = `Pipeline Stage: ${{stage}} • OCR Confidence: 99.4% • Font: CC Wild Words`;

  if (modal) modal.style.display = 'flex';
}}

function closePagePreview() {{
  const modal = document.getElementById('preview-modal');
  if (modal) modal.style.display = 'none';
}}

// Documentation Modal
function openDocsModal() {{
  const modal = document.getElementById('docs-modal');
  if (modal) modal.style.display = 'flex';
}}

function closeDocsModal() {{
  const modal = document.getElementById('docs-modal');
  if (modal) modal.style.display = 'none';
}}

// Escape key listener for modals
document.addEventListener('keydown', function(e) {{
  if (e.key === 'Escape') {{
    closePagePreview();
    closeDocsModal();
    closeGpuModal();
  }}
}});

// Alternative package downloads without alert()
function downloadIndividualPngs() {{
  showToast('Packaging 24 individual 300 DPI PNG spreads into ZIP package...');
  setTimeout(() => {{
    downloadZipArchive();
  }}, 800);
}}

function downloadIdmlPackage() {{
  const content = ['ACL Adobe InDesign Package', 'Project: {project_name}', 'Version: 2.4', 'Layout: Japanese Right-to-Left (Manga Spreads)', 'Typography: CC Wild Words, Anime Ace, Manga Temple', 'Status: Verified'].join(String.fromCharCode(10));
  const blob = new Blob([content], {{ type: 'text/plain' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = '{file_safe_project}_InDesign_IDML.idml';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('Generated Adobe InDesign (.IDML) typography package');
}}

</script>

</body>
</html>
"""

# Render the Google Stitch component seamlessly
components.html(queue_monitor_html, height=1200, scrolling=True)
