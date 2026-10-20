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
<aside class="fixed left-0 top-0 h-full w-[220px] bg-surface-container-lowest z-50 flex flex-col justify-between shadow-[0_1px_8px_rgba(0,0,0,0.04)] select-none">
  <div class="flex flex-col">
    <div class="px-space-md pt-space-lg pb-space-md border-b border-[#E4DFD6]">
      <div class="font-headline-md text-headline-md text-primary tracking-tight notranslate" translate="no">ACL</div>
      <div class="font-body-sm text-body-sm text-on-surface-variant font-medium leading-tight">Automated Comic Localization</div>
      <div class="mt-space-xs inline-flex items-center gap-1 px-space-xs py-0.5 rounded-full bg-surface-container text-on-surface-variant font-code-sm text-code-sm notranslate" translate="no">
        <span>C1SE.80</span>
      </div>
    </div>

    <!-- Navigation Stack -->
    <nav class="flex flex-col gap-1 px-space-sm mt-space-xs">
      <a class="flex items-center gap-space-sm px-space-sm py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface transition-colors font-body-md text-body-md cursor-pointer" onclick="navigateParent('workspace')">
        <span class="material-symbols-outlined text-[20px]">grid_view</span>
        <span>Dashboard</span>
      </a>
      <a class="flex items-center gap-space-sm px-space-sm py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface transition-colors font-body-md text-body-md cursor-pointer" onclick="navigateParent('workspace')">
        <span class="material-symbols-outlined text-[20px]">folder</span>
        <span>Projects</span>
      </a>
      <a class="flex items-center gap-space-sm px-space-sm py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface transition-colors font-body-md text-body-md cursor-pointer" onclick="navigateParent('team-roles')">
        <span class="material-symbols-outlined text-[20px]">groups</span>
        <span>Team Roles</span>
      </a>
      <a class="flex items-center gap-space-sm px-space-sm py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface transition-colors font-body-md text-body-md cursor-pointer" onclick="navigateParent('chapter-studio')">
        <span class="material-symbols-outlined text-[20px]">auto_stories</span>
        <span>Chapter Studio</span>
      </a>
      <a class="flex items-center gap-space-sm px-space-sm py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface transition-colors font-body-md text-body-md cursor-pointer" onclick="navigateParent('review-studio')">
        <span class="material-symbols-outlined text-[20px]">rate_review</span>
        <span>Review Studio</span>
      </a>
      <a class="flex items-center gap-space-sm px-space-sm py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface transition-colors font-body-md text-body-md cursor-pointer" onclick="navigateParent('typesetting')">
        <span class="material-symbols-outlined text-[20px]">format_shapes</span>
        <span>Typesetting</span>
      </a>
      <a aria-current="page" class="flex items-center gap-space-sm px-space-sm py-2 rounded-lg bg-primary-container text-on-primary font-title-md font-semibold cursor-pointer" onclick="navigateParent('queue-monitor')">
        <span class="material-symbols-outlined text-[20px]">monitoring</span>
        <span>Queue Monitor</span>
      </a>
      <a class="flex items-center gap-space-sm px-space-sm py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface transition-colors font-body-md text-body-md cursor-pointer" onclick="navigateParent('settings')">
        <span class="material-symbols-outlined text-[20px]">tune</span>
        <span>Personal Settings</span>
      </a>
    </nav>
  </div>

  <div class="p-space-md border-t border-[#E4DFD6]">
    <div class="flex items-center justify-between px-space-sm py-2 rounded-lg bg-surface-container-low">
      <div class="flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-secondary"></span>
        <span class="font-code-sm text-code-sm text-on-surface-variant notranslate" translate="no">v2.4.0-prod</span>
      </div>
      <span class="material-symbols-outlined text-outline text-[16px]">cloud_done</span>
    </div>
  </div>
</aside>

<!-- MAIN APP SHELL -->
<div class="pl-[220px]">

  <!-- TOP HEADER BAR (SaaS Pro with Notification & Profile Dropdown) -->
  <header class="fixed top-0 left-[220px] right-0 h-16 bg-surface-container-lowest/95 backdrop-blur-md z-40 px-8 flex items-center justify-between border-b border-[#E4DFD6]">
    
    <!-- Left: ACL Studio / Workspace / {project_name} / Queue Monitor Breadcrumb -->
    <div class="flex items-center gap-2">
      <span class="text-base font-bold text-on-surface">ACL Studio</span>
      <span class="text-outline-variant font-light text-sm">/</span>
      <a class="text-sm text-on-surface-variant font-medium hover:text-on-surface transition-colors cursor-pointer" onclick="navigateParent('workspace')">Workspace</a>
      <span class="text-outline-variant font-light text-sm">/</span>
      <a class="text-sm text-on-surface-variant font-medium hover:text-primary-container transition-colors cursor-pointer notranslate" translate="no" onclick="navigateParent('chapter-studio?project=' + encodeURIComponent('{project_name}'))" title="Open Chapter Studio for {project_name}">{project_name}</a>
      <span class="text-outline-variant font-light text-sm">/</span>
      <span class="text-sm text-primary-container font-semibold">Queue Monitor</span>
    </div>

    <!-- Center/Right Header Controls -->
    <div class="flex items-center gap-4">
      
      <!-- Node Tokyo-01 Pill Badge -->
      <div class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#E8EDF4] text-[#414754] border border-[#D0D7DE] font-code text-xs font-medium cursor-pointer transition-colors" title="Active Processing Node">
        <span class="material-symbols-outlined text-[15px] text-[#57606A]">memory</span>
        <span>Node Tokyo-01 (GPU Active)</span>
      </div>

      <!-- INTERACTIVE NOTIFICATION BELL WITH RED DOT -->
      <div class="relative">
        <button id="notif-btn" onclick="toggleNotifDropdown(event)" class="relative p-1.5 rounded-full hover:bg-surface-container text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer" title="Notifications">
          <span class="material-symbols-outlined text-[22px]">notifications</span>
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

      <!-- User Profile Menu (Avatar + Chevron Dropdown) -->
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
            <div class="relative inline-flex items-center bg-surface-container-lowest border border-outline-variant/60 rounded-full px-space-md py-1.5 text-on-surface shadow-sm cursor-pointer hover:bg-surface-container-low transition-colors">
              <span class="w-2 h-2 rounded-full bg-secondary mr-2 inline-block animate-ping"></span>
              <span class="font-label-md text-label-md">Auto-refresh: <strong>5s</strong></span>
            </div>
            <button id="pause-queue-btn" onclick="togglePauseQueue()" class="inline-flex items-center gap-1.5 px-space-md py-1.5 rounded-full border border-outline-variant/60 bg-surface-container-lowest text-on-surface hover:bg-surface-container-low transition-colors shadow-sm font-label-md text-label-md cursor-pointer" type="button">
              <span id="pause-icon" class="material-symbols-outlined text-[16px] text-on-surface-variant">pause</span>
              <span id="pause-label">Pause Queue</span>
            </button>
          </div>
        </div>

        <!-- 2. CHAPTER OVERALL PROGRESS CARD -->
        <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 p-space-lg shadow-sm">
          <!-- Row 1: Header & Metrics -->
          <div class="flex flex-col sm:flex-row sm:items-baseline justify-between gap-space-xs mb-space-sm">
            <div class="flex items-center gap-space-sm flex-wrap">
              <h2 class="font-headline-sm text-headline-sm text-on-surface font-semibold">Active Chapter: <span class="notranslate" translate="no">{project_name}</span></h2>
              <span class="font-code-sm text-code-sm bg-surface-container-high text-on-surface-variant px-space-xs py-0.5 rounded notranslate" translate="no">#CH-112-RAW</span>
            </div>
            <div class="text-left sm:text-right">
              <div class="font-headline-sm text-headline-sm text-primary-container font-bold" id="progress-percentage-label">16 / 24 Pages Processed (68%)</div>
              <div class="font-body-sm text-body-sm text-outline">Estimated completion: ~2m 45s</div>
            </div>
          </div>
          <!-- Row 2: Large Progress Bar -->
          <div class="w-full h-3 bg-surface-container-highest rounded-full overflow-hidden mb-space-lg relative">
            <div class="h-full bg-primary-container rounded-full relative progress-animated" id="progress-bar-fill" style="width: 68%;"></div>
          </div>
          <!-- Row 3: 7-Stage Pipeline Visual Stepper -->
          <div class="grid grid-cols-2 md:grid-cols-7 gap-space-xs pt-space-xs">
            <div class="flex flex-col items-center text-center p-space-xs rounded-lg hover:bg-surface-container-low transition-colors">
              <div class="w-8 h-8 rounded-full bg-secondary-container text-secondary flex items-center justify-center mb-1.5 shadow-sm">
                <span class="material-symbols-outlined text-[16px] font-bold">check</span>
              </div>
              <span class="font-label-md text-label-md text-on-surface font-semibold">1. Queued</span>
              <span class="font-code-sm text-code-sm text-secondary font-medium">Completed</span>
            </div>
            <div class="flex flex-col items-center text-center p-space-xs rounded-lg hover:bg-surface-container-low transition-colors">
              <div class="w-8 h-8 rounded-full bg-secondary-container text-secondary flex items-center justify-center mb-1.5 shadow-sm">
                <span class="material-symbols-outlined text-[16px] font-bold">check</span>
              </div>
              <span class="font-label-md text-label-md text-on-surface font-semibold">2. Detection</span>
              <span class="font-code-sm text-code-sm text-secondary font-medium notranslate" translate="no">YOLOv8 ✓</span>
            </div>
            <div class="flex flex-col items-center text-center p-space-xs rounded-lg hover:bg-surface-container-low transition-colors">
              <div class="w-8 h-8 rounded-full bg-secondary-container text-secondary flex items-center justify-center mb-1.5 shadow-sm">
                <span class="material-symbols-outlined text-[16px] font-bold">check</span>
              </div>
              <span class="font-label-md text-label-md text-on-surface font-semibold">3. OCR</span>
              <span class="font-code-sm text-code-sm text-secondary font-medium notranslate" translate="no">Manga OCR ✓</span>
            </div>
            <div class="flex flex-col items-center text-center p-space-xs rounded-lg bg-primary-fixed/30 transition-colors">
              <div class="relative w-8 h-8 rounded-full bg-primary-container text-on-primary flex items-center justify-center mb-1.5 shadow-sm">
                <span class="material-symbols-outlined text-[16px]">edit_note</span>
                <span class="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-error border-2 border-surface-container-lowest"></span>
              </div>
              <span class="font-label-md text-label-md text-primary-container font-bold">4. Review</span>
              <span class="font-code-sm text-code-sm px-1.5 py-0.5 rounded-full bg-primary-container text-on-primary font-semibold">1 Active</span>
            </div>
            <div class="flex flex-col items-center text-center p-space-xs rounded-lg hover:bg-surface-container-low transition-colors">
              <div class="w-8 h-8 rounded-full bg-surface-container-high text-on-surface-variant flex items-center justify-center mb-1.5 shadow-sm animate-pulse">
                <span class="material-symbols-outlined text-[16px] text-tertiary">brush</span>
              </div>
              <span class="font-label-md text-label-md text-on-surface font-semibold">5. Inpainting</span>
              <span class="font-code-sm text-code-sm text-on-surface-variant notranslate" translate="no">LaMa GAN</span>
            </div>
            <div class="flex flex-col items-center text-center p-space-xs rounded-lg opacity-80">
              <div class="w-8 h-8 rounded-full bg-surface-container text-outline flex items-center justify-center mb-1.5">
                <span class="material-symbols-outlined text-[16px]">text_fields</span>
              </div>
              <span class="font-label-md text-label-md text-on-surface-variant font-medium">6. Typesetting</span>
              <span class="font-code-sm text-code-sm text-outline">CC Wild Words</span>
            </div>
            <div class="flex flex-col items-center text-center p-space-xs rounded-lg opacity-60">
              <div class="w-8 h-8 rounded-full bg-surface-container text-outline flex items-center justify-center mb-1.5">
                <span class="material-symbols-outlined text-[16px]">archive</span>
              </div>
              <span class="font-label-md text-label-md text-on-surface-variant font-medium">7. Completed</span>
              <span class="font-code-sm text-code-sm text-outline">ZIP Export</span>
            </div>
          </div>
        </div>

        <!-- 3. HARDWARE & CLUSTER HEALTH MINI-METRICS ROW -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-space-md">
          <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 p-space-md shadow-sm flex flex-col justify-between">
            <div class="flex items-center justify-between mb-space-xs">
              <span class="font-body-sm text-body-sm text-outline font-medium">GPU Cluster (VRAM Health)</span>
              <span class="material-symbols-outlined text-[18px] text-primary-container">memory</span>
            </div>
            <div>
              <div class="font-title-md text-title-md text-on-surface font-semibold notranslate" translate="no">NVIDIA RTX 4090 (24GB)</div>
              <div class="font-code-md text-code-md text-on-surface-variant mt-0.5 notranslate" translate="no">14.8 GB / 24.0 GB Used (61%)</div>
            </div>
            <div class="mt-space-sm pt-space-xs border-t border-surface-container-high flex items-center justify-between">
              <div class="w-full bg-surface-container-highest h-1.5 rounded-full mr-space-sm overflow-hidden">
                <div class="bg-primary-container h-full rounded-full" style="width: 61%;"></div>
              </div>
              <span class="font-code-sm text-code-sm bg-secondary-container text-secondary px-space-xs py-0.5 rounded whitespace-nowrap font-medium notranslate" translate="no">Normal Temp 58°C</span>
            </div>
          </div>

          <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 p-space-md shadow-sm flex flex-col justify-between">
            <div class="flex items-center justify-between mb-space-xs">
              <span class="font-body-sm text-body-sm text-outline font-medium">Async Task Throughput</span>
              <span class="material-symbols-outlined text-[18px] text-primary-container">speed</span>
            </div>
            <div>
              <div class="font-title-md text-title-md text-on-surface font-semibold">14.2 sec / page avg</div>
              <div class="font-code-md text-code-md text-on-surface-variant mt-0.5">Throughput: 4.2 pages/min</div>
            </div>
            <div class="mt-space-sm pt-space-xs border-t border-surface-container-high flex items-center justify-between">
              <span class="font-body-sm text-body-sm text-secondary font-medium flex items-center gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-secondary inline-block"></span>
                <span>0 Dropped Frames</span>
              </span>
              <span class="font-code-sm text-code-sm text-outline notranslate" translate="no">Queue Latency: 120ms</span>
            </div>
          </div>

          <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 p-space-md shadow-sm flex flex-col justify-between">
            <div class="flex items-center justify-between mb-space-xs">
              <span class="font-body-sm text-body-sm text-outline font-medium">API Quota Rate Limit</span>
              <span class="material-symbols-outlined text-[18px] text-primary-container">api</span>
            </div>
            <div>
              <div class="font-title-md text-title-md text-on-surface font-semibold notranslate" translate="no">Gemini 1.5 Pro Client</div>
              <div class="font-code-md text-code-md text-on-surface-variant mt-0.5 notranslate" translate="no">42 / 60 RPM Active</div>
            </div>
            <div class="mt-space-sm pt-space-xs border-t border-surface-container-high flex items-center justify-between">
              <div class="w-full bg-surface-container-highest h-1.5 rounded-full mr-space-sm overflow-hidden">
                <div class="bg-secondary h-full rounded-full" style="width: 70%;"></div>
              </div>
              <span class="font-code-sm text-code-sm text-secondary font-medium whitespace-nowrap notranslate" translate="no">Optimal (No Throttle)</span>
            </div>
          </div>
        </div>

        <!-- 4. DETAILED PAGE TASKS TABLE -->
        <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 overflow-hidden shadow-sm">
          <div class="p-space-md border-b border-outline-variant/50 flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm bg-surface-container-lowest">
            <div class="flex items-center gap-space-xs overflow-x-auto pb-1 sm:pb-0">
              <button id="task-filter-all" onclick="filterTaskRows('all')" class="px-space-sm py-1 rounded-lg text-primary-container bg-primary-fixed/40 font-title-md text-title-md text-xs font-bold whitespace-nowrap cursor-pointer transition-all" type="button">All Tasks (24)</button>
              <button id="task-filter-completed" onclick="filterTaskRows('completed')" class="px-space-sm py-1 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container font-label-md text-label-md whitespace-nowrap transition-colors cursor-pointer" type="button">Completed (12)</button>
              <button id="task-filter-inprogress" onclick="filterTaskRows('inprogress')" class="px-space-sm py-1 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container font-label-md text-label-md whitespace-nowrap transition-colors cursor-pointer" type="button">In Progress (4)</button>
              <button id="task-filter-queued" onclick="filterTaskRows('queued')" class="px-space-sm py-1 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container font-label-md text-label-md whitespace-nowrap transition-colors cursor-pointer" type="button">Queued (8)</button>
            </div>
            <div class="relative w-full sm:w-64">
              <span class="material-symbols-outlined absolute left-2.5 top-2 text-[16px] text-outline">search</span>
              <input id="task-table-search" oninput="searchTaskRows(this.value)" class="w-full h-8 pl-8 pr-3 text-xs font-body-sm text-on-surface bg-surface-container-lowest border border-outline-variant/60 rounded-lg focus:outline-none focus:border-primary-container focus:ring-1 focus:ring-primary-container" placeholder="Filter by page or status..." type="text"/>
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
                  <td class="py-3.5 px-space-md font-title-md font-semibold text-primary-container">Page 013</td>
                  <td class="py-3.5 px-space-md font-code-sm text-code-sm text-on-surface-variant notranslate" translate="no">page_013.png</td>
                  <td class="py-3.5 px-space-md text-on-surface font-medium">Waiting Review (OCR Correction)</td>
                  <td class="py-3.5 px-space-md">
                    <div class="flex items-center gap-2">
                      <span class="inline-flex items-center gap-1 bg-primary-fixed text-primary px-space-sm py-0.5 rounded-full font-code-sm text-code-sm font-semibold">
                        <span class="material-symbols-outlined text-[13px]">rate_review</span>
                        <span>Waiting Review</span>
                      </span>
                      <a class="font-title-md text-xs text-primary-container font-bold hover:underline cursor-pointer" onclick="navigateParent('review-studio')">Review Now →</a>
                    </div>
                  </td>
                  <td class="py-3.5 px-space-md text-right font-code-sm text-code-sm text-primary font-medium notranslate" translate="no">12:08:14 (Just now)</td>
                </tr>
                <tr data-status="inprogress" class="task-row hover:bg-surface-container-low/60 transition-colors">
                  <td class="py-3.5 px-space-md font-title-md font-semibold text-on-surface">Page 014</td>
                  <td class="py-3.5 px-space-md font-code-sm text-code-sm text-on-surface-variant notranslate" translate="no">page_014.png</td>
                  <td class="py-3.5 px-space-md text-on-surface font-medium">LaMa Inpainting (Background Clean)</td>
                  <td class="py-3.5 px-space-md">
                    <div class="flex items-center gap-2">
                      <span class="inline-flex items-center gap-1.5 bg-secondary-fixed text-on-secondary-fixed-variant px-space-sm py-0.5 rounded-full font-code-sm text-code-sm font-semibold">
                        <span class="material-symbols-outlined text-[13px] animate-spin">sync</span>
                        <span>Inpainting</span>
                      </span>
                      <a class="font-title-md text-xs text-primary-container font-bold hover:underline cursor-pointer" onclick="navigateParent('typesetting')">Typeset →</a>
                    </div>
                  </td>
                  <td class="py-3.5 px-space-md text-right font-code-sm text-code-sm text-outline notranslate" translate="no">12:08:52 (In flight)</td>
                </tr>
                <tr data-status="inprogress" class="task-row hover:bg-surface-container-low/60 transition-colors">
                  <td class="py-3.5 px-space-md font-title-md font-semibold text-on-surface">Page 015</td>
                  <td class="py-3.5 px-space-md font-code-sm text-code-sm text-on-surface-variant notranslate" translate="no">page_015.png</td>
                  <td class="py-3.5 px-space-md text-on-surface font-medium">Manga OCR v2.1 Extraction</td>
                  <td class="py-3.5 px-space-md">
                    <span class="inline-flex items-center gap-1.5 bg-secondary-fixed text-on-secondary-fixed-variant px-space-sm py-0.5 rounded-full font-code-sm text-code-sm font-semibold">
                      <span class="material-symbols-outlined text-[13px] animate-spin">sync</span>
                      <span>OCR Extraction</span>
                    </span>
                  </td>
                  <td class="py-3.5 px-space-md text-right font-code-sm text-code-sm text-outline notranslate" translate="no">12:09:01 (In flight)</td>
                </tr>
                <tr data-status="inprogress" class="task-row hover:bg-surface-container-low/60 transition-colors">
                  <td class="py-3.5 px-space-md font-title-md font-semibold text-on-surface">Page 016</td>
                  <td class="py-3.5 px-space-md font-code-sm text-code-sm text-on-surface-variant notranslate" translate="no">page_016.png</td>
                  <td class="py-3.5 px-space-md text-on-surface font-medium">YOLOv8 Speech Bubble Detection</td>
                  <td class="py-3.5 px-space-md">
                    <span class="inline-flex items-center gap-1.5 bg-secondary-fixed text-on-secondary-fixed-variant px-space-sm py-0.5 rounded-full font-code-sm text-code-sm font-semibold">
                      <span class="material-symbols-outlined text-[13px] animate-spin">autorenew</span>
                      <span>YOLO Detection</span>
                    </span>
                  </td>
                  <td class="py-3.5 px-space-md text-right font-code-sm text-code-sm text-outline notranslate" translate="no">12:09:10 (In flight)</td>
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
          <div class="flex items-center gap-space-xs font-code-sm text-code-sm">
            <span class="w-2 h-2 rounded-full bg-secondary"></span>
            <span>Python Celery / AsyncIO Worker ID: <strong class="text-on-surface notranslate" translate="no">#acl-worker-8421</strong> • Redis Cache: <strong class="text-secondary notranslate" translate="no">Connected</strong> • SQLite Session: <strong class="text-on-surface notranslate" translate="no">Synchronized</strong></span>
          </div>
          <a class="font-code-sm text-code-sm text-primary-container hover:underline flex items-center gap-1 cursor-pointer" onclick="downloadPipelineLog()">
            <span class="material-symbols-outlined text-[14px]">download</span>
            <span>Download Full Pipeline Log (.LOG)</span>
          </a>
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
              <span class="font-code-sm text-code-sm text-on-surface-variant notranslate" translate="no">Batch ID: #CH-112-RAW</span>
            </div>
            <h1 class="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">Chapter Release Pack</h1>
            <p class="font-body-md text-body-md text-on-surface-variant mt-0.5">All chapter pipeline tasks completed successfully with zero validation errors.</p>
          </div>
          <div class="flex items-center gap-space-sm flex-wrap">
            <div class="inline-flex items-center gap-1.5 bg-secondary-container/40 text-on-secondary-container px-3 py-1.5 rounded-full shadow-sm">
              <span class="material-symbols-outlined text-[18px] text-secondary">check_circle</span>
              <span class="font-code-sm text-code-sm font-semibold tracking-wide">All 24/24 Pages Complete</span>
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
                <a class="font-label-md text-label-md text-primary-container hover:text-primary underline underline-offset-2 transition-colors cursor-pointer" onclick="alert('Downloading individual PNG package...')">Individual Pages (.PNG)</a>
                <span class="text-outline-variant">•</span>
                <a class="font-label-md text-label-md text-primary-container hover:text-primary underline underline-offset-2 transition-colors cursor-pointer" onclick="alert('Packaging Adobe InDesign (.IDML)...')">InDesign (.IDML) Package</a>
              </div>
              <div class="flex items-center gap-3 mt-3 pt-2.5 border-t border-secondary/20">
                <a class="font-label-md text-label-md font-semibold text-primary-container hover:text-primary inline-flex items-center gap-1 cursor-pointer" onclick="navigateParent('workspace')">
                  <span class="material-symbols-outlined text-[16px]">grid_view</span>
                  <span>Back to Projects</span>
                </a>
                <span class="text-outline-variant">•</span>
                <a class="font-label-md text-label-md font-semibold text-primary-container hover:text-primary inline-flex items-center gap-1 cursor-pointer" onclick="navigateParent('chapter-studio')">
                  <span class="material-symbols-outlined text-[16px]">cloud_upload</span>
                  <span>Upload Next Chapter</span>
                </a>
              </div>
            </div>
          </div>
        </div>

        <!-- Final Summary Metrics Row -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-gutter-lg">
          <div class="bg-surface-container-lowest rounded-xl p-space-md shadow-sm border border-[#E4DFD6] flex flex-col justify-between">
            <div class="flex items-start justify-between">
              <div>
                <span class="font-code-sm text-code-sm uppercase tracking-wider font-semibold text-on-surface-variant">Total Pages Localized</span>
                <div class="font-headline-lg text-headline-lg text-on-surface mt-1 font-bold">24 <span class="font-body-md text-body-md font-normal text-on-surface-variant">Pages</span></div>
              </div>
              <div class="w-10 h-10 rounded-full bg-secondary-container/50 text-secondary flex items-center justify-center">
                <span class="material-symbols-outlined text-[22px]">auto_stories</span>
              </div>
            </div>
            <div class="mt-4 pt-3 border-t border-[#E4DFD6] flex items-center gap-1.5 font-body-sm text-body-sm text-secondary">
              <span class="material-symbols-outlined text-[16px]">check_circle</span>
              <span>100% of staged batch completed without errors</span>
            </div>
          </div>

          <div class="bg-surface-container-lowest rounded-xl p-space-md shadow-sm border border-[#E4DFD6] flex flex-col justify-between">
            <div class="flex items-start justify-between">
              <div>
                <span class="font-code-sm text-code-sm uppercase tracking-wider font-semibold text-on-surface-variant">Average Processing Time</span>
                <div class="font-headline-lg text-headline-lg text-on-surface mt-1 font-bold">14.2 <span class="font-body-md text-body-md font-normal text-on-surface-variant">sec / page</span></div>
              </div>
              <div class="w-10 h-10 rounded-full bg-primary-fixed text-primary flex items-center justify-center">
                <span class="material-symbols-outlined text-[22px]">speed</span>
              </div>
            </div>
            <div class="mt-4 pt-3 border-t border-[#E4DFD6] flex items-center gap-1.5 font-body-sm text-body-sm text-secondary">
              <span class="material-symbols-outlined text-[16px]">bolt</span>
              <span>Total elapsed time: 5m 41s</span>
            </div>
          </div>

          <div class="bg-surface-container-lowest rounded-xl p-space-md shadow-sm border border-[#E4DFD6] flex flex-col justify-between">
            <div class="flex items-start justify-between">
              <div>
                <span class="font-code-sm text-code-sm uppercase tracking-wider font-semibold text-on-surface-variant">Translation &amp; Inpaint Quality</span>
                <div class="font-headline-lg text-headline-lg text-on-surface mt-1 font-bold">99.8% <span class="font-body-md text-body-md font-normal text-on-surface-variant">Accuracy</span></div>
              </div>
              <div class="w-10 h-10 rounded-full bg-secondary-container/50 text-secondary flex items-center justify-center">
                <span class="material-symbols-outlined text-[22px]">verified_user</span>
              </div>
            </div>
            <div class="mt-4 pt-3 border-t border-[#E4DFD6] flex items-center gap-1.5 font-body-sm text-body-sm text-secondary">
              <span class="material-symbols-outlined text-[16px]">task_alt</span>
              <span>Human verification signoff recorded</span>
            </div>
          </div>
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

// Search filter inside task table
function searchTaskRows(query) {{
  const term = query.toLowerCase().trim();
  const rows = document.querySelectorAll('.task-row');
  rows.forEach(r => {{
    const matchesFilter = (currentFilter === 'all' || r.getAttribute('data-status') === currentFilter);
    const text = r.innerText.toLowerCase();
    if (matchesFilter && (!term || text.includes(term))) {{
      r.style.display = '';
    }} else {{
      r.style.display = 'none';
    }}
  }});
}}
function navigateParent(path) {{
  const target = '/' + path.replace(/^\\//, '');
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

// Tab switcher between Active Queue and Completed ZIP export
function switchView(viewName) {{
  const viewActive = document.getElementById('view-active');
  const viewCompleted = document.getElementById('view-completed');
  const tabActive = document.getElementById('tab-active');
  const tabCompleted = document.getElementById('tab-completed');

  if (viewName === 'completed') {{
    viewActive.classList.add('hidden');
    viewCompleted.classList.remove('hidden');
    tabCompleted.classList.add('bg-primary-container', 'text-on-primary');
    tabCompleted.classList.remove('bg-surface-container', 'text-on-surface-variant');
    tabActive.classList.remove('bg-primary-container', 'text-on-primary');
    tabActive.classList.add('bg-surface-container', 'text-on-surface-variant');
  }} else {{
    viewCompleted.classList.add('hidden');
    viewActive.classList.remove('hidden');
    tabActive.classList.add('bg-primary-container', 'text-on-primary');
    tabActive.classList.remove('bg-surface-container', 'text-on-surface-variant');
    tabCompleted.classList.remove('bg-primary-container', 'text-on-primary');
    tabCompleted.classList.add('bg-surface-container', 'text-on-surface-variant');
  }}
}}

// Progress simulation
let simPercent = 68;
function simulateJobProgress() {{
  if (isPaused) {{
    showToast('Queue is currently paused. Click Resume first.');
    return;
  }}
  simPercent = Math.min(100, simPercent + 8);
  const bar = document.getElementById('progress-bar-fill');
  const label = document.getElementById('progress-percentage-label');
  const pages = Math.round((simPercent / 100) * 24);
  if (bar) bar.style.width = simPercent + '%';
  if (label) label.innerText = `${{pages}} / 24 Pages Processed (${{simPercent}}%)`;

  showToast(`Simulated step: ${{pages}}/24 Pages processed (${{simPercent}}%)`);

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
Batch ID: #CH-112-RAW
Total Pages: 24
Pipeline Stages:
1. Ingestion: Complete (24/24)
2. YOLOv8 Text Detection: Complete (24/24) - mAP 0.942
3. Manga OCR v2.1: Complete (24/24) - Zero retries
4. Human Interactive Review: Signed off by Lead Editor
5. LaMa GAN Inpainting: Complete (24/24)
6. Typography & Typesetting: Complete (24/24) - CC Wild Words
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
</script>

</body>
</html>
"""

# Render the Google Stitch component seamlessly
components.html(queue_monitor_html, height=1200, scrolling=True)
