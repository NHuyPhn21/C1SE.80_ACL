import { request } from "./client";
import type { GlossaryTerm, SettingsSnapshot, SystemLogEntry } from "./types";

export const getSettings = (userId: string) =>
  request<SettingsSnapshot>(`/api/settings?user_id=${encodeURIComponent(userId)}`);
export const getGlossary = (userId: string, projectId?: number) =>
  request<GlossaryTerm[]>(
    `/api/settings/glossary?user_id=${encodeURIComponent(userId)}${
      projectId !== undefined ? `&project_id=${projectId}` : ""
    }`
  );
export const getSettingsLogs = (userId: string, projectId?: number, level?: string) =>
  request<SystemLogEntry[]>(
    `/api/settings/logs?user_id=${encodeURIComponent(userId)}${
      projectId !== undefined ? `&project_id=${projectId}` : ""
    }${level && level !== "ALL" ? `&level=${encodeURIComponent(level)}` : ""}`
  );
export const clearSettingsLogs = (userId: string, projectId?: number) =>
  request<{ deleted_count: number; message: string }>(
    `/api/settings/logs?user_id=${encodeURIComponent(userId)}${
      projectId !== undefined ? `&project_id=${projectId}` : ""
    }`,
    { method: "DELETE" }
  );
export const createGlossary = (
  userId: string,
  projectId: number,
  sourceTerm: string,
  targetTerm: string
) =>
  request<GlossaryTerm>(`/api/settings/glossary?user_id=${encodeURIComponent(userId)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      project_id: projectId,
      source_term: sourceTerm,
      target_term: targetTerm,
    }),
  });
export const updateGlossary = (
  userId: string,
  glossaryId: number,
  sourceTerm: string,
  targetTerm: string
) =>
  request<GlossaryTerm>(
    `/api/settings/glossary/${glossaryId}?user_id=${encodeURIComponent(userId)}`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        source_term: sourceTerm,
        target_term: targetTerm,
      }),
    }
  );
export const deleteGlossary = (userId: string, glossaryId: number) =>
  request<{ deleted_id: number; message: string }>(
    `/api/settings/glossary/${glossaryId}?user_id=${encodeURIComponent(userId)}`,
    { method: "DELETE" }
  );
export const saveApiKey = (userId: string, projectId: number, apiKey: string) => request<{ message: string }>(`/api/settings/api-key?user_id=${encodeURIComponent(userId)}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ project_id: projectId, provider: "gemini", api_key: apiKey }) });
export const testApiKey = (projectId: number, apiKey: string) => request<{ message: string }>("/api/settings/api-key/test", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ project_id: projectId, provider: "gemini", api_key: apiKey }) });
export const testSavedApiKey = (userId: string, projectId: number) => request<{ message: string }>(`/api/settings/api-key/test-saved?user_id=${encodeURIComponent(userId)}&project_id=${projectId}`, { method: "POST" });
