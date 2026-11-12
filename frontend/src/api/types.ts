import type { Chapter, Page, Region } from "../types";

export type LoginResponse = {
  user: { id: string; email: string; full_name: string; role: string };
  tokens: { access_token: string; refresh_token: string | null; expires_in: number | null };
};
export type ProjectSummary = { id: number; title: string; description: string; total_pages: number; completed_pages: number; progress_percent: number };
export type TeamMember = { user_id: number; name: string; email: string; role: string; is_owner: boolean };
export type ChapterSummary = { id: number; project_id: number; chapter_number: number; chapter_name: string; pages: unknown[] };
export type QueuePage = { id: number; page_number: number; filename: string; status: string; rendered: boolean };
export type QueueSnapshot = { project_id: number; chapter_id: number | null; task: { id: number; status: string; progress_percent: number } | null; total_pages: number; completed_pages: number; failed_pages: number; pages: QueuePage[]; logs: { level: string; message: string; timestamp: string }[] };
export type SettingsSnapshot = { user: { id: number; full_name: string; email: string; role: string; created_at: string | null }; providers: { gemini: boolean; sendgrid: boolean } };
export type GlossaryTerm = { id: number; project_id: number; source_term: string; target_term: string };
export type SystemLogEntry = { id: number; level: string; message: string; timestamp: string | null };
export type { Chapter, Page, Region };
