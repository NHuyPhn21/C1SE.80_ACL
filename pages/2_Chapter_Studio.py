"""ACL Chapter Studio — Batch Image Upload & AI Pipeline Setup — Screen ACL-06 (Live Backend Connected)."""

import os
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

from utils.auth_session import require_auth
from backend.image_utils import BASE_DIR

# Enforce authentication guard
user = require_auth()

user_initials = (user.full_name[:2] if user.full_name else "PH").upper()
user_name = user.full_name or "Phan Nhat Huy"
project_name = st.query_params.get("project", "Shonen Weekly #112")

# Quét các file ảnh thật trong thư mục dự án để hiển thị sẵn trên bảng Staging
raw_manga_dir = BASE_DIR / "data" / "raw_images" / "AisazuNihaIrarenai"
uploads_dir = BASE_DIR / "data" / "raw_images" / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)

available_files = []
if raw_manga_dir.exists():
    for f in sorted(raw_manga_dir.iterdir()):
        if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            size_mb = round(f.stat().st_size / (1024 * 1024), 2)
            available_files.append({"name": f.name, "size": f"{size_mb} MB", "folder": "AisazuNihaIrarenai"})

# Lấy mặc định 2 trang mẫu (ví dụ 045.jpg, 046.jpg) để staging ban đầu hoặc toàn bộ nếu ít hơn
default_staged = [f for f in available_files if f["name"] in {"045.jpg", "046.jpg"}]
if not default_staged and available_files:
    default_staged = available_files[:3]

initial_rows_html = ""
initial_filenames = []
for idx, item in enumerate(default_staged, start=1):
    fname = item["name"]
    fsize = item["size"]
    initial_filenames.append(fname)
    initial_rows_html += f"""
          <div class="flex items-center justify-between p-space-sm rounded-lg bg-surface-container-low hover:bg-surface-container transition-colors staged-file-row" data-filename="{fname}" id="row-file-{idx}">
            <div class="flex items-center gap-space-md min-w-0">
              <div class="w-10 h-10 rounded-lg bg-primary-container text-on-primary flex items-center justify-center shrink-0 shadow-sm">
                <span class="material-symbols-outlined text-[22px]">image</span>
              </div>
              <div class="flex flex-col min-w-0">
                <span class="font-title-md text-body-md font-semibold text-on-surface truncate notranslate" translate="no">{fname}</span>
                <span class="font-code-sm text-code-sm text-on-surface-variant notranslate" translate="no">{fsize} • Raw Manga Scan (Ready)</span>
              </div>
            </div>
            <div class="flex items-center gap-space-lg shrink-0">
              <span class="bg-secondary-container text-on-secondary-container font-code-sm text-code-sm font-semibold px-space-sm py-space-xs rounded-full flex items-center gap-space-xs">
                <span class="material-symbols-outlined text-[14px]">check_circle</span>
                <span>Ready for pipeline</span>
              </span>
              <button aria-label="Remove {fname}" onclick="removeFileRow('row-file-{idx}')" class="text-on-surface-variant hover:text-error transition-colors p-space-xs rounded-full hover:bg-surface-container-high cursor-pointer" type="button">
                <span class="material-symbols-outlined text-[20px]">delete</span>
              </button>
            </div>
          </div>
    """

initial_count = len(initial_filenames)

chapter_studio_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<meta content="web_dashboard" name="shell-type"/>
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
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

font {{
  font-family: inherit !important;
  font-size: inherit !important;
  line-height: inherit !important;
  color: inherit !important;
  letter-spacing: inherit !important;
  vertical-align: baseline !important;
  display: inline !important;
}}

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

@keyframes pulseGlow {{
  0%, 100% {{ box-shadow: 0 0 0 0 rgba(37, 50, 111, 0.2); }}
  50% {{ box-shadow: 0 0 0 8px rgba(37, 50, 111, 0); }}
}}
.pulse-glow {{
  animation: pulseGlow 2s infinite;
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

<body class="bg-background font-body-md text-on-surface antialiased">

<!-- FIXED LEFT SIDEBAR -->
<aside class="fixed left-0 top-0 h-full w-[220px] bg-surface-container-lowest border-r border-surface-variant z-50 flex flex-col justify-between select-none">
  <div class="flex flex-col">
    <div class="p-space-lg border-b border-surface-variant">
      <div class="font-headline-md text-headline-md text-primary-container tracking-tight leading-none notranslate" translate="no">ACL</div>
      <p class="font-code-sm text-code-sm text-outline mt-space-xs tracking-tight">Automated Comic Localization</p>
    </div>

    <nav class="flex flex-col gap-space-xs p-space-sm mt-space-xs">
      <a class="flex items-center gap-space-sm px-space-md py-space-sm rounded-full text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors cursor-pointer" onclick="navigateParent('workspace')">
        <span class="material-symbols-outlined text-[20px]">grid_view</span>
        <span class="font-title-md text-body-md">Dashboard</span>
      </a>
      <a class="flex items-center gap-space-sm px-space-md py-space-sm rounded-full text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors cursor-pointer" onclick="navigateParent('workspace')">
        <span class="material-symbols-outlined text-[20px]">folder</span>
        <span class="font-title-md text-body-md">Projects</span>
      </a>
      <a class="flex items-center gap-space-sm px-space-md py-space-sm rounded-full text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors cursor-pointer" onclick="navigateParent('team-roles')">
        <span class="material-symbols-outlined text-[20px]">groups</span>
        <span class="font-title-md text-body-md">Team Roles</span>
      </a>
      <a aria-current="page" class="flex items-center gap-space-sm px-space-md py-space-sm transition-colors bg-primary-container text-on-primary font-title-md rounded-full shadow-sm cursor-pointer" onclick="navigateParent('chapter-studio')">
        <span class="material-symbols-outlined text-[20px]">cloud_upload</span>
        <span class="font-title-md text-body-md">Chapter Studio</span>
      </a>
      <a class="flex items-center gap-space-sm px-space-md py-space-sm rounded-full text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors cursor-pointer" onclick="navigateParent('review-studio')">
        <span class="material-symbols-outlined text-[20px]">vertical_split</span>
        <span class="font-title-md text-body-md">Review Studio</span>
      </a>
      <a class="flex items-center gap-space-sm px-space-md py-space-sm rounded-full text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors cursor-pointer" onclick="navigateParent('typesetting')">
        <span class="material-symbols-outlined text-[20px]">edit_note</span>
        <span class="font-title-md text-body-md">Typesetting</span>
      </a>
      <a class="flex items-center gap-space-sm px-space-md py-space-sm rounded-full text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors cursor-pointer" onclick="navigateParent('queue-monitor')">
        <span class="material-symbols-outlined text-[20px]">schedule</span>
        <span class="font-title-md text-body-md">Queue Monitor</span>
      </a>
      <a class="flex items-center gap-space-sm px-space-md py-space-sm rounded-full text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors cursor-pointer" onclick="navigateParent('settings')">
        <span class="material-symbols-outlined text-[20px]">settings</span>
        <span class="font-title-md text-body-md">Personal Settings</span>
      </a>
    </nav>
  </div>

  <div class="p-space-md border-t border-surface-variant flex items-center justify-between">
    <span class="font-code-sm text-code-sm text-outline bg-surface-container px-space-sm py-space-xs rounded-full notranslate" translate="no">v2.4.0-prod</span>
    <span class="flex h-2 w-2 rounded-full bg-secondary" title="System Ready"></span>
  </div>
</aside>

<!-- MAIN APP SHELL -->
<div class="pl-[220px]">

  <!-- TOP HEADER BAR -->
  <header class="fixed top-0 left-[220px] right-0 h-16 bg-surface-container-lowest/90 backdrop-blur-md border-b border-surface-variant z-40 flex items-center justify-between px-gutter-lg">
    <div class="flex items-center gap-space-sm">
      <span class="material-symbols-outlined text-outline text-[20px]">palette</span>
      <span class="font-label-md text-label-md text-on-surface-variant font-medium">Workspace Canvas</span>
    </div>
    <div class="flex items-center gap-space-md">
      <div class="w-8 h-8 rounded-full bg-primary-container flex items-center justify-center text-on-primary font-headline-sm text-body-sm font-semibold select-none shadow-sm notranslate" translate="no">{user_initials}</div>
      <button onclick="navigateParent('login?logout=1')" class="text-on-surface-variant hover:text-primary-container text-xs font-semibold px-2 py-1 rounded border border-[#E4DFD6] hover:bg-surface-variant transition-colors" title="Sign out">
        Sign out
      </button>
    </div>
  </header>

  <!-- MAIN VIEWPORT CONTENT -->
  <main class="w-full pt-16 bg-background min-h-screen p-gutter-lg">
    <div class="flex flex-col w-full">

      <!-- Top Breadcrumb & Metadata Navigation -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-space-sm mb-space-lg">
        <div class="flex items-center gap-space-sm font-label-md text-label-md text-on-surface-variant flex-wrap">
          <a class="flex items-center gap-space-xs text-on-surface-variant hover:text-primary transition-colors cursor-pointer" onclick="navigateParent('workspace')">
            <span class="material-symbols-outlined text-[18px]">arrow_back</span>
            <span>Back to Projects</span>
          </a>
          <span class="text-outline-variant font-code-sm">/</span>
          <span class="text-on-surface-variant notranslate" translate="no">{project_name}</span>
          <span class="text-outline-variant font-code-sm">/</span>
          <span class="font-title-md text-primary font-semibold">Chapter Studio</span>
          <a class="text-xs font-semibold px-2.5 py-1 rounded-full bg-secondary-container/40 text-on-secondary-container hover:bg-secondary-container transition-colors cursor-pointer ml-1 inline-flex items-center gap-1" onclick="navigateParent('review-studio?project=' + encodeURIComponent('{project_name}'))">
            <span>Review Studio</span>
            <span class="material-symbols-outlined text-[13px]">arrow_forward</span>
          </a>
        </div>

        <div class="flex items-center gap-space-sm">
          <span class="bg-surface-container px-space-md py-space-xs rounded-full font-code-sm text-code-sm text-outline flex items-center gap-space-xs">
            <span class="w-2 h-2 rounded-full bg-secondary"></span>
            <span class="notranslate" translate="no">STAGE: LIVE_INGESTION</span>
          </span>
          <span class="bg-surface-container-high text-on-surface-variant px-space-md py-space-xs rounded-full font-code-sm text-code-sm notranslate" translate="no">
            BATCH #CH-112-RAW
          </span>
        </div>
      </div>

      <!-- Workspace Title Area -->
      <div class="mb-space-xl">
        <h1 class="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">Chapter Studio</h1>
        <p class="font-body-md text-body-md text-on-surface-variant mt-space-xs">Upload chapter raw scans and configure AI pipeline execution.</p>
      </div>

      <!-- Hidden real file input -->
      <input type="file" id="batch-file-input" multiple accept="image/png,image/jpeg,image/webp" class="hidden"/>

      <!-- Batch Upload Drag-and-Drop Dropzone -->
      <div class="w-full relative group" id="drop-zone" onclick="document.getElementById('batch-file-input').click()">
        <div class="bg-surface-container-lowest rounded-xl p-space-xl text-center shadow-sm transition-all duration-200 cursor-pointer flex flex-col items-center justify-center min-h-[260px] relative overflow-hidden bg-gradient-to-b from-surface-container-lowest to-surface-container-low/40">
          <div class="absolute inset-2 rounded-lg pointer-events-none stroke-primary-container/40 group-hover:stroke-primary-container transition-colors">
            <svg class="w-full h-full" xmlns="http://www.w3.org/2000/svg">
              <rect class="text-primary-container/30 group-hover:text-primary-container transition-colors" fill="none" height="100%" rx="8" stroke="currentColor" stroke-dasharray="8 8" stroke-width="2" width="100%"></rect>
            </svg>
          </div>
          <div class="w-16 h-16 rounded-full bg-primary-fixed flex items-center justify-center text-primary-container mb-space-sm group-hover:scale-105 transition-transform shadow-sm">
            <span class="material-symbols-outlined text-[36px]">cloud_upload</span>
          </div>
          <h2 class="font-headline-sm text-headline-sm font-bold text-on-surface mt-space-xs">Drag &amp; drop comic pages here</h2>
          <p class="font-body-md text-body-md text-on-surface-variant mt-space-xs max-w-md">Accepts JPG, PNG batches up to 50 pages • Connected to AisazuNihaIrarenai Dataset</p>
          <div class="mt-space-lg flex items-center gap-space-sm">
            <button class="bg-surface-container-lowest text-primary-container font-title-md text-body-md font-semibold px-space-lg py-2.5 rounded-full inline-flex items-center gap-space-xs shadow-sm hover:bg-surface-container transition-colors border border-primary-container/20" type="button">
              <span class="material-symbols-outlined text-[20px]">folder_open</span>
              <span>Browse Files from Computer</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Uploaded Batch Files Staging Table -->
      <div class="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm mt-space-lg">
        <div class="flex items-center justify-between pb-space-md mb-space-sm border-b border-[#E4DFD6]">
          <div class="flex items-center gap-space-sm">
            <h3 class="font-headline-sm text-headline-sm font-bold text-on-surface" id="staging-title">Uploaded Pages ({initial_count} files ready)</h3>
            <span class="bg-secondary-container text-on-secondary-container font-code-sm text-code-sm px-space-sm py-space-xs rounded-full font-medium">Batch Verified</span>
          </div>
          <button onclick="clearAllFiles()" class="font-label-md text-body-sm font-semibold text-error hover:opacity-80 transition-opacity flex items-center gap-space-xs cursor-pointer" type="button">
            <span class="material-symbols-outlined text-[16px]">delete_sweep</span>
            <span>Clear all</span>
          </button>
        </div>

        <!-- Staging Rows List -->
        <div class="flex flex-col gap-space-xs" id="staging-list">
          {initial_rows_html}
        </div>
      </div>

      <!-- Language Configuration & AI Model Selector Row -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-space-lg mt-space-lg">
        <div class="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm flex flex-col justify-between border border-[#E4DFD6]">
          <div>
            <label class="font-title-md text-body-md font-semibold text-on-surface mb-space-xs block">Source Language</label>
            <div class="relative mt-space-xs">
              <select id="source-lang-select" class="w-full bg-surface-container-low rounded-lg p-space-sm font-title-md text-body-md font-semibold text-on-surface border border-transparent hover:border-[#E4DFD6] focus:outline-none focus:ring-2 focus:ring-primary-container transition-all cursor-pointer">
                <option value="ja" selected>Japanese (Raw Manga)</option>
                <option value="en">English (Original Comic)</option>
              </select>
            </div>
          </div>
          <div class="mt-space-md pt-space-sm bg-surface-container-low p-space-sm rounded-lg flex items-center gap-space-xs text-on-surface-variant">
            <span class="material-symbols-outlined text-primary text-[18px]">document_scanner</span>
            <span class="font-code-sm text-code-sm"><span class="font-semibold text-on-surface notranslate" translate="no">YOLOv8 + Manga OCR v2.1</span> Active • IoU Collision Filter Enabled</span>
          </div>
        </div>

        <div class="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm flex flex-col justify-between border border-[#E4DFD6]">
          <div>
            <label class="font-title-md text-body-md font-semibold text-on-surface mb-space-xs block">Target Language</label>
            <div class="relative mt-space-xs">
              <select id="target-lang-select" class="w-full bg-surface-container-low rounded-lg p-space-sm font-title-md text-body-md font-semibold text-on-surface border border-transparent hover:border-[#E4DFD6] focus:outline-none focus:ring-2 focus:ring-primary-container transition-all cursor-pointer">
                <option value="vi" selected>Vietnamese</option>
                <option value="en">English</option>
              </select>
            </div>
          </div>
          <div class="mt-space-md pt-space-sm bg-surface-container-low p-space-sm rounded-lg flex items-center gap-space-xs text-on-surface-variant">
            <span class="material-symbols-outlined text-primary text-[18px]">psychology</span>
            <span class="font-code-sm text-code-sm"><span class="font-semibold text-on-surface notranslate" translate="no">Gemini 3.8 Flash Batch Translator</span> • 1-Request JSON Mode</span>
          </div>
        </div>
      </div>

      <!-- Pipeline Launch Action Card -->
      <div class="bg-primary-fixed rounded-xl p-space-lg flex flex-col md:flex-row md:items-center justify-between gap-space-lg mt-space-lg shadow-sm border border-primary-container/20">
        <div class="flex flex-col">
          <div class="flex items-center gap-space-sm">
            <span class="material-symbols-outlined text-primary-container text-[24px]">rocket_launch</span>
            <h3 class="font-headline-sm text-headline-sm font-bold text-primary-container" id="launch-banner-title">Ready to process {initial_count} pages in Asynchronous Queue</h3>
          </div>
          <div class="mt-space-sm flex flex-wrap items-center gap-space-xs font-code-sm text-code-sm text-primary-container/90">
            <span class="bg-surface-container-lowest/80 px-space-xs py-0.5 rounded font-medium">Queue</span>
            <span class="material-symbols-outlined text-[14px]">arrow_forward</span>
            <span class="bg-surface-container-lowest/80 px-space-xs py-0.5 rounded font-medium notranslate" translate="no">YOLOv8 Detection</span>
            <span class="material-symbols-outlined text-[14px]">arrow_forward</span>
            <span class="bg-surface-container-lowest/80 px-space-xs py-0.5 rounded font-medium notranslate" translate="no">Manga OCR</span>
            <span class="material-symbols-outlined text-[14px]">arrow_forward</span>
            <span class="bg-surface-container-lowest/80 px-space-xs py-0.5 rounded font-medium">Review Studio</span>
            <span class="material-symbols-outlined text-[14px]">arrow_forward</span>
            <span class="bg-surface-container-lowest/80 px-space-xs py-0.5 rounded font-medium notranslate" translate="no">Fast Inpainting</span>
            <span class="material-symbols-outlined text-[14px]">arrow_forward</span>
            <span class="bg-surface-container-lowest/80 px-space-xs py-0.5 rounded font-medium">Auto-Typesetting</span>
          </div>
        </div>

        <div class="shrink-0 flex items-center">
          <button class="bg-primary-container hover:bg-primary text-on-primary font-title-md text-title-md font-semibold h-12 px-space-xl rounded-full shadow-md flex items-center gap-space-sm transition-transform active:scale-95 cursor-pointer pulse-glow" id="start-pipeline-btn" type="button">
            <span>Start AI Pipeline</span>
            <span class="material-symbols-outlined text-[20px]">play_arrow</span>
          </button>
        </div>
      </div>

    </div>
  </main>
</div>

<script>
function navigateParent(path) {{
  const targetUrl = window.location.origin + '/' + path.replace(/^\/+/, '');
  const a = document.createElement('a');
  a.href = targetUrl;
  a.target = '_top';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}}

function removeFileRow(rowId) {{
  const row = document.getElementById(rowId);
  if (row) {{
    row.remove();
    updateStagedCount();
  }}
}}

function clearAllFiles() {{
  const list = document.getElementById('staging-list');
  if (list) {{
    list.innerHTML = '';
    updateStagedCount();
  }}
}}

function updateStagedCount() {{
  const rows = document.querySelectorAll('#staging-list > .staged-file-row');
  const count = rows.length;
  const title = document.getElementById('staging-title');
  const launchTitle = document.getElementById('launch-banner-title');
  if (title) title.innerText = `Uploaded Pages (${{count}} files ready)`;
  if (launchTitle) launchTitle.innerText = `Ready to process ${{count}} pages in Asynchronous Queue`;
}}

function getStagedFilenames() {{
  const rows = document.querySelectorAll('#staging-list > .staged-file-row');
  const names = [];
  rows.forEach(r => {{
    const fname = r.getAttribute('data-filename');
    if (fname) names.push(fname);
  }});
  return names;
}}

const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('batch-file-input');

if (dropZone) {{
  ['dragenter', 'dragover'].forEach(eventName => {{
    dropZone.addEventListener(eventName, (e) => {{
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.add('scale-[1.01]');
    }}, false);
  }});
  ['dragleave', 'drop'].forEach(eventName => {{
    dropZone.addEventListener(eventName, (e) => {{
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.remove('scale-[1.01]');
    }}, false);
  }});
  dropZone.addEventListener('drop', (e) => {{
    handleNewFiles(e.dataTransfer.files);
  }}, false);
}}

if (fileInput) {{
  fileInput.addEventListener('change', function() {{
    handleNewFiles(this.files);
  }});
}}

function handleNewFiles(files) {{
  if (!files || files.length === 0) return;
  const list = document.getElementById('staging-list');
  // Khi chọn file mới từ máy tính, xóa danh sách mặc định để chỉ chạy đúng các file người dùng vừa chọn
  list.innerHTML = '';
  for (let i = 0; i < files.length; i++) {{
    const file = files[i];
    const fileId = 'row-file-custom-' + Date.now() + '-' + i;
    const sizeMb = (file.size / (1024 * 1024)).toFixed(2);
    const row = document.createElement('div');
    row.id = fileId;
    row.setAttribute('data-filename', file.name);
    row.className = "flex items-center justify-between p-space-sm rounded-lg bg-surface-container-low hover:bg-surface-container transition-colors staged-file-row";
    row.innerHTML = `
      <div class="flex items-center gap-space-md min-w-0">
        <div class="w-10 h-10 rounded-lg bg-primary-container text-on-primary flex items-center justify-center shrink-0 shadow-sm">
          <span class="material-symbols-outlined text-[22px]">image</span>
        </div>
        <div class="flex flex-col min-w-0">
          <span class="font-title-md text-body-md font-semibold text-on-surface truncate notranslate" translate="no">${{file.name}}</span>
          <span class="font-code-sm text-code-sm text-on-surface-variant notranslate" translate="no">${{sizeMb}} MB • Selected from Computer</span>
        </div>
      </div>
      <div class="flex items-center gap-space-lg shrink-0">
        <span class="bg-secondary-container text-on-secondary-container font-code-sm text-code-sm font-semibold px-space-sm py-space-xs rounded-full flex items-center gap-space-xs">
          <span class="material-symbols-outlined text-[14px]">check_circle</span>
          <span>Ready for pipeline</span>
        </span>
        <button onclick="removeFileRow('${{fileId}}')" class="text-on-surface-variant hover:text-error transition-colors p-space-xs rounded-full hover:bg-surface-container-high cursor-pointer" type="button">
          <span class="material-symbols-outlined text-[20px]">delete</span>
        </button>
      </div>
    `;
    list.appendChild(row);
  }}
  updateStagedCount();
}}

const startBtn = document.getElementById('start-pipeline-btn');
if (startBtn) {{
  startBtn.addEventListener('click', function() {{
    const files = getStagedFilenames();
    if (files.length === 0) {{
      alert('Please select at least 1 comic page before starting the AI pipeline!');
      return;
    }}
    const btn = this;
    btn.disabled = true;
    btn.innerHTML = `<span class="material-symbols-outlined animate-spin text-[20px]">sync</span><span>Dispatching ${{files.length}} Pages to AI Backend...</span>`;
    
    const filesParam = encodeURIComponent(files.join(','));
    const projParam = encodeURIComponent('{project_name}');
    setTimeout(() => {{
      navigateParent(`queue-monitor?project=${{projParam}}&run_pipeline=1&files=${{filesParam}}`);
    }}, 400);
  }});
}}
</script>

</body>
</html>
"""

components.html(chapter_studio_html, height=1150, scrolling=True)