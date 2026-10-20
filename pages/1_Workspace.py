"""ACL Project Workspace Dashboard (Series Grid) — Screen ACL-04.

Pixel-perfect implementation matching Google Stitch Project 'UX/UI_ACL' (ID: 15081338219515375601).
Screen: ACL-04: Project Workspace Dashboard (Series Grid) (ID: e059faed1a96475fa8505860a5b240bc).
Modal: ACL-04-MODAL: Create New Project Modal Overlay.
100% English UI Labels with interactive Notification Bell, Sidebar Logo A, and Demo Metric Layout.
"""

import base64
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from utils.auth_session import require_auth


# Enforce route guard
user = require_auth()

# Paths to local assets
BASE_DIR = Path(__file__).parents[1]
THUMBNAILS_DIR = BASE_DIR / "assets" / "thumbnails"


def _read_b64(path: Path) -> str:
    if path.exists():
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        ext = path.suffix.lstrip(".").lower()
        mime = "jpeg" if ext in ("jpg", "jpeg") else ext
        return f"data:image/{mime};base64,{encoded}"
    return ""


# Load local thumbnail images
img_shonen = _read_b64(THUMBNAILS_DIR / "shonen_112.jpg")
img_one_piece = _read_b64(THUMBNAILS_DIR / "one_piece_1115.jpg")
img_jjk = _read_b64(THUMBNAILS_DIR / "jujutsu_kaisen_sp.jpg")

# Fallback hosted URLs if local images are empty
if not img_shonen:
    img_shonen = "https://lh3.googleusercontent.com/aida-public/AB6AXuCouWYpEluHUOsa8793_1pcc3bsFHUelQ4VxCMtSF-0TotamM87oa9GpM5U_koXaAbfzpsT4QTcjhDNh0ZBgk4_BPkVEBon5UzMYYeyaDOTXqPB8WotRTPUogbpkUfuW1BBPNcVHTEgOY-FNrXHO97tLEsYnxYhJbVrLf8Y4nwRYYTv6dEl-B9mG-unhw7qYfZe44h4AWtCQmLqU9Ts2CslWdhdDxVbe3sJ6uKJAg77NTRr4SE6t9_8JQ"
if not img_one_piece:
    img_one_piece = "https://lh3.googleusercontent.com/aida-public/AB6AXuAYm_zWj8CDD3H367j852PD0RIUl7QIqhlqTrORUeZxFT3KHo7ii4hC1lk7SyYEcth_3DSWFpyQFJHI23DLbMUiUmrkU72abnzio3966PXWOs-lbD3RS1JcEdx-Xy7QWt1lVs8QfNyP3YPIo3lMBF_PRoGxqZb1G53j3_pBOLq7g1RafiPGbV5tROMV-nSvQhOX7d2ye69mDBiutBo7z_2O_7mKUBn5oHmIScEgdFDZQ18mcmYMegizsQ"
if not img_jjk:
    img_jjk = "https://lh3.googleusercontent.com/aida-public/AB6AXuD26WWqUxM5U3gasZ3VVyzBw7c2ZLb-bGuLvNUPocDFE1RIRxkwlueSU_use8VJFYZF5iLET0WzsB_ocHyMO9usznzDCro5-qRYZtihAuD2EPhqUjglOhsrwQHSbLDT9oEiuGiT1JnfudhvYrTztpFhxWuwVXLCIrOMZF6PYReXyG7qtt9ciy3v1U62DxuwLuxKQdaIGOrDroZuPIZfE0uIDUAj_6LJaikByPfjKj3cz_whPC_neRkUCA"

user_initials = (user.full_name[:2] if user.full_name else "PH").upper()
user_name = user.full_name or "Phan Van Quan"

workspace_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<meta content="web_dashboard" name="shell-type"/>
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<!-- Comprehensive Google Fonts import with explicit Vietnamese & Latin-Ext subsets -->
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
/* Reset font inheritance during Google Translate */
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

<!-- FIXED LEFT SIDEBAR (Mục 1 & Mục 2) -->
<aside class="fixed left-0 top-0 h-full w-[220px] bg-surface-container-lowest z-50 flex flex-col justify-between py-5 border-r border-[#E4DFD6]">
  <div>
    <!-- Brand / Logo Area: Square Badge with 'A' (Mục 1) -->
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

  <!-- Sidebar Footer: Documentation & Core Online (Mục 2) -->
  <div class="px-5 pt-3 border-t border-[#E4DFD6] flex flex-col gap-2.5">
    <a class="flex items-center gap-2 text-on-surface-variant hover:text-on-surface text-xs font-medium cursor-pointer transition-colors" onclick="alert('ACL Documentation v2.4: System guides, Manga-OCR pipelines, and API specs.')">
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

  <!-- TOP HEADER BAR (Mục 3 + Chuông Thông Báo Đỏ) -->
  <header class="fixed top-0 left-[220px] right-0 h-16 bg-surface-container-lowest/95 backdrop-blur-md z-40 px-8 flex items-center justify-between border-b border-[#E4DFD6]">
    
    <!-- Left: ACL Studio / Projects Breadcrumb (Mục 3) -->
    <div class="flex items-center gap-2">
      <span class="text-base font-bold text-on-surface">ACL Studio</span>
      <span class="text-outline-variant font-light text-sm">/</span>
      <span class="text-sm text-on-surface-variant font-medium">Projects</span>
    </div>

    <!-- Center/Right Header Controls -->
    <div class="flex items-center gap-4">
      
      <!-- Search Input (Filter batches or series...) -->
      <div class="hidden md:flex items-center bg-surface-container-low rounded-full px-3.5 py-1.5 border border-[#E4DFD6]">
        <span class="material-symbols-outlined text-[18px] text-on-surface-variant mr-1.5">search</span>
        <input id="header-search-input" class="bg-transparent text-xs outline-none placeholder:text-on-surface-variant w-44 text-on-surface" placeholder="Filter batches or series..." type="text"/>
      </div>

      <!-- Node Tokyo-01 (GPU idle) Pill Badge (Mục 3) -->
      <a onclick="navigateParent('queue-monitor')" class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#E8EDF4] hover:bg-[#D8E2EE] text-[#414754] hover:text-[#191C19] border border-[#D0D7DE] font-code text-xs font-medium cursor-pointer transition-colors" title="View GPU Cluster Queue on Node Tokyo-01">
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
            <div class="p-3 hover:bg-surface-container-low transition-colors cursor-pointer" onclick="navigateParent('review-studio')">
              <div class="flex items-start gap-2.5">
                <span class="notif-dot w-2 h-2 rounded-full bg-[#DC2626] mt-1.5 shrink-0"></span>
                <div>
                  <p class="text-xs font-semibold text-on-surface">Batch #CH-112-RAW Ready</p>
                  <p class="text-[11px] text-on-surface-variant mt-0.5">Manga-OCR extraction completed. 18/24 pages reviewed.</p>
                  <span class="font-code text-[10px] text-outline mt-1 block">2 mins ago</span>
                </div>
              </div>
            </div>
            <div class="p-3 hover:bg-surface-container-low transition-colors cursor-pointer" onclick="navigateParent('queue-monitor')">
              <div class="flex items-start gap-2.5">
                <span class="notif-dot w-2 h-2 rounded-full bg-[#DC2626] mt-1.5 shrink-0"></span>
                <div>
                  <p class="text-xs font-semibold text-on-surface">Node Tokyo-01 Idle</p>
                  <p class="text-[11px] text-on-surface-variant mt-0.5">GPU cluster ready for dispatching new inpainting batch.</p>
                  <span class="font-code text-[10px] text-outline mt-1 block">15 mins ago</span>
                </div>
              </div>
            </div>
            <div class="p-3 hover:bg-surface-container-low transition-colors cursor-pointer" onclick="navigateParent('team-roles')">
              <div class="flex items-start gap-2.5">
                <span class="notif-dot w-2 h-2 rounded-full bg-[#DC2626] mt-1.5 shrink-0"></span>
                <div>
                  <p class="text-xs font-semibold text-on-surface">Team Role Accepted</p>
                  <p class="text-[11px] text-on-surface-variant mt-0.5">Tran Ha (TH) joined as Japanese Translator.</p>
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

      <!-- Filter / Slider Icon -->
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
            <a class="flex items-center gap-2.5 px-4 py-2 text-xs font-medium text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low transition-colors cursor-pointer" onclick="navigateParent('team-roles')">
              <span class="material-symbols-outlined text-[18px]">groups</span>
              <span>Team Workspace</span>
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
    <div id="main-content-wrap" class="max-w-7xl mx-auto flex flex-col w-full transition-all duration-200">
      
      <!-- Page Title & Create Project Button Row -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 class="font-headline text-3xl font-bold text-on-surface tracking-tight">Projects</h1>
          <p class="text-sm text-on-surface-variant mt-1 font-normal">
            Manage your ongoing comic localization series and translation pipelines.
          </p>
        </div>
        <button id="create-project-btn" class="inline-flex items-center gap-2 h-11 px-6 rounded-full bg-primary text-on-primary text-sm font-semibold hover:bg-primary-container transition-all shadow-sm active:scale-95 cursor-pointer self-start sm:self-auto" type="button">
          <span class="material-symbols-outlined text-[20px]">add</span>
          <span>Create New Project</span>
        </button>
      </div>

      <!-- SECTION 1: 3 PROJECT CARDS (Mục 4, 5, 6 - Placed at Top like Demo) -->
      <div id="projects-grid" class="grid grid-cols-1 md:grid-cols-3 gap-6">

        <!-- Card 1: Shonen Weekly #112 -->
        <div class="project-card bg-surface-container-lowest rounded-2xl p-6 border border-[#E4DFD6] shadow-sm hover:shadow-md transition-all flex flex-col justify-between min-h-[270px]" data-title="shonen weekly #112 japanese vietnamese in review">
          <div>
            <!-- Header with Title & Circular Badge (01) (Mục 4) -->
            <div class="flex items-center justify-between mb-1">
              <h3 class="font-headline text-lg font-bold text-on-surface">Shonen Weekly #112</h3>
              <span class="w-6 h-6 rounded-full border border-[#C4C7C5] text-xs text-[#5A5E62] flex items-center justify-center font-medium font-code">01</span>
            </div>
            <!-- Subtitle with English -> Vietnamese Format (Mục 6) -->
            <p class="text-xs text-on-surface-variant font-medium">24 pages • Japanese -&gt; Vietnamese</p>

            <!-- Status Pill Badge -->
            <div class="mt-3">
              <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#E6F4EA] text-[#137333] font-code text-xs font-semibold">
                <span class="w-1.5 h-1.5 rounded-full bg-[#137333]"></span>
                <span>In review</span>
              </span>
            </div>

            <!-- Progress Track (75%) -->
            <div class="mt-5">
              <div class="flex justify-between items-center text-xs text-on-surface-variant font-medium mb-1.5">
                <span>Progress: 18/24 Pages Reviewed</span>
                <span class="font-semibold text-on-surface">75%</span>
              </div>
              <div class="w-full bg-[#E8EAED] rounded-full h-1.5 overflow-hidden">
                <div class="bg-primary-container h-1.5 rounded-full" style="width: 75%"></div>
              </div>
            </div>
          </div>

          <!-- Footer with Avatars + '+2 trans' (Mục 5) & Action Link -->
          <div class="mt-6 pt-4 border-t border-[#E4DFD6]/60 flex items-center justify-between">
            <div class="flex items-center cursor-pointer group/team p-1 -m-1 rounded-lg hover:bg-surface-container-low transition-colors" onclick="navigateParent('team-roles?project=Shonen+Weekly+%23112')" title="Manage team roles & permissions for Shonen Weekly #112">
              <div class="flex items-center -space-x-1.5">
                <div class="w-7 h-7 rounded-full bg-[#D4E9D7] text-[#1E5A2A] border-2 border-white flex items-center justify-center font-code text-[11px] font-bold" title="Minh Hoang (Typesetter)">MH</div>
                <div class="w-7 h-7 rounded-full bg-[#E5D9F2] text-[#4D2C7A] border-2 border-white flex items-center justify-center font-code text-[11px] font-bold" title="Tran Ha (Translator)">TH</div>
                <div class="w-7 h-7 rounded-full bg-[#D6E4FF] text-[#1D39C4] border-2 border-white flex items-center justify-center font-code text-[11px] font-bold" title="Quoc Nam (Lead Editor)">QN</div>
              </div>
              <!-- Text +2 trans (Mục 5) -->
              <span class="text-xs text-on-surface-variant font-medium ml-2 group-hover/team:text-primary-container transition-colors">+2 trans</span>
              <span class="material-symbols-outlined text-[15px] text-on-surface-variant ml-1 opacity-70 group-hover/team:opacity-100 group-hover/team:text-primary-container transition-all" title="Team Workspace">groups</span>
            </div>
            
            <a class="inline-flex items-center gap-1 text-xs font-semibold text-primary-container hover:underline cursor-pointer group" onclick="navigateParent('chapter-studio?project=Shonen+Weekly+%23112')">
              <span>Open Chapter Studio</span>
              <span class="material-symbols-outlined text-[16px] group-hover:translate-x-0.5 transition-transform">arrow_forward</span>
            </a>
          </div>
        </div>

        <!-- Card 2: One Piece — Chapter 1115 -->
        <div class="project-card bg-surface-container-lowest rounded-2xl p-6 border border-[#E4DFD6] shadow-sm hover:shadow-md transition-all flex flex-col justify-between min-h-[270px]" data-title="one piece chapter 1115 japanese vietnamese inpainting">
          <div>
            <!-- Header with Title & Circular Badge (02) (Mục 4) -->
            <div class="flex items-center justify-between mb-1">
              <h3 class="font-headline text-lg font-bold text-on-surface">One Piece — Chapter 1115</h3>
              <span class="w-6 h-6 rounded-full border border-[#C4C7C5] text-xs text-[#5A5E62] flex items-center justify-center font-medium font-code">02</span>
            </div>
            <!-- Subtitle with English -> Vietnamese Format (Mục 6) -->
            <p class="text-xs text-on-surface-variant font-medium">19 pages • Japanese -&gt; Vietnamese</p>

            <!-- Status Pill Badge -->
            <div class="mt-3">
              <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#EDE7F6] text-[#5E35B1] font-code text-xs font-semibold">
                <span class="material-symbols-outlined text-[14px]">water_drop</span>
                <span>Inpainting</span>
              </span>
            </div>

            <!-- Progress Track (68%) -->
            <div class="mt-5">
              <div class="flex justify-between items-center text-xs text-on-surface-variant font-medium mb-1.5">
                <span>Progress: 14/19 Pages Processed</span>
                <span class="font-semibold text-on-surface">68%</span>
              </div>
              <div class="w-full bg-[#E8EAED] rounded-full h-1.5 overflow-hidden">
                <div class="bg-primary-container h-1.5 rounded-full" style="width: 68%"></div>
              </div>
            </div>
          </div>

          <!-- Footer with Avatars & Action Link -->
          <div class="mt-6 pt-4 border-t border-[#E4DFD6]/60 flex items-center justify-between">
            <div class="flex items-center cursor-pointer group/team p-1 -m-1 rounded-lg hover:bg-surface-container-low transition-colors" onclick="navigateParent('team-roles?project=One+Piece+-+Chapter+1115')" title="Manage team roles & permissions for One Piece — Chapter 1115">
              <div class="flex items-center -space-x-1.5">
                <div class="w-7 h-7 rounded-full bg-[#D4E9D7] text-[#1E5A2A] border-2 border-white flex items-center justify-center font-code text-[11px] font-bold" title="Linh Huong">LH</div>
                <div class="w-7 h-7 rounded-full bg-primary-container text-on-primary border-2 border-white flex items-center justify-center font-code text-[11px] font-bold" title="Phuc Hai">PH</div>
              </div>
              <span class="material-symbols-outlined text-[15px] text-on-surface-variant ml-1.5 opacity-70 group-hover/team:opacity-100 group-hover/team:text-primary-container transition-all" title="Team Workspace">groups</span>
            </div>
            
            <a class="inline-flex items-center gap-1 text-xs font-semibold text-primary-container hover:underline cursor-pointer group" onclick="navigateParent('queue-monitor?project=One+Piece+-+Chapter+1115')">
              <span>View Queue</span>
              <span class="material-symbols-outlined text-[16px] group-hover:translate-x-0.5 transition-transform">arrow_forward</span>
            </a>
          </div>
        </div>

        <!-- Card 3: Jujutsu Kaisen — Special -->
        <div class="project-card bg-surface-container-lowest rounded-2xl p-6 border border-[#E4DFD6] shadow-sm hover:shadow-md transition-all flex flex-col justify-between min-h-[270px]" data-title="jujutsu kaisen special english vietnamese completed">
          <div>
            <!-- Header with Title & Circular Badge (03) (Mục 4) -->
            <div class="flex items-center justify-between mb-1">
              <h3 class="font-headline text-lg font-bold text-on-surface">Jujutsu Kaisen — Special</h3>
              <span class="w-6 h-6 rounded-full border border-[#C4C7C5] text-xs text-[#5A5E62] flex items-center justify-center font-medium font-code">03</span>
            </div>
            <!-- Subtitle with English -> Vietnamese Format (Mục 6) -->
            <p class="text-xs text-on-surface-variant font-medium">32 pages • English -&gt; Vietnamese</p>

            <!-- Status Pill Badge -->
            <div class="mt-3">
              <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#E6F4EA] text-[#137333] font-code text-xs font-semibold">
                <span class="material-symbols-outlined text-[14px]">check_circle</span>
                <span>Completed</span>
              </span>
            </div>

            <!-- Progress Track (100%) -->
            <div class="mt-5">
              <div class="flex justify-between items-center text-xs text-on-surface-variant font-medium mb-1.5">
                <span>Progress: 32/32 Pages Complete</span>
                <span class="font-semibold text-on-surface">100%</span>
              </div>
              <div class="w-full bg-[#E8EAED] rounded-full h-1.5 overflow-hidden">
                <div class="bg-[#137333] h-1.5 rounded-full" style="width: 100%"></div>
              </div>
            </div>
          </div>

          <!-- Footer with Avatars & Download ZIP Link -->
          <div class="mt-6 pt-4 border-t border-[#E4DFD6]/60 flex items-center justify-between">
            <div class="flex items-center cursor-pointer group/team p-1 -m-1 rounded-lg hover:bg-surface-container-low transition-colors" onclick="navigateParent('team-roles?project=Jujutsu+Kaisen+-+Special')" title="Manage team roles & permissions for Jujutsu Kaisen — Special">
              <div class="flex items-center -space-x-1.5">
                <div class="w-7 h-7 rounded-full bg-[#D4E9D7] text-[#1E5A2A] border-2 border-white flex items-center justify-center font-code text-[11px] font-bold" title="Minh Hoang">MH</div>
                <div class="w-7 h-7 rounded-full bg-[#E8F5E9] text-[#2E7D32] border-2 border-white flex items-center justify-center font-code text-[11px] font-bold" title="Linh Huong">LH</div>
                <div class="w-7 h-7 rounded-full bg-[#E5D9F2] text-[#4D2C7A] border-2 border-white flex items-center justify-center font-code text-[11px] font-bold" title="Tran Ha">TH</div>
                <div class="w-7 h-7 rounded-full bg-primary-container text-on-primary border-2 border-white flex items-center justify-center font-code text-[11px] font-bold" title="Phuc Hai">PH</div>
              </div>
              <span class="material-symbols-outlined text-[15px] text-on-surface-variant ml-1.5 opacity-70 group-hover/team:opacity-100 group-hover/team:text-primary-container transition-all" title="Team Workspace">groups</span>
            </div>
            
            <a class="inline-flex items-center gap-1 text-xs font-semibold text-[#137333] hover:underline cursor-pointer group" onclick="downloadSampleZip('Jujutsu_Kaisen_Special_Vietnamese.zip')">
              <span>Download ZIP</span>
              <span class="material-symbols-outlined text-[16px]">download</span>
            </a>
          </div>
        </div>

      </div>

      <!-- SECTION 2: 3 STATS METRIC CARDS (Mục 7 - Placed Below Projects like Demo) -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">

        <!-- Stat 1: Active Projects -->
        <div class="bg-surface-container-lowest rounded-2xl p-6 border border-[#E4DFD6] shadow-sm hover:shadow-md hover:border-primary-container/40 transition-all cursor-pointer flex items-center justify-between group" onclick="scrollToProjects()" title="Jump to Active Projects">
          <div>
            <span class="text-xs font-medium text-on-surface-variant block mb-1 group-hover:text-primary-container transition-colors">Active Projects</span>
            <div class="flex items-baseline gap-2">
              <span class="text-3xl font-bold text-on-surface font-headline">3</span>
              <span class="text-xs font-semibold text-[#137333] font-code">+1 this week</span>
            </div>
          </div>
          <div class="w-12 h-12 rounded-xl bg-[#F0F4F8] group-hover:bg-primary-container/10 transition-colors flex items-center justify-center text-on-surface-variant group-hover:text-primary-container">
            <span class="material-symbols-outlined text-[24px] text-[#414754] group-hover:text-primary-container transition-colors">folder</span>
          </div>
        </div>

        <!-- Stat 2: In Queue -->
        <div class="bg-surface-container-lowest rounded-2xl p-6 border border-[#E4DFD6] shadow-sm hover:shadow-md hover:border-primary-container/40 transition-all cursor-pointer flex items-center justify-between group" onclick="navigateParent('queue-monitor')" title="Open Queue Monitor for pending OCR tasks">
          <div>
            <span class="text-xs font-medium text-on-surface-variant block mb-1 group-hover:text-primary-container transition-colors">In Queue</span>
            <div class="flex items-baseline gap-2">
              <span class="text-3xl font-bold text-on-surface font-headline">19</span>
              <span class="text-xs text-on-surface-variant font-code">pages pending OCR</span>
            </div>
          </div>
          <div class="w-12 h-12 rounded-xl bg-[#F0F4F8] group-hover:bg-primary-container/10 transition-colors flex items-center justify-center text-on-surface-variant group-hover:text-primary-container">
            <span class="material-symbols-outlined text-[24px] text-[#414754] group-hover:text-primary-container transition-colors">hourglass_empty</span>
          </div>
        </div>

        <!-- Stat 3: Storage Allocation -->
        <div class="bg-surface-container-lowest rounded-2xl p-6 border border-[#E4DFD6] shadow-sm hover:shadow-md hover:border-primary-container/40 transition-all cursor-pointer flex items-center justify-between group" onclick="navigateParent('settings')" title="Manage storage and workspace settings">
          <div>
            <span class="text-xs font-medium text-on-surface-variant block mb-1 group-hover:text-primary-container transition-colors">Storage Allocation</span>
            <div class="flex items-baseline gap-2">
              <span class="text-3xl font-bold text-on-surface font-headline">1.2 GB</span>
              <span class="text-xs text-on-surface-variant font-code">/ 10 GB (12%)</span>
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

<!-- MODAL OVERLAY: [ACL-04-MODAL] Create New Project Modal -->
<div id="create-project-modal" class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/45 backdrop-blur-sm transition-all duration-200 opacity-0 pointer-events-none">
  <!-- Modal Card Container -->
  <div class="bg-surface-container-lowest w-full max-w-[520px] rounded-2xl shadow-2xl p-6 sm:p-8 flex flex-col relative transition-transform transform scale-95 border border-[#E4DFD6]">
    <!-- Modal Header -->
    <div class="flex items-start justify-between">
      <div>
        <div class="flex items-center gap-2 mb-1">
          <span class="w-2 h-2 rounded-full bg-primary-container"></span>
          <span class="font-code text-xs uppercase tracking-wider text-on-surface-variant font-semibold">New Workspace Entity</span>
        </div>
        <h2 class="font-headline text-2xl font-bold text-on-surface tracking-tight">Create New Project</h2>
      </div>
      <!-- Close Button -->
      <button id="modal-close-x" aria-label="Close dialog" class="w-9 h-9 rounded-full bg-surface-container flex items-center justify-center text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-colors cursor-pointer" type="button">
        <span class="material-symbols-outlined text-[20px]">close</span>
      </button>
    </div>
    
    <p class="text-sm text-on-surface-variant mt-1.5 mb-6">
      Set up a new comic series or chapter bundle for your localization team.
    </p>

    <!-- Form Fields Stack -->
    <form id="create-project-form" class="flex flex-col gap-[18px]">
      <!-- Field 1: Project / Series Name -->
      <div class="flex flex-col">
        <label class="text-xs font-semibold text-on-surface mb-1.5 flex items-center justify-between" for="series-name">
          <span>Project / Series Name</span>
          <span class="font-code text-xs text-on-surface-variant font-normal">Required</span>
        </label>
        <input id="series-name" class="w-full h-[44px] px-3.5 bg-surface-container-low text-on-surface text-sm rounded-lg placeholder:text-outline focus:bg-surface-container-lowest focus:outline-none focus:ring-2 focus:ring-primary-container/25 transition-all border border-[#E4DFD6]" placeholder="e.g. Shonen Weekly #112" required type="text"/>
      </div>

      <!-- Field 2: Description -->
      <div class="flex flex-col">
        <label class="text-xs font-semibold text-on-surface mb-1.5 flex items-center justify-between" for="series-desc">
          <span>Description</span>
          <span class="font-code text-xs text-on-surface-variant font-normal">Optional</span>
        </label>
        <textarea id="series-desc" class="w-full h-[90px] p-3 bg-surface-container-low text-on-surface text-sm rounded-lg resize-none placeholder:text-outline focus:bg-surface-container-lowest focus:outline-none focus:ring-2 focus:ring-primary-container/25 transition-all border border-[#E4DFD6]" placeholder="Enter chapter notes, release target date, or source notes..." rows="3"></textarea>
      </div>

      <!-- Field 3: Language Pair Selection -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <!-- Source Language -->
        <div class="flex flex-col">
          <label class="text-xs font-semibold text-on-surface mb-1.5 block">Source Language</label>
          <select id="source-lang-select" class="w-full h-[44px] px-3 rounded-lg bg-surface-container-low text-on-surface text-sm border border-[#E4DFD6] focus:outline-none focus:ring-2 focus:ring-primary-container/25">
            <option value="JA">Japanese (Raw Manga)</option>
            <option value="EN">English (Scanlation)</option>
            <option value="KO">Korean (Webtoon)</option>
          </select>
          <span class="font-code text-[11px] text-on-surface-variant mt-1">JA OCR / Vertical Layout</span>
        </div>
        <!-- Target Language -->
        <div class="flex flex-col">
          <label class="text-xs font-semibold text-on-surface mb-1.5 block">Target Language</label>
          <select id="target-lang-select" class="w-full h-[44px] px-3 rounded-lg bg-surface-container-low text-on-surface text-sm border border-[#E4DFD6] focus:outline-none focus:ring-2 focus:ring-primary-container/25">
            <option value="VI" selected>Vietnamese</option>
            <option value="EN">English</option>
          </select>
          <span class="font-code text-[11px] text-on-surface-variant mt-1">Latin Diacritics Engine</span>
        </div>
      </div>

      <!-- Translation Preset Pill Indicator -->
      <div class="bg-surface-container p-3 rounded-lg flex items-center justify-between border border-[#E4DFD6]/60">
        <div class="flex items-center gap-2.5">
          <span class="material-symbols-outlined text-primary-container text-[20px]">tune</span>
          <div class="flex flex-col">
            <span class="text-xs text-on-surface font-semibold">Pipeline Preset: Manga Standard</span>
            <span class="font-code text-[11px] text-on-surface-variant">Auto-segmentation • Inpainting GAN v2 • SFX preservation</span>
          </div>
        </div>
        <span class="font-code text-xs text-secondary bg-secondary-container/60 px-2 py-0.5 rounded-full font-medium">Default</span>
      </div>

      <!-- Modal Footer Action Buttons -->
      <div class="flex items-center justify-end gap-3 mt-4 pt-4 border-t border-[#E4DFD6]">
        <button id="modal-cancel-btn" class="px-6 h-[42px] rounded-full bg-surface-container hover:bg-surface-container-high text-on-surface text-sm font-semibold transition-colors cursor-pointer" type="button">
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
// Parent navigation bridge for seamless Streamlit router interaction
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

function scrollToProjects() {{
  const el = document.getElementById('projects-grid');
  if (el) {{
    el.scrollIntoView({{ behavior: 'smooth' }});
  }}
}}

function downloadSampleZip(filename) {{
  const blob = new Blob(["ACL Localized Comic Export Bundle Placeholder"], {{ type: 'application/zip' }});
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}}

// Interactive Notification Dropdown Toggle (Yêu cầu thông báo)
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

// Close dropdowns when clicking outside
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

// Modal controls (ACL-04-MODAL)
const modal = document.getElementById('create-project-modal');
const modalBox = modal.querySelector('div');
const createBtn = document.getElementById('create-project-btn');
const closeX = document.getElementById('modal-close-x');
const cancelBtn = document.getElementById('modal-cancel-btn');
const form = document.getElementById('create-project-form');
const nameInput = document.getElementById('series-name');
const mainWrap = document.getElementById('main-content-wrap');

function showModal() {{
  modal.classList.remove('opacity-0', 'pointer-events-none');
  modalBox.classList.remove('scale-95');
  modalBox.classList.add('scale-100');
  if (mainWrap) {{
    mainWrap.classList.add('opacity-90', 'blur-[1px]', 'filter');
  }}
  setTimeout(() => {{ if (nameInput) nameInput.focus(); }}, 100);
}}

function dismissModal() {{
  modal.classList.add('opacity-0', 'pointer-events-none');
  modalBox.classList.add('scale-95');
  modalBox.classList.remove('scale-100');
  if (mainWrap) {{
    mainWrap.classList.remove('opacity-90', 'blur-[1px]', 'filter');
  }}
}}

if (createBtn) createBtn.addEventListener('click', showModal);
if (closeX) closeX.addEventListener('click', dismissModal);
if (cancelBtn) cancelBtn.addEventListener('click', dismissModal);

modal.addEventListener('click', (e) => {{
  if (e.target === modal) dismissModal();
}});

window.addEventListener('keydown', (e) => {{
  if (e.key === 'Escape' && !modal.classList.contains('opacity-0')) dismissModal();
}});

if (form) {{
  form.addEventListener('submit', (e) => {{
    e.preventDefault();
    const title = nameInput.value.trim();
    if (!title) return;
    
    const submitBtn = document.getElementById('modal-submit-btn');
    submitBtn.innerHTML = '<span class="material-symbols-outlined text-[18px] animate-spin">progress_activity</span><span>Creating Series...</span>';
    submitBtn.disabled = true;

    setTimeout(() => {{
      const grid = document.getElementById('projects-grid');
      const count = grid.children.length + 1;
      const numStr = count < 10 ? '0' + count : '' + count;
      const newCard = document.createElement('div');
      newCard.className = 'project-card bg-surface-container-lowest rounded-2xl p-6 border border-[#E4DFD6] shadow-sm hover:shadow-md transition-all flex flex-col justify-between min-h-[270px]';
      newCard.setAttribute('data-title', title.toLowerCase());
      newCard.innerHTML = `
        <div>
          <div class="flex items-center justify-between mb-1">
            <h3 class="font-headline text-lg font-bold text-on-surface">${{title}}</h3>
            <span class="w-6 h-6 rounded-full border border-[#C4C7C5] text-xs text-[#5A5E62] flex items-center justify-center font-medium font-code">${{numStr}}</span>
          </div>
          <p class="text-xs text-on-surface-variant font-medium">0 pages • Japanese -&gt; Vietnamese</p>
          <div class="mt-3">
            <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#E6F4EA] text-[#137333] font-code text-xs font-semibold">
              <span class="w-1.5 h-1.5 rounded-full bg-[#137333]"></span>
              <span>In review</span>
            </span>
          </div>
          <div class="mt-5">
            <div class="flex justify-between items-center text-xs text-on-surface-variant font-medium mb-1.5">
              <span>Progress: Ready for Upload</span>
              <span class="font-semibold text-on-surface">0%</span>
            </div>
            <div class="w-full bg-[#E8EAED] rounded-full h-1.5 overflow-hidden">
              <div class="bg-primary-container h-1.5 rounded-full" style="width: 5%"></div>
            </div>
          </div>
        </div>
        <div class="mt-6 pt-4 border-t border-[#E4DFD6]/60 flex items-center justify-between">
          <div class="flex items-center cursor-pointer group/team p-1 -m-1 rounded-lg hover:bg-surface-container-low transition-colors" onclick="navigateParent('team-roles?project=' + encodeURIComponent('${{title}}'))" title="Manage team roles & permissions for ${{title}}">
            <div class="w-7 h-7 rounded-full bg-primary-container text-on-primary border-2 border-white flex items-center justify-center font-code text-[11px] font-bold" title="{user_name}">{user_initials}</div>
            <span class="material-symbols-outlined text-[15px] text-on-surface-variant ml-1.5 opacity-70 group-hover/team:opacity-100 group-hover/team:text-primary-container transition-all" title="Team Workspace">groups</span>
          </div>
          <a class="inline-flex items-center gap-1 text-xs font-semibold text-primary-container hover:underline cursor-pointer group" onclick="navigateParent('chapter-studio?project=' + encodeURIComponent('${{title}}'))">
            <span>Open Chapter Studio</span>
            <span class="material-symbols-outlined text-[16px] group-hover:translate-x-0.5 transition-transform">arrow_forward</span>
          </a>
        </div>
      `;
      grid.prepend(newCard);
      
      submitBtn.innerHTML = '<span class="material-symbols-outlined text-[18px]">folder_special</span><span>Create Project</span>';
      submitBtn.disabled = false;
      nameInput.value = '';
      dismissModal();
    }}, 400);
  }});
}}
</script>
</body>
</html>
"""

# Render the Google Stitch component seamlessly
components.html(workspace_html, height=1050, scrolling=True)
