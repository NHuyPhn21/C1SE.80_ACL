import { useState } from "react";
import type { ProjectSummary } from "./api";
import type { ScreenName } from "./components/AppLayout";
import { AuthScreen, type AuthSession } from "./features/auth/AuthScreen";
import {
  ChapterScreen,
  QueueScreen,
  ReviewScreen,
  SettingsScreen,
  TeamScreen,
  TypesettingScreen,
  WorkspaceScreen,
} from "./features/screens";

const SESSION_KEY = "acl.auth";

export default function App() {
  const [session, setSession] = useState<AuthSession | null>(() => {
    try {
      const saved = localStorage.getItem(SESSION_KEY);
      return saved ? (JSON.parse(saved) as AuthSession) : null;
    } catch {
      return null;
    }
  });
  const [screen, setScreen] = useState<ScreenName>("workspace");
  const [activeProject, setActiveProject] = useState<ProjectSummary | null>(null);

  const handleLogout = () => {
    localStorage.removeItem(SESSION_KEY);
    setSession(null);
    setActiveProject(null);
    setScreen("workspace");
  };

  const navigate = (nextScreen: ScreenName, project?: ProjectSummary) => {
    if (project) {
      setActiveProject(project);
    }
    setScreen(nextScreen);
  };

  if (!session) {
    return (
      <AuthScreen
        onAuthenticated={(nextSession) => {
          setSession(nextSession);
          localStorage.setItem(SESSION_KEY, JSON.stringify(nextSession));
        }}
      />
    );
  }

  if (screen === "team" && activeProject) {
    return (
      <TeamScreen
        session={session}
        project={activeProject}
        onNavigate={navigate}
        onLogout={handleLogout}
      />
    );
  }

  if (screen === "chapter" && activeProject) {
    return (
      <ChapterScreen
        session={session}
        project={activeProject}
        onNavigate={navigate}
        onLogout={handleLogout}
      />
    );
  }

  if (screen === "queue" && activeProject) {
    return (
      <QueueScreen
        session={session}
        project={activeProject}
        onNavigate={navigate}
        onLogout={handleLogout}
      />
    );
  }

  if (screen === "review" && activeProject) {
    return (
      <ReviewScreen
        session={session}
        project={activeProject}
        onNavigate={navigate}
        onLogout={handleLogout}
      />
    );
  }

  if (screen === "typesetting" && activeProject) {
    return (
      <TypesettingScreen
        session={session}
        project={activeProject}
        onNavigate={navigate}
        onLogout={handleLogout}
      />
    );
  }

  if (screen === "settings") {
    return (
      <SettingsScreen
        session={session}
        activeProject={activeProject}
        onSyncProject={setActiveProject}
        onNavigate={navigate}
        onLogout={handleLogout}
      />
    );
  }

  return (
    <WorkspaceScreen
      session={session}
      activeProject={activeProject}
      onSyncProject={setActiveProject}
      onNavigate={navigate}
      onLogout={handleLogout}
    />
  );
}
