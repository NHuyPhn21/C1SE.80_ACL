import { request } from "./client";
import type { ChapterSummary, ProjectSummary, TeamMember } from "./types";

export const getProjects = (userId: string) =>
  request<ProjectSummary[]>(`/api/projects?user_id=${encodeURIComponent(userId)}`);

export const createProject = (userId: string, title: string, description: string) =>
  request<ProjectSummary>(`/api/projects?user_id=${encodeURIComponent(userId)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, description }),
  });

export const updateProject = (projectId: number, title: string, description: string, userId?: string) =>
  request<ProjectSummary>(
    `/api/projects/${projectId}${userId ? `?user_id=${encodeURIComponent(userId)}` : ""}`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, description }),
    },
  );

export const deleteProject = (projectId: number, userId?: string) =>
  request<{ deleted_project_id: number; message: string }>(
    `/api/projects/${projectId}${userId ? `?user_id=${encodeURIComponent(userId)}` : ""}`,
    { method: "DELETE" },
  );

export const getProjectMembers = (projectId: number) =>
  request<TeamMember[]>(`/api/projects/${projectId}/members`);

export const inviteProjectMember = (
  projectId: number,
  email: string,
  role: string,
  callerUserId?: string,
) =>
  request<TeamMember>(
    `/api/projects/${projectId}/members${callerUserId ? `?caller_user_id=${encodeURIComponent(callerUserId)}` : ""}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, role }),
    },
  );

export const removeProjectMember = (
  projectId: number,
  memberUserId: number,
  callerUserId?: string,
) =>
  request<{ removed_user_id: number; message: string }>(
    `/api/projects/${projectId}/members/${memberUserId}${callerUserId ? `?caller_user_id=${encodeURIComponent(callerUserId)}` : ""}`,
    { method: "DELETE" },
  );

export const updateProjectMemberRole = (
  projectId: number,
  memberUserId: number,
  role: string,
  callerUserId?: string,
) =>
  request<TeamMember>(
    `/api/projects/${projectId}/members/${memberUserId}${callerUserId ? `?caller_user_id=${encodeURIComponent(callerUserId)}` : ""}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ role }),
    },
  );

export const createChapter = (projectId: number, chapterName: string) =>
  request<ChapterSummary>(`/api/projects/${projectId}/chapters`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chapter_name: chapterName }),
  });

export const getProjectChapters = (projectId: number) =>
  request<ChapterSummary[]>(`/api/projects/${projectId}/chapters`);

export const deleteChapter = (projectId: number, chapterId: number, userId?: string) =>
  request<{ deleted_chapter_id: number; message: string }>(
    `/api/projects/${projectId}/chapters/${chapterId}${userId ? `?user_id=${encodeURIComponent(userId)}` : ""}`,
    { method: "DELETE" },
  );

export const deleteProjectData = (projectId: number, userId?: string) =>
  request<{ deleted_chapters: number; message: string }>(
    `/api/projects/${projectId}/data${userId ? `?user_id=${encodeURIComponent(userId)}` : ""}`,
    { method: "DELETE" },
  );
