import { useState } from "react";
import { AuthScreen } from "./features/auth/AuthScreen";
import type { AuthSession } from "./features/auth/AuthScreen";
import { ChapterScreen, QueueScreen, ReviewScreen, SettingsScreen, TeamScreen, TypesettingScreen, WorkspaceScreen } from "./features/screens";
import type { ProjectSummary } from "./api";

const API_ORIGIN = import.meta.env.VITE_API_ORIGIN ?? "";
const SESSION_KEY = "acl.auth";

export default function App() {
  const [session, setSession] = useState<AuthSession | null>(() => {
    try {
      const saved = localStorage.getItem(SESSION_KEY);
      return saved ? JSON.parse(saved) as AuthSession : null;
    } catch {
      return null;
    }
  });
  const [screen, setScreen] = useState<"workspace" | "team" | "chapter" | "queue" | "review" | "typesetting" | "settings">("workspace");
  const [teamProject, setTeamProject] = useState<ProjectSummary | null>(null);
  const [chapterProject, setChapterProject] = useState<ProjectSummary | null>(null);
  const [queueProject, setQueueProject] = useState<ProjectSummary | null>(null);
  const [reviewProject, setReviewProject] = useState<ProjectSummary | null>(null);
  const [typesettingProject, setTypesettingProject] = useState<ProjectSummary | null>(null);

  if (!session) {
    return <AuthScreen onAuthenticated={(nextSession) => {
      setSession(nextSession);
      localStorage.setItem(SESSION_KEY, JSON.stringify(nextSession));
    }} />;
  }

  if (screen === "team" && teamProject) {
    return <TeamScreen session={session} project={teamProject} onBack={() => setScreen("workspace")} onLogout={() => { localStorage.removeItem(SESSION_KEY); setSession(null); }} />;
  }
  if (screen === "chapter" && chapterProject) {
    return <ChapterScreen session={session} project={chapterProject} onBack={() => setScreen("workspace")} onOpenQueue={() => { setQueueProject(chapterProject); setScreen("queue"); }} onOpenReview={() => { setReviewProject(chapterProject); setScreen("review"); }} onOpenTypesetting={() => { setTypesettingProject(chapterProject); setScreen("typesetting"); }} onLogout={() => { localStorage.removeItem(SESSION_KEY); setSession(null); }} />;
  }
  if (screen === "queue" && queueProject) {
    return <QueueScreen session={session} project={queueProject} onBack={() => setScreen("workspace")} onOpenReview={() => { setReviewProject(queueProject); setScreen("review"); }} onOpenTypesetting={() => { setTypesettingProject(queueProject); setScreen("typesetting"); }} onLogout={() => { localStorage.removeItem(SESSION_KEY); setSession(null); }} />;
  }
  if (screen === "review" && reviewProject) {
    return <ReviewScreen session={session} project={reviewProject} onBack={() => setScreen("workspace")} onOpenQueue={() => { setQueueProject(reviewProject); setScreen("queue"); }} onOpenTypesetting={() => { setTypesettingProject(reviewProject); setScreen("typesetting"); }} onLogout={() => { localStorage.removeItem(SESSION_KEY); setSession(null); }} />;
  }
  if (screen === "typesetting" && typesettingProject) {
    return <TypesettingScreen session={session} project={typesettingProject} onBack={() => setScreen("workspace")} onOpenReview={() => { setReviewProject(typesettingProject); setScreen("review"); }} onOpenQueue={() => { setQueueProject(typesettingProject); setScreen("queue"); }} onLogout={() => { localStorage.removeItem(SESSION_KEY); setSession(null); }} />;
  }
  if (screen === "settings") {
    return <SettingsScreen session={session} onBack={() => setScreen("workspace")} onLogout={() => { localStorage.removeItem(SESSION_KEY); setSession(null); }} />;
  }

  return <WorkspaceScreen session={session} onOpenTeam={(project) => { setTeamProject(project); setScreen("team"); }} onOpenChapter={(project) => { setChapterProject(project); setScreen("chapter"); }} onOpenQueue={(project) => { setQueueProject(project); setScreen("queue"); }} onOpenReview={(project) => { setReviewProject(project); setScreen("review"); }} onOpenTypesetting={(project) => { setTypesettingProject(project); setScreen("typesetting"); }} onOpenSettings={() => setScreen("settings")} onLogout={() => {
    localStorage.removeItem(SESSION_KEY);
    setSession(null);
  }} />;
}
