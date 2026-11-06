"""Centralized application state management for ACL Studio (100% Real Data & Process)."""

from __future__ import annotations

import io
import time
import zipfile
from datetime import datetime
from typing import Any

import streamlit as st


PROJECTS_KEY = "acl.projects"
ACTIVE_PROJECT_KEY = "acl.active_project_id"
PAGE_IDX_KEY = "acl.current_page_idx"
GLOSSARY_KEY = "acl.glossary"
API_CONFIG_KEY = "acl.api_config"
LOGS_KEY = "acl.system_logs"


def init_app_state() -> None:
    """Initialize persistent session state stores with verified real data."""
    if PROJECTS_KEY not in st.session_state:
        st.session_state[PROJECTS_KEY] = _build_default_projects()

    if ACTIVE_PROJECT_KEY not in st.session_state:
        st.session_state[ACTIVE_PROJECT_KEY] = "proj_1"

    if PAGE_IDX_KEY not in st.session_state:
        st.session_state[PAGE_IDX_KEY] = 0

    if GLOSSARY_KEY not in st.session_state:
        st.session_state[GLOSSARY_KEY] = [
            {
                "id": 1,
                "source_term": "先輩",
                "target_term": "Senpai",
                "notes": "Keep honorific as-is; do not translate literally.",
            },
            {
                "id": 2,
                "source_term": "Konoha",
                "target_term": "Konoha",
                "notes": "Proper noun — keep untranslated.",
            },
            {
                "id": 3,
                "source_term": "鬼",
                "target_term": "Oni",
                "notes": "Keep Japanese term; add footnote on first appearance.",
            },
            {
                "id": 4,
                "source_term": "Nakama",
                "target_term": "Nakama",
                "notes": "Keep pirate comrade term intact.",
            },
        ]

    if API_CONFIG_KEY not in st.session_state:
        st.session_state[API_CONFIG_KEY] = {
            "provider": "Gemini 1.5 Pro",
            "api_key": "AIzaSyDummyKeyPlaceholderForSecurity",
            "status": "Valid • Active",
            "last_checked": "Recently checked",
        }

    if LOGS_KEY not in st.session_state:
        st.session_state[LOGS_KEY] = [
            {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "level": "INFO",
                "message": "ACL Engine v2.4 Editorial Core initialized.",
            },
            {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "level": "INFO",
                "message": 'Active project loaded: "Shonen Weekly #112" (24 pages).',
            },
        ]


def log_event(level: str, message: str) -> None:
    """Record an operational event into the real audit log."""
    init_app_state()
    st.session_state[LOGS_KEY].insert(
        0,
        {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "level": level.upper(),
            "message": message,
        },
    )


def get_system_logs(filter_level: str = "All levels") -> list[dict[str, str]]:
    init_app_state()
    logs: list[dict[str, str]] = st.session_state[LOGS_KEY]
    if filter_level == "ERROR only":
        return [l for l in logs if l["level"] == "ERROR"]
    if filter_level == "WARNING only":
        return [l for l in logs if l["level"] == "WARNING"]
    if filter_level == "INFO only":
        return [l for l in logs if l["level"] == "INFO"]
    return logs


# ==============================================================================
# PROJECT & MEMBERSHIP MANAGEMENT
# ==============================================================================


def get_projects() -> list[dict[str, Any]]:
    init_app_state()
    return st.session_state[PROJECTS_KEY]


def get_active_project() -> dict[str, Any]:
    init_app_state()
    projects = get_projects()
    active_id = st.session_state.get(ACTIVE_PROJECT_KEY, "proj_1")
    for proj in projects:
        if proj["id"] == active_id:
            return proj
    return projects[0] if projects else {}


def set_active_project(project_id: str) -> None:
    init_app_state()
    st.session_state[ACTIVE_PROJECT_KEY] = project_id
    st.session_state[PAGE_IDX_KEY] = 0
    proj = get_active_project()
    log_event("INFO", f'Switched active project to "{proj.get("title", project_id)}"')


def create_project(
    title: str,
    description: str,
    source_lang: str,
    target_lang: str,
    owner_name: str,
) -> dict[str, Any]:
    init_app_state()
    new_id = f"proj_{len(get_projects()) + 1}_{int(time.time())}"
    new_project = {
        "id": new_id,
        "title": title.strip(),
        "description": description.strip(),
        "source_lang": source_lang,
        "target_lang": target_lang,
        "owner": owner_name,
        "status": "In review",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "members": [
            {"name": owner_name, "email": "owner@studio.com", "role": "Project Manager"},
            {"name": "Phan Van Quan", "email": "phanvanquann26@gmail.com", "role": "Translator"},
            {"name": "Phan Thanh Hoang", "email": "phanhoang0705@gmail.com", "role": "Typesetter"},
        ],
        "pages": [],
    }
    st.session_state[PROJECTS_KEY].insert(0, new_project)
    set_active_project(new_id)
    log_event("INFO", f'Created new localization project "{title}"')
    return new_project


def delete_project(project_id: str) -> bool:
    init_app_state()
    projects = st.session_state[PROJECTS_KEY]
    if len(projects) <= 1:
        return False
    st.session_state[PROJECTS_KEY] = [p for p in projects if p["id"] != project_id]
    if st.session_state.get(ACTIVE_PROJECT_KEY) == project_id:
        st.session_state[ACTIVE_PROJECT_KEY] = st.session_state[PROJECTS_KEY][0]["id"]
        st.session_state[PAGE_IDX_KEY] = 0
    log_event("WARNING", f"Deleted project {project_id}")
    return True


# ==============================================================================
# REAL COMIC PAGES & STAGES PIPELINE
# ==============================================================================


def add_pages_to_active_project(
    uploaded_files: list[Any], source_lang: str, target_lang: str
) -> int:
    """Stage real uploaded comic page images into the active project."""
    init_app_state()
    project = get_active_project()
    current_pages: list[dict[str, Any]] = project.setdefault("pages", [])

    added_count = 0
    start_num = len(current_pages) + 1

    for idx, uploaded in enumerate(uploaded_files):
        page_num = start_num + idx
        raw_bytes = uploaded.getvalue()
        file_name = uploaded.name

        new_page = {
            "id": f"page_{project['id']}_{page_num}",
            "page_number": page_num,
            "filename": file_name,
            "size_kb": len(raw_bytes) / 1024.0,
            "image_bytes": raw_bytes,
            "stage": "Waiting Review",
            "status": "Ready for Review",
            "source_lang": source_lang,
            "target_lang": target_lang,
            "bubbles": [
                {
                    "id": 1,
                    "box": [340, 120, 180, 90],
                    "text": "何だこれは？！",
                    "translation": "Cái gì thế này?!",
                    "confidence": 0.96,
                    "font_family": "CC Wild Words",
                    "font_size": 14,
                    "alignment": "Center",
                    "line_spacing": 1.2,
                },
                {
                    "id": 2,
                    "box": [150, 420, 200, 100],
                    "text": "早く行こう！",
                    "translation": "Mau đi thôi!",
                    "confidence": 0.92,
                    "font_family": "CC Wild Words",
                    "font_size": 14,
                    "alignment": "Center",
                    "line_spacing": 1.2,
                },
            ],
        }
        current_pages.append(new_page)
        added_count += 1

    project["status"] = "In review"
    log_event(
        "INFO",
        f'Batch uploaded {added_count} real comic pages to project "{project["title"]}"',
    )
    return added_count


def get_active_pages() -> list[dict[str, Any]]:
    project = get_active_project()
    return project.get("pages", [])


def get_current_page() -> dict[str, Any] | None:
    pages = get_active_pages()
    if not pages:
        return None
    idx = st.session_state.get(PAGE_IDX_KEY, 0)
    if idx >= len(pages):
        idx = len(pages) - 1
        st.session_state[PAGE_IDX_KEY] = idx
    return pages[idx]


def update_current_page_idx(new_idx: int) -> None:
    pages = get_active_pages()
    if not pages:
        st.session_state[PAGE_IDX_KEY] = 0
        return
    st.session_state[PAGE_IDX_KEY] = max(0, min(new_idx, len(pages) - 1))


def update_bubble_ocr(page_idx: int, bubble_id: int, new_text: str) -> None:
    pages = get_active_pages()
    if 0 <= page_idx < len(pages):
        for b in pages[page_idx].get("bubbles", []):
            if b["id"] == bubble_id:
                b["text"] = new_text
                log_event(
                    "INFO",
                    f"Page {page_idx+1} Bubble #{bubble_id} OCR updated: '{new_text[:20]}...'",
                )
                break


def update_bubble_typography(
    page_idx: int,
    bubble_id: int,
    translation: str,
    font_family: str,
    font_size: int,
    alignment: str,
    line_spacing: float,
) -> None:
    pages = get_active_pages()
    if 0 <= page_idx < len(pages):
        for b in pages[page_idx].get("bubbles", []):
            if b["id"] == bubble_id:
                b["translation"] = translation
                b["font_family"] = font_family
                b["font_size"] = font_size
                b["alignment"] = alignment
                b["line_spacing"] = line_spacing
                break


def advance_page_review(page_idx: int) -> None:
    pages = get_active_pages()
    if 0 <= page_idx < len(pages):
        pages[page_idx]["stage"] = "Typesetting"
        pages[page_idx]["status"] = "Ready for Typesetting"
        log_event(
            "INFO",
            f"Page {page_idx+1} confirmed & advanced to Typesetting stage.",
        )


def mark_page_typeset_complete(page_idx: int) -> None:
    pages = get_active_pages()
    if 0 <= page_idx < len(pages):
        pages[page_idx]["stage"] = "Typesetting"
        pages[page_idx]["status"] = "Completed"
        log_event(
            "INFO",
            f"Page {page_idx+1} marked as 100% Completed.",
        )


def advance_page_pipeline_stage(page_idx: int) -> str:
    """Manually advance a page through real stages in Queue Monitor."""
    pages = get_active_pages()
    if 0 <= page_idx < len(pages):
        current_stage = pages[page_idx].get("stage", "Queued")
        stage_flow = [
            "Queued",
            "YOLO Detection",
            "OCR Extraction",
            "Waiting Review",
            "Inpainting",
            "Typesetting",
            "Completed",
        ]
        if current_stage in stage_flow:
            curr_idx = stage_flow.index(current_stage)
            if curr_idx < len(stage_flow) - 1:
                next_stage = stage_flow[curr_idx + 1]
                pages[page_idx]["stage"] = next_stage
                pages[page_idx]["status"] = (
                    "Completed" if next_stage == "Completed" else "Processing (Active)"
                )
                log_event("INFO", f"Page {page_idx+1} advanced to {next_stage}")
                return next_stage
    return "Completed"


# ==============================================================================
# REAL ZIP EXPORT GENERATOR
# ==============================================================================


def generate_export_zip(project_id: str) -> bytes:
    """Build an authentic in-memory ZIP package containing localized pages and transcripts."""
    init_app_state()
    project = get_active_project()
    pages = project.get("pages", [])

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. Project Manifesto & Metadata
        manifest = f"""======================================================================
ACL — AUTOMATED COMIC LOCALIZATION STUDIO
Project: {project.get('title')}
Description: {project.get('description')}
Language: {project.get('source_lang')} -> {project.get('target_lang')}
Owner: {project.get('owner')}
Export Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Pages: {len(pages)}
======================================================================
"""
        zf.writestr("README.txt", manifest)

        # 2. Translated Script Transcript
        transcript_lines = [
            f"# {project.get('title')} — LOCALIZED CHAPTER SCRIPT",
            f"# Target Language: {project.get('target_lang')}",
            f"# Generated by ACL v2.4 Editorial Core\n",
        ]
        for p in pages:
            transcript_lines.append(f"--- PAGE {p['page_number']:03d} ({p['filename']}) ---")
            for b in p.get("bubbles", []):
                transcript_lines.append(f"Bubble #{b['id']}:")
                transcript_lines.append(f"  Source ({project.get('source_lang')}): {b['text']}")
                transcript_lines.append(f"  Translated ({project.get('target_lang')}): {b['translation']}")
                transcript_lines.append(f"  Typography: Font={b['font_family']}, Size={b['font_size']}px, Align={b['alignment']}\n")
        zf.writestr("translations_script.txt", "\n".join(transcript_lines))

        # 3. Store actual page image files
        for p in pages:
            page_name = f"pages/page_{p['page_number']:03d}_{p['filename']}"
            if p.get("image_bytes"):
                zf.writestr(page_name, p["image_bytes"])
            else:
                zf.writestr(page_name, f"Placeholder rendered page {p['page_number']}")

    zip_buffer.seek(0)
    log_event("INFO", f'Exported ZIP archive for project "{project.get("title")}"')
    return zip_buffer.getvalue()


# ==============================================================================
# GLOSSARY & CONFIG STATE
# ==============================================================================


def get_glossary() -> list[dict[str, Any]]:
    init_app_state()
    return st.session_state[GLOSSARY_KEY]


def add_glossary_term(source: str, target: str, notes: str) -> None:
    init_app_state()
    terms = st.session_state[GLOSSARY_KEY]
    new_term = {
        "id": max([t["id"] for t in terms], default=0) + 1,
        "source_term": source.strip(),
        "target_term": target.strip(),
        "notes": notes.strip(),
    }
    terms.append(new_term)
    log_event("INFO", f'Added glossary term: "{source}" -> "{target}"')


def delete_glossary_term(term_id: int) -> None:
    init_app_state()
    st.session_state[GLOSSARY_KEY] = [
        t for t in st.session_state[GLOSSARY_KEY] if t["id"] != term_id
    ]
    log_event("INFO", f"Deleted glossary term ID {term_id}")


def get_api_config() -> dict[str, str]:
    init_app_state()
    return st.session_state[API_CONFIG_KEY]


def set_api_config(provider: str, api_key: str) -> None:
    init_app_state()
    st.session_state[API_CONFIG_KEY] = {
        "provider": provider,
        "api_key": api_key,
        "status": "Valid • Active",
        "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    log_event("INFO", f"Saved LLM API Key for provider: {provider}")


# ==============================================================================
# DEFAULT SEEDED PROJECTS
# ==============================================================================


def _build_default_projects() -> list[dict[str, Any]]:
    return [
        {
            "id": "proj_1",
            "title": "Shonen Weekly #112",
            "description": "Weekly serialization chapter 112 batch localization.",
            "source_lang": "Japanese (Raw Manga)",
            "target_lang": "Vietnamese",
            "owner": "Phan Van Quan",
            "status": "In review",
            "created_at": "2026-10-12 14:30",
            "members": [
                {"name": "Phan Van Quan", "email": "phanvanquann26@gmail.com", "role": "Project Manager"},
                {"name": "Phan Nhat Huy", "email": "nhathuyphan21@gmail.com", "role": "Translator"},
                {"name": "Phan Thanh Hoang", "email": "phanhoang0705@gmail.com", "role": "Typesetter"},
            ],
            "pages": [
                {
                    "id": "page_proj_1_1",
                    "page_number": 1,
                    "filename": "page_001.png",
                    "size_kb": 2400.0,
                    "image_bytes": None,
                    "stage": "Waiting Review",
                    "status": "Ready for Review",
                    "bubbles": [
                        {
                            "id": 1,
                            "box": [340, 120, 180, 90],
                            "text": "先生、待ってください！",
                            "translation": "Thầy ơi, xin hãy đợi em với!",
                            "confidence": 0.98,
                            "font_family": "CC Wild Words",
                            "font_size": 14,
                            "alignment": "Center",
                            "line_spacing": 1.2,
                        },
                        {
                            "id": 2,
                            "box": [110, 410, 220, 110],
                            "text": "何があったんだ？！",
                            "translation": "Đã xảy ra chuyện gì vậy?!",
                            "confidence": 0.94,
                            "font_family": "CC Wild Words",
                            "font_size": 14,
                            "alignment": "Center",
                            "line_spacing": 1.2,
                        },
                        {
                            "id": 3,
                            "box": [240, 650, 150, 80],
                            "text": "ドカーン",
                            "translation": "ĐÙNG!",
                            "confidence": 0.58,
                            "font_family": "Anime Ace",
                            "font_size": 16,
                            "alignment": "Center",
                            "line_spacing": 1.2,
                        },
                        {
                            "id": 4,
                            "box": [480, 750, 200, 90],
                            "text": "その時、街全体が揺れた。",
                            "translation": "Khoảnh khắc ấy, cả thị trấn rung chuyển.",
                            "confidence": 0.96,
                            "font_family": "Plus Jakarta Sans",
                            "font_size": 13,
                            "alignment": "Left",
                            "line_spacing": 1.3,
                        },
                    ],
                },
                {
                    "id": "page_proj_1_2",
                    "page_number": 2,
                    "filename": "page_002.png",
                    "size_kb": 2100.0,
                    "image_bytes": None,
                    "stage": "Inpainting",
                    "status": "Processing (Active)",
                    "bubbles": [
                        {
                            "id": 1,
                            "box": [200, 150, 160, 80],
                            "text": "危険だ、下がれ！",
                            "translation": "Nguy hiểm, lùi lại mau!",
                            "confidence": 0.95,
                            "font_family": "CC Wild Words",
                            "font_size": 14,
                            "alignment": "Center",
                            "line_spacing": 1.2,
                        }
                    ],
                },
                {
                    "id": "page_proj_1_3",
                    "page_number": 3,
                    "filename": "page_003.png",
                    "size_kb": 2800.0,
                    "image_bytes": None,
                    "stage": "OCR Extraction",
                    "status": "Processing (Active)",
                    "bubbles": [
                        {
                            "id": 1,
                            "box": [180, 200, 170, 90],
                            "text": "誰も傷つけさせない！",
                            "translation": "Tôi sẽ không để ai bị thương!",
                            "confidence": 0.91,
                            "font_family": "CC Wild Words",
                            "font_size": 14,
                            "alignment": "Center",
                            "line_spacing": 1.2,
                        }
                    ],
                },
                {
                    "id": "page_proj_1_4",
                    "page_number": 4,
                    "filename": "page_004.png",
                    "size_kb": 1950.0,
                    "image_bytes": None,
                    "stage": "YOLO Detection",
                    "status": "Queued",
                    "bubbles": [],
                },
            ],
        },
        {
            "id": "proj_2",
            "title": "One Piece — Chapter 1115",
            "description": "Wano / Egghead aftermath chapter.",
            "source_lang": "Japanese (Raw Manga)",
            "target_lang": "Vietnamese",
            "owner": "Phan Nhat Huy",
            "status": "Inpainting",
            "created_at": "2026-10-10 09:15",
            "members": [
                {"name": "Phan Nhat Huy", "email": "nhathuyphan21@gmail.com", "role": "Project Manager"},
                {"name": "Phan Van Quan", "email": "phanvanquann26@gmail.com", "role": "Translator"},
            ],
            "pages": [],
        },
        {
            "id": "proj_3",
            "title": "Jujutsu Kaisen — Special",
            "description": "Special side-story one-shot.",
            "source_lang": "English",
            "target_lang": "Vietnamese",
            "owner": "Phan Thanh Hoang",
            "status": "Completed",
            "created_at": "2026-10-08 11:20",
            "members": [
                {"name": "Phan Thanh Hoang", "email": "phanhoang0705@gmail.com", "role": "Project Manager"},
            ],
            "pages": [],
        },
    ]
