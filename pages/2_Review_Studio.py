"""ACL Interactive Review Studio — OCR Verification & Text Correction — Screen ACL-07 (Live SQLite Connected)."""

import json
import os
from pathlib import Path
from PIL import Image
import streamlit as st
import streamlit.components.v1 as components

from utils.auth_session import require_auth
from backend.database import SessionLocal
from backend.models import ComicPage, TextRegion
from backend.image_utils import (
    BASE_DIR,
    resolve_project_path,
    encode_image_to_base64,
    process_comic_page,
    _deduplicate_db_regions,
)
from ai_core.translator import translate_manga_text

# Enforce authentication guard
user = require_auth()

user_initials = (user.full_name[:2] if user.full_name else "PH").upper()
user_name = user.full_name or "Phan Nhat Huy"
project_name = st.query_params.get("project", "Shonen Weekly #112")

db = SessionLocal()
try:
    all_pages = db.query(ComicPage).order_by(ComicPage.id.asc()).all()

    # =====================================================================
    # 1. XỬ LÝ LƯU CHỈNH SỬA OCR TỪ GIAO DIỆN HTML (NẾU CÓ)
    # =====================================================================
    if st.query_params.get("save_ocr") == "1":
        target_pid = int(st.query_params.get("page_id", 0))
        updates_raw = st.query_params.get("updates", "{}")
        next_route = st.query_params.get("next", "typesetting")
        try:
            updates_dict = json.loads(updates_raw)
            retranslate_needed = False
            for reg_id_str, new_ja_text in updates_dict.items():
                reg = db.query(TextRegion).filter(TextRegion.id == int(reg_id_str)).first()
                if reg and new_ja_text.strip() and reg.original_text != new_ja_text.strip():
                    reg.original_text = new_ja_text.strip()
                    reg.translated_text = ""  # Reset để Gemini dịch lại câu vừa sửa
                    retranslate_needed = True
            db.commit()

            if retranslate_needed and target_pid:
                translate_manga_text(page_id=target_pid)
                process_comic_page(page_id=target_pid, use_lama_api=False)
        except Exception as e:
            print(f"⚠️ Lỗi khi lưu chỉnh sửa OCR: {e}")

        st.query_params.clear()
        st.query_params["project"] = project_name
        st.query_params["page_id"] = str(target_pid)
        if next_route == "typesetting":
            st.switch_page("pages/4_Typesetting.py")
        else:
            st.rerun()

    # =====================================================================
    # 2. XÁC ĐỊNH TRANG TRUYỆN HIỆN TẠI ĐANG XEM
    # =====================================================================
    req_page_id = st.query_params.get("page_id")
    req_page_name = st.query_params.get("page_name")

    current_page = None
    if req_page_id and str(req_page_id).isdigit():
        current_page = db.query(ComicPage).filter(ComicPage.id == int(req_page_id)).first()
    elif req_page_name:
        current_page = db.query(ComicPage).filter(ComicPage.original_path.like(f"%{req_page_name}%")).first()

    if not current_page and all_pages:
        current_page = all_pages[-1]

    # Nạp ảnh gốc và danh sách các vùng chữ từ SQLite
    orig_b64 = ""
    img_w, img_h = 1600, 2560
    regions_data = []
    page_idx = 1
    total_pages = max(1, len(all_pages))
    current_page_id = current_page.id if current_page else 1
    page_filename = "046.jpg"
    prev_page_id = current_page_id
    next_page_id = current_page_id

    if current_page:
        page_ids = [p.id for p in all_pages]
        if current_page.id in page_ids:
            idx_pos = page_ids.index(current_page.id)
            page_idx = idx_pos + 1
            prev_page_id = page_ids[max(0, idx_pos - 1)]
            next_page_id = page_ids[min(len(page_ids) - 1, idx_pos + 1)]

        orig_real_path = resolve_project_path(current_page.original_path)
        page_filename = os.path.basename(orig_real_path)
        if os.path.exists(orig_real_path):
            orig_b64 = encode_image_to_base64(orig_real_path)
            with Image.open(orig_real_path) as im:
                img_w, img_h = im.size

        raw_regs = db.query(TextRegion).filter(TextRegion.page_id == current_page.id).all()
        clean_regs = _deduplicate_db_regions(raw_regs) if raw_regs else []
        if not clean_regs and raw_regs:
            clean_regs = raw_regs

        for idx, r in enumerate(clean_regs, start=1):
            bbox = json.loads(r.bbox_json)
            x1, y1, x2, y2 = map(int, bbox[:4])
            left_pct = round((x1 / max(1, img_w)) * 100, 2)
            top_pct = round((y1 / max(1, img_h)) * 100, 2)
            width_pct = round(((x2 - x1) / max(1, img_w)) * 100, 2)
            height_pct = round(((y2 - y1) / max(1, img_h)) * 100, 2)

            regions_data.append({
                "index": idx,
                "id": r.id,
                "bbox": [x1, y1, x2, y2],
                "left_pct": left_pct,
                "top_pct": top_pct,
                "width_pct": width_pct,
                "height_pct": height_pct,
                "original_text": r.original_text or "",
                "translated_text": r.translated_text or "",
            })
finally:
    db.close()

# Sinh HTML cho các khung Bounding Box trên ảnh và các thẻ Card OCR bên phải
overlays_html = ""
cards_html = ""

for item in regions_data:
    idx = item["index"]
    rid = item["id"]
    ja_text = item["original_text"].replace('"', '&quot;')
    vi_text = item["translated_text"].replace('"', '&quot;')
    bbox_str = f"[{item['bbox'][0]}, {item['bbox'][1]}, {item['bbox'][2]}, {item['bbox'][3]}]"
    is_active_cls = "active-ocr" if idx == 1 else ""
    ring_cls = "ring-4 ring-primary" if idx == 1 else "ring-2 ring-primary/80"

    overlays_html += f"""
      <div onclick="selectBox({idx})" id="overlay-box-{idx}"
           style="left: {item['left_pct']}%; top: {item['top_pct']}%; width: {item['width_pct']}%; height: {item['height_pct']}%;"
           class="absolute bg-primary-container/15 hover:bg-primary-container/30 rounded-xs cursor-pointer transition-all {ring_cls}">
        <div class="absolute -top-3.5 left-0 bg-primary text-on-primary px-1.5 py-0.2 rounded-full font-code-sm text-[10px] font-bold flex items-center gap-0.5 shadow-sm whitespace-nowrap notranslate" translate="no">
          <span>#{idx}</span>
        </div>
      </div>
    """

    cards_html += f"""
      <div id="ocr-card-{idx}" onclick="selectBox({idx})" class="ocr-card {is_active_cls} bg-surface-container-low p-space-md rounded-xl shadow-xs hover:bg-surface-container-high/40 border border-[#E4DFD6] transition-all cursor-pointer">
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2">
            <span class="w-6 h-6 rounded-full bg-primary text-on-primary font-code-sm text-code-sm font-bold flex items-center justify-center notranslate" translate="no">{idx}</span>
            <span class="font-title-md text-label-md text-on-surface font-semibold">Speech Bubble #{idx}</span>
            <span class="font-code-sm text-code-sm text-on-surface-variant notranslate" translate="no">• Bbox {bbox_str}</span>
          </div>
          <span class="px-2.5 py-0.5 rounded-full bg-secondary-container text-on-secondary-container font-code-sm text-code-sm font-semibold flex items-center gap-1 notranslate" translate="no">
            <span class="material-symbols-outlined text-[14px]">verified</span>
            <span>ID #{rid}</span>
          </span>
        </div>
        <div class="mb-2">
          <label class="block font-code-sm text-code-sm text-on-surface-variant mb-1 notranslate" translate="no">OCR Transcription (Raw Japanese)</label>
          <input data-region-id="{rid}" class="ocr-input-field w-full bg-surface-container-lowest px-3 py-2 rounded-lg font-body-lg text-body-lg text-on-surface font-medium focus:ring-2 focus:ring-primary focus:outline-none transition-all border border-[#E4DFD6] notranslate" translate="no" type="text" value="{ja_text}"/>
        </div>
        <div class="flex items-center justify-between text-on-surface-variant pt-1 font-body-sm text-body-sm">
          <div class="flex items-center gap-1.5 text-secondary font-medium truncate pr-2">
            <span class="material-symbols-outlined text-[16px]">translate</span>
            <span class="truncate">VI: {vi_text if vi_text else 'Chưa dịch'}</span>
          </div>
        </div>
      </div>
    """

total_regions_count = len(regions_data)

review_studio_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
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
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #1d1b18;
  }}
}}
::-webkit-scrollbar {{ display: none; }}
.material-symbols-outlined {{
  font-family: 'Material Symbols Outlined';
  font-size: 20px;
  line-height: 1;
  display: inline-block;
}}
.ocr-card {{ transition: all 0.2s ease; }}
.ocr-card.active-ocr {{
  box-shadow: 0 0 0 2px #25326f;
  background-color: #ffffff;
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
        "surface-variant": "#e7e1dc",
        "primary-fixed": "#dee1ff",
        "outline": "#767681",
        "surface-container-high": "#ede7e2",
        "on-surface": "#1d1b18",
        "error": "#ba1a1a",
        "on-surface-variant": "#454650",
        "inverse-surface": "#32302d",
        "surface": "#fff8f3",
        "surface-container": "#f3ede7",
        "secondary-container": "#d3e7ac",
        "primary": "#0c1b59",
        "surface-container-low": "#f9f2ed",
        "on-secondary-container": "#576839",
        "surface-container-highest": "#e7e1dc",
        "on-primary": "#ffffff",
        "surface-container-lowest": "#ffffff",
        "primary-container": "#25326f"
      }},
      spacing: {{
        "space-xs": "0.25rem",
        "space-sm": "0.5rem",
        "space-md": "1rem",
        "space-lg": "1.5rem",
        "space-xl": "2rem"
      }}
    }}
  }}
}};
</script>
</head>

<body class="bg-surface text-on-surface antialiased">

<!-- FIXED LEFT SIDEBAR -->
<aside class="fixed left-0 top-0 h-full w-[220px] bg-surface-container-lowest z-50 flex flex-col justify-between shadow-sm border-r border-[#E4DFD6] select-none">
  <div class="flex flex-col">
    <div class="px-space-md pt-space-lg pb-space-md border-b border-[#E4DFD6]">
      <div class="text-2xl font-bold text-primary tracking-tight notranslate" translate="no">ACL</div>
      <div class="text-xs text-on-surface-variant font-medium">Automated Comic Localization</div>
    </div>

    <nav class="flex flex-col gap-1 px-space-sm mt-space-xs text-sm">
      <a class="flex items-center gap-space-sm px-space-sm py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high cursor-pointer" onclick="navigateParent('workspace')">
        <span class="material-symbols-outlined">grid_view</span>
        <span>Dashboard</span>
      </a>
      <a class="flex items-center gap-space-sm px-space-sm py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high cursor-pointer" onclick="navigateParent('chapter-studio?project=' + encodeURIComponent('{project_name}'))">
        <span class="material-symbols-outlined">auto_stories</span>
        <span>Chapter Studio</span>
      </a>
      <a aria-current="page" class="flex items-center gap-space-sm px-space-sm py-2 rounded-lg bg-primary-container text-on-primary font-semibold cursor-pointer">
        <span class="material-symbols-outlined">rate_review</span>
        <span>Review Studio</span>
      </a>
      <a class="flex items-center gap-space-sm px-space-sm py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high cursor-pointer" onclick="navigateParent('typesetting?page_id={current_page_id}')">
        <span class="material-symbols-outlined">format_shapes</span>
        <span>Typesetting</span>
      </a>
      <a class="flex items-center gap-space-sm px-space-sm py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high cursor-pointer" onclick="navigateParent('queue-monitor?project=' + encodeURIComponent('{project_name}'))">
        <span class="material-symbols-outlined">monitoring</span>
        <span>Queue Monitor</span>
      </a>
    </nav>
  </div>
  <div class="p-space-md border-t border-[#E4DFD6]">
    <div class="flex items-center justify-between px-space-sm py-2 rounded-lg bg-surface-container-low text-xs font-mono">
      <span>SQLite • Connected</span>
      <span class="w-2 h-2 rounded-full bg-secondary"></span>
    </div>
  </div>
</aside>

<!-- MAIN APP SHELL -->
<div class="pl-[220px]">
  <header class="fixed top-0 left-[220px] right-0 h-16 bg-surface-container-lowest/90 backdrop-blur-md z-40 flex items-center justify-between px-space-lg border-b border-[#E4DFD6]">
    <div class="flex items-center gap-2 text-xs text-on-surface-variant">
      <a class="font-medium text-on-surface cursor-pointer" onclick="navigateParent('workspace')">Workspace</a>
      <span>/</span>
      <span class="text-primary font-semibold">Interactive Review Studio ({page_filename})</span>
    </div>
    <div class="flex items-center gap-space-md">
      <div class="w-8 h-8 rounded-full bg-primary-container flex items-center justify-center text-xs text-on-primary font-semibold notranslate" translate="no">{user_initials}</div>
    </div>
  </header>

  <main class="relative pt-16 min-h-screen bg-surface w-full px-space-lg py-space-md">
    <div class="flex flex-col w-full">

      <!-- Header Title & Pagination Strip -->
      <div class="bg-surface-container-lowest rounded-xl p-space-md shadow-sm mb-space-md flex flex-wrap items-center justify-between gap-y-3 border border-[#E4DFD6]">
        <div>
          <div class="flex items-center gap-space-sm">
            <h1 class="text-xl font-bold text-on-surface">Interactive Review Studio</h1>
            <span class="px-2.5 py-0.5 rounded-full bg-primary-container text-on-primary font-mono text-xs">{page_filename} (Page ID: {current_page_id})</span>
          </div>
          <p class="text-xs text-on-surface-variant mt-0.5">
            Inspect YOLOv8 detection boxes ({total_regions_count} bubbles) and refine raw MangaOCR transcription in real time.
          </p>
        </div>

        <!-- Center Pagination Control -->
        <div class="inline-flex items-center gap-2 bg-surface-container-low px-2 py-1.5 rounded-full border border-[#E4DFD6]">
          <button onclick="navigateParent('review-studio?page_id={prev_page_id}')" class="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-surface-container-lowest text-on-surface text-xs font-semibold shadow-xs hover:bg-surface cursor-pointer" type="button">
            <span class="material-symbols-outlined text-[16px]">chevron_left</span>
            <span>Prev Page</span>
          </button>
          <div class="px-3 text-sm text-on-surface flex items-baseline gap-1 select-none">
            <span class="font-bold">Page {page_idx}</span>
            <span class="text-xs text-on-surface-variant">of {total_pages}</span>
          </div>
          <button onclick="navigateParent('review-studio?page_id={next_page_id}')" class="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-surface-container-lowest text-on-surface text-xs font-semibold shadow-xs hover:bg-surface cursor-pointer" type="button">
            <span>Next Page</span>
            <span class="material-symbols-outlined text-[16px]">chevron_right</span>
          </button>
        </div>
      </div>

      <!-- Dual Split Workspace -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-space-lg items-start">

        <!-- LEFT PANEL: Real Original Page & YOLOv8 Bounding Boxes -->
        <div class="bg-surface-container-lowest rounded-xl p-space-md shadow-sm flex flex-col border border-[#E4DFD6]">
          <div class="flex items-center justify-between pb-space-sm mb-space-sm border-b border-[#E4DFD6]">
            <div class="flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-full bg-primary"></span>
              <span class="text-sm font-semibold text-on-surface">Original Page — YOLOv8 Detection Preview</span>
            </div>
            <span class="font-mono text-xs text-on-surface-variant">{img_w} × {img_h} px • {total_regions_count} Regions</span>
          </div>

          <div class="relative w-full min-h-[620px] bg-inverse-surface rounded-xl p-4 flex items-center justify-center overflow-auto select-none">
            <div class="relative inline-block shadow-2xl rounded-xs overflow-hidden" id="manga-canvas">
              <img src="data:image/jpeg;base64,{orig_b64}" alt="Original Manga Page" class="max-h-[600px] w-auto block select-none"/>
              {overlays_html}
            </div>
          </div>
        </div>

        <!-- RIGHT PANEL: Real Extracted Text (Manga OCR Correction) -->
        <div class="bg-surface-container-lowest rounded-xl p-space-md shadow-sm flex flex-col border border-[#E4DFD6]">
          <div class="flex items-center justify-between pb-space-sm mb-space-sm border-b border-[#E4DFD6]">
            <div>
              <h2 class="text-sm font-bold text-on-surface">Extracted Text (Manga OCR — {total_regions_count} Bubbles)</h2>
              <p class="text-xs text-on-surface-variant">Click any box on the manga page or edit Japanese text below before proceeding.</p>
            </div>
          </div>

          <div class="flex flex-col gap-3 max-h-[620px] overflow-y-auto pr-1" id="ocr-cards-container">
            {cards_html}
          </div>
        </div>

      </div>

      <!-- Sticky Bottom Action Footer -->
      <div class="mt-space-lg bg-surface-container-lowest rounded-xl p-space-md shadow-md flex flex-wrap items-center justify-between gap-4 border border-[#E4DFD6]">
        <div class="flex items-center gap-2 text-secondary text-xs font-medium">
          <span class="material-symbols-outlined text-[18px]">cloud_done</span>
          <span class="text-on-surface-variant">Connected to SQLite Database • <span class="text-secondary font-semibold">Page ID #{current_page_id}</span></span>
        </div>

        <div class="flex items-center gap-3">
          <button onclick="saveAndProceed('review')" class="px-5 py-2.5 rounded-full bg-surface-container text-on-surface hover:bg-surface-container-high transition-colors text-xs font-semibold flex items-center gap-2 cursor-pointer border border-[#E4DFD6]" type="button">
            <span class="material-symbols-outlined text-[18px]">save</span>
            <span>Save OCR Edits &amp; Re-Translate</span>
          </button>
          <button onclick="saveAndProceed('typesetting')" id="confirm-btn" class="px-6 py-2.5 rounded-full bg-primary-container text-on-primary hover:bg-primary shadow-md transition-all text-xs font-semibold flex items-center gap-2 cursor-pointer" type="button">
            <span>Confirm &amp; Proceed to Typesetting</span>
            <span class="material-symbols-outlined text-[18px]">arrow_forward</span>
          </button>
        </div>
      </div>

    </div>
  </main>
</div>

<script>
const TOTAL_BOXES = {total_regions_count};

function navigateParent(path) {{
  const targetUrl = window.location.origin + '/' + path.replace(/^\/+/, '');
  const a = document.createElement('a');
  a.href = targetUrl;
  a.target = '_top';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}}

function selectBox(boxIndex) {{
  for (let i = 1; i <= TOTAL_BOXES; i++) {{
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
        box.classList.add('ring-4', 'bg-primary-container/35');
      }} else {{
        box.classList.remove('ring-4', 'bg-primary-container/35');
      }}
    }}
  }}
}}

function saveAndProceed(nextRoute) {{
  const inputs = document.querySelectorAll('.ocr-input-field');
  const updates = {{}};
  inputs.forEach(inp => {{
    const rid = inp.getAttribute('data-region-id');
    if (rid) updates[rid] = inp.value;
  }});

  const btn = document.getElementById('confirm-btn');
  if (btn) {{
    btn.innerHTML = `<span class="material-symbols-outlined animate-spin text-[18px]">sync</span><span>Syncing SQLite &amp; Rendering...</span>`;
  }}

  const encodedUpdates = encodeURIComponent(JSON.stringify(updates));
  const proj = encodeURIComponent('{project_name}');
  navigateParent(`review-studio?project=${{proj}}&page_id={current_page_id}&save_ocr=1&next=${{nextRoute}}&updates=${{encodedUpdates}}`);
}}
</script>

</body>
</html>
"""

components.html(review_studio_html, height=1150, scrolling=True)