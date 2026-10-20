"""ACL Team Workspace & Member Role Assignment — Screen ACL-05.

Pixel-perfect implementation matching Google Stitch Project 'UX/UI_ACL' (ID: 15081338219515375601).
Screen: ACL-05: Team Workspace & Member Role Assignment (ID: 10cfe054e1664c7e957a7651597002af).
Includes full Vietnamese Unicode font support with fallback metrics to ensure Google Translate never breaks fonts.
100% English UI Labels with interactive Notification Bell, Sidebar Logo A, and 3 KPI Metric Cards.
"""

import streamlit as st
import streamlit.components.v1 as components

from utils.auth_session import require_auth


# Enforce authentication guard
user = require_auth()

user_initials = (user.full_name[:2] if user.full_name else "PH").upper()
user_name = user.full_name or "Phan Van Quan"
project_name = st.query_params.get("project", "Shonen Weekly #112")

team_workspace_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<meta content="web_dashboard" name="shell-type"/>
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
<!-- Comprehensive Google Fonts import with explicit Vietnamese & Latin-Ext subsets -->
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,600&family=Sora:wght@600;700;800&subset=vietnamese,latin,latin-ext&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet"/>

<style>
@layer base {{
  html, body {{
    margin: 0;
    padding: 0;
    background: #f8faf7;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #191c19;
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
  }}
  body {{ overscroll-behavior: none; }}
  main > :first-child {{ margin-top: 0 !important; }}
  main > :last-child {{ margin-bottom: 0 !important; }}
}}

/* Google Translate DOM Injection Compatibility Fixes */
font {{
  font-family: inherit !important;
  font-size: inherit !important;
  line-height: inherit !important;
}}
.notranslate {{
  translate: no !important;
}}

/* Hide native scrollbar while retaining scroll capability */
::-webkit-scrollbar {{ display: none; }}

@keyframes fadeIn {{
  from {{ opacity: 0; transform: translateY(-4px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
.animate-fadeIn {{
  animation: fadeIn 0.3s ease-out forwards;
}}
</style>

<script src="https://cdn.tailwindcss.com"></script>
<script id="tailwind-config">
tailwind.config = {{
  darkMode: "class",
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
        "tertiary-container": "#383063",
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
        error: "#ba1a1a",
        "error-container": "#ffdad6",
        "on-error-container": "#93000a",
        "tertiary-fixed": "#e6deff"
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
</head>
<body class="bg-surface font-sans text-on-surface antialiased">

<!-- FIXED LEFT SIDEBAR (Đồng bộ chuẩn logo A và Footer với Workspace) -->
<aside class="fixed left-0 top-0 h-full w-[220px] bg-surface-container-lowest z-50 flex flex-col justify-between py-5 border-r border-[#E4DFD6]">
  <div>
    <!-- Brand / Logo Area: Square Badge with 'A' (Đồng bộ hoàn toàn) -->
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
      <a class="flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all cursor-pointer" onclick="navigateParent('workspace')">
        <span class="material-symbols-outlined text-[20px]">grid_view</span>
        <span>Dashboard</span>
      </a>
      <a class="flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all cursor-pointer" onclick="navigateParent('workspace')">
        <span class="material-symbols-outlined text-[20px]">folder</span>
        <span>Projects</span>
      </a>
      <a aria-current="page" class="flex items-center gap-3 px-3 py-2 transition-all bg-primary-container text-on-primary text-xs font-semibold rounded-xl cursor-pointer shadow-sm" onclick="navigateParent('team-roles')">
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

  <!-- Sidebar Footer: Documentation & Core Online (Đồng bộ hoàn toàn) -->
  <div class="px-5 pt-3 border-t border-[#E4DFD6] flex flex-col gap-2.5">
    <a class="flex items-center gap-2 text-on-surface-variant hover:text-on-surface text-xs font-medium cursor-pointer transition-colors" onclick="alert('ACL Documentation v2.4: System guides, RBAC permissions, and API specs.')">
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

  <!-- TOP HEADER BAR (Đồng bộ chuẩn nhận diện: ACL Studio / Projects... + Chuông đỏ) -->
  <header class="fixed top-0 left-[220px] right-0 h-16 bg-surface-container-lowest/95 backdrop-blur-md z-40 px-8 flex items-center justify-between border-b border-[#E4DFD6]">
    
    <!-- Left: ACL Studio / Projects / Shonen Weekly #112 / Team Workspace -->
    <div class="flex items-center gap-2 flex-wrap">
      <a class="text-base font-bold text-on-surface hover:text-primary-container transition-colors cursor-pointer" onclick="navigateParent('workspace')">ACL Studio</a>
      <span class="text-outline-variant font-light text-sm">/</span>
      <a class="text-sm text-on-surface-variant font-medium hover:text-on-surface transition-colors cursor-pointer" onclick="navigateParent('workspace')">Projects</a>
      <span class="text-outline-variant font-light text-sm">/</span>
      <a class="text-sm text-on-surface-variant font-medium hover:text-primary-container transition-colors cursor-pointer notranslate" translate="no" onclick="navigateParent('chapter-studio?project=' + encodeURIComponent('{project_name}'))" title="Open Chapter Studio for {project_name}">{project_name}</a>
      <span class="text-outline-variant font-light text-sm">/</span>
      <span class="text-sm text-primary-container font-semibold">Team Workspace</span>
    </div>

    <!-- Center/Right Header Controls -->
    <div class="flex items-center gap-4">
      
      <!-- Search Input -->
      <div class="hidden md:flex items-center bg-surface-container-low rounded-full px-3.5 py-1.5 border border-[#E4DFD6]">
        <span class="material-symbols-outlined text-[18px] text-on-surface-variant mr-1.5">search</span>
        <input class="bg-transparent text-xs outline-none placeholder:text-on-surface-variant w-36 text-on-surface" placeholder="Filter workspace..." type="text"/>
      </div>

      <!-- Node Tokyo-01 (GPU idle) Pill Badge -->
      <a onclick="navigateParent('queue-monitor')" class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#E8EDF4] hover:bg-[#D8E2EE] text-[#414754] hover:text-[#191C19] border border-[#D0D7DE] font-code text-xs font-medium cursor-pointer transition-colors" title="View GPU Cluster Queue on Node Tokyo-01">
        <span class="material-symbols-outlined text-[15px] text-[#57606A]">memory</span>
        <span>Node Tokyo-01 (GPU idle)</span>
      </a>

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
            <div class="p-3 hover:bg-surface-container-low transition-colors cursor-pointer" onclick="navigateParent('team-roles')">
              <div class="flex items-start gap-2.5">
                <span class="notif-dot w-2 h-2 rounded-full bg-[#DC2626] mt-1.5 shrink-0"></span>
                <div>
                  <p class="text-xs font-semibold text-on-surface">Team Role Accepted</p>
                  <p class="text-[11px] text-on-surface-variant mt-0.5">Tran Ha (TH) joined as Japanese Translator.</p>
                  <span class="font-code text-[10px] text-outline mt-1 block">Just now</span>
                </div>
              </div>
            </div>
            <div class="p-3 hover:bg-surface-container-low transition-colors cursor-pointer" onclick="navigateParent('review-studio')">
              <div class="flex items-start gap-2.5">
                <span class="notif-dot w-2 h-2 rounded-full bg-[#DC2626] mt-1.5 shrink-0"></span>
                <div>
                  <p class="text-xs font-semibold text-on-surface">Batch #CH-112-RAW Ready</p>
                  <p class="text-[11px] text-on-surface-variant mt-0.5">Manga-OCR extraction completed. 18/24 pages reviewed.</p>
                  <span class="font-code text-[10px] text-outline mt-1 block">15 mins ago</span>
                </div>
              </div>
            </div>
            <div class="p-3 hover:bg-surface-container-low transition-colors cursor-pointer" onclick="navigateParent('queue-monitor')">
              <div class="flex items-start gap-2.5">
                <span class="notif-dot w-2 h-2 rounded-full bg-[#DC2626] mt-1.5 shrink-0"></span>
                <div>
                  <p class="text-xs font-semibold text-on-surface">Node Tokyo-01 Idle</p>
                  <p class="text-[11px] text-on-surface-variant mt-0.5">GPU cluster ready for dispatching new inpainting batch.</p>
                  <span class="font-code text-[10px] text-outline mt-1 block">1 hour ago</span>
                </div>
              </div>
            </div>
          </div>
          <div class="pt-2 px-4 border-t border-[#E4DFD6]/70 text-center">
            <a class="text-xs font-semibold text-primary-container hover:underline cursor-pointer" onclick="navigateParent('queue-monitor')">
              View all pipeline tasks →
            </a>
          </div>
        </div>
      </div>

      <!-- Filter preferences icon -->
      <button onclick="document.getElementById('inviteInput')?.focus(); showToast('Personnel Management: Focus on member allocation');" class="p-1.5 rounded-full hover:bg-surface-container text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer" title="Focus Member Invitation Form">
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
            <a class="flex items-center gap-2.5 px-4 py-2 text-xs font-medium text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low transition-colors cursor-pointer" onclick="navigateParent('workspace')">
              <span class="material-symbols-outlined text-[18px]">grid_view</span>
              <span>Workspace Dashboard</span>
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
  <main class="w-full min-h-screen pt-20 pb-12 bg-surface px-8">
    <div class="max-w-7xl mx-auto flex flex-col w-full">

      <!-- Interactive Feedback Banner Notification -->
      <div class="fixed top-20 right-8 z-50 transform translate-y-[-20px] opacity-0 pointer-events-none transition-all duration-300 ease-out bg-surface-container-lowest shadow-xl rounded-xl p-4 flex items-center gap-3 border border-[#E4DFD6]" id="toastNotification">
        <div class="w-8 h-8 rounded-full bg-secondary/15 flex items-center justify-center text-secondary">
          <span class="material-symbols-outlined text-[18px]">check_circle</span>
        </div>
        <div class="flex flex-col">
          <span class="font-title-md text-body-sm text-on-surface" id="toastMessage">Invitation dispatched successfully</span>
          <span class="font-code-sm text-code-sm text-on-surface-variant">Access permissions provisioned for {project_name}</span>
        </div>
      </div>

      <!-- Quick Back to Projects Link & Live Status Bar -->
      <div class="flex items-center justify-between gap-4 mb-6 flex-wrap">
        <div class="flex items-center gap-2.5">
          <a class="inline-flex items-center gap-1.5 text-xs font-semibold text-primary-container hover:text-primary transition-colors py-1.5 px-3.5 rounded-full bg-primary-fixed/40 hover:bg-primary-fixed/70 cursor-pointer" onclick="navigateParent('workspace')">
            <span class="material-symbols-outlined text-[16px]">arrow_back</span>
            <span>Back to Projects</span>
          </a>
          <a class="inline-flex items-center gap-1.5 text-xs font-semibold text-on-surface-variant hover:text-on-surface hover:bg-surface-container transition-colors py-1.5 px-3.5 rounded-full bg-surface-container-low cursor-pointer border border-[#E4DFD6]" onclick="navigateParent('chapter-studio?project=' + encodeURIComponent('{project_name}'))" title="Proceed to Chapter Studio for this series">
            <span>Open Chapter Studio</span>
            <span class="material-symbols-outlined text-[15px]">arrow_forward</span>
          </a>
        </div>
        <div class="inline-flex items-center gap-2 px-3 py-1 bg-surface-container-low rounded-full border border-[#E4DFD6]/60">
          <span class="w-2 h-2 rounded-full bg-secondary animate-pulse"></span>
          <span class="font-code text-xs text-on-surface-variant">RBAC Sync: Enforced &amp; Active</span>
        </div>
      </div>

      <!-- Header Section: Title & Invite Button -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 class="font-headline text-3xl font-bold text-on-surface tracking-tight">Team Workspace &amp; Roles</h1>
          <p class="text-sm text-on-surface-variant mt-1 font-normal">
            Assign roles and permissions for project: <span class="text-on-surface font-semibold notranslate" translate="no">{project_name}</span>
          </p>
        </div>
        <button class="inline-flex items-center gap-2 h-11 px-6 rounded-full bg-primary text-on-primary text-sm font-semibold hover:bg-primary-container transition-all shadow-sm active:scale-95 cursor-pointer self-start sm:self-auto" onclick="document.getElementById('inviteInput').focus()">
          <span class="material-symbols-outlined text-[18px]">person_add</span>
          <span>+ Invite Member</span>
        </button>
      </div>

      <!-- 3 KPI METRIC CARDS (Bố cục 3 thẻ rời thoáng đãng chuẩn Demo) -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        
        <!-- Card 1: TOTAL MEMBERS -->
        <div class="bg-surface-container-lowest p-6 rounded-2xl shadow-sm border border-[#E4DFD6] hover:shadow-md hover:border-primary-container/40 transition-all cursor-pointer flex items-center justify-between group" onclick="scrollToMemberTable()" title="Scroll down to Member Roles Table">
          <div>
            <span class="font-code text-xs uppercase tracking-wider text-on-surface-variant font-semibold block mb-1 group-hover:text-primary-container transition-colors">TOTAL MEMBERS</span>
            <div class="flex items-baseline gap-2">
              <span id="memberCountLarge" class="font-headline text-3xl font-bold text-on-surface">3</span>
              <span class="inline-flex items-center gap-1 text-xs font-semibold text-[#137333] font-code">
                <span class="w-1.5 h-1.5 rounded-full bg-[#137333]"></span>
                <span>Active</span>
              </span>
            </div>
            <p class="text-xs text-on-surface-variant mt-1">Full editorial team assigned</p>
          </div>
          <div class="w-12 h-12 rounded-xl bg-[#F0F4F8] group-hover:bg-primary-container/10 transition-colors flex items-center justify-center text-primary-container">
            <span class="material-symbols-outlined text-[24px]">group</span>
          </div>
        </div>

        <!-- Card 2: ASSIGNED WORKLOAD -->
        <div class="bg-surface-container-lowest p-6 rounded-2xl shadow-sm border border-[#E4DFD6] hover:shadow-md hover:border-primary-container/40 transition-all cursor-pointer flex items-center justify-between group" onclick="navigateParent('chapter-studio?project=' + encodeURIComponent('{project_name}'))" title="Open Chapter Studio for this workload">
          <div class="flex-1 pr-4">
            <span class="font-code text-xs uppercase tracking-wider text-on-surface-variant font-semibold block mb-1 group-hover:text-primary-container transition-colors">ASSIGNED WORKLOAD</span>
            <div class="flex items-baseline gap-1.5">
              <span class="font-headline text-3xl font-bold text-on-surface">24 / 24</span>
              <span class="text-xs text-on-surface-variant font-medium">Pages</span>
            </div>
            <!-- Green Progress Bar (100% Assigned) -->
            <div class="w-full bg-[#E8EAED] rounded-full h-1.5 mt-2.5 overflow-hidden">
              <div class="bg-[#137333] h-1.5 rounded-full" style="width: 100%"></div>
            </div>
          </div>
          <div class="w-12 h-12 rounded-xl bg-[#E8F5E9] group-hover:bg-[#C8E6C9] transition-colors flex items-center justify-center text-[#137333] shrink-0">
            <span class="material-symbols-outlined text-[24px]">assignment_turned_in</span>
          </div>
        </div>

        <!-- Card 3: ACCESS LEVEL -->
        <div class="bg-surface-container-lowest p-6 rounded-2xl shadow-sm border border-[#E4DFD6] hover:shadow-md hover:border-primary-container/40 transition-all cursor-pointer flex items-center justify-between group" onclick="showToast('Security Verified: SOC2 Type II Ingestion Encrypted (TLS 1.3)')" title="View Security Details">
          <div>
            <span class="font-code text-xs uppercase tracking-wider text-on-surface-variant font-semibold block mb-1 group-hover:text-primary-container transition-colors">ACCESS LEVEL</span>
            <span class="font-headline text-lg font-bold text-on-surface block">Private Workspace</span>
            <div class="flex items-center gap-1.5 mt-1.5">
              <span class="px-2 py-0.5 rounded bg-surface-container font-code text-[11px] font-semibold text-on-surface-variant border border-[#E4DFD6]/60">SOC2 Ingestion</span>
              <span class="text-xs text-[#137333] font-medium">Encrypted</span>
            </div>
          </div>
          <div class="w-12 h-12 rounded-xl bg-[#F0F4F8] group-hover:bg-primary-container/10 transition-colors flex items-center justify-center text-primary-container">
            <span class="material-symbols-outlined text-[24px]">verified_user</span>
          </div>
        </div>

      </div>

      <!-- Quick Invite Form Bar -->
      <div class="bg-surface-container-lowest p-5 mb-8 rounded-2xl shadow-sm border border-[#E4DFD6]">
        <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <div class="flex items-center gap-2 text-on-surface pr-2 min-w-max">
            <span class="material-symbols-outlined text-primary-container text-[20px]">forward_to_inbox</span>
            <span class="text-sm text-on-surface font-bold">Quick Invite:</span>
          </div>
          <div class="flex-1 min-w-0">
            <input class="w-full h-11 px-4 bg-surface-container-low focus:bg-surface-container-lowest text-on-surface placeholder:text-outline text-sm rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-container/25 transition-all border border-[#E4DFD6]" id="inviteInput" placeholder="colleague@studio.com" type="email"/>
          </div>
          <div class="w-full sm:w-52">
            <div class="relative">
              <select class="w-full h-11 px-3 pr-8 bg-surface-container-low text-on-surface text-xs font-semibold rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-container/25 appearance-none cursor-pointer border border-[#E4DFD6]" id="roleSelect">
                <option value="Translator">Translator</option>
                <option value="Typesetter">Typesetter</option>
                <option value="Project Manager">Project Manager</option>
              </select>
              <span class="material-symbols-outlined absolute right-2.5 top-3 text-[18px] text-outline pointer-events-none">expand_more</span>
            </div>
          </div>
          <button class="h-11 px-6 rounded-full bg-primary hover:bg-primary-container text-on-primary text-xs font-semibold transition-all shadow-sm flex items-center justify-center gap-2 whitespace-nowrap active:scale-95 cursor-pointer" id="sendInviteBtn">
            <span class="material-symbols-outlined text-[16px]">send</span>
            <span>Send Invite</span>
          </button>
        </div>
      </div>

      <!-- Member Management Table Container -->
      <div class="bg-surface-container-lowest rounded-2xl shadow-sm overflow-hidden mb-8 border border-[#E4DFD6]">
        <!-- Table Header & 1-Click Role Filter Pills -->
        <div class="px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-container-low border-b border-[#E4DFD6]">
          <div class="flex items-center gap-2">
            <h3 class="font-headline text-base font-bold text-on-surface">Workspace Members</h3>
            <span id="memberCountBadge" class="w-5 h-5 rounded-full bg-surface-container-high text-on-surface-variant font-code text-xs flex items-center justify-center font-semibold">3</span>
          </div>
          
          <!-- 1-Click Fast Filtering Pills (Nghiệp vụ tiện lợi) -->
          <div class="flex items-center gap-2">
            <span class="font-code text-xs text-on-surface-variant">Filter:</span>
            <button onclick="filterMembers('all')" id="filter-all" class="px-3 py-1 rounded-full font-code text-xs bg-surface-container-lowest text-on-surface font-semibold shadow-xs border border-[#E4DFD6] cursor-pointer">All (3)</button>
            <button onclick="filterMembers('Translator')" id="filter-trans" class="px-3 py-1 rounded-full font-code text-xs text-on-surface-variant hover:text-on-surface hover:bg-surface-container-lowest transition-colors cursor-pointer">Translators (1)</button>
            <button onclick="filterMembers('Typesetter')" id="filter-type" class="px-3 py-1 rounded-full font-code text-xs text-on-surface-variant hover:text-on-surface hover:bg-surface-container-lowest transition-colors cursor-pointer">Typesetters (1)</button>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left table-fixed border-collapse">
            <thead>
              <tr class="bg-surface-container-low/60 text-on-surface font-headline text-xs uppercase tracking-wider border-b border-[#E4DFD6]">
                <th class="py-3.5 px-6 w-[35%]" scope="col">Member Name &amp; Email</th>
                <th class="py-3.5 px-6 w-[25%]" scope="col">Assigned Role</th>
                <th class="py-3.5 px-6 w-[22%]" scope="col">Active Tasks</th>
                <th class="py-3.5 px-6 w-[18%] text-right" scope="col">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-surface-container-high/40 text-sm" id="memberTableBody">
              
              <!-- Row 1: Project Manager (Owner) -->
              <tr class="member-row hover:bg-surface-container-low/40 transition-colors group" data-role="Project Manager">
                <td class="py-4 px-6">
                  <div class="flex items-center gap-3.5">
                    <div class="w-9 h-9 rounded-full bg-primary-container text-on-primary flex items-center justify-center font-bold text-xs shadow-xs notranslate" translate="no">
                      PN
                    </div>
                    <div class="flex flex-col min-w-0">
                      <div class="flex items-center gap-1.5">
                        <span class="font-semibold text-on-surface truncate notranslate" translate="no">Phan Nhat Huy</span>
                        <span class="material-symbols-outlined text-[15px] text-primary" title="Authenticated Project Lead">verified</span>
                      </div>
                      <span class="font-code text-xs text-on-surface-variant truncate notranslate" translate="no">nhathuyphan21@gmail.com</span>
                    </div>
                  </div>
                </td>
                <td class="py-4 px-6">
                  <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full font-code text-xs font-semibold bg-tertiary-fixed text-tertiary shadow-xs">
                    <span class="material-symbols-outlined text-[14px]">shield_person</span>
                    <span>Project Manager</span>
                  </span>
                </td>
                <td class="py-4 px-6">
                  <div class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-primary-container shrink-0"></span>
                    <span class="text-xs text-on-surface font-medium">Overall Supervision • 24 pages</span>
                  </div>
                </td>
                <td class="py-4 px-6 text-right">
                  <span class="inline-flex items-center px-3 py-1 rounded-full font-code text-xs bg-surface-container-high text-on-surface-variant font-medium cursor-not-allowed">
                    Owner
                  </span>
                </td>
              </tr>

              <!-- Row 2: Translator -->
              <tr class="member-row hover:bg-surface-container-low/40 transition-colors group" id="member-row-pq" data-role="Translator">
                <td class="py-4 px-6">
                  <div class="flex items-center gap-3.5">
                    <div class="w-9 h-9 rounded-full bg-secondary text-on-secondary flex items-center justify-center font-bold text-xs shadow-xs notranslate" translate="no">
                      PV
                    </div>
                    <div class="flex flex-col min-w-0">
                      <span class="font-semibold text-on-surface truncate notranslate" translate="no">Phan Van Quan</span>
                      <span class="font-code text-xs text-on-surface-variant truncate notranslate" translate="no">phanvanquann26@gmail.com</span>
                    </div>
                  </div>
                </td>
                <td class="py-4 px-6">
                  <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full font-code text-xs font-semibold bg-secondary-container text-on-secondary-container shadow-xs">
                    <span class="material-symbols-outlined text-[14px]">translate</span>
                    <span>Translator</span>
                  </span>
                </td>
                <td class="py-4 px-6">
                  <div class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-secondary shrink-0"></span>
                    <span class="text-xs text-on-surface font-medium">Reviewing Pages 1–12</span>
                  </div>
                </td>
                <td class="py-4 px-6 text-right">
                  <button class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-error text-xs font-semibold bg-error-container/30 hover:bg-error-container hover:text-on-error-container transition-all cursor-pointer border border-error/20" onclick="removeMember('member-row-pq', 'Phan Van Quan')">
                    <span class="material-symbols-outlined text-[13px]">person_remove</span>
                    <span>Remove</span>
                  </button>
                </td>
              </tr>

              <!-- Row 3: Typesetter -->
              <tr class="member-row hover:bg-surface-container-low/40 transition-colors group" id="member-row-th" data-role="Typesetter">
                <td class="py-4 px-6">
                  <div class="flex items-center gap-3.5">
                    <div class="w-9 h-9 rounded-full bg-tertiary-container text-on-primary flex items-center justify-center font-bold text-xs shadow-xs notranslate" translate="no">
                      PT
                    </div>
                    <div class="flex flex-col min-w-0">
                      <span class="font-semibold text-on-surface truncate notranslate" translate="no">Phan Thanh Hoang</span>
                      <span class="font-code text-xs text-on-surface-variant truncate notranslate" translate="no">phanhoang0705@gmail.com</span>
                    </div>
                  </div>
                </td>
                <td class="py-4 px-6">
                  <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full font-code text-xs font-semibold bg-surface-variant text-on-surface-variant shadow-xs">
                    <span class="material-symbols-outlined text-[14px]">format_paint</span>
                    <span>Typesetter</span>
                  </span>
                </td>
                <td class="py-4 px-6">
                  <div class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-tertiary shrink-0"></span>
                    <span class="text-xs text-on-surface font-medium">Typesetting Pages 13–24</span>
                  </div>
                </td>
                <td class="py-4 px-6 text-right">
                  <button class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-error text-xs font-semibold bg-error-container/30 hover:bg-error-container hover:text-on-error-container transition-all cursor-pointer border border-error/20" onclick="removeMember('member-row-th', 'Phan Thanh Hoang')">
                    <span class="material-symbols-outlined text-[13px]">person_remove</span>
                    <span>Remove</span>
                  </button>
                </td>
              </tr>

            </tbody>
          </table>
        </div>
      </div>

      <!-- Role Permissions Guide Card with Checklist Format (Xịn và dễ đọc) -->
      <div class="bg-surface-container-lowest rounded-2xl p-6 shadow-sm mb-6 border border-[#E4DFD6]">
        <div class="flex items-center justify-between pb-3 mb-6 border-b border-[#E4DFD6]">
          <div class="flex items-center gap-2.5">
            <span class="material-symbols-outlined text-primary-container text-[22px]">policy</span>
            <h3 class="font-headline text-base font-bold text-on-surface">Role Permissions Guide</h3>
          </div>
          <span class="font-code text-xs text-on-surface-variant bg-surface-container-high px-2.5 py-1 rounded-full border border-[#E4DFD6]/60">Security Scope: Project-Level Only</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          <!-- Project Manager Details -->
          <div class="flex flex-col bg-surface-container-low p-5 rounded-xl border border-[#E4DFD6]/60">
            <div class="flex items-center gap-2 mb-2">
              <span class="w-2.5 h-2.5 rounded-full bg-primary-container"></span>
              <h4 class="font-headline text-sm font-bold text-on-surface">Project Manager</h4>
            </div>
            <p class="text-xs text-on-surface-variant mb-4 leading-relaxed">
              Highest operational tier inside the project sandbox. Oversees localization deadlines and structural delivery.
            </p>
            <ul class="flex flex-col gap-2 text-xs text-on-surface mt-auto">
              <li class="flex items-start gap-2">
                <span class="material-symbols-outlined text-secondary text-[16px] mt-0.5">check</span>
                <span>Full project pipeline execution &amp; AI batch triggers</span>
              </li>
              <li class="flex items-start gap-2">
                <span class="material-symbols-outlined text-secondary text-[16px] mt-0.5">check</span>
                <span>Member invitations &amp; role privilege allocation</span>
              </li>
              <li class="flex items-start gap-2">
                <span class="material-symbols-outlined text-secondary text-[16px] mt-0.5">check</span>
                <span>Chapter uploads, page re-ordering &amp; PSD/ZIP exports</span>
              </li>
            </ul>
          </div>

          <!-- Translator Details -->
          <div class="flex flex-col bg-surface-container-low p-5 rounded-xl border border-[#E4DFD6]/60">
            <div class="flex items-center gap-2 mb-2">
              <span class="w-2.5 h-2.5 rounded-full bg-secondary"></span>
              <h4 class="font-headline text-sm font-bold text-on-surface">Translator</h4>
            </div>
            <p class="text-xs text-on-surface-variant mb-4 leading-relaxed">
              Dedicated linguist workspace. Focused on textual accuracy, reading direction nuances, and terminology consistency.
            </p>
            <ul class="flex flex-col gap-2 text-xs text-on-surface mt-auto">
              <li class="flex items-start gap-2">
                <span class="material-symbols-outlined text-secondary text-[16px] mt-0.5">check</span>
                <span>Full access to Review Studio &amp; Transcription stage</span>
              </li>
              <li class="flex items-start gap-2">
                <span class="material-symbols-outlined text-secondary text-[16px] mt-0.5">check</span>
                <span>Manga OCR correction &amp; character line assignment</span>
              </li>
              <li class="flex items-start gap-2">
                <span class="material-symbols-outlined text-secondary text-[16px] mt-0.5">check</span>
                <span>Project Glossary lookup &amp; auto-translation validation</span>
              </li>
            </ul>
          </div>

          <!-- Typesetter Details -->
          <div class="flex flex-col bg-surface-container-low p-5 rounded-xl border border-[#E4DFD6]/60">
            <div class="flex items-center gap-2 mb-2">
              <span class="w-2.5 h-2.5 rounded-full bg-tertiary"></span>
              <h4 class="font-headline text-sm font-bold text-on-surface">Typesetter</h4>
            </div>
            <p class="text-xs text-on-surface-variant mb-4 leading-relaxed">
              Visual craftsmanship tier. Manages letter spacing, balloon padding, SFX styling, and font typography pairings.
            </p>
            <ul class="flex flex-col gap-2 text-xs text-on-surface mt-auto">
              <li class="flex items-start gap-2">
                <span class="material-symbols-outlined text-secondary text-[16px] mt-0.5">check</span>
                <span>Full Live Typesetting Canvas interaction</span>
              </li>
              <li class="flex items-start gap-2">
                <span class="material-symbols-outlined text-secondary text-[16px] mt-0.5">check</span>
                <span>Font family adjustments &amp; CJK vertical text orientation</span>
              </li>
              <li class="flex items-start gap-2">
                <span class="material-symbols-outlined text-secondary text-[16px] mt-0.5">check</span>
                <span>Stroke outlines, drop shadow, and bubble boundary refinement</span>
              </li>
            </ul>
          </div>

        </div>
      </div>

      <!-- Activity Audit Stream Footnote -->
      <div class="flex flex-col sm:flex-row items-center justify-between gap-4 px-2 py-2 text-on-surface-variant font-code text-xs">
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-[16px]">history</span>
          <span>Last role modification: 14 minutes ago by <span class="notranslate" translate="no">nhathuyphan21@gmail.com</span></span>
        </div>
        <div class="flex items-center gap-4">
          <a class="hover:text-on-surface transition-colors flex items-center gap-1 cursor-pointer" onclick="downloadAuditLog()">
            <span>Download Audit Log (.CSV)</span>
            <span class="material-symbols-outlined text-[14px]">download</span>
          </a>
        </div>
      </div>

    </div>
  </main>
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

function scrollToMemberTable() {{
  const el = document.getElementById('memberTableBody');
  if (el) {{
    el.scrollIntoView({{ behavior: 'smooth' }});
  }}
}}

// Interactive Notification Dropdown Toggle
function toggleNotifDropdown(e) {{
  e.stopPropagation();
  const profileDropdown = document.getElementById('profile-dropdown');
  if (profileDropdown) profileDropdown.classList.add('hidden');
  const dropdown = document.getElementById('notif-dropdown');
  if (dropdown) {{
    dropdown.classList.toggle('hidden');
  }}
}}

// Interactive Profile Dropdown Toggle (Avatar + Chevron)
function toggleProfileDropdown(e) {{
  e.stopPropagation();
  const notifDropdown = document.getElementById('notif-dropdown');
  if (notifDropdown) notifDropdown.classList.add('hidden');
  const dropdown = document.getElementById('profile-dropdown');
  if (dropdown) {{
    dropdown.classList.toggle('hidden');
  }}
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

// 1-Click Role Filter Handler
function filterMembers(role) {{
  const rows = document.querySelectorAll('.member-row');
  rows.forEach(r => {{
    if (role === 'all' || r.getAttribute('data-role') === role) {{
      r.style.display = '';
    }} else {{
      r.style.display = 'none';
    }}
  }});

  // Update button active styling
  const btns = [
    {{ id: 'filter-all', match: role === 'all' }},
    {{ id: 'filter-trans', match: role === 'Translator' }},
    {{ id: 'filter-type', match: role === 'Typesetter' }}
  ];
  btns.forEach(b => {{
    const el = document.getElementById(b.id);
    if (el) {{
      if (b.match) {{
        el.className = 'px-3 py-1 rounded-full font-code text-xs bg-surface-container-lowest text-on-surface font-semibold shadow-xs border border-[#E4DFD6] cursor-pointer';
      }} else {{
        el.className = 'px-3 py-1 rounded-full font-code text-xs text-on-surface-variant hover:text-on-surface hover:bg-surface-container-lowest transition-colors cursor-pointer';
      }}
    }}
  }});
}}

function downloadAuditLog() {{
  const csvContent = "data:text/csv;charset=utf-8,Timestamp,Actor,Action,Target,Role\\n2026-10-17 11:30:00,nhathuyphan21@gmail.com,ROLE_UPDATE,phanvanquann26@gmail.com,Translator\\n2026-10-17 11:28:15,nhathuyphan21@gmail.com,ROLE_UPDATE,phanhoang0705@gmail.com,Typesetter";
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `ACL_Audit_Log_${{encodeURIComponent('{project_name}')}}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  showToast("Audit log CSV exported successfully");
}}

// Toast notification micro-interaction
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
  }}, 3500);
}}

// Quick Invite Handler
document.getElementById('sendInviteBtn')?.addEventListener('click', () => {{
  const emailInput = document.getElementById('inviteInput');
  const roleSelect = document.getElementById('roleSelect');
  
  if (!emailInput || !emailInput.value.trim() || !emailInput.checkValidity()) {{
    emailInput.focus();
    showToast('Please enter a valid email address');
    return;
  }}

  const email = emailInput.value.trim();
  const role = roleSelect.value;
  const initial = email.charAt(0).toUpperCase();

  const tbody = document.getElementById('memberTableBody');
  if (tbody) {{
    const tr = document.createElement('tr');
    const tempId = 'member-row-' + Date.now();
    tr.id = tempId;
    tr.className = 'member-row hover:bg-surface-container-low/40 transition-colors group animate-fadeIn';
    tr.setAttribute('data-role', role);
    
    let badgeStyle = '';
    let icon = '';
    if (role === 'Translator') {{
      badgeStyle = 'bg-secondary-container text-on-secondary-container';
      icon = 'translate';
    }} else if (role === 'Typesetter') {{
      badgeStyle = 'bg-surface-variant text-on-surface-variant';
      icon = 'format_paint';
    }} else {{
      badgeStyle = 'bg-tertiary-fixed text-tertiary';
      icon = 'shield_person';
    }}

    tr.innerHTML = `
      <td class="py-4 px-6">
        <div class="flex items-center gap-3.5">
          <div class="w-9 h-9 rounded-full bg-primary text-on-primary flex items-center justify-center font-bold text-xs shadow-xs notranslate" translate="no">
            ${{initial}}
          </div>
          <div class="flex flex-col min-w-0">
            <span class="font-semibold text-on-surface truncate notranslate" translate="no">${{email.split('@')[0]}}</span>
            <span class="font-code text-xs text-on-surface-variant truncate notranslate" translate="no">${{email}}</span>
          </div>
        </div>
      </td>
      <td class="py-4 px-6">
        <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full font-code text-xs font-semibold ${{badgeStyle}} shadow-xs">
          <span class="material-symbols-outlined text-[14px]">${{icon}}</span>
          ${{role}}
        </span>
      </td>
      <td class="py-4 px-6">
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-secondary shrink-0"></span>
          <span class="text-xs text-on-surface font-medium">Invitation Pending • Awaiting accept</span>
        </div>
      </td>
      <td class="py-4 px-6 text-right">
        <button onclick="removeMember('${{tempId}}', '${{email}}')" class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-error text-xs font-semibold bg-error-container/30 hover:bg-error-container hover:text-on-error-container transition-all cursor-pointer border border-error/20">
          <span class="material-symbols-outlined text-[13px]">person_remove</span>
          <span>Revoke</span>
        </button>
      </td>
    `;
    tbody.appendChild(tr);

    // Update member count badges
    const totalCount = tbody.querySelectorAll('.member-row').length;
    const badgeEl = document.getElementById('memberCountBadge');
    const largeEl = document.getElementById('memberCountLarge');
    if (badgeEl) badgeEl.textContent = totalCount;
    if (largeEl) largeEl.textContent = totalCount;
  }}

  showToast(`Invite dispatched to ${{email}} as ${{role}}`);
  emailInput.value = '';
}});

// Remove member action
function removeMember(rowId, name) {{
  const row = document.getElementById(rowId);
  if (row) {{
    row.style.opacity = '0';
    row.style.transform = 'translateX(20px)';
    row.style.transition = 'all 0.3s ease';
    setTimeout(() => {{
      row.remove();
      const tbody = document.getElementById('memberTableBody');
      const totalCount = tbody.querySelectorAll('.member-row').length;
      const badgeEl = document.getElementById('memberCountBadge');
      const largeEl = document.getElementById('memberCountLarge');
      if (badgeEl) badgeEl.textContent = totalCount;
      if (largeEl) largeEl.textContent = totalCount;
      showToast(`Revoked project permissions for ${{name}}`);
    }}, 300);
  }}
}}
</script>
</body>
</html>
"""

# Render the Google Stitch component seamlessly
components.html(team_workspace_html, height=1280, scrolling=True)
