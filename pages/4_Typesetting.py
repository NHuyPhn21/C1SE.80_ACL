"""ACL Live Typesetting Editor — Speech Bubble Typography Studio — Screen ACL-08 (Live Backend Connected)."""

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

# Enforce authentication guard
user = require_auth()

user_initials = (user.full_name[:2] if user.full_name else "PH").upper()
user_name = user.full_name or "Phan Nhat Huy"
project_name = st.query_params.get("project", "Shonen Weekly #112")

db = SessionLocal()
try:
    all_pages = db.query(ComicPage).order_by(ComicPage.id.asc()).all()

    # =====================================================================
    # 1. NẾU NGƯỜI DÙNG BẤM LƯU BẢN DỊCH TIẾNG VIỆT & RENDER LẠI TRANG
    # =====================================================================
    if st.query_params.get("save_typeset") == "1":
        target_pid = int(st.query_params.get("page_id", 0))
        updates_raw = st.query_params.get("updates", "{}")
        go_queue = st.query_params.get("go_queue", "0")
        try:
            updates_dict = json.loads(updates_raw)
            for reg_id_str, new_vi_text in updates_dict.items():
                reg = db.query(TextRegion).filter(TextRegion.id == int(reg_id_str)).first()
                if reg and new_vi_text is not None:
                    reg.translated_text = new_vi_text.strip()
            db.commit()

            # Chạy lại bước Inpainting + Auto-Typesetting để vẽ ngay chữ tiếng Việt mới lên ảnh
            if target_pid:
                final_path = process_comic_page(page_id=target_pid, use_lama_api=False)
                page_obj = db.query(ComicPage).filter(ComicPage.id == target_pid).first()
                if page_obj and final_path:
                    page_obj.rendered_path = str(Path(final_path).relative_to(BASE_DIR)).replace("\\", "/")
                    page_obj.status = "COMPLETED"
                    db.commit()
        except Exception as e:
            print(f"⚠️ Lỗi khi lưu và vẽ lại trang tại Typesetting: {e}")

        st.query_params.clear()
        st.query_params["project"] = project_name
        st.query_params["page_id"] = str(target_pid)
        if go_queue == "1":
            st.switch_page("pages/5_Queue_Monitor.py")
        else:
            st.rerun()

    # =====================================================================
    # 2. LẤY DỮ LIỆU TRANG HIỆN TẠI ĐỂ HIỂN THỊ LÊN CANVAS
    # =====================================================================
    req_page_id = st.query_params.get("page_id")
    current_page = None
    if req_page_id and str(req_page_id).isdigit():
        current_page = db.query(ComicPage).filter(ComicPage.id == int(req_page_id)).first()
    if not current_page and all_pages:
        current_page = all_pages[-1]

    rendered_b64 = ""
    orig_b64 = ""
    img_w, img_h = 1600, 2560
    regions_list = []
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

        orig_real = resolve_project_path(current_page.original_path)
        page_filename = os.path.basename(orig_real)
        if os.path.exists(orig_real):
            orig_b64 = encode_image_to_base64(orig_real)
            with Image.open(orig_real) as im:
                img_w, img_h = im.size

        # Tìm file ảnh đã dịch trong data/rendered_pages
        rendered_candidate = BASE_DIR / "data" / "rendered_pages" / f"final_{page_filename}"
        if current_page.rendered_path and os.path.exists(resolve_project_path(current_page.rendered_path)):
            rendered_real = resolve_project_path(current_page.rendered_path)
        elif rendered_candidate.exists():
            rendered_real = str(rendered_candidate)
        else:
            rendered_real = orig_real

        if os.path.exists(rendered_real):
            rendered_b64 = encode_image_to_base64(rendered_real)

        raw_regs = db.query(TextRegion).filter(TextRegion.page_id == current_page.id).all()
        clean_regs = _deduplicate_db_regions(raw_regs) if raw_regs else []
        if not clean_regs and raw_regs:
            clean_regs = raw_regs

        for idx, r in enumerate(clean_regs, start=1):
            bbox = json.loads(r.bbox_json)
            x1, y1, x2, y2 = map(int, bbox[:4])
            regions_list.append({
                "index": idx,
                "id": r.id,
                "left_pct": round((x1 / max(1, img_w)) * 100, 2),
                "top_pct": round((y1 / max(1, img_h)) * 100, 2),
                "width_pct": round(((x2 - x1) / max(1, img_w)) * 100, 2),
                "height_pct": round(((y2 - y1) / max(1, img_h)) * 100, 2),
                "original_text": r.original_text or "",
                "translated_text": r.translated_text or "",
            })
finally:
    db.close()

# Tạo các vùng click trong suốt trên ảnh để chọn nhanh bóng thoại cần sửa
click_hotspots_html = ""
bubble_options_html = ""

for item in regions_list:
    idx = item["index"]
    rid = item["id"]
    vi_short = (item["translated_text"][:28] + "...") if len(item["translated_text"]) > 28 else item["translated_text"]
    click_hotspots_html += f"""
      <div onclick="selectBubble({idx - 1})" id="hotspot-{idx - 1}"
           style="left: {item['left_pct']}%; top: {item['top_pct']}%; width: {item['width_pct']}%; height: {item['height_pct']}%;"
           title="Click to edit Bubble #{idx}"
           class="absolute cursor-pointer rounded-sm transition-all hover:ring-2 hover:ring-primary-container/80 hover:bg-primary-container/10">
      </div>
    """
    bubble_options_html += f'<option value="{idx - 1}">Bubble #{idx} — {vi_short}</option>'

regions_json = json.dumps(regions_list, ensure_ascii=False)
total_bubbles = len(regions_list)

typesetting_html = f"""<!DOCTYPE html>
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
      <a class="flex items-center gap-space-sm px-space-sm py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high cursor-pointer" onclick="navigateParent('review-studio?page_id={current_page_id}')">
        <span class="material-symbols-outlined">rate_review</span>
        <span>Review Studio</span>
      </a>
      <a aria-current="page" class="flex items-center gap-space-sm px-space-sm py-2 rounded-lg bg-primary-container text-on-primary font-semibold cursor-pointer">
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
      <span>HLcomic1 Font • Active</span>
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
      <span class="text-primary-container font-semibold">Live Typesetting Studio (final_{page_filename})</span>
    </div>
    <div class="flex items-center gap-space-md">
      <div class="w-8 h-8 rounded-full bg-primary-container flex items-center justify-center text-xs text-on-primary font-semibold notranslate" translate="no">{user_initials}</div>
    </div>
  </header>

  <main class="relative pt-16 min-h-screen bg-surface w-full px-space-lg py-space-md">
    <div class="flex flex-col w-full">

      <!-- Top Workspace Context Bar -->
      <div class="flex flex-col md:flex-row md:items-center justify-between pb-space-md gap-space-sm">
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-xl font-bold text-on-surface">Live Typesetting Editor</h1>
            <span class="px-2 py-0.5 rounded-full bg-secondary-container text-secondary font-mono text-xs font-semibold">Collision Avoidance Active</span>
          </div>
          <p class="text-xs text-on-surface-variant mt-0.5">
            Click any speech bubble on the rendered page to refine Vietnamese dialogue and re-render instantaneously.
          </p>
        </div>

        <!-- Center Pagination Control -->
        <div class="inline-flex items-center gap-1.5 p-1 bg-surface-container rounded-full shadow-sm border border-[#E4DFD6]">
          <button onclick="navigateParent('typesetting?page_id={prev_page_id}')" class="inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-on-surface hover:bg-surface-container-lowest text-xs font-semibold cursor-pointer" type="button">
            <span class="material-symbols-outlined text-[18px]">arrow_back</span>
            <span>Prev Page</span>
          </button>
          <div class="px-3 py-1 bg-surface-container-lowest rounded-full shadow-xs text-xs font-semibold text-on-surface">
            <span>Page {page_idx} of {total_pages} ({page_filename})</span>
          </div>
          <button onclick="navigateParent('typesetting?page_id={next_page_id}')" class="inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-on-surface hover:bg-surface-container-lowest text-xs font-semibold cursor-pointer" type="button">
            <span>Next Page</span>
            <span class="material-symbols-outlined text-[18px]">arrow_forward</span>
          </button>
        </div>
      </div>

      <!-- Main Split Editor Workspace -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-space-md w-full items-start">

        <!-- LEFT PANEL: Real Rendered Manga Page Stage (col-span-7) -->
        <div class="lg:col-span-7 bg-surface-container-lowest rounded-xl p-space-md shadow-sm flex flex-col gap-space-sm border border-[#E4DFD6]">
          <div class="flex items-center justify-between pb-2 border-b border-[#E4DFD6]">
            <div class="flex items-center gap-2">
              <span class="text-sm font-semibold text-on-surface">Rendered Page Output (final_{page_filename})</span>
              <span class="px-2 py-0.5 rounded bg-surface-container text-on-surface-variant font-mono text-xs">{img_w} × {img_h} px</span>
            </div>
            <label class="inline-flex items-center gap-2 cursor-pointer select-none">
              <input onchange="toggleOriginalImage(this.checked)" class="sr-only peer" id="toggle-original-bg" type="checkbox"/>
              <span class="w-8 h-4 bg-surface-container-high rounded-full peer peer-checked:bg-primary-container transition-colors relative after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:w-3 after:h-3 after:rounded-full after:transition-transform peer-checked:after:translate-x-4"></span>
              <span class="text-xs font-semibold text-on-surface-variant">Compare Original Japanese</span>
            </label>
          </div>

          <div class="relative w-full rounded-lg bg-inverse-surface p-4 flex items-center justify-center min-h-[640px] overflow-auto select-none">
            <div class="relative inline-block shadow-2xl rounded-xs overflow-hidden" id="manga-sheet">
              <img id="rendered-page-img" src="data:image/jpeg;base64,{rendered_b64}" alt="Rendered Vietnamese Manga Page" class="max-h-[620px] w-auto block select-none"/>
              {click_hotspots_html}
            </div>
          </div>
        </div>

        <!-- RIGHT PANEL: Typography Inspector & Controls (col-span-5) -->
        <div class="lg:col-span-5 bg-surface-container-lowest rounded-xl p-space-lg shadow-sm flex flex-col gap-space-md border border-[#E4DFD6]">
          <div class="flex items-center justify-between pb-2 border-b border-[#E4DFD6]">
            <div>
              <h2 class="text-base font-bold text-on-surface">Dialogue &amp; Typography Inspector</h2>
              <span class="text-xs text-on-surface-variant">Edit Vietnamese translation and re-burn into speech bubbles</span>
            </div>
            <span id="active-bubble-badge" class="px-2.5 py-1 rounded-full bg-primary-fixed text-primary font-mono text-xs font-bold">
              Bubble #1 / {total_bubbles}
            </span>
          </div>

          <!-- Selector chọn nhanh bóng thoại -->
          <div class="flex flex-col gap-1">
            <label class="font-mono text-xs uppercase font-semibold text-on-surface-variant">Select Speech Bubble ({total_bubbles} detected)</label>
            <select id="bubble-selector" onchange="selectBubble(parseInt(this.value))" class="w-full bg-surface-container-low text-on-surface text-xs font-semibold rounded-lg p-2.5 border border-[#E4DFD6] focus:outline-none focus:ring-2 focus:ring-primary-container cursor-pointer">
              {bubble_options_html}
            </select>
          </div>

          <!-- Raw Japanese Text (Read-only reference) -->
          <div class="flex flex-col gap-1">
            <label class="font-mono text-xs uppercase font-semibold text-on-surface-variant">Original Japanese (MangaOCR)</label>
            <div id="ja-ref-box" class="w-full bg-surface-container-low rounded-lg px-3 py-2 text-xs font-medium text-on-surface-variant border border-[#E4DFD6] notranslate" translate="no">
              ...
            </div>
          </div>

          <!-- Translated Vietnamese Text Input -->
          <div class="flex flex-col gap-1.5">
            <div class="flex items-center justify-between">
              <label class="font-mono text-xs uppercase font-semibold text-primary" for="vn-text-editor">
                Translated Vietnamese Text (Editable)
              </label>
              <span class="font-mono text-[11px] text-secondary font-semibold">Auto-Fit Distance Transform</span>
            </div>
            <textarea oninput="updateCurrentBubbleText(this.value)" class="w-full bg-surface-container-low rounded-lg p-3 text-sm font-semibold text-on-surface focus:outline-none focus:ring-2 focus:ring-primary-container border border-[#E4DFD6]" id="vn-text-editor" rows="4" placeholder="Nhập lời thoại tiếng Việt..."></textarea>
          </div>

          <!-- Nút Re-render trực tiếp lên trang truyện -->
          <button onclick="saveAndRenderPage(0)" id="rerender-btn" class="w-full py-3 rounded-xl bg-secondary text-on-secondary hover:opacity-95 font-semibold text-xs shadow-sm flex items-center justify-center gap-2 cursor-pointer transition-all active:scale-98" type="button">
            <span class="material-symbols-outlined text-[18px]">auto_fix_high</span>
            <span>Save Edits &amp; Re-Render Page Image Now</span>
          </button>

          <div class="pt-2 border-t border-[#E4DFD6] text-xs text-on-surface-variant space-y-1">
            <div class="flex items-center justify-between">
              <span>Font Engine:</span>
              <strong class="font-mono text-on-surface">HLcomic1_normal.ttf (Size 8–22px)</strong>
            </div>
            <div class="flex items-center justify-between">
              <span>Inpainting Engine:</span>
              <strong class="font-mono text-secondary">Topological Mask + OpenCV Telea</strong>
            </div>
          </div>
        </div>

      </div>

      <!-- BOTTOM ACTION BAR -->
      <div class="w-full bg-surface-container-lowest rounded-xl p-space-md shadow-sm mt-space-md flex flex-col sm:flex-row items-center justify-between gap-space-md border border-[#E4DFD6]">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-full bg-secondary-container flex items-center justify-center text-secondary">
            <span class="material-symbols-outlined text-[20px]">check</span>
          </div>
          <div class="flex flex-col">
            <span class="text-sm font-semibold text-on-surface">{total_bubbles} Speech Bubbles Configured on {page_filename}</span>
            <span class="text-xs text-on-surface-variant">Output saved at: <code>data/rendered_pages/final_{page_filename}</code></span>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <button onclick="navigateParent('review-studio?page_id={current_page_id}')" class="px-5 h-10 rounded-full bg-surface-container hover:bg-surface-container-high text-on-surface text-xs font-semibold flex items-center gap-1.5 cursor-pointer border border-[#E4DFD6]" type="button">
            <span class="material-symbols-outlined text-[16px]">arrow_back</span>
            <span>Back to Review Studio</span>
          </button>
          <button onclick="saveAndRenderPage(1)" class="px-7 h-10 rounded-full bg-primary-container hover:bg-primary text-on-primary text-xs font-bold shadow-md flex items-center gap-1.5 cursor-pointer" type="button">
            <span>Mark Page Complete &amp; View Queue</span>
            <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
          </button>
        </div>
      </div>

    </div>
  </main>
</div>

<script>
const REGIONS = {regions_json};
const RENDERED_B64 = "{rendered_b64}";
const ORIG_B64 = "{orig_b64}";
let currentIdx = 0;
const editedTranslations = {{}};

// Khởi tạo dữ liệu ban đầu
REGIONS.forEach(r => {{
  editedTranslations[r.id] = r.translated_text;
}});

function navigateParent(path) {{
  const targetUrl = window.location.origin + '/' + path.replace(/^\/+/, '');
  const a = document.createElement('a');
  a.href = targetUrl;
  a.target = '_top';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}}

function selectBubble(idx) {{
  if (!REGIONS || REGIONS.length === 0) return;
  currentIdx = Math.max(0, Math.min(REGIONS.length - 1, idx));
  const item = REGIONS[currentIdx];

  const selector = document.getElementById('bubble-selector');
  if (selector) selector.value = String(currentIdx);

  const badge = document.getElementById('active-bubble-badge');
  if (badge) badge.innerText = `Bubble #${{item.index}} / ${{REGIONS.length}}`;

  const jaBox = document.getElementById('ja-ref-box');
  if (jaBox) jaBox.innerText = item.original_text || '(Empty)';

  const editor = document.getElementById('vn-text-editor');
  if (editor) editor.value = editedTranslations[item.id] !== undefined ? editedTranslations[item.id] : item.translated_text;

  // Highlight hotspot trên ảnh
  REGIONS.forEach((_, i) => {{
    const hs = document.getElementById('hotspot-' + i);
    if (hs) {{
      if (i === currentIdx) {{
        hs.classList.add('ring-4', 'ring-primary-container', 'bg-primary-container/20');
      }} else {{
        hs.classList.remove('ring-4', 'ring-primary-container', 'bg-primary-container/20');
      }}
    }}
  }});
}}

function updateCurrentBubbleText(val) {{
  if (!REGIONS || REGIONS.length === 0) return;
  const item = REGIONS[currentIdx];
  editedTranslations[item.id] = val;
}}

function toggleOriginalImage(showOrig) {{
  const img = document.getElementById('rendered-page-img');
  if (!img) return;
  img.src = 'data:image/jpeg;base64,' + (showOrig ? ORIG_B64 : RENDERED_B64);
}}

function saveAndRenderPage(goQueue) {{
  const btn = document.getElementById('rerender-btn');
  if (btn) {{
    btn.innerHTML = `<span class="material-symbols-outlined animate-spin text-[18px]">sync</span><span>Re-rendering Vietnamese Typography...</span>`;
  }}
  const encoded = encodeURIComponent(JSON.stringify(editedTranslations));
  const proj = encodeURIComponent('{project_name}');
  navigateParent(`typesetting?project=${{proj}}&page_id={current_page_id}&save_typeset=1&go_queue=${{goQueue}}&updates=${{encoded}}`);
}}

// Mặc định chọn Bubble #1 khi mở trang
if (REGIONS.length > 0) {{
  selectBubble(0);
}}
</script>

</body>
</html>
"""

components.html(typesetting_html, height=1150, scrolling=True)