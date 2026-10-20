"""ACL Personal Settings — API Key, Glossary CRUD & Real-Time Logs — Screens ACL-10, ACL-11, ACL-12.

Pixel-perfect implementation of Google Stitch Project 'UX/UI_ACL' (ID: 15081338219515375601).
Screens:
- ACL-10: Cloud LLM API Key & Monthly Quota
- ACL-11: Custom Glossary CRUD & Add Term Modal
- ACL-12: Real-Time System Logs Terminal Console
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

settings_html = f"""<!DOCTYPE html>
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

.console-terminal {{
  background-color: #1c1a17;
  color: #f6f0ea;
  font-family: 'JetBrains Mono', monospace;
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
      <a class="flex items-center gap-space-sm px-space-sm py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface transition-colors font-body-md text-body-md cursor-pointer" onclick="navigateParent('queue-monitor')">
        <span class="material-symbols-outlined text-[20px]">monitoring</span>
        <span>Queue Monitor</span>
      </a>
      <a aria-current="page" class="flex items-center gap-space-sm px-space-sm py-2 rounded-lg bg-primary-container text-on-primary font-title-md font-semibold cursor-pointer" onclick="navigateParent('settings')">
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
      <span class="text-primary-container font-semibold">Personal Settings</span>
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
  <main class="relative pt-16 bg-surface min-h-screen">
    <div class="px-gutter-lg py-margin-lg max-w-5xl mx-auto w-full">

      <!-- Top Header & Metadata Area -->
      <div class="flex flex-col md:flex-row md:items-end justify-between gap-space-md mb-space-lg">
        <div>
          <div class="flex items-center gap-space-xs text-on-surface-variant font-code-sm text-code-sm uppercase tracking-wider mb-space-xs">
            <span>Security &amp; Automation</span>
            <span>/</span>
            <span class="notranslate" translate="no">Cluster 04</span>
          </div>
          <h1 class="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">Personal Settings</h1>
          <p class="font-body-md text-body-md text-on-surface-variant mt-1">Manage your API access, custom glossary and system diagnostics.</p>
        </div>
        <div class="flex items-center gap-space-xs bg-surface-container-high px-space-md py-space-xs rounded-full self-start md:self-auto border border-[#E4DFD6]">
          <span class="w-2 h-2 rounded-full bg-secondary"></span>
          <span class="font-code-sm text-code-sm text-on-surface notranslate" translate="no">Environment: Production • v2.4.0-prod</span>
        </div>
      </div>

      <!-- Tab Navigation -->
      <div class="flex items-center gap-space-lg bg-surface-container-low px-space-md pt-space-xs rounded-xl mb-space-lg border border-[#E4DFD6]">
        <button onclick="switchTab('api')" id="tab-btn-api" class="flex items-center gap-space-xs py-space-sm font-title-md text-title-md text-primary-container bg-surface-container-lowest px-space-md rounded-lg shadow-sm cursor-pointer transition-all" type="button">
          <span class="material-symbols-outlined text-[18px]">key</span>
          <span>API Key Config</span>
        </button>
        <button onclick="switchTab('glossary')" id="tab-btn-glossary" class="flex items-center gap-space-xs py-space-sm font-body-md text-body-md text-on-surface-variant hover:text-on-surface px-space-sm rounded-lg transition-colors cursor-pointer" type="button">
          <span class="material-symbols-outlined text-[18px]">menu_book</span>
          <span>Custom Glossary</span>
          <span class="bg-surface-container-highest text-on-surface-variant text-[10px] font-code-sm px-1.5 py-0.5 rounded-full" id="glossary-count-badge">4</span>
        </button>
        <button onclick="switchTab('logs')" id="tab-btn-logs" class="flex items-center gap-space-xs py-space-sm font-body-md text-body-md text-on-surface-variant hover:text-on-surface px-space-sm rounded-lg transition-colors cursor-pointer" type="button">
          <span class="material-symbols-outlined text-[18px]">receipt_long</span>
          <span>System Logs</span>
        </button>
      </div>

      <!-- TAB 1: API KEY CONFIG (ACL-10) -->
      <div id="tab-content-api" class="space-y-space-lg">
        <!-- Card 1: Cloud LLM API key -->
        <div class="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm border border-[#E4DFD6]">
          <div class="flex items-start gap-space-md">
            <div class="w-10 h-10 rounded-full bg-primary-container text-on-primary flex items-center justify-center shrink-0 shadow-sm">
              <span class="material-symbols-outlined text-[20px]">encrypted</span>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between">
                <h2 class="font-headline-sm text-headline-sm text-on-surface font-semibold">Cloud LLM API Key</h2>
                <span class="font-code-sm text-code-sm bg-surface-container text-on-surface-variant px-space-sm py-0.5 rounded-full notranslate" translate="no">REST v1beta</span>
              </div>
              <p class="font-body-md text-body-md text-on-surface-variant mt-1">Used by the translation client. Stored encrypted via environment variables, never exposed to the frontend.</p>
            </div>
          </div>

          <div class="mt-space-lg space-y-space-lg pl-0 md:pl-14">
            <!-- Provider Select -->
            <div class="space-y-space-xs">
              <label class="block font-label-md text-label-md text-on-surface font-semibold">Provider</label>
              <div class="relative max-w-xl">
                <select id="llm-provider-select" class="w-full bg-surface-container-low rounded-lg px-space-md py-space-sm font-title-md text-title-md text-on-surface border border-transparent hover:border-[#E4DFD6] focus:outline-none focus:ring-2 focus:ring-primary-container transition-all cursor-pointer">
                  <option value="gemini" selected>Google Gemini 1.5 Pro (Multimodal CJK-tuned)</option>
                  <option value="openai">OpenAI GPT-4o (Vision &amp; Formatting)</option>
                  <option value="claude">Anthropic Claude 3.5 Sonnet</option>
                </select>
              </div>
            </div>

            <!-- API Key Input Field -->
            <div class="space-y-space-xs">
              <div class="flex items-center justify-between max-w-xl">
                <label class="font-label-md text-label-md text-on-surface font-semibold" for="api-key-input">API Key</label>
                <span class="font-code-sm text-code-sm text-on-surface-variant notranslate" translate="no">SHA-256 Checksum: e84f…3c91</span>
              </div>
              <div class="relative max-w-xl flex items-center bg-surface-container-low rounded-lg px-space-md py-space-xs border border-transparent focus-within:border-[#E4DFD6]">
                <input class="bg-transparent font-code-md text-code-md tracking-widest text-on-surface w-full focus:outline-none select-all notranslate" translate="no" id="api-key-input" type="password" value="AIzaSyC128470192847192384710293847"/>
                <button onclick="toggleKeyVisibility()" class="ml-space-sm shrink-0 font-label-md text-label-md text-primary-container bg-surface-container-lowest hover:bg-surface-container-high px-space-sm py-1 rounded transition-colors flex items-center gap-1 shadow-sm cursor-pointer" type="button">
                  <span class="material-symbols-outlined text-[15px]" id="visibility-icon">visibility</span>
                  <span id="visibility-label">Show</span>
                </button>
              </div>

              <!-- Status Indicator & Security Meta -->
              <div class="flex flex-wrap items-center justify-between gap-space-sm max-w-xl pt-1">
                <div class="flex items-center gap-space-xs">
                  <span class="inline-flex items-center gap-1 bg-secondary-container text-on-secondary-container font-label-md text-label-md px-2.5 py-0.5 rounded-full font-medium">
                    <span class="material-symbols-outlined text-[14px]">check_circle</span>
                    <span>Valid</span>
                  </span>
                  <span class="font-body-sm text-body-sm text-on-surface-variant">Last checked 2 hours ago</span>
                </div>
                <div class="flex items-center gap-1 font-body-sm text-body-sm text-on-surface-variant">
                  <span class="material-symbols-outlined text-[14px]">lock</span>
                  <span class="notranslate" translate="no">AES-256 GCM encrypted at rest</span>
                </div>
              </div>
            </div>

            <!-- Save CTA -->
            <div class="pt-2 flex items-center gap-3">
              <button onclick="saveApiKey()" class="px-6 py-2.5 rounded-full bg-primary-container hover:bg-primary text-on-primary font-title-md text-label-md font-semibold shadow-md transition-all cursor-pointer" type="button">
                Save &amp; Verify Key
              </button>
              <span id="save-key-feedback" class="font-body-sm text-body-sm text-secondary font-medium hidden">✓ Key encrypted and saved</span>
            </div>
          </div>
        </div>

        <!-- Card 2: Quota & Usage -->
        <div class="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm border border-[#E4DFD6]">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-title-md text-title-md text-on-surface font-semibold">Monthly Quota Consumption</h3>
            <span class="font-code-sm text-code-sm text-on-surface-variant notranslate" translate="no">Billing Period: Oct 2026</span>
          </div>
          <div class="w-full bg-surface-container rounded-full h-2 mb-2 overflow-hidden">
            <div class="bg-secondary h-2 rounded-full" style="width: 30%"></div>
          </div>
          <div class="flex items-center justify-between font-code-sm text-code-sm text-on-surface-variant">
            <span>Consumed: <strong class="text-on-surface notranslate" translate="no">$14.80</strong> / $50.00 Limit</span>
            <span class="text-secondary font-semibold">70% Budget Remaining</span>
          </div>
        </div>
      </div>

      <!-- TAB 2: CUSTOM GLOSSARY CRUD (ACL-11) -->
      <div id="tab-content-glossary" class="hidden space-y-space-lg">
        <div class="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm border border-[#E4DFD6]">
          <!-- Header Row -->
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-space-md border-b border-[#E4DFD6]">
            <div>
              <h2 class="font-headline-sm text-headline-sm text-on-surface font-semibold">Custom Glossary Terms</h2>
              <p class="font-body-md text-body-md text-on-surface-variant mt-0.5">Enforced in translation prompt context for high-fidelity character naming and honorific consistency.</p>
            </div>
            <button onclick="openAddTermModal()" class="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-full bg-primary-container hover:bg-primary text-on-primary font-title-md text-label-md font-semibold shadow-md transition-all cursor-pointer whitespace-nowrap" type="button">
              <span class="material-symbols-outlined text-[18px]">add</span>
              <span>Add New Term</span>
            </button>
          </div>

          <!-- Glossary Table -->
          <div class="overflow-x-auto mt-space-md">
            <table class="w-full text-left border-collapse" id="glossary-table">
              <thead>
                <tr class="bg-surface-container-low text-on-surface font-title-md text-xs uppercase tracking-wider border-b border-[#E4DFD6]">
                  <th class="py-3 px-4 font-bold w-[25%]">Source Term (Raw JA)</th>
                  <th class="py-3 px-4 font-bold w-[25%]">Target Term (Vietnamese)</th>
                  <th class="py-3 px-4 font-bold w-[35%]">Context Notes &amp; Rules</th>
                  <th class="py-3 px-4 font-bold w-[15%] text-right">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#E4DFD6] font-body-sm text-body-sm" id="glossary-tbody">
                <tr class="hover:bg-surface-container-low/60 transition-colors" id="term-row-1">
                  <td class="py-3.5 px-4 font-title-md font-semibold text-on-surface notranslate" translate="no">先生 (Sensei)</td>
                  <td class="py-3.5 px-4 font-title-md font-medium text-secondary notranslate" translate="no">Thầy</td>
                  <td class="py-3.5 px-4 text-on-surface-variant">Keep honorific as-is; do not translate literally to "tiên sinh".</td>
                  <td class="py-3.5 px-4 text-right">
                    <button onclick="removeGlossaryTerm('term-row-1')" class="text-error hover:underline font-label-md text-xs cursor-pointer">Remove</button>
                  </td>
                </tr>
                <tr class="hover:bg-surface-container-low/60 transition-colors" id="term-row-2">
                  <td class="py-3.5 px-4 font-title-md font-semibold text-on-surface notranslate" translate="no">木ノ葉 (Konoha)</td>
                  <td class="py-3.5 px-4 font-title-md font-medium text-secondary notranslate" translate="no">Làng Lá (Konoha)</td>
                  <td class="py-3.5 px-4 text-on-surface-variant">Proper noun — capitalize first letter.</td>
                  <td class="py-3.5 px-4 text-right">
                    <button onclick="removeGlossaryTerm('term-row-2')" class="text-error hover:underline font-label-md text-xs cursor-pointer">Remove</button>
                  </td>
                </tr>
                <tr class="hover:bg-surface-container-low/60 transition-colors" id="term-row-3">
                  <td class="py-3.5 px-4 font-title-md font-semibold text-on-surface notranslate" translate="no">鬼 (Oni)</td>
                  <td class="py-3.5 px-4 font-title-md font-medium text-secondary notranslate" translate="no">Quỷ (Oni)</td>
                  <td class="py-3.5 px-4 text-on-surface-variant">Keep Japanese term in brackets on first appearance.</td>
                  <td class="py-3.5 px-4 text-right">
                    <button onclick="removeGlossaryTerm('term-row-3')" class="text-error hover:underline font-label-md text-xs cursor-pointer">Remove</button>
                  </td>
                </tr>
                <tr class="hover:bg-surface-container-low/60 transition-colors" id="term-row-4">
                  <td class="py-3.5 px-4 font-title-md font-semibold text-on-surface notranslate" translate="no">仲間 (Nakama)</td>
                  <td class="py-3.5 px-4 font-title-md font-medium text-secondary notranslate" translate="no">Đồng đội</td>
                  <td class="py-3.5 px-4 text-on-surface-variant">Used in pirate context; conveys deep bond.</td>
                  <td class="py-3.5 px-4 text-right">
                    <button onclick="removeGlossaryTerm('term-row-4')" class="text-error hover:underline font-label-md text-xs cursor-pointer">Remove</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Add Term Modal Overlay -->
        <div id="add-term-modal" class="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 hidden">
          <div class="bg-surface-container-lowest rounded-2xl max-w-lg w-full p-space-lg shadow-2xl border border-[#E4DFD6]">
            <div class="flex items-center justify-between pb-3 border-b border-[#E4DFD6]">
              <h3 class="font-headline-sm text-headline-sm text-on-surface font-semibold">Add Glossary Term</h3>
              <button onclick="closeAddTermModal()" class="text-outline hover:text-on-surface cursor-pointer">
                <span class="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>
            <div class="space-y-3 mt-4">
              <div>
                <label class="block font-label-md text-xs font-semibold text-on-surface mb-1">Source Term (Raw Japanese)</label>
                <input id="modal-src-term" placeholder="e.g. 術 (Jutsu)" class="w-full bg-surface-container-low px-3 py-2 rounded-lg font-body-md text-on-surface border border-transparent focus:border-[#E4DFD6] focus:outline-none"/>
              </div>
              <div>
                <label class="block font-label-md text-xs font-semibold text-on-surface mb-1">Target Term (Vietnamese Localization)</label>
                <input id="modal-tgt-term" placeholder="e.g. Nhẫn thuật" class="w-full bg-surface-container-low px-3 py-2 rounded-lg font-body-md text-on-surface border border-transparent focus:border-[#E4DFD6] focus:outline-none"/>
              </div>
              <div>
                <label class="block font-label-md text-xs font-semibold text-on-surface mb-1">Translation Guidance / Notes</label>
                <textarea id="modal-notes" rows="2" placeholder="Rules for the LLM when encountering this term..." class="w-full bg-surface-container-low px-3 py-2 rounded-lg font-body-md text-on-surface border border-transparent focus:border-[#E4DFD6] focus:outline-none resize-none"></textarea>
              </div>
            </div>
            <div class="flex items-center justify-end gap-3 mt-6 pt-3 border-t border-[#E4DFD6]">
              <button onclick="closeAddTermModal()" class="px-5 py-2 rounded-full border border-[#E4DFD6] text-on-surface font-label-md text-label-md cursor-pointer hover:bg-surface-container">Cancel</button>
              <button onclick="submitNewTerm()" class="px-6 py-2 rounded-full bg-primary-container text-on-primary font-label-md text-label-md font-semibold cursor-pointer hover:bg-primary">Save Term</button>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 3: SYSTEM LOGS CONSOLE (ACL-12) -->
      <div id="tab-content-logs" class="hidden space-y-space-lg">
        <div class="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm border border-[#E4DFD6]">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-space-md border-b border-[#E4DFD6]">
            <div>
              <h2 class="font-headline-sm text-headline-sm text-on-surface font-semibold">Real-Time System Logs</h2>
              <p class="font-body-md text-body-md text-on-surface-variant mt-0.5">Live diagnostic stream from worker sub-processes, GPU VRAM allocator, and translation pipeline.</p>
            </div>
            <div class="flex items-center gap-2">
              <button onclick="clearConsole()" class="px-3.5 py-1.5 rounded-full bg-surface-container hover:bg-surface-container-high text-on-surface font-label-md text-xs font-semibold transition-colors cursor-pointer border border-[#E4DFD6]">
                Clear Console
              </button>
              <button onclick="downloadLogs()" class="px-3.5 py-1.5 rounded-full bg-primary-fixed hover:bg-primary-fixed-dim text-on-primary-fixed font-label-md text-xs font-semibold transition-colors cursor-pointer">
                Export Diagnostics (.LOG)
              </button>
            </div>
          </div>

          <!-- Terminal Screen Container -->
          <div class="console-terminal rounded-xl p-4 mt-space-md text-xs leading-relaxed max-h-[460px] overflow-y-auto font-mono border border-black/20 shadow-inner" id="console-output">
            <div class="text-secondary font-semibold">[12:04:02.112] INFO  &gt;&gt; Async Celery worker daemon initialized (pid 8421, thread pool: 4)</div>
            <div class="text-outline-variant">[12:04:15.820] DEBUG &gt;&gt; Loading YOLOv8x-Manga checkpoint into GPU memory: VRAM allocated 2.4 GB</div>
            <div class="text-[#F6F0EA]">[12:04:22.014] INFO  &gt;&gt; Page 001.png through 012.png ingestion verified: 12 files queued</div>
            <div class="text-amber-400 font-medium">[12:06:40.401] WARN  &gt;&gt; Cloud LLM API token quota at 30% monthly allocation threshold</div>
            <div class="text-rose-400 font-semibold">[12:07:02.912] ERROR &gt;&gt; LaMa inpainting worker CUDA OOM caught on batch #014 - dynamic retry activated</div>
            <div class="text-secondary font-semibold">[12:07:03.104] INFO  &gt;&gt; Retry succeeded with tile chunk size 512x512: Artifact score 0.012</div>
            <div class="text-[#F6F0EA]">[12:08:14.502] INFO  &gt;&gt; Page 013 marked Waiting Review: Human-in-the-loop inspection ready</div>
            <div class="text-[#F6F0EA]">[12:09:00.220] INFO  &gt;&gt; Manga OCR v2.1 vertical transcription completed for batch #CH-112-RAW</div>
            <div class="text-emerald-400 font-semibold">[12:10:18.991] SUCCESS &gt;&gt; All 24 pages synchronized in SQLite session. Ready for export.</div>
          </div>
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

// Tab switcher for Settings
function switchTab(tabName) {{
  ['api', 'glossary', 'logs'].forEach(t => {{
    const content = document.getElementById('tab-content-' + t);
    const btn = document.getElementById('tab-btn-' + t);
    if (t === tabName) {{
      if (content) content.classList.remove('hidden');
      if (btn) {{
        btn.classList.add('bg-surface-container-lowest', 'text-primary-container', 'shadow-sm', 'font-title-md');
        btn.classList.remove('text-on-surface-variant', 'font-body-md');
      }}
    }} else {{
      if (content) content.classList.add('hidden');
      if (btn) {{
        btn.classList.remove('bg-surface-container-lowest', 'text-primary-container', 'shadow-sm', 'font-title-md');
        btn.classList.add('text-on-surface-variant', 'font-body-md');
      }}
    }}
  }});
}}

// Support deep-linking via query parameters (e.g. ?tab=logs)
try {{
  const currentSearch = window.location.search || (window.parent && window.parent.location ? window.parent.location.search : '');
  const urlParams = new URLSearchParams(currentSearch);
  const reqTab = urlParams.get('tab');
  if (reqTab && ['api', 'glossary', 'logs'].includes(reqTab)) {{
    switchTab(reqTab);
  }}
}} catch (e) {{}}

// Toggle API Key visibility
function toggleKeyVisibility() {{
  const input = document.getElementById('api-key-input');
  const icon = document.getElementById('visibility-icon');
  const label = document.getElementById('visibility-label');
  if (input.type === 'password') {{
    input.type = 'text';
    if (icon) icon.innerText = 'visibility_off';
    if (label) label.innerText = 'Hide';
  }} else {{
    input.type = 'password';
    if (icon) icon.innerText = 'visibility';
    if (label) label.innerText = 'Show';
  }}
}}

// Save API Key feedback
function saveApiKey() {{
  const fb = document.getElementById('save-key-feedback');
  if (fb) {{
    fb.classList.remove('hidden');
    setTimeout(() => {{
      fb.classList.add('hidden');
    }}, 2500);
  }}
}}

// Add Term Modal controls
function openAddTermModal() {{
  const modal = document.getElementById('add-term-modal');
  if (modal) modal.classList.remove('hidden');
}}

function closeAddTermModal() {{
  const modal = document.getElementById('add-term-modal');
  if (modal) modal.classList.add('hidden');
}}

function submitNewTerm() {{
  const src = document.getElementById('modal-src-term').value.trim();
  const tgt = document.getElementById('modal-tgt-term').value.trim();
  const notes = document.getElementById('modal-notes').value.trim();
  if (!src || !tgt) {{
    alert('Please provide both Source and Target terms.');
    return;
  }}

  const tbody = document.getElementById('glossary-tbody');
  const rowId = 'term-row-' + Date.now();
  const tr = document.createElement('tr');
  tr.id = rowId;
  tr.className = "hover:bg-surface-container-low/60 transition-colors";
  tr.innerHTML = `
    <td class="py-3.5 px-4 font-title-md font-semibold text-on-surface notranslate" translate="no">${{src}}</td>
    <td class="py-3.5 px-4 font-title-md font-medium text-secondary notranslate" translate="no">${{tgt}}</td>
    <td class="py-3.5 px-4 text-on-surface-variant">${{notes || 'No specific rules provided.'}}</td>
    <td class="py-3.5 px-4 text-right">
      <button onclick="removeGlossaryTerm('${{rowId}}')" class="text-error hover:underline font-label-md text-xs cursor-pointer">Remove</button>
    </td>
  `;
  tbody.appendChild(tr);

  closeAddTermModal();
  document.getElementById('modal-src-term').value = '';
  document.getElementById('modal-tgt-term').value = '';
  document.getElementById('modal-notes').value = '';

  const badge = document.getElementById('glossary-count-badge');
  if (badge) {{
    const current = parseInt(badge.innerText) || 4;
    badge.innerText = current + 1;
  }}
}}

function removeGlossaryTerm(rowId) {{
  const row = document.getElementById(rowId);
  if (row) {{
    row.remove();
    const badge = document.getElementById('glossary-count-badge');
    if (badge) {{
      const current = parseInt(badge.innerText) || 4;
      badge.innerText = Math.max(0, current - 1);
    }}
  }}
}}

// Logs controls
function clearConsole() {{
  const consoleEl = document.getElementById('console-output');
  if (consoleEl) {{
    consoleEl.innerHTML = '<div class="text-outline-variant font-mono">[Console buffer cleared by operator]</div>';
  }}
}}

function downloadLogs() {{
  const text = document.getElementById('console-output')?.innerText || 'No log data';
  const blob = new Blob([text], {{ type: 'text/plain' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'acl_system_diagnostics.log';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}}
</script>

</body>
</html>
"""

# Render the Google Stitch component seamlessly
components.html(settings_html, height=1150, scrolling=True)
