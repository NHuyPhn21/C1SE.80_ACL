"""ACL Live Typesetting Editor — Speech Bubble Typography Studio — Screen ACL-08.

Pixel-perfect implementation of Google Stitch Project 'UX/UI_ACL' (ID: 15081338219515375601).
Screen: ACL-08: Live Typesetting Editor — Speech Bubble Typography Studio.
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

typesetting_html = f"""<!DOCTYPE html>
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
      <a aria-current="page" class="flex items-center gap-space-sm px-space-sm py-2 rounded-lg bg-primary-container text-on-primary font-title-md font-semibold cursor-pointer" onclick="navigateParent('typesetting')">
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
      <a class="font-medium text-on-surface hover:text-primary-container transition-colors cursor-pointer" onclick="navigateParent('workspace')">Workspace</a>
      <span class="material-symbols-outlined text-[16px] text-outline">chevron_right</span>
      <span class="text-primary-container font-semibold">Typesetting Studio</span>
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

      <!-- Top Workspace Context Bar -->
      <div class="flex flex-col md:flex-row md:items-center justify-between pb-space-md gap-space-sm">
        <div class="flex flex-col">
          <div class="flex items-center gap-2">
            <h1 class="font-headline-md text-headline-md text-on-surface tracking-tight">Live Typesetting Editor</h1>
            <span class="px-space-xs py-0.5 rounded-full bg-primary/10 text-primary font-code-sm text-code-sm font-medium notranslate" translate="no">BETA-PRO</span>
          </div>
          <div class="flex items-center gap-2 font-body-md text-body-md text-on-surface-variant flex-wrap">
            <a class="hover:text-primary transition-colors cursor-pointer font-medium text-on-surface notranslate" translate="no" onclick="navigateParent('workspace')">Shonen Weekly #112</a>
            <span>•</span>
            <span id="header-page-label">Page 14</span>
            <span class="text-outline-variant">/</span>
            <span class="font-code-sm text-code-sm text-outline notranslate" translate="no">BATCH #CH-112-RAW</span>
            <a class="text-xs font-semibold px-2 py-0.5 rounded-full bg-surface-container text-primary hover:bg-surface-container-high transition-colors cursor-pointer ml-1 inline-flex items-center gap-1" onclick="navigateParent('review-studio')" title="Back to Review Studio">
              <span class="material-symbols-outlined text-[13px]">arrow_back</span>
              <span>Review Studio</span>
            </a>
          </div>
        </div>

        <!-- Center Pagination Control -->
        <div class="inline-flex items-center gap-1.5 p-1 bg-surface-container rounded-full shadow-sm self-start md:self-center border border-[#E4DFD6]">
          <button onclick="changePage(-1)" class="inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-on-surface hover:bg-surface-container-lowest transition-all font-label-md text-label-md font-medium cursor-pointer" type="button">
            <span class="material-symbols-outlined text-[18px]">arrow_back</span>
            <span>Prev Page</span>
          </button>
          <div class="relative inline-flex items-center gap-1 px-3 py-1 bg-surface-container-lowest rounded-full shadow-xs cursor-pointer hover:bg-surface-container-low transition-colors">
            <span class="font-label-md text-label-md font-semibold text-on-surface" id="pagination-display">Page 14 of 24</span>
            <span class="material-symbols-outlined text-[16px] text-outline">unfold_more</span>
          </div>
          <button onclick="changePage(1)" class="inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-on-surface hover:bg-surface-container-lowest transition-all font-label-md text-label-md font-medium cursor-pointer" type="button">
            <span>Next Page</span>
            <span class="material-symbols-outlined text-[18px]">arrow_forward</span>
          </button>
        </div>

        <!-- Right Status Tag -->
        <div class="flex items-center gap-2">
          <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-secondary-container/60 text-on-secondary-container font-label-md text-label-md font-medium">
            <span class="material-symbols-outlined text-[16px] text-secondary">verified</span>
            <span class="notranslate" translate="no">LaMa Inpainting Cleaned</span>
          </div>
        </div>
      </div>

      <!-- Main Split Editor Workspace -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-space-md w-full items-start">

        <!-- LEFT PANEL: Inpainted Canvas Stage (col-span-7) -->
        <div class="lg:col-span-7 bg-surface-container-lowest rounded-xl p-space-md shadow-sm flex flex-col gap-space-sm border border-[#E4DFD6]">
          <!-- Stage Subheader -->
          <div class="flex items-center justify-between pb-2 border-b border-[#E4DFD6]">
            <div class="flex items-center gap-2">
              <span class="font-title-md text-title-md text-on-surface font-semibold">Inpainted Canvas &amp; Live Text Overlay</span>
              <span class="hidden sm:inline-block px-2 py-0.5 rounded bg-surface-container text-on-surface-variant font-code-sm text-code-sm notranslate" translate="no">1600 × 2560 px • Cleaned (LaMa GAN)</span>
            </div>
            <label class="inline-flex items-center gap-2 cursor-pointer select-none">
              <input class="sr-only peer" id="toggle-original-bg" type="checkbox"/>
              <span class="w-7 h-4 bg-surface-container-high rounded-full peer peer-checked:bg-primary-container transition-colors relative after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:w-3 after:h-3 after:rounded-full after:transition-transform peer-checked:after:translate-x-3"></span>
              <span class="font-body-sm text-body-sm text-on-surface-variant">Show Original OCR</span>
            </label>
          </div>

          <!-- Manga Canvas Viewport -->
          <div class="relative w-full rounded-lg bg-inverse-surface p-space-md flex items-center justify-center min-h-[620px] overflow-hidden select-none" id="viewport-box">
            <!-- Live Manga Page Sheet Mockup -->
            <div class="relative w-full max-w-[480px] aspect-[1/1.55] bg-[#FFFFFF] shadow-2xl rounded-sm overflow-hidden flex flex-col justify-between p-4" id="manga-sheet">
              <!-- Comic Panel Grids -->
              <div class="w-full h-full grid grid-cols-2 grid-rows-3 gap-2 p-3 bg-[#FCFCFD]">
                <!-- Panel 1: Dynamic Action (Top) -->
                <div class="col-span-2 row-span-1 rounded-sm bg-gradient-to-br from-surface-dim/40 via-surface-variant/20 to-surface-dim/30 relative overflow-hidden flex items-end p-2">
                  <svg class="absolute inset-0 w-full h-full opacity-35 text-on-surface" fill="none" viewbox="0 0 400 200">
                    <path d="M0 0L400 200M400 0L0 200M200 0L200 200M0 100L400 100M50 0L350 200M350 0L50 200" stroke="currentColor" stroke-dasharray="3 3" stroke-width="1.5"></path>
                    <circle cx="200" cy="100" fill="none" r="45" stroke="currentColor" stroke-width="2"></circle>
                  </svg>
                  <div class="relative z-10 text-[9px] font-code-sm text-outline uppercase tracking-widest bg-surface-container-lowest/80 px-1 rounded notranslate" translate="no">Panel 01 • Dynamic Perspective</div>
                </div>

                <!-- Panel 2: Character Focus (Middle-Left) -->
                <div class="col-span-1 row-span-1 rounded-sm bg-surface-container relative overflow-hidden flex flex-col justify-between p-2">
                  <div class="w-16 h-16 rounded-full bg-outline-variant/30 self-center mt-3 flex items-center justify-center">
                    <span class="material-symbols-outlined text-outline-variant text-[28px]">face</span>
                  </div>
                  <div class="text-[8px] font-code-sm text-outline bg-surface-container-lowest/90 px-1 rounded self-start notranslate" translate="no">Panel 02 • Close-up</div>
                </div>

                <!-- Panel 3: Sound Effect Inpainted Core (Middle-Right) -->
                <div class="col-span-1 row-span-1 rounded-sm bg-surface-variant/30 relative overflow-hidden flex items-center justify-center p-2">
                  <svg class="absolute inset-0 w-full h-full opacity-20 text-on-surface" viewbox="0 0 100 100">
                    <polygon fill="currentColor" points="50,5 64,38 98,40 70,62 80,95 50,75 20,95 30,62 2,40 36,38"></polygon>
                  </svg>
                  <div class="text-[8px] font-code-sm text-outline absolute bottom-1 right-1 bg-surface-container-lowest/80 px-1 rounded notranslate" translate="no">Panel 03 • Impact</div>
                </div>

                <!-- Panel 4: Panoramic Destruction (Bottom) -->
                <div class="col-span-2 row-span-1 rounded-sm bg-gradient-to-t from-surface-dim/40 to-transparent relative overflow-hidden flex items-end justify-between p-2">
                  <div class="w-full flex items-center justify-between text-[8px] font-code-sm text-outline bg-surface-container-lowest/90 px-1.5 py-0.5 rounded notranslate" translate="no">
                    <span>Panel 04 • Cityscape Horizon</span>
                    <span>100% Inpainted (Artifacts: 0.02)</span>
                  </div>
                </div>
              </div>

              <!-- OVERLAY 1: ACTIVE SPEECH BUBBLE #1 (Top-Right) -->
              <div class="absolute top-[8%] right-[8%] z-20 group cursor-pointer" id="bubble-target-1">
                <div class="relative bg-surface-container-lowest rounded-[28px] px-5 py-4 shadow-lg min-w-[155px] text-center transition-transform hover:scale-[1.01] ring-2 ring-primary-container">
                  <div class="absolute -top-3.5 left-1/2 -translate-x-1/2 bg-primary-container text-on-primary font-code-sm text-code-sm font-semibold px-2.5 py-0.5 rounded-full flex items-center gap-1 shadow-sm whitespace-nowrap notranslate" translate="no">
                    <span class="w-1.5 h-1.5 rounded-full bg-secondary-fixed"></span>
                    <span>#1 Selected • Active</span>
                  </div>
                  <div class="absolute -top-1 -left-1 w-2.5 h-2.5 bg-surface-container-lowest border border-primary-container rounded-xs"></div>
                  <div class="absolute -top-1 -right-1 w-2.5 h-2.5 bg-surface-container-lowest border border-primary-container rounded-xs"></div>
                  <div class="absolute -bottom-1 -left-1 w-2.5 h-2.5 bg-surface-container-lowest border border-primary-container rounded-xs"></div>
                  <div class="absolute -bottom-1 -right-1 w-2.5 h-2.5 bg-surface-container-lowest border border-primary-container rounded-xs"></div>
                  
                  <!-- Typeset Live Vietnamese Dialogue -->
                  <div class="font-headline-sm text-headline-sm text-on-surface font-bold leading-tight select-text tracking-wide drop-shadow-[0_1px_1px_rgba(255,255,255,0.9)]" id="canvas-text-1">
                    Thầy ơi,<br/>xin hãy đợi em với!
                  </div>
                  <div class="absolute -bottom-2 right-6 w-3 h-3 bg-surface-container-lowest rotate-45 border-r border-b border-primary-container"></div>
                </div>
              </div>

              <!-- OVERLAY 2: EXCLAMATION BUBBLE #2 (Middle-Left) -->
              <div class="absolute top-[38%] left-[7%] z-10 group cursor-pointer" id="bubble-target-2">
                <div class="relative bg-surface-container-lowest/95 rounded-[30px] px-4 py-3 shadow-sm min-w-[140px] text-center border border-dashed border-outline-variant hover:border-primary-container transition-colors">
                  <div class="absolute -top-3 left-3 bg-surface-container text-on-surface-variant font-code-sm text-code-sm px-2 py-0.5 rounded-full notranslate" translate="no">
                    #2 Dialogue
                  </div>
                  <div class="font-body-md text-body-md font-semibold text-on-surface leading-snug">
                    Chuyện gì đã<br/>xảy ra thế này?!
                  </div>
                </div>
              </div>

              <!-- OVERLAY 3: CENTER BACKGROUND SFX #3 -->
              <div class="absolute top-[44%] right-[12%] z-10 group cursor-pointer" id="bubble-target-3">
                <div class="relative px-3 py-1.5 flex flex-col items-center">
                  <div class="absolute -top-3 right-0 bg-surface-container text-on-surface-variant font-code-sm text-code-sm px-2 py-0.2 rounded-full notranslate" translate="no">
                    #3 SFX
                  </div>
                  <div class="font-headline-lg text-headline-lg font-bold tracking-tighter text-on-surface italic transform -rotate-6 select-none" style="text-shadow: -2px -2px 0 #fff, 2px -2px 0 #fff, -2px 2px 0 #fff, 2px 2px 0 #fff;">
                    *RẦM RẦM*
                  </div>
                  <span class="font-code-sm text-code-sm text-outline-variant uppercase tracking-wider bg-surface-container-lowest/80 px-1 rounded -mt-1 notranslate" translate="no">[Explosion SFX]</span>
                </div>
              </div>

              <!-- OVERLAY 4: NARRATION RECTANGLE #4 (Bottom-Right) -->
              <div class="absolute bottom-[8%] right-[6%] left-[28%] z-10 group cursor-pointer" id="bubble-target-4">
                <div class="relative bg-surface-container-lowest/95 rounded-md px-3.5 py-2.5 shadow-sm border border-dashed border-outline-variant hover:border-primary-container transition-colors">
                  <div class="absolute -top-2.5 left-2 bg-surface-container text-on-surface-variant font-code-sm text-code-sm px-1.5 py-0.2 rounded notranslate" translate="no">
                    #4 Narration Box
                  </div>
                  <p class="font-body-sm text-body-sm text-on-surface leading-normal text-left font-medium">
                    Vào lúc đó, toàn bộ thành phố rung chuyển dữ dội dưới làn sương dày đặc.
                  </p>
                </div>
              </div>

            </div>

            <!-- Floating Bottom Canvas Utility HUD -->
            <div class="absolute bottom-4 inset-x-4 flex items-center justify-between pointer-events-none px-2">
              <div class="pointer-events-auto inline-flex items-center gap-1 bg-surface-container-lowest/90 backdrop-blur-md px-2 py-1 rounded-full shadow-md text-on-surface border border-[#E4DFD6]">
                <button onclick="zoomCanvas(-0.1)" aria-label="Zoom out" class="w-7 h-7 flex items-center justify-center rounded-full hover:bg-surface-container transition-colors cursor-pointer" type="button">
                  <span class="material-symbols-outlined text-[16px]">remove</span>
                </button>
                <span class="font-code-sm text-code-sm px-1 font-semibold" id="zoom-value-label">100%</span>
                <button onclick="zoomCanvas(0.1)" aria-label="Zoom in" class="w-7 h-7 flex items-center justify-center rounded-full hover:bg-surface-container transition-colors cursor-pointer" type="button">
                  <span class="material-symbols-outlined text-[16px]">add</span>
                </button>
                <div class="w-px h-4 bg-outline-variant mx-1"></div>
                <button onclick="resetZoom()" class="inline-flex items-center gap-1 px-2 py-1 rounded-full hover:bg-surface-container text-on-surface font-label-md text-label-md transition-colors cursor-pointer" type="button">
                  <span class="material-symbols-outlined text-[15px]">fit_screen</span>
                  <span class="hidden sm:inline">Fit</span>
                </button>
              </div>

              <div class="pointer-events-auto inline-flex items-center gap-2 bg-surface-container-lowest/90 backdrop-blur-md px-2.5 py-1 rounded-full shadow-md border border-[#E4DFD6]">
                <button class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-on-surface hover:bg-surface-container font-label-md text-label-md transition-colors cursor-pointer" type="button">
                  <span class="material-symbols-outlined text-[16px]">grid_4x4</span>
                  <span>Guides</span>
                </button>
                <button class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-surface-container text-primary font-label-md text-label-md font-semibold hover:bg-surface-container-high transition-colors cursor-pointer" type="button">
                  <span class="material-symbols-outlined text-[16px]">auto_fix_high</span>
                  <span>Re-inpaint Bubble</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- RIGHT PANEL: Typography Inspector & Controls (col-span-5) -->
        <div class="lg:col-span-5 bg-surface-container-lowest rounded-xl p-space-lg shadow-sm flex flex-col gap-space-md border border-[#E4DFD6]">
          <!-- Panel Header -->
          <div class="flex items-center justify-between pb-2 border-b border-[#E4DFD6]">
            <div class="flex flex-col">
              <h2 class="font-headline-sm text-headline-sm text-on-surface font-semibold">Typography Settings</h2>
              <span class="font-body-sm text-body-sm text-on-surface-variant">Lettering styling, kerning &amp; layout engine</span>
            </div>
            <div class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-primary-fixed text-on-primary-fixed font-code-sm text-code-sm font-semibold notranslate" translate="no">
              <span class="w-1.5 h-1.5 rounded-full bg-primary"></span>
              <span>Bubble #1 (Dialogue)</span>
            </div>
          </div>

          <!-- CONTROL 1: Translated Vietnamese Text Input -->
          <div class="flex flex-col gap-1.5">
            <div class="flex items-center justify-between">
              <label class="font-code-sm text-code-sm uppercase tracking-wider font-semibold text-on-surface-variant" for="vn-text-editor">
                Translated Vietnamese Text
              </label>
              <span class="font-code-sm text-code-sm text-secondary font-medium">99.4% Match</span>
            </div>
            <div class="relative">
              <textarea class="w-full bg-surface-container-low rounded-lg p-3 font-body-md text-body-md text-on-surface focus:outline-none focus:ring-2 focus:ring-primary-container transition-all resize-none shadow-inner border border-transparent focus:border-[#E4DFD6]" id="vn-text-editor" placeholder="Enter translated dialogue..." rows="3">Thầy ơi, xin hãy đợi em với!</textarea>
            </div>
            <div class="flex items-center justify-between font-body-sm text-body-sm text-on-surface-variant">
              <span class="inline-flex items-center gap-1">
                <span class="material-symbols-outlined text-[14px] text-primary">auto_awesome</span>
                <span class="notranslate" translate="no">Translated by Gemini 1.5 Pro</span>
              </span>
              <span class="text-outline">Term base: <strong class="text-on-surface notranslate" translate="no">Sensei → Thầy</strong></span>
            </div>
          </div>

          <!-- CONTROL 2: Font Family & Size Grid -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-space-sm">
            <!-- Font Family Selector -->
            <div class="flex flex-col gap-1.5">
              <label class="font-code-sm text-code-sm uppercase tracking-wider font-semibold text-on-surface-variant" for="font-family-select">
                Font Family
              </label>
              <div class="relative">
                <select class="w-full appearance-none bg-surface-container-low text-on-surface font-title-md text-body-md rounded-lg py-2.5 pl-3 pr-8 focus:outline-none focus:ring-2 focus:ring-primary-container border border-transparent hover:border-[#E4DFD6] transition-all cursor-pointer" id="font-family-select">
                  <option selected value="Plus Jakarta Sans">Plus Jakarta Sans (Default)</option>
                  <option value="Sora">Sora Display</option>
                  <option value="'CC Wild Words', sans-serif">CC Wild Words</option>
                  <option value="'Anime Ace', sans-serif">Anime Ace Bold</option>
                </select>
                <span class="material-symbols-outlined absolute right-2.5 top-3 text-[18px] text-outline pointer-events-none">expand_more</span>
              </div>
            </div>

            <!-- Font Size Numerical Stepper -->
            <div class="flex flex-col gap-1.5">
              <label class="font-code-sm text-code-sm uppercase tracking-wider font-semibold text-on-surface-variant">
                Font Size
              </label>
              <div class="flex items-center bg-surface-container-low rounded-lg p-1 border border-transparent hover:border-[#E4DFD6]">
                <button class="w-8 h-8 rounded-md bg-surface-container hover:bg-surface-container-high text-on-surface flex items-center justify-center transition-colors cursor-pointer" id="font-dec" type="button">
                  <span class="material-symbols-outlined text-[16px]">remove</span>
                </button>
                <div class="flex-1 text-center font-code-md text-code-md font-semibold text-on-surface" id="font-size-display">
                  18 px
                </div>
                <button class="w-8 h-8 rounded-md bg-surface-container hover:bg-surface-container-high text-on-surface flex items-center justify-center transition-colors cursor-pointer" id="font-inc" type="button">
                  <span class="material-symbols-outlined text-[16px]">add</span>
                </button>
              </div>
            </div>
          </div>

          <!-- CONTROL 3: Text Alignment Segmented Control -->
          <div class="flex flex-col gap-1.5">
            <label class="font-code-sm text-code-sm uppercase tracking-wider font-semibold text-on-surface-variant">
              Text Alignment &amp; Flow
            </label>
            <div class="grid grid-cols-3 gap-1 bg-surface-container-low p-1 rounded-lg">
              <button onclick="setTextAlign('left')" id="btn-align-left" class="py-1.5 rounded-md text-on-surface-variant hover:text-on-surface hover:bg-surface-container flex items-center justify-center transition-all cursor-pointer" type="button">
                <span class="material-symbols-outlined text-[18px]">format_align_left</span>
              </button>
              <button onclick="setTextAlign('center')" id="btn-align-center" class="py-1.5 rounded-md bg-primary-container text-on-primary flex items-center justify-center shadow-xs transition-all cursor-pointer" type="button">
                <span class="material-symbols-outlined text-[18px]">format_align_center</span>
              </button>
              <button onclick="setTextAlign('right')" id="btn-align-right" class="py-1.5 rounded-md text-on-surface-variant hover:text-on-surface hover:bg-surface-container flex items-center justify-center transition-all cursor-pointer" type="button">
                <span class="material-symbols-outlined text-[18px]">format_align_right</span>
              </button>
            </div>
          </div>

          <!-- CONTROL 4: Sliders for Line Height & Kerning -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-space-md pt-1">
            <!-- Line Height -->
            <div class="flex flex-col gap-1.5">
              <div class="flex items-center justify-between">
                <span class="font-code-sm text-code-sm font-semibold text-on-surface-variant">Line Height</span>
                <span class="font-code-sm text-code-sm px-1.5 py-0.5 rounded bg-surface-container text-on-surface font-semibold" id="line-height-val">1.20x</span>
              </div>
              <input oninput="updateLineHeight(this.value)" class="w-full accent-primary h-1.5 bg-surface-container-high rounded-lg cursor-pointer" max="2.0" min="0.8" step="0.05" type="range" value="1.20"/>
            </div>

            <!-- Kerning / Letter Spacing -->
            <div class="flex flex-col gap-1.5">
              <div class="flex items-center justify-between">
                <span class="font-code-sm text-code-sm font-semibold text-on-surface-variant">Letter Spacing</span>
                <span class="font-code-sm text-code-sm px-1.5 py-0.5 rounded bg-surface-container text-on-surface font-semibold" id="letter-spacing-val">+0.5 px</span>
              </div>
              <input oninput="updateLetterSpacing(this.value)" class="w-full accent-primary h-1.5 bg-surface-container-high rounded-lg cursor-pointer" max="4.0" min="-2.0" step="0.1" type="range" value="0.5"/>
            </div>
          </div>

          <!-- CONTROL 5: Typographic Badges & Stroke Toggles -->
          <div class="flex flex-col gap-2 pt-1">
            <span class="font-code-sm text-code-sm uppercase tracking-wider font-semibold text-on-surface-variant">
              Format Styles &amp; Readability
            </span>
            <div class="flex flex-wrap items-center gap-2">
              <button onclick="toggleBold()" id="btn-bold" class="px-3.5 py-1.5 rounded-lg bg-primary-container text-on-primary font-code-md text-code-md font-bold shadow-xs cursor-pointer" type="button">
                B
              </button>
              <button onclick="toggleItalic()" id="btn-italic" class="px-3.5 py-1.5 rounded-lg bg-surface-container hover:bg-surface-container-high text-on-surface font-code-md text-code-md italic transition-colors cursor-pointer" type="button">
                I
              </button>
              <label class="inline-flex items-center gap-2 ml-auto cursor-pointer select-none">
                <input checked id="stroke-toggle" onchange="toggleStroke(this.checked)" class="sr-only peer" type="checkbox"/>
                <span class="w-8 h-4.5 bg-surface-container-high rounded-full peer peer-checked:bg-secondary transition-colors relative after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:w-3.5 after:h-3.5 after:rounded-full after:transition-transform peer-checked:after:translate-x-3.5"></span>
                <span class="font-body-sm text-body-sm text-on-surface font-medium">1.5px White Stroke</span>
              </label>
            </div>
          </div>

          <!-- Global Batch Application & Defaults -->
          <div class="pt-2 flex flex-col gap-2 border-t border-[#E4DFD6]">
            <label class="inline-flex items-center gap-2.5 cursor-pointer">
              <input checked class="w-4 h-4 rounded text-primary focus:ring-primary accent-primary" type="checkbox"/>
              <span class="font-body-sm text-body-sm text-on-surface font-medium">Apply this font style to all speech bubbles on Page 14</span>
            </label>
            <div class="flex items-center justify-between pt-1">
              <button onclick="resetDefaults()" class="inline-flex items-center gap-1 font-body-sm text-body-sm text-primary hover:text-primary-container transition-colors font-medium cursor-pointer" type="button">
                <span class="material-symbols-outlined text-[16px]">restart_alt</span>
                <span>Reset to Auto-Fit Default</span>
              </button>
              <span class="font-code-sm text-code-sm text-outline">Auto-hyphenation: Enabled</span>
            </div>
          </div>

        </div>

      </div>

      <!-- BOTTOM ACTION BAR: Batch Progress & Navigation Footer -->
      <div class="w-full bg-surface-container-lowest rounded-xl p-space-md shadow-sm mt-space-md flex flex-col sm:flex-row items-center justify-between gap-space-md border border-[#E4DFD6]">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-full bg-secondary-container flex items-center justify-center text-on-secondary-container">
            <span class="material-symbols-outlined text-[20px]">check</span>
          </div>
          <div class="flex flex-col">
            <span class="font-title-md text-body-md font-semibold text-on-surface">Bubble 1 of 4 configured • Auto-typesetting applied</span>
            <span class="font-body-sm text-body-sm text-on-surface-variant flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full bg-secondary"></span>
              <span>Unsaved changes: None (Autosynced to cloud)</span>
            </span>
          </div>
        </div>

        <div class="flex items-center gap-3 w-full sm:w-auto justify-end">
          <button onclick="navigateParent('review-studio')" class="inline-flex items-center justify-center px-6 h-11 rounded-full bg-surface-container hover:bg-surface-container-high text-on-surface font-title-md text-label-md font-semibold transition-all cursor-pointer border border-[#E4DFD6]" type="button">
            <span class="material-symbols-outlined text-[18px] mr-1">arrow_back</span>
            <span>Review Studio</span>
          </button>
          <button onclick="navigateParent('queue-monitor')" class="inline-flex items-center justify-center px-8 h-11 rounded-full bg-primary-container hover:bg-primary text-on-primary font-title-md text-label-md font-bold shadow-md hover:scale-[1.01] active:scale-[0.99] transition-all cursor-pointer" type="button">
            <span>Mark Page Complete &amp; View Queue</span>
            <span class="material-symbols-outlined text-[18px] ml-1.5">arrow_forward</span>
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

// Interactive client behavior for Typesetting Editor
const editor = document.getElementById('vn-text-editor');
const canvasTarget = document.getElementById('canvas-text-1');
const fontSizeDisplay = document.getElementById('font-size-display');
const fontInc = document.getElementById('font-inc');
const fontDec = document.getElementById('font-dec');
const familySelect = document.getElementById('font-family-select');

let currentSize = 18;
let isBold = true;
let isItalic = false;

if (editor && canvasTarget) {{
  editor.addEventListener('input', (e) => {{
    const formatted = e.target.value.replace(/\\n/g, '<br/>');
    canvasTarget.innerHTML = formatted || '...';
  }});
}}

if (fontInc && fontSizeDisplay && canvasTarget) {{
  fontInc.addEventListener('click', () => {{
    if (currentSize < 36) {{
      currentSize += 1;
      fontSizeDisplay.textContent = currentSize + ' px';
      canvasTarget.style.fontSize = currentSize + 'px';
    }}
  }});
}}

if (fontDec && fontSizeDisplay && canvasTarget) {{
  fontDec.addEventListener('click', () => {{
    if (currentSize > 10) {{
      currentSize -= 1;
      fontSizeDisplay.textContent = currentSize + ' px';
      canvasTarget.style.fontSize = currentSize + 'px';
    }}
  }});
}}

if (familySelect && canvasTarget) {{
  familySelect.addEventListener('change', (e) => {{
    canvasTarget.style.fontFamily = e.target.value;
  }});
}}

function setTextAlign(align) {{
  if (canvasTarget) {{
    canvasTarget.style.textAlign = align;
  }}
  ['left', 'center', 'right'].forEach(a => {{
    const btn = document.getElementById('btn-align-' + a);
    if (btn) {{
      if (a === align) {{
        btn.classList.add('bg-primary-container', 'text-on-primary', 'shadow-xs');
        btn.classList.remove('text-on-surface-variant');
      }} else {{
        btn.classList.remove('bg-primary-container', 'text-on-primary', 'shadow-xs');
        btn.classList.add('text-on-surface-variant');
      }}
    }}
  }});
}}

function updateLineHeight(val) {{
  const label = document.getElementById('line-height-val');
  if (label) label.innerText = parseFloat(val).toFixed(2) + 'x';
  if (canvasTarget) canvasTarget.style.lineHeight = val;
}}

function updateLetterSpacing(val) {{
  const label = document.getElementById('letter-spacing-val');
  if (label) label.innerText = (parseFloat(val) >= 0 ? '+' : '') + parseFloat(val).toFixed(1) + ' px';
  if (canvasTarget) canvasTarget.style.letterSpacing = val + 'px';
}}

function toggleBold() {{
  isBold = !isBold;
  const btn = document.getElementById('btn-bold');
  if (canvasTarget) canvasTarget.style.fontWeight = isBold ? 'bold' : 'normal';
  if (btn) {{
    if (isBold) {{
      btn.classList.add('bg-primary-container', 'text-on-primary');
      btn.classList.remove('bg-surface-container', 'text-on-surface');
    }} else {{
      btn.classList.remove('bg-primary-container', 'text-on-primary');
      btn.classList.add('bg-surface-container', 'text-on-surface');
    }}
  }}
}}

function toggleItalic() {{
  isItalic = !isItalic;
  const btn = document.getElementById('btn-italic');
  if (canvasTarget) canvasTarget.style.fontStyle = isItalic ? 'italic' : 'normal';
  if (btn) {{
    if (isItalic) {{
      btn.classList.add('bg-primary-container', 'text-on-primary');
      btn.classList.remove('bg-surface-container', 'text-on-surface');
    }} else {{
      btn.classList.remove('bg-primary-container', 'text-on-primary');
      btn.classList.add('bg-surface-container', 'text-on-surface');
    }}
  }}
}}

function toggleStroke(checked) {{
  if (canvasTarget) {{
    canvasTarget.style.textShadow = checked ? '-1.5px -1.5px 0 #fff, 1.5px -1.5px 0 #fff, -1.5px 1.5px 0 #fff, 1.5px 1.5px 0 #fff' : 'none';
  }}
}}

function resetDefaults() {{
  currentSize = 18;
  if (fontSizeDisplay) fontSizeDisplay.textContent = '18 px';
  if (canvasTarget) {{
    canvasTarget.style.fontSize = '18px';
    canvasTarget.style.fontFamily = 'Plus Jakarta Sans';
    canvasTarget.style.textAlign = 'center';
    canvasTarget.style.lineHeight = '1.2';
    canvasTarget.style.letterSpacing = '0.5px';
    canvasTarget.style.fontWeight = 'bold';
    canvasTarget.style.fontStyle = 'normal';
  }}
  setTextAlign('center');
}}

// Page navigation
let currentPage = 14;
const totalPages = 24;
function changePage(delta) {{
  currentPage = Math.max(1, Math.min(totalPages, currentPage + delta));
  const display = document.getElementById('pagination-display');
  const headerDisplay = document.getElementById('header-page-label');
  if (display) display.innerText = 'Page ' + currentPage + ' of ' + totalPages;
  if (headerDisplay) headerDisplay.innerText = 'Page ' + currentPage;
}}

let zoomLevel = 1.0;
function zoomCanvas(delta) {{
  zoomLevel = Math.max(0.7, Math.min(1.5, zoomLevel + delta));
  const sheet = document.getElementById('manga-sheet');
  const label = document.getElementById('zoom-value-label');
  if (sheet) sheet.style.transform = `scale(${{zoomLevel}})`;
  if (label) label.innerText = Math.round(zoomLevel * 100) + '%';
}}

function resetZoom() {{
  zoomLevel = 1.0;
  const sheet = document.getElementById('manga-sheet');
  const label = document.getElementById('zoom-value-label');
  if (sheet) sheet.style.transform = 'scale(1)';
  if (label) label.innerText = '100%';
}}
</script>

</body>
</html>
"""

# Render the Google Stitch component seamlessly
components.html(typesetting_html, height=1150, scrolling=True)
