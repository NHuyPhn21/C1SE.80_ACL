import { request } from "./client";
import type { Chapter, Page, QueueSnapshot, Region } from "./types";

export const getChapter = (chapterId: number) => request<Chapter>(`/api/chapters/${chapterId}`);
export const getProjectQueue = (projectId: number) => request<QueueSnapshot>(`/api/projects/${projectId}/queue`);
export const startProjectQueue = (projectId: number, chapterId: number) => request<QueueSnapshot>(`/api/projects/${projectId}/queue/start`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ chapter_id: chapterId }) });
export const uploadPage = (file: File, chapterId?: number) => { const body = new FormData(); body.append("file", file); return request<Page>(`/api/upload${chapterId ? `?chapter_id=${chapterId}` : ""}`, { method: "POST", body }); };
export const updateBubble = (regionId: number, patch: Partial<Region>) => request<Region>(`/api/bubbles/${regionId}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(patch) });
export const createBubble = (pageId: number, bbox: [number, number, number, number], originalText = "") => request<Region>(`/api/pages/${pageId}/bubbles`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ bbox, original_text: originalText }) });
export const deleteBubble = (regionId: number) => request<{ deleted_region_id: number; message: string; region: Region }>(`/api/bubbles/${regionId}`, { method: "DELETE" });
export const restoreBubble = (region: Region & { page_id: number }) => request<Region>("/api/bubbles/restore", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ region_id: region.id, page_id: region.page_id, bbox: region.bbox, original_text: region.original_text, translated_text: region.translated_text, font_size: region.font_size }) });
export const typesetPage = (pageId: number, regionId: number, translatedText: string, fontSize?: number) => request<Page>(`/api/pages/${pageId}/typeset`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ region_id: regionId, translated_text: translatedText, font_size: fontSize }) });
export const translatePage = (pageId: number, regions: Record<number, string>) => request<Page>("/api/translate", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ page_id: pageId, regions }) });
export const rerunPageOcr = (pageId: number) => request<Page>(`/api/pages/${pageId}/ocr`, { method: "POST" });
