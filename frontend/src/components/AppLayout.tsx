import type { ReactNode } from "react";
import type { ProjectSummary } from "../api";
import type { AuthSession } from "../features/auth/AuthScreen";
import { AppIcon, type IconName } from "./AppIcon";
import { UserMenu } from "./UserMenu";

export type ScreenName =
  | "workspace"
  | "chapter"
  | "queue"
  | "review"
  | "typesetting"
  | "team"
  | "settings";

type NavItem = {
  screen: ScreenName;
  label: string;
  icon: IconName;
  requiresProject?: boolean;
};

const WORKSPACE_ITEMS: NavItem[] = [
  { screen: "workspace", label: "Projects", icon: "projects" },
];

const STUDIO_ITEMS: NavItem[] = [
  { screen: "chapter", label: "Chapter Studio", icon: "chapter", requiresProject: true },
  { screen: "queue", label: "Queue Monitor", icon: "queue", requiresProject: true },
  { screen: "review", label: "Review Studio", icon: "review", requiresProject: true },
  { screen: "typesetting", label: "Typesetting", icon: "typesetting", requiresProject: true },
  { screen: "team", label: "Team & Roles", icon: "users", requiresProject: true },
];

const SYSTEM_ITEMS: NavItem[] = [
  { screen: "settings", label: "Personal Settings", icon: "settings" },
];

type AppLayoutProps = {
  session: AuthSession;
  activeScreen: ScreenName;
  activeProject: ProjectSummary | null;
  breadcrumbs: string[];
  headerControls?: ReactNode;
  onNavigate: (screen: ScreenName) => void;
  onLogout: () => void;
  children: ReactNode;
};

export function AppLayout({
  session,
  activeScreen,
  activeProject,
  breadcrumbs,
  headerControls,
  onNavigate,
  onLogout,
  children,
}: AppLayoutProps) {
  const renderNavButton = (item: NavItem) => {
    const disabled = Boolean(item.requiresProject && !activeProject);
    const isActive = activeScreen === item.screen;
    return (
      <button
        key={item.screen}
        type="button"
        className={isActive ? "active" : ""}
        disabled={disabled}
        title={disabled ? "Select or create a project first" : item.label}
        onClick={() => onNavigate(item.screen)}
      >
        <AppIcon name={item.icon} />
        <span>{item.label}</span>
      </button>
    );
  };

  return (
    <div className="dashboard-page">
      <aside className="dashboard-sidebar">
        <div className="dashboard-sidebar-top">
          <button
            type="button"
            className="dashboard-brand"
            onClick={() => onNavigate("workspace")}
          >
            <span>A</span>
            <strong>ACL</strong>
            <small>v2.4 Editorial Core</small>
          </button>

          <div className="sidebar-section">
            <span className="sidebar-section-label">Workspace</span>
            <nav className="dashboard-nav" aria-label="Workspace navigation">
              {WORKSPACE_ITEMS.map(renderNavButton)}
            </nav>
          </div>

          <div className="sidebar-section">
            <span className="sidebar-section-label">Project Studio</span>
            <div className={`sidebar-project-pill ${activeProject ? "has-project" : ""}`}>
              <small>{activeProject ? `Project #${String(activeProject.id).padStart(2, "0")}` : "No Project Selected"}</small>
              <strong>{activeProject ? activeProject.title : "Choose a project"}</strong>
            </div>
            <nav className="dashboard-nav" aria-label="Project studio navigation">
              {STUDIO_ITEMS.map(renderNavButton)}
            </nav>
          </div>

          <div className="sidebar-section">
            <span className="sidebar-section-label">System</span>
            <nav className="dashboard-nav" aria-label="System navigation">
              {SYSTEM_ITEMS.map(renderNavButton)}
            </nav>
          </div>
        </div>

        <div className="dashboard-sidebar-bottom">
          <div>● Core Engine • Online</div>
        </div>
      </aside>

      <main className="dashboard-main">
        <header className="dashboard-header">
          <div className="dashboard-breadcrumbs">
            <strong>ACL Studio</strong>
            {breadcrumbs.map((crumb, index) => (
              <span key={`${crumb}-${index}`} className="crumb-item">
                <span className="crumb-sep">/</span>
                {index === breadcrumbs.length - 1 ? <b>{crumb}</b> : <em>{crumb}</em>}
              </span>
            ))}
          </div>
          <div className="dashboard-actions">
            {headerControls}
            <span className="gpu-pill">● Node Tokyo-01 (GPU idle)</span>
            <UserMenu user={session.user} onLogout={onLogout} />
          </div>
        </header>
        {children}
      </main>
    </div>
  );
}
