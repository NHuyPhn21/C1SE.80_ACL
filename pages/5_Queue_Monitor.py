"""ACL Queue Monitor & Async Pipeline Tracking — Screen ACL-09 & ACL-09-DONE (Non-Blocking Render-First)."""

import base64
import io
import json
import os
import time
import zipfile
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

from utils.auth_session import require_auth
from backend.pipeline import run_full_acl_pipeline
from backend.image_utils import BASE_DIR, encode_image_to_base64
from backend.database import SessionLocal
from backend.models import ComicPage

# Enforce authentication guard
user = require_auth()

user_initials = (user.full_name[:2] if user.full_name else "PH").upper()
user_name = user.full_name or "Phan Nhat Huy"
project_name = st.query_params.get("project", "Shonen Weekly #112")
file_safe_project = project_name.replace(" ", "_").replace("#", "")

# Kiểm tra xem có đang nhận lệnh chạy AI từ Chapter Studio không
run_flag = st.query_params.get("run_pipeline", "0")
files_param = st.query_params.get("files", "")
files_to_run = [f.strip() for f in files_param.split(",") if f.strip()] if (run_flag == "1" and files_param) else []
is_currently_running = len(files_to_run) > 0

# =====================================================================
# 1. ĐỌC DỮ LIỆU THẬT TỪ THƯ MỤC RENDERED_PAGES ĐỂ HIỂN THỊ NGAY LẬP TỨC
# =====================================================================
rendered_dir = BASE_DIR / "data" / "rendered_pages"
rendered_dir.mkdir(parents=True, exist_ok=True)
rendered_files = sorted(list(rendered_dir.glob("final_*.*")))

zip_base64 = ""
total_zip_mb = 0.0
preview_images_b64 = {}

if rendered_files and not is_currently_running:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for fpath in rendered_files:
            zf.write(fpath, arcname=fpath.name)
            total_zip_mb += fpath.stat().st_size / (1024 * 1024)
            try:
                preview_images_b64[fpath.name] = encode_image_to_base64(str(fpath))
            except Exception:
                pass
    zip_base64 = base64.b64encode(zip_buffer.getvalue()).decode("utf-8")

total_zip_mb_str = f"{max(0.2, round(total_zip_mb, 2))} MB"

if is_currently_running:
    batch_code = "#CH-RUNNING"
    total_pages = len(files_to_run)
    processed_pages = 0
    progress_pct = 45
    est_time = f"Processing {', '.join(files_to_run)}..."
elif len(rendered_files) > 0:
    batch_code = "#CH-LIVE-ACL"
    total_pages = len(rendered_files)
    processed_pages = len(rendered_files)
    progress_pct = 100
    est_time = "Completed"
else:
    batch_code = "#CH-112-RAW"
    total_pages = 1
    processed_pages = 0
    progress_pct = 0
    est_time = "Ready"

# Sinh bảng trạng thái
artifact_rows_html = ""
active_rows_html = ""

if is_currently_running:
    for idx, fname in enumerate(files_to_run, start=1):
        active_rows_html += f"""
        <tr class="bg-primary-fixed/20">
          <td class="py-3.5 px-4 font-semibold text-primary-container">Page {idx:03d}</td>
          <td class="py-3.5 px-4 font-mono text-xs text-on-surface">{fname}</td>
          <td class="py-3.5 px-4 text-primary font-semibold">Running YOLOv8 + MangaOCR + Gemini 3.8 + Inpaint...</td>
          <td class="py-3.5 px-4">
            <span class="inline-flex items-center gap-1.5 bg-[#FFF3E0] text-[#E65100] px-3 py-1 rounded-full font-mono text-xs font-semibold border border-[#FFE0B2]">
              <span class="material-symbols-outlined text-[14px] animate-spin">sync</span>
              <span>AI Processing...</span>
            </span>
          </td>
          <td class="py-3.5 px-4 text-right font-mono text-xs text-outline">Please wait (~5-10s)</td>
        </tr>
        """
else:
    for idx, fpath in enumerate(rendered_files, start=1):
        fname = fpath.name
        orig_name = fname.replace("final_", "")
        fsize_mb = round(fpath.stat().st_size / (1024 * 1024), 2)

        artifact_rows_html += f"""
            <tr class="hover:bg-surface-container-low/60 transition-colors">
              <td class="py-3.5 px-4 font-semibold text-on-surface flex items-center gap-2">
                <span class="w-6 h-6 rounded-full border border-primary-container text-primary-container font-mono text-xs font-bold inline-flex items-center justify-center">{idx}</span>
                <span>Page {idx:03d}</span>
              </td>
              <td class="py-3.5 px-4 font-mono text-xs text-on-surface-variant notranslate" translate="no">{fname} ({fsize_mb} MB)</td>
              <td class="py-3.5 px-4 text-on-surface font-medium flex items-center gap-1.5">
                <span class="material-symbols-outlined text-[16px] text-secondary">verified</span>
                <span>Typesetting Done</span>
              </td>
              <td class="py-3.5 px-4">
                <span class="inline-flex items-center gap-1 bg-secondary-container text-secondary px-2.5 py-0.5 rounded-full font-mono text-xs font-semibold">
                  <span class="material-symbols-outlined text-[13px]">check_circle</span>
                  <span>Completed</span>
                </span>
              </td>
              <td class="py-3.5 px-4 text-right space-x-1">
                <button onclick="openPagePreview('Page {idx:03d} — Localized Output', '{fname}', 'Auto-Typesetting Complete', 'Verified 100% Quality')" class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-surface-container hover:bg-surface-container-high transition-colors cursor-pointer border border-[#E4DFD6]">
                  <span class="material-symbols-outlined text-[14px]">visibility</span>
                  <span>Preview Page</span>
                </button>
                <button onclick="navigateParent('review-studio?page_name={orig_name}')" class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-primary-fixed text-on-primary-fixed hover:opacity-90 transition-colors cursor-pointer">
                  <span class="material-symbols-outlined text-[14px]">rate_review</span>
                  <span>Review</span>
                </button>
              </td>
            </tr>
        """

        active_rows_html += f"""
            <tr class="hover:bg-surface-container-low/60 transition-colors">
              <td class="py-3.5 px-4 font-semibold text-on-surface">Page {idx:03d}</td>
              <td class="py-3.5 px-4 font-mono text-xs text-on-surface-variant notranslate" translate="no">{orig_name} → {fname}</td>
              <td class="py-3.5 px-4 text-on-surface font-medium">Typesetting Complete</td>
              <td class="py-3.5 px-4">
                <span class="inline-flex items-center gap-1 bg-secondary-container text-secondary px-2.5 py-0.5 rounded-full font-mono text-xs font-semibold">
                  <span class="material-symbols-outlined text-[13px]">check_circle</span>
                  <span>Completed</span>
                </span>
              </td>
              <td class="py-3.5 px-4 text-right font-mono text-xs text-primary-container font-semibold cursor-pointer hover:underline" onclick="openPagePreview('Page {idx:03d}', '{fname}', 'Completed', 'Ready')">Preview →</td>
            </tr>
        """

preview_map_json = json.dumps(preview_images_b64)
auto_open_completed = "false" if is_currently_running else ("true" if len(rendered_files) > 0 else "false")

# =====================================================================
# 2. VẼ GIAO DIỆN HTML NGAY LẬP TỨC (KHÔNG BAO GIỜ BỊ TRẮNG TRANG)
# =====================================================================
queue_monitor_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet"/>
<style>
  html, body {{ margin: 0; padding: 0; background: #fff8f3; font-family: 'Plus Jakarta Sans', sans-serif; color: #1d1b18; }}
  ::-webkit-scrollbar {{ display: none; }}
  .material-symbols-outlined {{ font-family: 'Material Symbols Outlined'; font-size: 20px; line-height: 1; display: inline-block; }}
  @keyframes moveBg {{ 0% {{ background-position: 0 0; }} 100% {{ background-position: 2rem 0; }} }}
  .progress-animated {{
    background-image: linear-gradient(45deg, rgba(255,255,255,0.18) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.18) 50%, rgba(255,255,255,0.18) 75%, transparent 75%, transparent);
    background-size: 1rem 1rem;
    animation: moveBg 1.5s linear infinite;
  }}
</style>
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = {{
  theme: {{
    extend: {{
      colors: {{
        "secondary": "#536435",
        "outline-variant": "#c6c5d1",
        "primary-fixed": "#dee1ff",
        "outline": "#767681",
        "surface-container-high": "#ede7e2",
        "on-surface": "#1d1b18",
        "on-surface-variant": "#454650",
        "surface": "#fff8f3",
        "surface-container": "#f3ede7",
        "secondary-container": "#d3e7ac",
        "primary": "#0c1b59",
        "surface-container-low": "#f9f2ed",
        "surface-container-highest": "#e7e1dc",
        "on-primary": "#ffffff",
        "surface-container-lowest": "#ffffff",
        "primary-container": "#25326f"
      }}
    }}
  }}
}};
</script>
</head>
<body class="bg-surface text-on-surface antialiased">

<!-- SIDEBAR -->
<aside class="fixed left-0 top-0 h-full w-[220px] bg-surface-container-lowest z-50 flex flex-col justify-between py-5 border-r border-[#E4DFD6]">
  <div>
    <div class="px-5 mb-6 flex items-center gap-3">
      <div class="w-9 h-9 rounded-xl bg-primary-container text-on-primary flex items-center justify-center font-bold text-lg shadow-sm shrink-0">A</div>
      <div>
        <h1 class="text-[17px] font-bold text-on-surface leading-none">ACL</h1>
        <p class="font-mono text-[11px] text-on-surface-variant mt-1">v2.4 Editorial Core</p>
      </div>
    </div>
    <nav class="px-3 flex flex-col gap-1">
      <a class="flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold text-on-surface-variant hover:bg-surface-container cursor-pointer" onclick="navigateParent('workspace')">
        <span class="material-symbols-outlined">grid_view</span><span>Dashboard</span>
      </a>
      <a class="flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold text-on-surface-variant hover:bg-surface-container cursor-pointer" onclick="navigateParent('chapter-studio?project=' + encodeURIComponent('{project_name}'))">
        <span class="material-symbols-outlined">cloud_upload</span><span>Chapter Studio</span>
      </a>
      <a class="flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold text-on-surface-variant hover:bg-surface-container cursor-pointer" onclick="navigateParent('review-studio?project=' + encodeURIComponent('{project_name}'))">
        <span class="material-symbols-outlined">vertical_split</span><span>Review Studio</span>
      </a>
      <a class="flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold text-on-surface-variant hover:bg-surface-container cursor-pointer" onclick="navigateParent('typesetting')">
        <span class="material-symbols-outlined">edit_note</span><span>Typesetting</span>
      </a>
      <a class="flex items-center gap-3 px-3 py-2 bg-primary-container text-on-primary text-xs font-semibold rounded-xl cursor-pointer shadow-sm">
        <span class="material-symbols-outlined">schedule</span><span>Queue Monitor</span>
      </a>
    </nav>
  </div>
</aside>

<div class="pl-[220px]">
  <header class="fixed top-0 left-[220px] right-0 h-16 bg-surface-container-lowest/95 backdrop-blur-md z-40 px-8 flex items-center justify-between border-b border-[#E4DFD6]">
    <div class="flex items-center gap-2 text-sm">
      <a class="font-bold text-on-surface cursor-pointer" onclick="navigateParent('workspace')">ACL Studio</a>
      <span>/</span>
      <span class="text-primary-container font-semibold">Queue Monitor</span>
    </div>
    <div class="w-8 h-8 rounded-full bg-primary-container flex items-center justify-center font-bold text-xs text-on-primary">{user_initials}</div>
  </header>

  <main class="relative pt-20 px-8 pb-12 max-w-7xl mx-auto space-y-6">
    <div class="flex items-center justify-between gap-4 border-b border-[#E4DFD6] pb-3">
      <div class="flex items-center gap-2">
        <button onclick="switchView('active')" id="tab-active" class="px-4 py-2 rounded-full text-xs font-semibold bg-primary-container text-on-primary cursor-pointer">
          Live Pipeline Queue ({total_pages} Pages)
        </button>
        <button onclick="switchView('completed')" id="tab-completed" class="px-4 py-2 rounded-full text-xs font-semibold bg-surface-container text-on-surface-variant cursor-pointer">
          Completed Chapter &amp; ZIP Export ({len(rendered_files)} Ready)
        </button>
      </div>
      <div class="flex items-center gap-2">
        <button onclick="navigateParent('review-studio')" class="px-4 py-1.5 rounded-full bg-surface-container text-primary font-semibold text-xs border border-[#E4DFD6] cursor-pointer">Open Review Studio</button>
        <button onclick="navigateParent('typesetting')" class="px-4 py-1.5 rounded-full bg-primary-container text-on-primary font-semibold text-xs cursor-pointer">Open Live Typesetting</button>
      </div>
    </div>

    <!-- ACTIVE VIEW -->
    <div id="view-active" class="space-y-6">
      <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 p-6 shadow-sm">
        <div class="flex items-baseline justify-between mb-3">
          <h2 class="text-lg font-bold">Active Chapter: {project_name} <span class="text-xs font-mono bg-surface-container px-2 py-0.5 rounded ml-2">{batch_code}</span></h2>
          <div class="text-right">
            <div class="text-lg text-primary-container font-bold">{processed_pages} / {total_pages} Pages Processed ({progress_pct}%)</div>
            <div class="text-xs text-outline">{est_time}</div>
          </div>
        </div>
        <div class="w-full h-3 bg-surface-container-highest rounded-full overflow-hidden mb-6">
          <div class="h-full bg-primary-container rounded-full progress-animated" style="width: {progress_pct}%;"></div>
        </div>

        <table class="w-full text-left border-collapse border rounded-xl overflow-hidden">
          <thead>
            <tr class="bg-surface-container-low text-xs uppercase border-b">
              <th class="py-3 px-4">Page</th>
              <th class="py-3 px-4">Filename</th>
              <th class="py-3 px-4">Current Stage</th>
              <th class="py-3 px-4">Status</th>
              <th class="py-3 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y text-xs">
            {active_rows_html}
          </tbody>
        </table>
      </div>
    </div>

    <!-- COMPLETED VIEW -->
    <div id="view-completed" class="hidden space-y-6">
      <div class="rounded-2xl bg-secondary-container/30 p-8 shadow-sm border border-secondary/20 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        <div class="space-y-1">
          <div class="flex items-center gap-2">
            <h2 class="text-2xl font-bold">Chapter Localization 100% Complete!</h2>
            <span class="bg-secondary text-white text-xs px-2.5 py-0.5 rounded-full uppercase font-semibold">Ready for Release</span>
          </div>
          <p class="text-sm text-on-surface-variant">All {len(rendered_files)} localized pages in <code>data/rendered_pages/</code> are ready for preview and ZIP download.</p>
        </div>
        <button onclick="downloadZipArchive()" class="inline-flex items-center gap-3 bg-primary-container text-on-primary hover:bg-primary px-8 py-3.5 rounded-full shadow-md font-semibold cursor-pointer" type="button">
          <span class="material-symbols-outlined">folder_zip</span>
          <span>Download Chapter (ZIP)</span>
          <span class="bg-primary px-2.5 py-0.5 rounded-full text-xs font-mono">{total_zip_mb_str}</span>
        </button>
      </div>

      <div class="bg-surface-container-lowest rounded-2xl border border-outline-variant/50 overflow-hidden shadow-sm">
        <div class="p-4 border-b flex items-center justify-between">
          <h3 class="text-base font-bold">Completed Chapter Artifacts (Real Output Files)</h3>
          <span class="font-mono text-xs px-2.5 py-0.5 rounded-full bg-secondary-container text-secondary font-semibold">{len(rendered_files)} Rendered</span>
        </div>
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-surface-container-low text-xs uppercase border-b">
              <th class="py-3 px-4">Page</th>
              <th class="py-3 px-4">Filename</th>
              <th class="py-3 px-4">Final Stage</th>
              <th class="py-3 px-4">Status</th>
              <th class="py-3 px-4 text-right">Action &amp; Preview</th>
            </tr>
          </thead>
          <tbody class="divide-y text-xs">
            {artifact_rows_html}
          </tbody>
        </table>
      </div>
    </div>

    <!-- PREVIEW LIGHTBOX MODAL -->
    <div id="preview-modal" style="display: none;" onclick="if (event.target === this) closePagePreview()" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 cursor-pointer">
      <div class="bg-surface-container-lowest rounded-2xl shadow-2xl max-w-4xl w-full border border-[#E4DFD6] overflow-hidden cursor-default" onclick="event.stopPropagation()">
        <div class="flex items-center justify-between px-6 py-3.5 border-b bg-surface-container-low">
          <div>
            <h3 id="preview-modal-title" class="text-base font-bold">Page Preview</h3>
            <p id="preview-modal-subtitle" class="font-mono text-xs text-on-surface-variant">Rendered Output</p>
          </div>
          <button onclick="closePagePreview()" class="p-1.5 rounded-full hover:bg-surface-container cursor-pointer">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="p-4 bg-[#0f1117] flex items-center justify-center max-h-[75vh] overflow-y-auto">
          <img id="preview-modal-img" src="" alt="Rendered Manga Page" class="max-h-[70vh] w-auto rounded shadow-lg object-contain"/>
        </div>
      </div>
    </div>
  </main>
</div>

<script>
const PREVIEW_IMAGES = {preview_map_json};
const REAL_ZIP_BASE64 = "{zip_base64}";

function navigateParent(path) {{
  const targetUrl = window.location.origin + '/' + path.replace(/^\/+/, '');
  const a = document.createElement('a');
  a.href = targetUrl;
  a.target = '_top';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}}

function switchView(viewName) {{
  const viewActive = document.getElementById('view-active');
  const viewCompleted = document.getElementById('view-completed');
  const tabActive = document.getElementById('tab-active');
  const tabCompleted = document.getElementById('tab-completed');
  if (viewName === 'completed') {{
    viewActive.classList.add('hidden');
    viewCompleted.classList.remove('hidden');
    tabCompleted.className = 'px-4 py-2 rounded-full text-xs font-semibold bg-primary-container text-on-primary cursor-pointer';
    tabActive.className = 'px-4 py-2 rounded-full text-xs font-semibold bg-surface-container text-on-surface-variant cursor-pointer';
  }} else {{
    viewCompleted.classList.add('hidden');
    viewActive.classList.remove('hidden');
    tabActive.className = 'px-4 py-2 rounded-full text-xs font-semibold bg-primary-container text-on-primary cursor-pointer';
    tabCompleted.className = 'px-4 py-2 rounded-full text-xs font-semibold bg-surface-container text-on-surface-variant cursor-pointer';
  }}
}}

function downloadZipArchive() {{
  if (!REAL_ZIP_BASE64 || REAL_ZIP_BASE64.length < 20) return;
  const a = document.createElement('a');
  a.href = 'data:application/zip;base64,' + REAL_ZIP_BASE64;
  a.download = '{file_safe_project}_Vietnamese_Release.zip';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}}

function openPagePreview(title, fileName, stage, status) {{
  const modal = document.getElementById('preview-modal');
  document.getElementById('preview-modal-title').innerText = title;
  document.getElementById('preview-modal-subtitle').innerText = `${{fileName}} • ${{stage}}`;
  const imgEl = document.getElementById('preview-modal-img');
  if (imgEl && PREVIEW_IMAGES[fileName]) {{
    imgEl.src = 'data:image/jpeg;base64,' + PREVIEW_IMAGES[fileName];
  }}
  if (modal) modal.style.display = 'flex';
}}

function closePagePreview() {{
  document.getElementById('preview-modal').style.display = 'none';
}}

if ({auto_open_completed}) {{
  switchView('completed');
}}
</script>
</body>
</html>
"""

components.html(queue_monitor_html, height=1200, scrolling=True)

# =====================================================================
# 3. CHẠY AI PIPELINE Ở CUỐI FILE SAU KHI ĐÃ VẼ XONG GIAO DIỆN HTML!
# =====================================================================
if is_currently_running:
    raw_dir = BASE_DIR / "data" / "raw_images" / "AisazuNihaIrarenai"
    uploads_dir = BASE_DIR / "data" / "raw_images" / "uploads"

    for idx, fname in enumerate(files_to_run, start=1):
        c1 = raw_dir / fname
        c2 = uploads_dir / fname
        target_path = c1 if c1.exists() else c2
        if target_path.exists():
            run_full_acl_pipeline(
                input_image_path=str(target_path),
                page_number=idx,
                force_reprocess=False,
                use_lama_api=False
            )

    st.query_params["run_pipeline"] = "0"
    st.rerun()