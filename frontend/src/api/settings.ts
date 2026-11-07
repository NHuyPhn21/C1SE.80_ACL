import { request } from "./client";
import type { GlossaryTerm, SettingsSnapshot, SystemLogEntry } from "./types";

export const getSettings = (userId: string) => request<SettingsSnapshot>(`/api/settings?user_id=${encodeURIComponent(userId)}`);
export const getGlossary = (userId: string) => request<GlossaryTerm[]>(`/api/settings/glossary?user_id=${encodeURIComponent(userId)}`);
export const getSettingsLogs = (userId: string) => request<SystemLogEntry[]>(`/api/settings/logs?user_id=${encodeURIComponent(userId)}`);
export const createGlossary = (userId: string, projectId: number, sourceTerm: string, targetTerm: string) => request<GlossaryTerm>(`/api/settings/glossary?user_id=${encodeURIComponent(userId)}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ project_id: projectId, source_term: sourceTerm, target_term: targetTerm }) });
export const saveApiKey = (userId: string, projectId: number, apiKey: string) => request<{ message: string }>(`/api/settings/api-key?user_id=${encodeURIComponent(userId)}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ project_id: projectId, provider: "gemini", api_key: apiKey }) });
export const testApiKey = (projectId: number, apiKey: string) => request<{ message: string }>("/api/settings/api-key/test", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ project_id: projectId, provider: "gemini", api_key: apiKey }) });
export const testSavedApiKey = (userId: string, projectId: number) => request<{ message: string }>(`/api/settings/api-key/test-saved?user_id=${encodeURIComponent(userId)}&project_id=${projectId}`, { method: "POST" });
