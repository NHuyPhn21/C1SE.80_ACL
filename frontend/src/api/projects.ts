import { request } from "./client";
import type { ChapterSummary, ProjectSummary, TeamMember } from "./types";

export const getProjects = (userId: string) => request<ProjectSummary[]>(`/api/projects?user_id=${encodeURIComponent(userId)}`);
export const createProject = (userId: string, title: string, description: string) => request<ProjectSummary>(`/api/projects?user_id=${encodeURIComponent(userId)}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title, description }) });
export const getProjectMembers = (projectId: number) => request<TeamMember[]>(`/api/projects/${projectId}/members`);
export const inviteProjectMember = (projectId: number, email: string, role: string) => request<TeamMember>(`/api/projects/${projectId}/members`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, role }) });
export const createChapter = (projectId: number, chapterName: string) => request<ChapterSummary>(`/api/projects/${projectId}/chapters`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ chapter_name: chapterName }) });
export const getProjectChapters = (projectId: number) => request<ChapterSummary[]>(`/api/projects/${projectId}/chapters`);
export const deleteChapter = (projectId: number, chapterId: number) => request<{ deleted_chapter_id: number; message: string }>(`/api/projects/${projectId}/chapters/${chapterId}`, { method: "DELETE" });
export const deleteProjectData = (projectId: number) => request<{ deleted_chapters: number; message: string }>(`/api/projects/${projectId}/data`, { method: "DELETE" });
