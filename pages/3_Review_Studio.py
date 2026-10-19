"""ACL Interactive Review Studio — OCR Verification & Text Correction — Screen ACL-07.

Pixel-perfect implementation of Google Stitch Project 'UX/UI_ACL' (ID: 15081338219515375601).
Screen: ACL-07: Interactive Review Studio — OCR Verification & Text Correction.
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

review_studio_html = f"""<!DOCTYPE html>
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

.ocr-card {{
  transition: all 0.2s ease;
}}
.ocr-card.active-ocr {{
  box-shadow: 0 0 0 2px #25326f;
  background-color: #ffffff;
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
      <a aria-current="page" class="flex items-center gap-space-sm px-space-sm py-2 rounded-lg transition-colors bg-primary-container text-on-primary font-title-md font-semibold cursor-pointer" onclick="navigateParent('review-studio')">
        <span class="material-symbols-outlined text-[20px]">rate_review</span>
        <span>Review Studio</span>
      </a>
      <a class="flex items-center gap-space-sm px-space-sm py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface transition-colors font-body-md text-body-md cursor-pointer" onclick="navigateParent('typesetting')">
        <span class="material-symbols-outlined text-[20px]">format_shapes</span>
        <span>Typesetting</span>
      </a>
      <a class="flex items-center gap-space-sm px-space-sm py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface transition-colors font-body-md text-body-md cursor-pointer" onclick="navigateParent('queue-monitor')">
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

  <!-- TOP HEADER BAR -->
  <header class="fixed top-0 left-[220px] right-0 h-16 bg-surface-container-lowest/90 backdrop-blur-md shadow-[0_1px_8px_rgba(0,0,0,0.04)] z-40 flex items-center justify-between px-space-lg border-b border-[#E4DFD6]">
    <div class="flex items-center gap-2 font-body-sm text-body-sm text-on-surface-variant">
      <span class="font-medium text-on-surface">Workspace</span>
      <span class="material-symbols-outlined text-[16px] text-outline">chevron_right</span>
      <span class="text-on-surface-variant">Studio Canvas</span>
    </div>
    <div class="flex items-center gap-space-md">
      <button aria-label="Notifications" class="flex items-center justify-center w-8 h-8 rounded-full text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors" type="button">
        <span class="material-symbols-outlined text-[20px]">notifications</span>
      </button>
      <button aria-label="Help &amp; Documentation" class="flex items-center justify-center w-8 h-8 rounded-full text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors" type="button">
        <span class="material-symbols-outlined text-[20px]">help</span>
      </button>
      <div class="w-8 h-8 rounded-full bg-primary-container flex items-center justify-center font-title-md text-label-md text-on-primary font-semibold tracking-wide select-none notranslate" translate="no" title="{user_name}">
        {user_initials}
      </div>
      <button onclick="navigateParent('login?logout=1')" class="text-on-surface-variant hover:text-primary-container text-xs font-semibold px-2 py-1 rounded border border-[#E4DFD6] hover:bg-surface-variant transition-colors" title="Sign out">
        Sign out
      </button>
    </div>
  </header>

  <!-- MAIN VIEWPORT CONTENT -->
  <main class="relative pt-16 min-h-screen bg-surface w-full px-space-lg py-space-md">
    <div class="flex flex-col w-full">

      <!-- Top Breadcrumb & Metadata Navigation -->
      <div class="flex items-center justify-between pb-space-sm mb-space-xs">
        <div class="flex items-center gap-space-xs text-on-surface-variant font-label-md text-label-md flex-wrap">
          <a class="flex items-center gap-1 text-on-surface-variant hover:text-primary transition-colors cursor-pointer" onclick="navigateParent('workspace')">
            <span class="material-symbols-outlined text-[16px]">arrow_back</span>
            <span>Workspace</span>
          </a>
          <span class="text-outline-variant">/</span>
          <a class="text-on-surface-variant hover:text-primary transition-colors cursor-pointer" onclick="navigateParent('chapter-studio')">Chapter Studio</a>
          <span class="text-outline-variant">/</span>
          <span class="text-on-surface font-medium notranslate" translate="no">Shonen Weekly #112</span>
          <span class="text-outline-variant">/</span>
          <span class="text-primary font-semibold">Interactive Review Studio</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="flex items-center gap-1.5 px-3 py-1 rounded-full bg-secondary-container/40 text-on-secondary-container font-code-sm text-code-sm font-semibold">
            <span class="material-symbols-outlined text-[15px]">check_circle</span>
            <span>18 / 24 Pages Reviewed</span>
          </span>
          <span class="px-2.5 py-1 rounded-full bg-surface-container font-code-sm text-code-sm text-on-surface-variant notranslate" translate="no">
            Engine: Manga-OCR v2.1
          </span>
        </div>
      </div>

      <!-- Header Title & Pagination Strip -->
      <div class="bg-surface-container-lowest rounded-xl p-space-md shadow-sm mb-space-md flex flex-wrap items-center justify-between gap-y-3 border border-[#E4DFD6]">
        <div class="flex flex-col min-w-[280px]">
          <div class="flex items-center gap-space-sm">
            <h1 class="font-headline-md text-headline-md text-on-surface tracking-tight">Interactive Review Studio</h1>
            <span class="px-2 py-0.5 rounded-full bg-primary-container text-on-primary font-code-sm text-code-sm notranslate" translate="no">OCR Stage</span>
          </div>
          <p class="font-body-sm text-body-sm text-on-surface-variant mt-0.5">
            Batch <span class="font-code-sm text-code-sm text-on-surface font-semibold notranslate" translate="no">#CH-112-RAW</span> • Inspect YOLOv8 detection boxes and refine raw text transcription.
          </p>
        </div>

        <!-- Center Pagination Control -->
        <div class="inline-flex items-center gap-2 bg-surface-container-low px-2 py-1.5 rounded-full border border-[#E4DFD6]">
          <button onclick="changePage(-1)" class="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-surface-container-lowest text-on-surface font-label-md text-label-md shadow-xs hover:bg-surface transition-colors cursor-pointer" type="button">
            <span class="material-symbols-outlined text-[16px]">chevron_left</span>
            <span>Prev Page</span>
          </button>
          <div class="px-3 font-title-md text-title-md text-on-surface flex items-baseline gap-1 select-none">
            <span class="font-bold" id="current-page-display">Page 14</span>
            <span class="font-body-sm text-body-sm text-on-surface-variant font-normal">of 24</span>
          </div>
          <button onclick="changePage(1)" class="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-surface-container-lowest text-on-surface font-label-md text-label-md shadow-xs hover:bg-surface transition-colors cursor-pointer" type="button">
            <span>Next Page</span>
            <span class="material-symbols-outlined text-[16px]">chevron_right</span>
          </button>
        </div>

        <!-- Quick Mode Toggles -->
        <div class="flex items-center gap-2">
          <button class="px-3 py-1.5 rounded-full bg-surface-container-high text-on-surface-variant hover:text-on-surface font-label-md text-label-md flex items-center gap-1.5 transition-colors cursor-pointer" type="button">
            <span class="material-symbols-outlined text-[18px]">layers</span>
            <span>Mask Layers</span>
          </button>
          <button class="px-3 py-1.5 rounded-full bg-primary text-on-primary font-label-md text-label-md flex items-center gap-1.5 hover:bg-primary-container transition-all cursor-pointer" type="button">
            <span class="material-symbols-outlined text-[18px]">tune</span>
            <span>Detection Sensitivity</span>
          </button>
        </div>
      </div>

      <!-- Dual Split Workspace -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-space-lg items-start">

        <!-- LEFT PANEL: Original Page Detection Preview -->
        <div class="bg-surface-container-lowest rounded-xl p-space-md shadow-sm flex flex-col border border-[#E4DFD6]">
          <!-- Panel Header -->
          <div class="flex items-center justify-between pb-space-sm mb-space-sm border-b border-[#E4DFD6]">
            <div class="flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-full bg-primary"></span>
              <span class="font-title-md text-title-md text-on-surface">Original Page — Detection Preview</span>
              <span class="px-2 py-0.5 rounded-full bg-surface-container text-on-surface-variant font-code-sm text-code-sm notranslate" translate="no">YOLOv8x-Manga</span>
            </div>
            <span class="font-code-sm text-code-sm text-on-surface-variant">1600 × 2560 px • 4 Regions</span>
          </div>

          <!-- Manga Canvas Area -->
          <div class="relative w-full min-h-[580px] bg-inverse-surface rounded-xl p-4 flex items-center justify-center overflow-hidden select-none" id="canvas-container">
            <!-- Archival Manga Spread with Panels Mockup -->
            <div class="relative w-[380px] h-[540px] bg-surface-container-lowest shadow-2xl rounded-sm p-4 flex flex-col gap-2 overflow-hidden" id="manga-canvas">
              
              <!-- Panel Architecture -->
              <div class="grid grid-cols-2 gap-2 h-44">
                <!-- Panel 1 (Top Left): Ambient artwork graphic -->
                <div class="relative bg-surface-container-high overflow-hidden rounded-xs p-2">
                  <svg class="absolute inset-0 w-full h-full text-on-surface-variant/20" preserveaspectratio="none" viewbox="0 0 100 100">
                    <line stroke="currentColor" stroke-width="0.75" x1="0" x2="100" y1="0" y2="100"></line>
                    <line stroke="currentColor" stroke-width="0.75" x1="100" x2="0" y1="0" y2="100"></line>
                    <line stroke="currentColor" stroke-width="0.5" x1="0" x2="100" y1="50" y2="50"></line>
                    <circle cx="50" cy="50" fill="none" r="30" stroke="currentColor" stroke-width="1"></circle>
                  </svg>
                  <div class="relative z-10 font-code-sm text-code-sm text-on-surface-variant opacity-40 notranslate" translate="no">PANEL #01</div>
                </div>

                <!-- Panel 2 (Top Right): Contains Bubble #1 -->
                <div class="relative bg-surface-container-low rounded-xs p-2 overflow-hidden flex flex-col justify-end">
                  <svg class="absolute inset-0 w-full h-full text-on-surface/10" viewbox="0 0 100 100">
                    <line stroke="currentColor" stroke-width="1.5" x1="50" x2="0" y1="50" y2="10"></line>
                    <line stroke="currentColor" stroke-width="1.5" x1="50" x2="100" y1="50" y2="20"></line>
                    <line stroke="currentColor" stroke-width="1.5" x1="50" x2="80" y1="50" y2="90"></line>
                    <line stroke="currentColor" stroke-width="1.5" x1="50" x2="20" y1="50" y2="80"></line>
                  </svg>
                  <!-- Speech Bubble Silhouette -->
                  <div class="w-24 h-28 bg-surface-container-lowest rounded-[40px] shadow-sm ml-auto mr-1 flex items-center justify-center p-2 text-center">
                    <span class="font-body-sm text-body-sm text-on-surface font-medium [writing-mode:vertical-rl] notranslate" translate="no">先生、待ってください！</span>
                  </div>
                </div>
              </div>

              <!-- Panel Center Wide (Contains Bubble #2 and SFX #3) -->
              <div class="relative h-44 bg-surface-container overflow-hidden rounded-xs p-3 flex items-center justify-between">
                <!-- Sound Effect Graphic Drawing in Panel -->
                <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <span class="font-headline-lg text-headline-lg font-bold text-on-surface/15 tracking-widest scale-125 rotate-[-8deg] select-none notranslate" translate="no">
                    ドカーン
                  </span>
                </div>
                <!-- Left Speech Balloon for Box 2 -->
                <div class="relative z-10 w-24 h-24 bg-surface-container-lowest rounded-[32px] flex items-center justify-center p-2 shadow-xs">
                  <span class="font-body-sm text-body-sm text-on-surface font-semibold [writing-mode:vertical-rl] notranslate" translate="no">何があったんだ？！</span>
                </div>
                <!-- Stylized screen-tone shading block -->
                <div class="w-28 h-32 bg-surface-container-highest/60 rounded-xs flex flex-col justify-between p-2">
                  <span class="font-code-sm text-code-sm text-on-surface-variant/40 notranslate" translate="no">SCENE DUST</span>
                  <div class="h-1.5 w-full bg-on-surface/10 rounded-full"></div>
                </div>
              </div>

              <!-- Bottom Full Panel (Contains Box #4 Narration) -->
              <div class="relative flex-1 bg-surface-container-high rounded-xs p-3 flex flex-col justify-end">
                <svg class="absolute inset-x-0 bottom-0 h-16 w-full text-on-surface-variant/20" preserveaspectratio="none" viewbox="0 0 200 60">
                  <polygon fill="currentColor" points="0,60 0,35 25,35 30,20 45,20 50,40 80,40 90,15 110,15 120,38 160,38 175,25 190,25 200,42 200,60"></polygon>
                </svg>
                <!-- Bottom Narration Rectangle -->
                <div class="relative z-10 w-44 bg-surface-container-lowest p-2 rounded-xs shadow-xs ml-auto">
                  <p class="font-body-sm text-body-sm text-on-surface font-medium leading-tight notranslate" translate="no">その時、街全体が揺れた。</p>
                </div>
              </div>

              <!-- YOLOv8 OVERLAY 1: Top-Right Bubble -->
              <div onclick="selectBox(1)" id="overlay-box-1" class="absolute top-6 right-6 w-32 h-36 bg-primary-container/10 rounded-sm cursor-pointer transition-all ring-2 ring-primary">
                <div class="absolute -top-3 left-0 bg-primary text-on-primary px-2 py-0.5 rounded-full font-code-sm text-code-sm font-bold flex items-center gap-1 shadow-sm notranslate" translate="no">
                  <span class="w-1.5 h-1.5 rounded-full bg-secondary-fixed"></span>
                  <span>#1 Bubble</span>
                </div>
                <!-- Resize Handles -->
                <span class="absolute -top-1 -left-1 w-2.5 h-2.5 bg-surface-container-lowest rounded-full ring-2 ring-primary"></span>
                <span class="absolute -top-1 -right-1 w-2.5 h-2.5 bg-surface-container-lowest rounded-full ring-2 ring-primary"></span>
                <span class="absolute -bottom-1 -left-1 w-2.5 h-2.5 bg-surface-container-lowest rounded-full ring-2 ring-primary"></span>
                <span class="absolute -bottom-1 -right-1 w-2.5 h-2.5 bg-surface-container-lowest rounded-full ring-2 ring-primary"></span>
              </div>

              <!-- YOLOv8 OVERLAY 2: Middle-Left Bubble -->
              <div onclick="selectBox(2)" id="overlay-box-2" class="absolute top-[204px] left-6 w-28 h-28 bg-primary-container/10 rounded-sm cursor-pointer transition-all hover:bg-primary-container/20 ring-2 ring-primary/80">
                <div class="absolute -top-3 left-0 bg-primary-container text-on-primary px-2 py-0.5 rounded-full font-code-sm text-code-sm font-bold flex items-center gap-1 shadow-sm notranslate" translate="no">
                  <span>#2 Bubble</span>
                </div>
              </div>

              <!-- YOLOv8 OVERLAY 3: Center SFX Warning State -->
              <div onclick="selectBox(3)" id="overlay-box-3" class="absolute top-[214px] left-36 w-36 h-24 bg-error-container/30 rounded-sm cursor-pointer transition-all ring-2 ring-error ring-offset-1">
                <div class="absolute -top-3.5 left-0 bg-error text-on-error px-2 py-0.5 rounded-full font-code-sm text-code-sm font-bold flex items-center gap-1 shadow-sm animate-pulse notranslate" translate="no">
                  <span class="material-symbols-outlined text-[13px]">warning</span>
                  <span>#3 SFX 0.52</span>
                </div>
              </div>

              <!-- YOLOv8 OVERLAY 4: Bottom Narration Box -->
              <div onclick="selectBox(4)" id="overlay-box-4" class="absolute bottom-6 right-6 w-48 h-20 bg-primary-container/10 rounded-sm cursor-pointer transition-all hover:bg-primary-container/20 ring-2 ring-primary/80">
                <div class="absolute -top-3 left-0 bg-primary-container text-on-primary px-2 py-0.5 rounded-full font-code-sm text-code-sm font-bold flex items-center gap-1 shadow-sm notranslate" translate="no">
                  <span>#4 Narration</span>
                </div>
              </div>

            </div>

            <!-- Floating Canvas Utility Dock -->
            <div class="absolute bottom-4 inset-x-0 mx-auto w-fit bg-surface-container-lowest/95 backdrop-blur-md px-4 py-1.5 rounded-full shadow-lg flex items-center gap-3 border border-[#E4DFD6]">
              <button onclick="zoomCanvas(0.1)" aria-label="Zoom In" class="text-on-surface-variant hover:text-primary transition-colors flex items-center p-1 cursor-pointer" type="button">
                <span class="material-symbols-outlined text-[20px]">zoom_in</span>
              </button>
              <button onclick="zoomCanvas(-0.1)" aria-label="Zoom Out" class="text-on-surface-variant hover:text-primary transition-colors flex items-center p-1 cursor-pointer" type="button">
                <span class="material-symbols-outlined text-[20px]">zoom_out</span>
              </button>
              <button id="zoom-label" class="font-code-sm text-code-sm text-on-surface-variant hover:text-on-surface font-semibold px-1 cursor-pointer" type="button">
                100%
              </button>
              <span class="w-px h-4 bg-outline-variant"></span>
              <button class="flex items-center gap-1 font-label-md text-label-md text-primary font-semibold hover:opacity-80 cursor-pointer" type="button">
                <span class="material-symbols-outlined text-[16px]">add_box</span>
                <span>Add Box</span>
              </button>
              <button class="flex items-center gap-1 font-label-md text-label-md text-on-surface-variant hover:text-on-surface cursor-pointer" type="button">
                <span class="material-symbols-outlined text-[16px]">call_merge</span>
                <span>Merge</span>
              </button>
              <button class="flex items-center gap-1 font-label-md text-label-md text-on-surface-variant hover:text-on-surface cursor-pointer" type="button">
                <span class="material-symbols-outlined text-[16px]">visibility_off</span>
                <span>Hide</span>
              </button>
            </div>
          </div>

          <!-- Quick Canvas Footnote -->
          <div class="mt-3 flex items-center justify-between text-on-surface-variant font-body-sm text-body-sm">
            <span class="flex items-center gap-1">
              <span class="material-symbols-outlined text-[16px] text-secondary">crop_free</span>
              <span>Click and drag canvas boxes to adjust OCR reading boundaries.</span>
            </span>
            <button class="text-primary hover:underline font-medium cursor-pointer" type="button">Re-detect Page</button>
          </div>
        </div>

        <!-- RIGHT PANEL: Extracted Text (Manga OCR Correction) -->
        <div class="bg-surface-container-lowest rounded-xl p-space-md shadow-sm flex flex-col border border-[#E4DFD6]">
          <!-- Panel Header -->
          <div class="flex items-center justify-between pb-space-sm mb-space-sm border-b border-[#E4DFD6]">
            <div>
              <h2 class="font-title-md text-title-md text-on-surface font-semibold">Extracted Text (Manga OCR)</h2>
              <p class="font-body-sm text-body-sm text-on-surface-variant">Review detected Japanese text strings before committing to translation stage.</p>
            </div>
            <button class="inline-flex items-center gap-1 px-3 py-1.5 rounded-full bg-primary-fixed text-on-primary-fixed hover:bg-primary-fixed-dim transition-colors font-label-md text-label-md font-semibold cursor-pointer" type="button">
              <span class="material-symbols-outlined text-[16px]">refresh</span>
              <span>Re-run OCR</span>
            </button>
          </div>

          <!-- Scrollable OCR Correction Stack -->
          <div class="flex flex-col gap-3.5 max-h-[580px] overflow-y-auto pr-1" id="ocr-cards-container">

            <!-- CARD ROW 1 (Box #1 Active Highlight) -->
            <div id="ocr-card-1" class="ocr-card active-ocr bg-surface-container-lowest p-space-md rounded-xl shadow-xs border border-[#E4DFD6] transition-all">
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                  <span class="w-6 h-6 rounded-full bg-primary text-on-primary font-code-sm text-code-sm font-bold flex items-center justify-center notranslate" translate="no">1</span>
                  <span class="font-title-md text-label-md text-on-surface font-semibold">Speech Bubble</span>
                  <span class="font-code-sm text-code-sm text-on-surface-variant">• Top Right</span>
                </div>
                <span class="px-2.5 py-0.5 rounded-full bg-secondary-container text-on-secondary-container font-code-sm text-code-sm font-semibold flex items-center gap-1 notranslate" translate="no">
                  <span class="material-symbols-outlined text-[14px]">verified</span>
                  <span>0.98 Confident</span>
                </span>
              </div>
              <div class="mb-2">
                <label class="block font-code-sm text-code-sm text-on-surface-variant mb-1 notranslate" translate="no">OCR Transcription (Raw JA)</label>
                <input class="w-full bg-surface-container-low px-3 py-2 rounded-lg font-body-lg text-body-lg text-on-surface font-medium focus:bg-surface-container-lowest focus:ring-2 focus:ring-primary focus:outline-none transition-all notranslate" translate="no" type="text" value="先生、待ってください！"/>
              </div>
              <div class="flex items-center justify-between text-on-surface-variant pt-1 font-body-sm text-body-sm">
                <div class="flex items-center gap-1.5 text-secondary font-medium">
                  <span class="material-symbols-outlined text-[16px]">menu_book</span>
                  <span>Matches glossary: 先生 (Sensei / Teacher)</span>
                </div>
                <div class="flex items-center gap-3">
                  <button class="text-primary hover:underline font-label-md text-label-md cursor-pointer" type="button">Split Line</button>
                  <button class="text-outline hover:text-on-surface transition-colors font-label-md text-label-md cursor-pointer" type="button">Re-detect</button>
                  <button class="text-error hover:underline font-label-md text-label-md cursor-pointer" type="button">Delete Box</button>
                </div>
              </div>
            </div>

            <!-- CARD ROW 2 (Box #2 Standard) -->
            <div id="ocr-card-2" class="ocr-card bg-surface-container-low p-space-md rounded-xl shadow-xs hover:bg-surface-container-high/50 border border-[#E4DFD6] transition-all">
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                  <span class="w-6 h-6 rounded-full bg-primary-container text-on-primary font-code-sm text-code-sm font-bold flex items-center justify-center notranslate" translate="no">2</span>
                  <span class="font-title-md text-label-md text-on-surface font-semibold">Exclamation Bubble</span>
                  <span class="font-code-sm text-code-sm text-on-surface-variant">• Middle Left</span>
                </div>
                <span class="px-2.5 py-0.5 rounded-full bg-secondary-container text-on-secondary-container font-code-sm text-code-sm font-semibold flex items-center gap-1 notranslate" translate="no">
                  <span class="material-symbols-outlined text-[14px]">check</span>
                  <span>0.94 Confident</span>
                </span>
              </div>
              <div class="mb-2">
                <label class="block font-code-sm text-code-sm text-on-surface-variant mb-1 notranslate" translate="no">OCR Transcription (Raw JA)</label>
                <input class="w-full bg-surface-container-lowest px-3 py-2 rounded-lg font-body-lg text-body-lg text-on-surface font-medium focus:ring-2 focus:ring-primary focus:outline-none transition-all notranslate" translate="no" type="text" value="何があったんだ？！"/>
              </div>
              <div class="flex items-center justify-between text-on-surface-variant pt-1 font-body-sm text-body-sm">
                <span class="font-code-sm text-code-sm text-outline">Detected font style: Bold Manga Gothic</span>
                <div class="flex items-center gap-3">
                  <button class="text-primary hover:underline font-label-md text-label-md cursor-pointer" type="button">Split</button>
                  <button class="text-error hover:underline font-label-md text-label-md cursor-pointer" type="button">Delete</button>
                </div>
              </div>
            </div>

            <!-- CARD ROW 3 (Box #3 SFX Warning State) -->
            <div id="ocr-card-3" class="ocr-card bg-error-container/30 p-space-md rounded-xl shadow-xs ring-2 ring-error transition-all">
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                  <span class="w-6 h-6 rounded-full bg-error text-on-error font-code-sm text-code-sm font-bold flex items-center justify-center notranslate" translate="no">3</span>
                  <span class="font-title-md text-label-md text-error font-semibold">Sound Effect (SFX)</span>
                  <span class="font-code-sm text-code-sm text-on-surface-variant">• Background</span>
                </div>
                <span class="px-2.5 py-0.5 rounded-full bg-error text-on-error font-code-sm text-code-sm font-bold flex items-center gap-1 notranslate" translate="no">
                  <span class="material-symbols-outlined text-[14px]">warning</span>
                  <span>0.52 Low Confidence</span>
                </span>
              </div>
              <!-- Alert Prompt Box -->
              <div class="mb-2 px-3 py-2 rounded-lg bg-error-container text-on-error-container flex items-start gap-2">
                <span class="material-symbols-outlined text-[18px] text-error shrink-0 mt-0.5">info</span>
                <p class="font-body-sm text-body-sm leading-tight">
                  OCR confidence low. Glyphs appear overlaid on screentone texture. Please confirm accuracy against visual canvas.
                </p>
              </div>
              <div class="mb-2">
                <label class="block font-code-sm text-code-sm text-error font-semibold mb-1 notranslate" translate="no">OCR Transcription (Verify Katakana)</label>
                <input class="w-full bg-surface-container-lowest px-3 py-2 rounded-lg font-headline-sm text-headline-sm text-on-surface font-bold ring-2 ring-error focus:ring-2 focus:ring-primary focus:outline-none transition-all notranslate" translate="no" type="text" value="ドカーン"/>
              </div>
              <div class="flex items-center justify-between pt-1">
                <span class="font-body-sm text-body-sm text-on-surface-variant">Predicted meaning: "BOOM / Loud Explosion"</span>
                <div class="flex items-center gap-2">
                  <button class="px-2.5 py-1 rounded-full bg-secondary-container text-on-secondary-container font-label-md text-label-md font-semibold hover:bg-secondary-fixed transition-colors cursor-pointer" type="button">
                    Accept Correction
                  </button>
                  <button class="px-2.5 py-1 rounded-full bg-surface-container text-on-surface-variant font-label-md text-label-md hover:text-on-surface transition-colors cursor-pointer" type="button">
                    Mark Artwork Only
                  </button>
                </div>
              </div>
            </div>

            <!-- CARD ROW 4 (Box #4 Narration) -->
            <div id="ocr-card-4" class="ocr-card bg-surface-container-low p-space-md rounded-xl shadow-xs hover:bg-surface-container-high/50 border border-[#E4DFD6] transition-all">
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                  <span class="w-6 h-6 rounded-full bg-primary-container text-on-primary font-code-sm text-code-sm font-bold flex items-center justify-center notranslate" translate="no">4</span>
                  <span class="font-title-md text-label-md text-on-surface font-semibold">Narration Box</span>
                  <span class="font-code-sm text-code-sm text-on-surface-variant">• Bottom Right</span>
                </div>
                <span class="px-2.5 py-0.5 rounded-full bg-secondary-container text-on-secondary-container font-code-sm text-code-sm font-semibold flex items-center gap-1 notranslate" translate="no">
                  <span class="material-symbols-outlined text-[14px]">check</span>
                  <span>0.96 Confident</span>
                </span>
              </div>
              <div class="mb-2">
                <label class="block font-code-sm text-code-sm text-on-surface-variant mb-1 notranslate" translate="no">OCR Transcription (Raw JA)</label>
                <input class="w-full bg-surface-container-lowest px-3 py-2 rounded-lg font-body-lg text-body-lg text-on-surface font-medium focus:ring-2 focus:ring-primary focus:outline-none transition-all notranslate" translate="no" type="text" value="その時、街全体が揺れた。"/>
              </div>
              <div class="flex items-center justify-between text-on-surface-variant pt-1 font-body-sm text-body-sm">
                <span class="font-code-sm text-code-sm text-outline">Layout: Horizontal Narration Block</span>
                <div class="flex items-center gap-3">
                  <button class="text-primary hover:underline font-label-md text-label-md cursor-pointer" type="button">Split</button>
                  <button class="text-error hover:underline font-label-md text-label-md cursor-pointer" type="button">Delete</button>
                </div>
              </div>
            </div>

          </div>
        </div>

      </div>

      <!-- Sticky Bottom Action Footer -->
      <div class="mt-space-lg bg-surface-container-lowest rounded-xl p-space-md shadow-md flex flex-wrap items-center justify-between gap-4 border border-[#E4DFD6]">
        <!-- Autosave status & Keyboard hint -->
        <div class="flex items-center gap-space-lg">
          <div class="flex items-center gap-2 text-secondary font-label-md text-label-md font-medium">
            <span class="material-symbols-outlined text-[18px]">cloud_done</span>
            <span class="text-on-surface-variant">Changes saved to draft • <span class="text-secondary font-semibold">Live Sync Active</span></span>
          </div>
          <div class="hidden md:flex items-center gap-1.5 text-on-surface-variant font-code-sm text-code-sm">
            <kbd class="px-2 py-0.5 bg-surface-container rounded-sm shadow-2xs font-semibold notranslate" translate="no">Ctrl + Enter</kbd>
            <span>to confirm &amp; next page</span>
          </div>
        </div>

        <!-- Primary / Secondary Action Buttons -->
        <div class="flex items-center gap-3">
          <button class="px-5 py-2.5 rounded-full bg-surface-container text-on-surface hover:bg-surface-container-high transition-colors font-title-md text-label-md flex items-center gap-2 cursor-pointer border border-[#E4DFD6]" type="button">
            <span class="material-symbols-outlined text-[18px]">flag</span>
            <span>Flag for Second Review</span>
          </button>
          <button onclick="confirmAndProceed()" class="px-6 py-2.5 rounded-full bg-primary-container text-on-primary hover:bg-primary shadow-md transition-all font-title-md text-label-md font-semibold flex items-center gap-2 cursor-pointer" type="button">
            <span>Confirm &amp; Proceed to Typesetting</span>
            <span class="material-symbols-outlined text-[18px]">arrow_forward</span>
          </button>
        </div>
      </div>

    </div>
  </main>
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
  }} catch (e) {{
    console.warn("Cross-origin frame navigation fallback triggered:", e);
  }}
  window.location.href = target;
}}

// Box selection synchronizer between Canvas and OCR Cards
function selectBox(boxIndex) {{
  for (let i = 1; i <= 4; i++) {{
    const card = document.getElementById('ocr-card-' + i);
    const box = document.getElementById('overlay-box-' + i);
    if (card) {{
      card.classList.remove('active-ocr');
      if (i === boxIndex) {{
        card.classList.add('active-ocr');
        card.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
      }}
    }}
    if (box) {{
      if (i === boxIndex) {{
        box.classList.add('ring-4');
      }} else {{
        box.classList.remove('ring-4');
      }}
    }}
  }}
}}

// Zoom handler
let currentZoom = 1.0;
function zoomCanvas(delta) {{
  currentZoom = Math.max(0.6, Math.min(1.8, currentZoom + delta));
  const canvas = document.getElementById('manga-canvas');
  const label = document.getElementById('zoom-label');
  if (canvas) {{
    canvas.style.transform = `scale(${{currentZoom}})`;
    canvas.style.transformOrigin = 'center center';
    canvas.style.transition = 'transform 0.2s ease';
  }}
  if (label) {{
    label.innerText = Math.round(currentZoom * 100) + '%';
  }}
}}

// Page navigation
let currentPage = 14;
const totalPages = 24;
function changePage(delta) {{
  currentPage = Math.max(1, Math.min(totalPages, currentPage + delta));
  const display = document.getElementById('current-page-display');
  if (display) {{
    display.innerText = 'Page ' + currentPage;
  }}
}}

// Confirm and proceed to typesetting
function confirmAndProceed() {{
  navigateParent('typesetting');
}}

// Keyboard shortcut: Ctrl + Enter
document.addEventListener('keydown', function(e) {{
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {{
    confirmAndProceed();
  }}
}});
</script>

</body>
</html>
"""

# Render the Google Stitch component seamlessly
components.html(review_studio_html, height=1150, scrolling=True)
