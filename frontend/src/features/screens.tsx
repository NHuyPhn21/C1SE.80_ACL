import { FormEvent, PointerEvent, useEffect, useMemo, useRef, useState } from "react";
import {
  clearSettingsLogs,
  createBubble,
  createChapter,
  createGlossary,
  createProject,
  updateProject,
  deleteBubble,
  deleteChapter,
  deleteGlossary,
  deleteProject,
  deleteProjectData,
  getChapter,
  getGlossary,
  getProjectChapters,
  getProjectMembers,
  getProjectQueue,
  getProjects,
  getSettings,
  getSettingsLogs,
  inviteProjectMember,
  removeProjectMember,
  updateGlossary,
  updateProjectMemberRole,
  rerunPageOcr,
  saveOcrDraft,
  flagPage,
  pageDownloadUrl,
  restoreBubble,
  saveApiKey,
  startProjectQueue,
  testApiKey,
  testSavedApiKey,
  translatePage,
  typesetPage,
  updateBubble,
  uploadPage,
} from "../api";
import type {
  ChapterSummary,
  GlossaryTerm,
  ProjectSummary,
  QueueSnapshot,
  SettingsSnapshot,
  SystemLogEntry,
  TeamMember,
} from "../api";
import { AppIcon } from "../components/AppIcon";
import { AppLayout, type ScreenName } from "../components/AppLayout";
import type { Chapter, Page, Region } from "../types";
import type { AuthSession } from "./auth/AuthScreen";

const API_ORIGIN = import.meta.env.VITE_API_ORIGIN ?? "";

type NavigateFn = (screen: ScreenName, project?: ProjectSummary) => void;

export function WorkspaceScreen({
  session,
  activeProject,
  onSyncProject,
  onNavigate,
  onLogout,
}: {
  session: AuthSession;
  activeProject: ProjectSummary | null;
  onSyncProject: (project: ProjectSummary | null) => void;
  onNavigate: NavigateFn;
  onLogout: () => void;
}) {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [editing, setEditing] = useState<ProjectSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");

  const removeProject = async (project: ProjectSummary) => {
    if (
      !window.confirm(
        `Permanently delete "${project.title}" with all chapters, pages, translations and rendered files? This cannot be undone.`,
      )
    )
      return;
    try {
      await deleteProject(project.id, session.user.id);
      const remaining = projects.filter((item) => item.id !== project.id);
      setProjects(remaining);
      if (activeProject?.id === project.id) onSyncProject(remaining[0] ?? null);
      setError("");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to delete project.");
    }
  };

  const loadProjects = async () => {
    setLoading(true);
    try {
      const loaded = await getProjects(session.user.id);
      setProjects(loaded);
      if (loaded.length > 0) {
        const matched = activeProject
          ? loaded.find((item) => item.id === activeProject.id)
          : null;
        onSyncProject(matched ?? loaded[0]);
      } else {
        onSyncProject(null);
      }
      setError("");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to load projects.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadProjects();
  }, []);

  const visibleProjects = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) return projects;
    return projects.filter((project) =>
      [project.title, project.description, String(project.id)].some((value) =>
        (value ?? "").toLowerCase().includes(normalized),
      ),
    );
  }, [projects, query]);

  return (
    <AppLayout
      session={session}
      activeScreen="workspace"
      activeProject={activeProject ?? projects[0] ?? null}
      breadcrumbs={["Projects"]}
      headerControls={
        <label className="project-search">
          <AppIcon name="search" />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Filter batches or series..."
            aria-label="Filter projects"
          />
        </label>
      }
      onNavigate={(screen) => onNavigate(screen, activeProject ?? projects[0])}
      onLogout={onLogout}
    >
      <section className="dashboard-content">
        <div className="dashboard-title">
          <div>
            <h1>Projects</h1>
            <p>Manage your ongoing comic localization series and translation pipelines.</p>
          </div>
          <button className="create-project-button" onClick={() => setShowCreate(true)}>
            ＋ Create New Project
          </button>
        </div>

        {error && <div className="dashboard-error">{error}</div>}

        {loading ? (
          <div className="dashboard-empty">Loading projects...</div>
        ) : projects.length === 0 ? (
          <div className="dashboard-empty">
            <h2>No projects yet</h2>
            <p>Create a project to start localizing your first comic series.</p>
            <button className="create-project-button" onClick={() => setShowCreate(true)}>
              ＋ Create New Project
            </button>
          </div>
        ) : visibleProjects.length === 0 ? (
          <div className="dashboard-empty">
            <h2>No matching projects</h2>
            <p>Try another project name, description, or ID.</p>
          </div>
        ) : (
          <div className="project-grid">
            {visibleProjects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                isSelected={activeProject?.id === project.id}
                onSelect={() => onSyncProject(project)}
                onOpen={() => onNavigate("chapter", project)}
                onTeam={() => onNavigate("team", project)}
                onQueue={() => onNavigate("queue", project)}
                onReview={() => onNavigate("review", project)}
                onTypesetting={() => onNavigate("typesetting", project)}
                onEdit={() => setEditing(project)}
                onDelete={() => void removeProject(project)}
              />
            ))}
          </div>
        )}

        {projects.length > 0 && (
          <div className="kpi-grid">
            <Kpi label="Active Projects" value={String(projects.length)} detail="Series in workspace" />
            <Kpi
              label="In Queue"
              value={String(
                projects.reduce(
                  (sum, project) => sum + Math.max(0, project.total_pages - project.completed_pages),
                  0,
                ),
              )}
              detail="Pages pending processing"
            />
            <Kpi
              label="Completed Pages"
              value={String(projects.reduce((sum, project) => sum + project.completed_pages, 0))}
              detail="Rendered & localized"
            />
          </div>
        )}
      </section>

      {showCreate && (
        <CreateProjectModal
          userId={session.user.id}
          onClose={() => setShowCreate(false)}
          onCreated={(project) => {
            setProjects((current) => [project, ...current]);
            onSyncProject(project);
            setShowCreate(false);
          }}
        />
      )}
      {editing && (
        <CreateProjectModal
          userId={session.user.id}
          project={editing}
          onClose={() => setEditing(null)}
          onCreated={(updated) => {
            setProjects((current) =>
              current.map((item) => (item.id === updated.id ? updated : item)),
            );
            if (activeProject?.id === updated.id) onSyncProject(updated);
            setEditing(null);
          }}
        />
      )}
    </AppLayout>
  );
}

export function ProjectCard({
  project,
  isSelected,
  onSelect,
  onOpen,
  onTeam,
  onQueue,
  onReview,
  onTypesetting,
  onEdit,
  onDelete,
}: {
  project: ProjectSummary;
  isSelected?: boolean;
  onSelect?: () => void;
  onOpen: () => void;
  onTeam: () => void;
  onQueue: () => void;
  onReview: () => void;
  onTypesetting: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
}) {
  const statusLabel =
    project.completed_pages === project.total_pages && project.total_pages > 0
      ? "Completed"
      : project.completed_pages > 0
        ? "In review"
        : "Not started";

  return (
    <article
      className={`project-card ${isSelected ? "selected" : ""}`}
      onClick={onSelect}
    >
      <div className="project-card-title">
        <h3>{project.title}</h3>
        <span>#{String(project.id).padStart(2, "0")}</span>
      </div>
      <p className="project-meta">{project.total_pages} pages • Japanese → Vietnamese</p>
      <div className="project-status">● {statusLabel}</div>
      <div className="progress-label">
        <span>
          Progress: {project.completed_pages}/{project.total_pages} Pages
        </span>
        <span>{project.progress_percent}%</span>
      </div>
      <div className="progress-track">
        <i style={{ width: `${project.progress_percent}%` }} />
      </div>
      <p className="project-description">{project.description || "No project description."}</p>
      <div className="project-card-actions" onClick={(event) => event.stopPropagation()}>
        <button className="project-open-button" onClick={onOpen}>
          Open Studio
        </button>
        <details className="project-actions-menu">
          <summary aria-label={`More actions for ${project.title}`}>
            <AppIcon name="more" />
          </summary>
          <div
            onClick={(event) => {
              if ((event.target as HTMLElement).closest("button")) {
                event.currentTarget.closest("details")?.removeAttribute("open");
              }
            }}
          >
            <button onClick={onQueue}>
              <AppIcon name="queue" /> Queue Monitor
            </button>
            <button onClick={onReview}>
              <AppIcon name="review" /> Review Studio
            </button>
            <button onClick={onTypesetting}>
              <AppIcon name="typesetting" /> Typesetting
            </button>
            <button onClick={onTeam}>
              <AppIcon name="users" /> Team &amp; Roles
            </button>
            {onEdit && <button onClick={onEdit}>✎ Edit project</button>}
            {onDelete && (
              <button className="danger-menu-item" onClick={onDelete}>
                🗑 Delete project
              </button>
            )}
          </div>
        </details>
      </div>
    </article>
  );
}

export function ReviewScreen({
  session,
  project,
  onNavigate,
  onLogout,
}: {
  session: AuthSession;
  project: ProjectSummary;
  onNavigate: NavigateFn;
  onLogout: () => void;
}) {
  const [chapters, setChapters] = useState<ChapterSummary[]>([]);
  const [chapterId, setChapterId] = useState<number | null>(null);
  const [chapter, setChapter] = useState<Chapter | null>(null);
  const [pageIndex, setPageIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [notice, setNotice] = useState("");
  const [activeRegionId, setActiveRegionId] = useState<number | null>(null);
  const dragMoved = useRef(false);
  const [error, setError] = useState("");
  const [imageSize, setImageSize] = useState({ width: 0, height: 0 });
  const [deletedBubble, setDeletedBubble] = useState<(Region & { page_id: number }) | null>(null);
  const [drawMode, setDrawMode] = useState(false);
  const [drawStart, setDrawStart] = useState<{ x: number; y: number } | null>(null);
  const [drawBox, setDrawBox] = useState<{ x: number; y: number; width: number; height: number } | null>(null);
  const [boxInteraction, setBoxInteraction] = useState<{
    regionId: number;
    mode: "move" | "resize";
    start: { x: number; y: number };
    bbox: Region["bbox"];
  } | null>(null);

  useEffect(() => {
    void getProjectChapters(project.id)
      .then((items) => {
        setChapters(items);
        setChapterId(items[items.length - 1]?.id ?? null);
      })
      .catch((requestError) =>
        setError(requestError instanceof Error ? requestError.message : "Unable to load chapters."),
      );
  }, [project.id]);

  useEffect(() => {
    if (!chapterId) {
      setLoading(false);
      return;
    }
    setLoading(true);
    void getChapter(chapterId)
      .then(setChapter)
      .catch((requestError) =>
        setError(requestError instanceof Error ? requestError.message : "Unable to load page."),
      )
      .finally(() => setLoading(false));
  }, [chapterId]);

  const page = chapter?.pages[pageIndex] ?? null;
  const imageUrl = page?.original_url ?? null;

  useEffect(() => {
    setImageSize({ width: 0, height: 0 });
  }, [imageUrl]);

  useEffect(() => {
    setNotice("");
    setActiveRegionId(null);
  }, [page?.id]);

  const reviewPageCount = chapter?.pages.length ?? 0;
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      if (target && /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName)) return;
      if (target?.isContentEditable || event.metaKey || event.ctrlKey || event.altKey) return;
      if (event.key === "ArrowLeft") setPageIndex((index) => Math.max(0, index - 1));
      if (event.key === "ArrowRight") setPageIndex((index) => Math.min(reviewPageCount - 1, index + 1));
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [reviewPageCount]);

  const updateOriginal = (regionId: number, text: string) => {
    if (!chapter || !page) return;
    setChapter({
      ...chapter,
      pages: chapter.pages.map((item) =>
        item.id === page.id
          ? {
              ...item,
              regions: item.regions.map((region) =>
                region.id === regionId ? { ...region, original_text: text } : region,
              ),
            }
          : item,
      ),
    });
  };

  const rerunOcr = async () => {
    if (!page) return;
    setSaving(true);
    setError("");
    setMessage("");
    setNotice("");
    try {
      const updated = await rerunPageOcr(page.id);
      setChapter((current) =>
        current
          ? {
              ...current,
              pages: current.pages.map((item) => (item.id === updated.id ? updated : item)),
            }
          : current,
      );
      setMessage("OCR completed. Review the detected text before translating.");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to re-run OCR.");
    } finally {
      setSaving(false);
    }
  };

  const replacePage = (updated: Page) =>
    setChapter((current) =>
      current
        ? { ...current, pages: current.pages.map((item) => (item.id === updated.id ? updated : item)) }
        : current,
    );

  const saveDraft = async () => {
    if (!page) return;
    setSaving(true);
    setError("");
    setMessage("");
    try {
      const editedText = Object.fromEntries(
        page.regions.map((region) => [region.id, region.original_text]),
      );
      const updated = await saveOcrDraft(page.id, editedText);
      replacePage(updated);
      setNotice("OCR draft saved. No translation was run.");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to save OCR draft.");
    } finally {
      setSaving(false);
    }
  };

  const flagForReview = async () => {
    if (!page) return;
    setError("");
    try {
      replacePage(await flagPage(page.id));
      setNotice("Page flagged for second review.");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to flag page.");
    }
  };

  const focusRegionText = (regionId: number) => {
    if (dragMoved.current) return;
    const field = document.getElementById(`ocr-region-${regionId}`) as HTMLTextAreaElement | null;
    if (!field) return;
    field.scrollIntoView({ behavior: "smooth", block: "center" });
    field.focus({ preventScroll: true });
    setActiveRegionId(regionId);
  };

  const saveAndTranslate = async () => {
    if (!page) return;
    setSaving(true);
    setError("");
    setMessage("");
    try {
      const editedText = Object.fromEntries(
        page.regions
          .filter((region) => region.original_text.trim())
          .map((region) => [region.id, region.original_text]),
      );
      const updated = await translatePage(page.id, editedText);
      setChapter((current) =>
        current
          ? {
              ...current,
              pages: current.pages.map((item) => (item.id === updated.id ? updated : item)),
            }
          : current,
      );
      setMessage("Translation and rendering complete. Proceed to Typesetting to review the final page.");
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to translate the reviewed OCR text.",
      );
    } finally {
      setSaving(false);
    }
  };

  const addBubble = async (coordinates: [number, number, number, number]) => {
    if (!page) return;
    try {
      const region = await createBubble(page.id, coordinates);
      setChapter((current) =>
        current
          ? {
              ...current,
              pages: current.pages.map((item) =>
                item.id === page.id ? { ...item, regions: [...item.regions, region] } : item,
              ),
            }
          : current,
      );
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to add bubble.");
    }
  };

  const getDrawPoint = (event: PointerEvent<HTMLDivElement>) => {
    const image = event.currentTarget.querySelector("img");
    if (!image) return null;
    const bounds = image.getBoundingClientRect();
    return {
      x: Math.max(0, Math.min(bounds.width, event.clientX - bounds.left)),
      y: Math.max(0, Math.min(bounds.height, event.clientY - bounds.top)),
    };
  };

  const handleDrawStart = (event: PointerEvent<HTMLDivElement>) => {
    if (!drawMode || event.button !== 0 || !imageSize.width || !imageSize.height) return;
    event.preventDefault();
    const point = getDrawPoint(event);
    if (!point) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    setDrawStart(point);
    setDrawBox({ x: point.x, y: point.y, width: 0, height: 0 });
  };

  const handleDrawMove = (event: PointerEvent<HTMLDivElement>) => {
    if (!drawStart) return;
    event.preventDefault();
    const point = getDrawPoint(event);
    if (!point) return;
    setDrawBox({
      x: Math.min(drawStart.x, point.x),
      y: Math.min(drawStart.y, point.y),
      width: Math.abs(point.x - drawStart.x),
      height: Math.abs(point.y - drawStart.y),
    });
  };

  const handleDrawEnd = async (event: PointerEvent<HTMLDivElement>) => {
    if (!drawStart) return;
    event.preventDefault();
    const point = getDrawPoint(event);
    const image = event.currentTarget.querySelector("img");
    const bounds = image?.getBoundingClientRect();
    setDrawStart(null);
    setDrawBox(null);
    if (!point || !bounds || point.x - drawStart.x === 0 || point.y - drawStart.y === 0) return;
    const x1 = Math.round((Math.min(drawStart.x, point.x) * imageSize.width) / bounds.width);
    const y1 = Math.round((Math.min(drawStart.y, point.y) * imageSize.height) / bounds.height);
    const x2 = Math.round((Math.max(drawStart.x, point.x) * imageSize.width) / bounds.width);
    const y2 = Math.round((Math.max(drawStart.y, point.y) * imageSize.height) / bounds.height);
    setDrawMode(false);
    await addBubble([x1, y1, x2, y2]);
  };

  const getImagePoint = (event: PointerEvent<HTMLElement>) => {
    const image = event.currentTarget.closest(".review-image-wrap")?.querySelector("img");
    if (!image) return null;
    const bounds = image.getBoundingClientRect();
    return {
      x: Math.max(
        0,
        Math.min(imageSize.width, ((event.clientX - bounds.left) * imageSize.width) / bounds.width),
      ),
      y: Math.max(
        0,
        Math.min(imageSize.height, ((event.clientY - bounds.top) * imageSize.height) / bounds.height),
      ),
    };
  };

  const updateLocalBbox = (regionId: number, bbox: Region["bbox"]) => {
    setChapter((current) =>
      current
        ? {
            ...current,
            pages: current.pages.map((item) =>
              item.id === page?.id
                ? {
                    ...item,
                    regions: item.regions.map((region) =>
                      region.id === regionId ? { ...region, bbox } : region,
                    ),
                  }
                : item,
            ),
          }
        : current,
    );
  };

  const handleBoxStart = (
    event: PointerEvent<HTMLElement>,
    region: Region,
    mode: "move" | "resize",
  ) => {
    if (drawMode || !imageSize.width || !imageSize.height) return;
    event.stopPropagation();
    event.preventDefault();
    const point = getImagePoint(event);
    if (!point) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    dragMoved.current = false;
    setBoxInteraction({ regionId: region.id, mode, start: point, bbox: region.bbox });
  };

  const handleBoxMove = (event: PointerEvent<HTMLElement>) => {
    if (!boxInteraction) return;
    event.preventDefault();
    const point = getImagePoint(event);
    if (!point) return;
    const [x1, y1, x2, y2] = boxInteraction.bbox;
    const dx = point.x - boxInteraction.start.x;
    const dy = point.y - boxInteraction.start.y;
    if (Math.abs(dx) + Math.abs(dy) > 3) dragMoved.current = true;
    const width = x2 - x1;
    const height = y2 - y1;
    const bbox: Region["bbox"] =
      boxInteraction.mode === "move"
        ? [
            Math.max(0, Math.min(imageSize.width - width, Math.round(x1 + dx))),
            Math.max(0, Math.min(imageSize.height - height, Math.round(y1 + dy))),
            Math.max(width, Math.min(imageSize.width, Math.round(x2 + dx))),
            Math.max(height, Math.min(imageSize.height, Math.round(y2 + dy))),
          ]
        : [
            x1,
            y1,
            Math.max(x1 + 4, Math.min(imageSize.width, Math.round(point.x))),
            Math.max(y1 + 4, Math.min(imageSize.height, Math.round(point.y))),
          ];
    updateLocalBbox(boxInteraction.regionId, bbox);
  };

  const handleBoxEnd = async (event: PointerEvent<HTMLElement>) => {
    if (!boxInteraction || !page) return;
    event.preventDefault();
    const region = page.regions.find((item) => item.id === boxInteraction.regionId);
    setBoxInteraction(null);
    if (!region) return;
    const point = getImagePoint(event);
    if (!point) return;
    const [x1, y1, x2, y2] = boxInteraction.bbox;
    const dx = point.x - boxInteraction.start.x;
    const dy = point.y - boxInteraction.start.y;
    const nextBbox: Region["bbox"] =
      boxInteraction.mode === "move"
        ? [
            Math.max(0, Math.min(imageSize.width - (x2 - x1), Math.round(x1 + dx))),
            Math.max(0, Math.min(imageSize.height - (y2 - y1), Math.round(y1 + dy))),
            Math.max(x2 - x1, Math.min(imageSize.width, Math.round(x2 + dx))),
            Math.max(y2 - y1, Math.min(imageSize.height, Math.round(y2 + dy))),
          ]
        : [
            x1,
            y1,
            Math.max(x1 + 4, Math.min(imageSize.width, Math.round(point.x))),
            Math.max(y1 + 4, Math.min(imageSize.height, Math.round(point.y))),
          ];
    try {
      await updateBubble(region.id, { bbox: nextBbox });
    } catch (requestError) {
      setError(
        requestError instanceof Error ? requestError.message : "Unable to save bubble position.",
      );
    }
  };

  const removeBubble = async (regionId: number) => {
    if (!window.confirm("Delete this text bubble?")) return;
    if (!page) return;
    const pageId = page.id;
    try {
      const deleted = await deleteBubble(regionId);
      setDeletedBubble({ ...deleted.region, page_id: pageId });
      setChapter((current) =>
        current
          ? {
              ...current,
              pages: current.pages.map((item) =>
                item.id === pageId
                  ? { ...item, regions: item.regions.filter((region) => region.id !== regionId) }
                  : item,
              ),
            }
          : current,
      );
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to delete bubble.");
    }
  };

  const undoDelete = async () => {
    if (!deletedBubble) return;
    try {
      const restored = await restoreBubble(deletedBubble);
      const pageId = deletedBubble.page_id;
      setChapter((current) =>
        current
          ? {
              ...current,
              pages: current.pages.map((item) =>
                item.id === pageId
                  ? { ...item, regions: [...item.regions, restored].sort((a, b) => a.id - b.id) }
                  : item,
              ),
            }
          : current,
      );
      setDeletedBubble(null);
    } catch (requestError) {
      setError(
        requestError instanceof Error ? requestError.message : "Unable to undo bubble deletion.",
      );
    }
  };

  return (
    <AppLayout
      session={session}
      activeScreen="review"
      activeProject={project}
      breadcrumbs={["Projects", project.title, "Review Studio"]}
      onNavigate={onNavigate}
      onLogout={onLogout}
    >
      <section className="review-content">
        {deletedBubble && (
          <div className="undo-bubble-banner">
            Bubble #{deletedBubble.id} deleted.{" "}
            <button onClick={() => void undoDelete()}>Undo</button>
          </div>
        )}

        <div className="dashboard-title">
          <div>
            <h1>Interactive Review Studio</h1>
            <p>{project.title} — OCR verification and text correction</p>
          </div>
          <select
            value={chapterId ?? ""}
            onChange={(event) => {
              setChapterId(Number(event.target.value));
              setPageIndex(0);
            }}
          >
            {chapters.length ? (
              chapters.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.chapter_name || `Chapter ${item.chapter_number}`}
                </option>
              ))
            ) : (
              <option value="">No chapters</option>
            )}
          </select>
        </div>

        {error && <div className="dashboard-error">{error}</div>}
        {notice && <div className="typesetting-message">{notice}</div>}
        {message && (
          <div className="typesetting-message">
            {message}{" "}
            <button onClick={() => onNavigate("typesetting")}>Go to Typesetting →</button>
          </div>
        )}

        {loading ? (
          <div className="dashboard-empty">Loading OCR data...</div>
        ) : !page ? (
          <div className="dashboard-empty">
            <h2>No OCR pages yet</h2>
            <p>Upload and process chapter pages before reviewing OCR.</p>
          </div>
        ) : (
          <>
            <div className="review-toolbar">
              <button disabled={pageIndex === 0} onClick={() => setPageIndex((index) => index - 1)}>
                ← Prev Page
              </button>
              <span>
                Page {pageIndex + 1} of {chapter?.pages.length}
                {page.status === "NEEDS_REVIEW" && (
                  <b className="page-flag"> • ⚑ Needs second review</b>
                )}
                {page.status === "REVIEW_DRAFT" && (
                  <b className="page-flag draft"> • ✎ Draft saved</b>
                )}
              </span>
              <button
                disabled={pageIndex >= (chapter?.pages.length ?? 1) - 1}
                onClick={() => setPageIndex((index) => index + 1)}
              >
                Next Page →
              </button>
              <button
                className={drawMode ? "draw-bubble-active" : ""}
                onClick={() => {
                  setDrawMode((current) => !current);
                  setDrawStart(null);
                  setDrawBox(null);
                }}
              >
                {drawMode ? "✕ Cancel drawing" : "＋ Draw bubble"}
              </button>
            </div>

            <div className="review-grid">
              <div className="review-image-panel">
                <h2>Original Page — Detection Preview</h2>
                <div
                  className={`review-image-wrap ${drawMode ? "draw-mode" : ""}`}
                  onPointerDown={handleDrawStart}
                  onPointerMove={handleDrawMove}
                  onPointerUp={(event) => void handleDrawEnd(event)}
                  onPointerCancel={() => {
                    setDrawStart(null);
                    setDrawBox(null);
                  }}
                >
                  <img
                    draggable={false}
                    style={{ pointerEvents: drawMode ? "none" : "auto" }}
                    src={`${API_ORIGIN}${page.original_url}`}
                    alt={page.page_number.toString()}
                    onLoad={(event) =>
                      setImageSize({
                        width: event.currentTarget.naturalWidth,
                        height: event.currentTarget.naturalHeight,
                      })
                    }
                  />
                  {imageSize.width > 0 &&
                    page.regions.map((region) => {
                      const [x, y, x2, y2] = region.bbox;
                      return (
                        <div
                          className={`bbox ${region.original_text ? "" : "low-confidence"} ${activeRegionId === region.id ? "active" : ""}`}
                          key={region.id}
                          onPointerDown={(event) => handleBoxStart(event, region, "move")}
                          onPointerMove={handleBoxMove}
                          onPointerUp={(event) => void handleBoxEnd(event)}
                          onClick={() => focusRegionText(region.id)}
                          style={{
                            left: `${(x / imageSize.width) * 100}%`,
                            top: `${(y / imageSize.height) * 100}%`,
                            width: `${((x2 - x) / imageSize.width) * 100}%`,
                            height: `${((y2 - y) / imageSize.height) * 100}%`,
                            pointerEvents: drawMode ? "none" : "auto",
                          }}
                        >
                          <b>{region.id}</b>
                          <i
                            className="bbox-resize-handle"
                            onPointerDown={(event) => handleBoxStart(event, region, "resize")}
                          />
                        </div>
                      );
                    })}
                  {drawBox && (
                    <div
                      className="draw-bubble-preview"
                      style={{
                        left: `${drawBox.x / (imageSize.width / 100)}%`,
                        top: `${drawBox.y / (imageSize.height / 100)}%`,
                        width: `${drawBox.width / (imageSize.width / 100)}%`,
                        height: `${drawBox.height / (imageSize.height / 100)}%`,
                      }}
                    />
                  )}
                </div>
              </div>

              <div className="ocr-panel">
                <div className="ocr-panel-title">
                  <h2>Extracted Text (Manga OCR)</h2>
                  <button disabled={saving} onClick={() => void rerunOcr()}>
                    <AppIcon name="refresh" /> Re-run OCR
                  </button>
                </div>
                {page.regions.map((region) => (
                  <div
                    className={`ocr-card ${!region.original_text ? "low-confidence" : ""} ${activeRegionId === region.id ? "active" : ""}`}
                    key={region.id}
                  >
                    <div>
                      <b>Bubble #{region.id} • Text Region</b>
                      <small>
                        Box: [{region.bbox.join(", ")}]{" "}
                        <button
                          className="delete-bubble-button"
                          aria-label={`Delete bubble ${region.id}`}
                          onClick={() => void removeBubble(region.id)}
                        >
                          <AppIcon name="trash" /> Delete
                        </button>
                      </small>
                    </div>
                    <textarea
                      id={`ocr-region-${region.id}`}
                      value={region.original_text}
                      onFocus={() => setActiveRegionId(region.id)}
                      onChange={(event) => updateOriginal(region.id, event.target.value)}
                    />
                    <span>
                      {region.original_text ? "✓ Verified OCR text" : "⚠ Needs transcription"}
                    </span>
                  </div>
                ))}
                <div className="review-secondary-actions">
                  <button disabled={saving} onClick={() => void saveDraft()}>
                    💾 Save OCR Draft
                  </button>
                  <button
                    disabled={saving || page.status === "NEEDS_REVIEW"}
                    onClick={() => void flagForReview()}
                  >
                    ⚑ {page.status === "NEEDS_REVIEW" ? "Flagged" : "Flag Page"}
                  </button>
                </div>
                <button
                  className="create-project-button review-save"
                  disabled={saving}
                  onClick={() => void saveAndTranslate()}
                >
                  {saving ? "Translating & Rendering... (30-60s)" : "Save OCR & Re-Translate →"}
                </button>
              </div>
            </div>
          </>
        )}
      </section>
    </AppLayout>
  );
}

const toAlignment = (value: string | null | undefined): "left" | "center" | "right" =>
  value === "left" || value === "right" ? value : "center";

export function TypesettingScreen({
  session,
  project,
  onNavigate,
  onLogout,
}: {
  session: AuthSession;
  project: ProjectSummary;
  onNavigate: NavigateFn;
  onLogout: () => void;
}) {
  const [chapters, setChapters] = useState<ChapterSummary[]>([]);
  const [chapterId, setChapterId] = useState<number | null>(null);
  const [chapter, setChapter] = useState<Chapter | null>(null);
  const [pageIndex, setPageIndex] = useState(0);
  const [regionId, setRegionId] = useState<number | null>(null);
  const [text, setText] = useState("");
  const [fontSize, setFontSize] = useState(24);
  const [alignment, setAlignment] = useState<"left" | "center" | "right">("center");
  const [compareOriginal, setCompareOriginal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [imageSize, setImageSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    void getProjectChapters(project.id)
      .then((items) => {
        setChapters(items);
        setChapterId(items[items.length - 1]?.id ?? null);
      })
      .catch((requestError) =>
        setError(requestError instanceof Error ? requestError.message : "Unable to load chapters."),
      );
  }, [project.id]);

  useEffect(() => {
    if (!chapterId) {
      setLoading(false);
      return;
    }
    setLoading(true);
    void getChapter(chapterId)
      .then((loaded) => {
        setChapter(loaded);
        setPageIndex(0);
      })
      .catch((requestError) =>
        setError(requestError instanceof Error ? requestError.message : "Unable to load chapter."),
      )
      .finally(() => setLoading(false));
  }, [chapterId]);

  const page = chapter?.pages[pageIndex] ?? null;
  const selectedRegion =
    page?.regions.find((region) => region.id === regionId) ?? page?.regions[0] ?? null;

  useEffect(() => {
    const first = page?.regions[0];
    setRegionId(first?.id ?? null);
    setText(first?.translated_text ?? "");
    setFontSize(first?.font_size ?? 24);
    setAlignment(toAlignment(first?.alignment));
  }, [page?.id]);

  // ← / → flip pages unless the user is typing in a form field.
  const pageCount = chapter?.pages.length ?? 0;
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      if (target && /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName)) return;
      if (target?.isContentEditable || event.metaKey || event.ctrlKey || event.altKey) return;
      if (event.key === "ArrowLeft") setPageIndex((index) => Math.max(0, index - 1));
      if (event.key === "ArrowRight") setPageIndex((index) => Math.min(pageCount - 1, index + 1));
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [pageCount]);

  const saveAndRender = async () => {
    if (!page || !selectedRegion) return;
    setSaving(true);
    setError("");
    setMessage("");
    try {
      const updated = await typesetPage(page.id, selectedRegion.id, text, fontSize, alignment);
      setChapter((current) =>
        current
          ? {
              ...current,
              pages: current.pages.map((item) => (item.id === updated.id ? updated : item)),
            }
          : current,
      );
      setMessage("Translation saved and page re-rendered.");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to re-render page.");
    } finally {
      setSaving(false);
    }
  };

  const imageUrl = page
    ? compareOriginal
      ? page.original_url
      : page.rendered_url ?? page.clean_url ?? page.original_url
    : null;

  useEffect(() => {
    setImageSize({ width: 0, height: 0 });
  }, [imageUrl]);

  return (
    <AppLayout
      session={session}
      activeScreen="typesetting"
      activeProject={project}
      breadcrumbs={["Projects", project.title, "Typesetting Studio"]}
      onNavigate={onNavigate}
      onLogout={onLogout}
    >
      <section className="typesetting-content">
        <div className="dashboard-title">
          <div>
            <h1>Typesetting Studio</h1>
            <p>{project.title} — final Vietnamese layout and page rendering</p>
          </div>
          <select
            value={chapterId ?? ""}
            onChange={(event) => setChapterId(Number(event.target.value))}
          >
            {chapters.length ? (
              chapters.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.chapter_name || `Chapter ${item.chapter_number}`}
                </option>
              ))
            ) : (
              <option value="">No chapters</option>
            )}
          </select>
        </div>

        {error && <div className="dashboard-error">{error}</div>}
        {message && <div className="typesetting-message">{message}</div>}

        {loading ? (
          <div className="dashboard-empty">Loading typesetting data...</div>
        ) : !page ? (
          <div className="dashboard-empty">
            <h2>No pages available</h2>
            <p>Upload and process real chapter pages before typesetting.</p>
          </div>
        ) : (
          <>
            <div className="typesetting-toolbar">
              <button disabled={pageIndex === 0} onClick={() => setPageIndex((index) => index - 1)}>
                ← Previous
              </button>
              <span>
                Page {pageIndex + 1} of {chapter?.pages.length}
                {page.status === "NEEDS_REVIEW" && (
                  <b className="page-flag"> • ⚑ Needs second review</b>
                )}
                {page.status === "REVIEW_DRAFT" && (
                  <b className="page-flag draft"> • ✎ Draft saved</b>
                )}
              </span>
              <button
                disabled={pageIndex >= (chapter?.pages.length ?? 1) - 1}
                onClick={() => setPageIndex((index) => index + 1)}
              >
                Next →
              </button>
              {page.rendered_url && (
                <a className="download-page-button" href={`${API_ORIGIN}${pageDownloadUrl(page.id)}`} download>
                  ⇩ Download Page
                </a>
              )}
              <small className="muted">Tip: use ← / → to flip pages</small>
              <label>
                <input
                  type="checkbox"
                  checked={compareOriginal}
                  onChange={(event) => setCompareOriginal(event.target.checked)}
                />{" "}
                Compare with Japanese original
              </label>
            </div>

            <div className="typesetting-grid">
              <div className="typesetting-preview">
                <div className="typesetting-preview-heading">
                  <h2>{compareOriginal ? "Japanese Original" : "Rendered Vietnamese Page"}</h2>
                  <span>{page.status}</span>
                </div>
                {imageUrl ? (
                  <div className="typesetting-image-wrap">
                    <img
                      src={`${API_ORIGIN}${imageUrl}`}
                      alt={`Page ${page.page_number}`}
                      onLoad={(event) =>
                        setImageSize({
                          width: event.currentTarget.naturalWidth,
                          height: event.currentTarget.naturalHeight,
                        })
                      }
                    />
                    {imageSize.width > 0 &&
                      page.regions.map((region, index) => {
                        const [x, y, x2, y2] = region.bbox;
                        return (
                          <button
                            className={`typesetting-bbox ${region.id === selectedRegion?.id ? "selected" : ""}`}
                            key={region.id}
                            aria-label={`Select bubble ${index + 1}`}
                            onClick={() => {
                              setRegionId(region.id);
                              setText(region.translated_text);
                              setFontSize(region.font_size ?? 24);
                              setAlignment(toAlignment(region.alignment));
                            }}
                            style={{
                              left: `${(x / imageSize.width) * 100}%`,
                              top: `${(y / imageSize.height) * 100}%`,
                              width: `${((x2 - x) / imageSize.width) * 100}%`,
                              height: `${((y2 - y) / imageSize.height) * 100}%`,
                            }}
                          >
                            <b>{index + 1}</b>
                          </button>
                        );
                      })}
                  </div>
                ) : (
                  <div className="dashboard-empty">No rendered image available.</div>
                )}
              </div>

              <aside className="typesetting-panel">
                <h2>Speech Bubble</h2>
                <label className="field-label" htmlFor="bubble-select">
                  Select region
                </label>
                <select
                  id="bubble-select"
                  value={selectedRegion?.id ?? ""}
                  onChange={(event) => {
                    const next = page.regions.find(
                      (region) => region.id === Number(event.target.value),
                    );
                    setRegionId(next?.id ?? null);
                    setText(next?.translated_text ?? "");
                    setFontSize(next?.font_size ?? 24);
                    setAlignment(toAlignment(next?.alignment));
                  }}
                >
                  {page.regions.map((region) => (
                    <option key={region.id} value={region.id}>
                      Bubble {region.id}
                    </option>
                  ))}
                </select>

                {selectedRegion ? (
                  <>
                    <div className="typesetting-source">
                      <span>Original OCR</span>
                      <p>{selectedRegion.original_text || "No OCR text"}</p>
                    </div>
                    <label className="field-label" htmlFor="typeset-text">
                      Vietnamese translation
                    </label>
                    <textarea
                      id="typeset-text"
                      value={text}
                      onChange={(event) => setText(event.target.value)}
                      rows={8}
                      placeholder="Enter translated dialogue..."
                    />
                    <label className="field-label" htmlFor="font-size">
                      Font size
                    </label>
                    <input
                      id="font-size"
                      type="number"
                      min="8"
                      max="120"
                      value={fontSize}
                      onChange={(event) => setFontSize(Number(event.target.value))}
                    />
                    <span className="field-label">Alignment</span>
                    <div className="alignment-group" role="group" aria-label="Text alignment">
                      {(["left", "center", "right"] as const).map((option) => (
                        <button
                          type="button"
                          key={option}
                          className={alignment === option ? "active" : ""}
                          aria-pressed={alignment === option}
                          onClick={() => setAlignment(option)}
                        >
                          {option === "left" ? "⇤ Left" : option === "right" ? "Right ⇥" : "↔ Center"}
                        </button>
                      ))}
                    </div>
                    <button
                      className="create-project-button full-width"
                      disabled={saving || !text.trim()}
                      onClick={() => void saveAndRender()}
                    >
                      {saving ? "Rendering..." : "⚡ Save & Re-render Now"}
                    </button>
                  </>
                ) : (
                  <p className="muted">No speech bubbles detected on this page.</p>
                )}
              </aside>
            </div>
          </>
        )}
      </section>
    </AppLayout>
  );
}

export function QueueScreen({
  session,
  project,
  onNavigate,
  onLogout,
}: {
  session: AuthSession;
  project: ProjectSummary;
  onNavigate: NavigateFn;
  onLogout: () => void;
}) {
  const [queue, setQueue] = useState<QueueSnapshot | null>(null);
  const [chapterId, setChapterId] = useState<number | null>(null);
  const [streamState, setStreamState] = useState<"connecting" | "live" | "done" | "polling">(
    "connecting",
  );
  const [streamKey, setStreamKey] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setChapterId(null);
    setLoading(true);
  }, [project.id]);

  const refresh = async () => {
    try {
      const snapshot = await getProjectQueue(project.id, chapterId);
      setQueue(snapshot);
      if (chapterId === null && snapshot.chapter_id) setChapterId(snapshot.chapter_id);
      setError("");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to load queue.");
    } finally {
      setLoading(false);
    }
  };

  // Initial load (also resolves the chapter id the stream needs).
  useEffect(() => {
    void refresh();
  }, [project.id, chapterId]);

  // Live updates over SSE; fall back to 5s polling whenever the stream is down.
  useEffect(() => {
    if (chapterId === null || typeof EventSource === "undefined") {
      if (chapterId !== null) {
        const timer = window.setInterval(() => void refresh(), 5000);
        return () => window.clearInterval(timer);
      }
      return;
    }
    let pollTimer: number | undefined;
    const stopPolling = () => {
      if (pollTimer !== undefined) {
        window.clearInterval(pollTimer);
        pollTimer = undefined;
      }
    };
    const source = new EventSource(
      `${API_ORIGIN}/api/projects/${project.id}/queue/stream?chapter_id=${chapterId}`,
    );
    setStreamState("connecting");
    source.onopen = () => {
      stopPolling();
      setStreamState("live");
    };
    source.onmessage = (event) => {
      try {
        setQueue(JSON.parse(event.data) as QueueSnapshot);
        setError("");
        setLoading(false);
      } catch {
        /* ignore malformed frame */
      }
    };
    source.addEventListener("done", () => {
      source.close();
      stopPolling();
      setStreamState("done");
    });
    source.onerror = () => {
      setStreamState("polling");
      if (pollTimer === undefined) {
        pollTimer = window.setInterval(() => void refresh(), 5000);
      }
      // EventSource retries by itself while CONNECTING; if it gave up, we keep polling.
    };
    return () => {
      source.close();
      stopPolling();
    };
  }, [project.id, chapterId, streamKey]);

  const start = async () => {
    if (!queue?.chapter_id) return;
    try {
      setQueue(await startProjectQueue(project.id, queue.chapter_id));
      setStreamKey((key) => key + 1);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to start pipeline.");
    }
  };

  const percent =
    queue?.task?.progress_percent ??
    (queue?.total_pages ? Math.round((queue.completed_pages / queue.total_pages) * 100) : 0);
  const pagePercent = queue?.total_pages
    ? Math.round((queue.completed_pages / queue.total_pages) * 100)
    : 0;
  const completed = Boolean(queue?.total_pages && queue.completed_pages === queue.total_pages);
  const hasRenderedPages = Boolean(queue?.pages.some((page) => page.rendered));
  const taskRunning = queue?.task?.status === "RUNNING" || queue?.task?.status === "QUEUED";
  const taskStatus = queue?.task?.status ?? "NOT_STARTED";
  const downloadZip = () => {
    window.location.href = `/api/projects/${project.id}/queue/export${queue?.chapter_id ? `?chapter_id=${queue.chapter_id}` : ""}`;
  };

  return (
    <AppLayout
      session={session}
      activeScreen="queue"
      activeProject={project}
      breadcrumbs={["Projects", project.title, "Queue Monitor"]}
      onNavigate={onNavigate}
      onLogout={onLogout}
    >
      <section className="queue-content">
        <div className="dashboard-title">
          <div>
            <h1>Queue Monitor</h1>
            <p>
              {completed
                ? "All chapter tasks completed successfully."
                : "Real-time task tracking for the asynchronous pipeline."}
            </p>
          </div>
          <div className="queue-actions">
            {queue && queue.chapters.length > 0 && (
              <select
                className="chapter-select"
                aria-label="Select chapter"
                value={chapterId ?? queue.chapter_id ?? ""}
                onChange={(event) => {
                  setLoading(true);
                  setChapterId(Number(event.target.value));
                }}
              >
                {queue.chapters.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.chapter_name || `Chapter ${item.chapter_number}`}
                  </option>
                ))}
              </select>
            )}
            <button onClick={() => void refresh()}>
              <AppIcon name="refresh" />{" "}
              {streamState === "live"
                ? "● Live Stream Connected"
                : streamState === "done"
                  ? "Stream finished · Refresh"
                  : streamState === "connecting"
                    ? "Connecting…"
                    : "Auto-refresh: 5s (stream offline)"}
            </button>
            <button
              className="create-project-button"
              disabled={!queue?.chapter_id || taskRunning}
              onClick={() => void start()}
            >
              {taskRunning
                ? `● ${queue?.task?.status === "QUEUED" ? "Queued" : "Running"} ${queue?.task?.progress_percent ?? 0}%`
                : completed || taskStatus === "FAILED"
                  ? "↻ Re-run Pipeline"
                  : "▶ Run Pipeline"}
            </button>
            {(completed || hasRenderedPages) && (
              <button className="create-project-button" onClick={downloadZip}>
                ⇩ Download Chapter (ZIP)
              </button>
            )}
          </div>
        </div>

        {error && <div className="dashboard-error">{error}</div>}

        {loading ? (
          <div className="dashboard-empty">Loading queue...</div>
        ) : !queue || !queue.total_pages ? (
          <div className="dashboard-empty">
            <h2>No queued pages</h2>
            <p>Upload chapter pages first. Queue data will appear here when real pages exist.</p>
          </div>
        ) : (
          <>
            <div className={completed ? "queue-complete" : "queue-hero"}>
              {completed && <div className="complete-icon">✓</div>}
              <div>
                <strong>
                  {completed
                    ? "Chapter Localization 100% Complete!"
                    : `Active Chapter: ${queue.chapters.find((item) => item.id === queue.chapter_id)?.chapter_name ?? project.title}`}
                </strong>
                <p>
                  {completed
                    ? `All ${queue.total_pages} pages have been detected, cleaned, translated, and typeset.`
                    : ""}
                </p>
                <b>
                  Task status: {taskStatus} · {queue.completed_pages} / {queue.total_pages} Pages
                  Processed ({pagePercent}%)
                </b>
              </div>
              <div className="queue-progress">
                <i style={{ width: `${percent}%` }} />
              </div>
              <div className="stage-line">
                <span>● Queued</span>
                <span>→</span>
                <span>● Detection</span>
                <span>→</span>
                <span>● OCR</span>
                <span>→</span>
                <span>● Review</span>
                <span>→</span>
                <span>○ Inpainting</span>
                <span>→</span>
                <span>○ Typesetting</span>
              </div>
            </div>

            <div className="queue-stats">
              <Kpi
                label={completed ? "Total Pages Localized" : "Worker Node"}
                value={completed ? `${queue.total_pages} Pages` : "Node Tokyo-01"}
                detail={completed ? "100% Completion" : "GPU worker status from queue"}
              />
              <Kpi
                label={completed ? "Average Processing Time" : "Throughput"}
                value="—"
                detail="Unavailable from current queue data"
              />
              <Kpi
                label={completed ? "Translation Provider" : "Review Queue"}
                value={
                  completed
                    ? "Configured backend"
                    : String(
                        queue.pages.filter(
                          (page) => page.status === "REVIEW" || page.status === "AWAITING_REVIEW",
                        ).length,
                      )
                }
                detail={completed ? "" : "Pages awaiting review"}
              />
            </div>

            <div className="queue-matrix">
              <div className="queue-matrix-head">
                <h2>
                  {completed ? "Completed Chapter Artifacts" : "Pipeline Task Execution Matrix"}
                </h2>
                <span>{queue.total_pages} pages total</span>
              </div>
              {queue.pages.map((page) => (
                <div className="queue-row" key={page.id}>
                  <b>Page {String(page.page_number).padStart(3, "0")}</b>
                  <span>{page.filename}</span>
                  <strong>{completed ? "Typesetting Done" : page.status}</strong>
                  <em
                    className={
                      page.status === "FAILED"
                        ? "failed"
                        : page.status === "COMPLETED"
                          ? "done"
                          : ""
                    }
                  >
                    {page.status === "COMPLETED" ? "✓ Completed" : page.status}
                  </em>
                </div>
              ))}
            </div>

            <div className="queue-log">
              <strong>
                ▣ {completed ? "Terminal Execution Summary" : "Live Worker Stream"}
              </strong>
              {queue.logs.length ? (
                queue.logs.map((log, index) => (
                  <div key={`${log.timestamp}-${index}`}>
                    [{log.timestamp}] {log.level} {log.message}
                  </div>
                ))
              ) : (
                <div>No worker logs yet.</div>
              )}
            </div>
          </>
        )}
      </section>
    </AppLayout>
  );
}

export function ChapterScreen({
  session,
  project,
  onNavigate,
  onLogout,
}: {
  session: AuthSession;
  project: ProjectSummary;
  onNavigate: NavigateFn;
  onLogout: () => void;
}) {
  const [chapters, setChapters] = useState<ChapterSummary[]>([]);
  const [selectedId, setSelectedId] = useState<number | "new">("new");
  const [newName, setNewName] = useState("");
  const chapter = chapters.find((item) => item.id === selectedId) ?? null;

  useEffect(() => {
    getProjectChapters(project.id)
      .then((loaded) => {
        setChapters(loaded);
        setSelectedId(loaded.length ? loaded[loaded.length - 1].id : "new");
      })
      .catch(() => setChapters([]));
  }, [project.id]);
  const [files, setFiles] = useState<File[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const MAX_BATCH_PAGES = 50;
  const MAX_BATCH_BYTES = 100 * 1024 * 1024; // 100MB

  const selectFiles = (selected: FileList | null) => {
    if (!selected) return;
    setError("");
    const valid = Array.from(selected).filter((file) => /\.(jpe?g|png|webp)$/i.test(file.name));
    if (valid.length !== selected.length) {
      setError("Only JPG, JPEG, PNG and WEBP files are supported.");
    }
    const combined = [...files, ...valid];
    if (combined.length > MAX_BATCH_PAGES) {
      setError(`Cannot exceed ${MAX_BATCH_PAGES} pages per chapter batch (selected: ${combined.length} files).`);
      return;
    }
    const totalBytes = combined.reduce((sum, item) => sum + item.size, 0);
    if (totalBytes > MAX_BATCH_BYTES) {
      setError(`Total batch size exceeds 100MB limit (${(totalBytes / 1024 / 1024).toFixed(1)} MB).`);
      return;
    }
    setFiles(combined);
  };

  const removeFile = (indexToRemove: number) => {
    setFiles((current) => current.filter((_, idx) => idx !== indexToRemove));
    setError("");
  };

  const createAndUpload = async () => {
    if (!files.length) return;
    if (files.length > MAX_BATCH_PAGES) {
      setError(`Cannot exceed ${MAX_BATCH_PAGES} pages per chapter batch.`);
      return;
    }
    const totalBytes = files.reduce((sum, item) => sum + item.size, 0);
    if (totalBytes > MAX_BATCH_BYTES) {
      setError(`Total batch size exceeds 100MB limit (${(totalBytes / 1024 / 1024).toFixed(1)} MB).`);
      return;
    }
    setBusy(true);
    setError("");
    const pendingFiles = [...files];
    try {
      const fallbackChapterTitle = `Chapter ${chapters.length + 1}`;
      const nextChapter =
        chapter ?? (await createChapter(project.id, newName.trim() || fallbackChapterTitle));
      if (!chapter) {
        setChapters((current) => [...current, nextChapter]);
        setSelectedId(nextChapter.id);
        setNewName("");
      }
      setFiles([]);
      onNavigate("queue");
      for (const file of pendingFiles) {
        await uploadPage(file, nextChapter.id);
      }
      await startProjectQueue(project.id, nextChapter.id);
    } catch (requestError) {
      setError(
        requestError instanceof Error ? requestError.message : "Upload or pipeline start failed.",
      );
    } finally {
      setBusy(false);
    }
  };

  const removeChapter = async () => {
    if (
      !chapter ||
      !window.confirm("Delete this chapter, its pages, OCR, translations and rendered files?")
    )
      return;
    setBusy(true);
    setError("");
    try {
      await deleteChapter(project.id, chapter.id, session.user.id);
      const remaining = chapters.filter((item) => item.id !== chapter.id);
      setChapters(remaining);
      setSelectedId(remaining.length ? remaining[remaining.length - 1].id : "new");
      setMessage("Chapter deleted.");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to delete chapter.");
    } finally {
      setBusy(false);
    }
  };

  const clearProject = async () => {
    if (
      !window.confirm(
        "Delete ALL old chapters, pages, OCR, translations, queue logs and rendered results in this project?",
      )
    )
      return;
    setBusy(true);
    setError("");
    try {
      await deleteProjectData(project.id, session.user.id);
      setChapters([]);
      setSelectedId("new");
      setMessage("All old project data was deleted. Upload new pages to start clean.");
    } catch (requestError) {
      setError(
        requestError instanceof Error ? requestError.message : "Unable to clear project data.",
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <AppLayout
      session={session}
      activeScreen="chapter"
      activeProject={project}
      breadcrumbs={["Projects", project.title, "Chapter Studio"]}
      onNavigate={onNavigate}
      onLogout={onLogout}
    >
      <section className="chapter-content">
        <div className="chapter-heading">
          <div>
            <h1>Chapter Studio</h1>
            <p>Upload chapter raw scans and configure AI pipeline execution.</p>
          </div>
          <div className="chapter-heading-actions">
            <span className="project-chip">Project: {project.title}</span>
            <button className="danger-button" disabled={busy} onClick={() => void clearProject()}>
              Clear old results
            </button>
            {chapter && (
              <button className="danger-button" disabled={busy} onClick={() => void removeChapter()}>
                Delete chapter
              </button>
            )}
          </div>
        </div>

        <div className="chapter-picker">
          <label>
            <strong>Chapter</strong>
            <select
              value={selectedId}
              disabled={busy}
              onChange={(event) =>
                setSelectedId(event.target.value === "new" ? "new" : Number(event.target.value))
              }
            >
              {chapters.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.chapter_name || `Chapter ${item.chapter_number}`}
                </option>
              ))}
              <option value="new">＋ New chapter…</option>
            </select>
          </label>
          {selectedId === "new" && (
            <label>
              <strong>New chapter name</strong>
              <input
                value={newName}
                maxLength={200}
                placeholder={`Chapter ${chapters.length + 1}`}
                onChange={(event) => setNewName(event.target.value)}
              />
            </label>
          )}
        </div>

        <label className="dropzone">
          <span className="upload-cloud">☁</span>
          <strong>Drag &amp; drop comic pages here</strong>
          <small>Accepts JPG, PNG batches up to 50 pages • 100MB per chapter</small>
          <span className="browse-button">Browse Files from Computer</span>
          <input
            type="file"
            multiple
            accept=".jpg,.jpeg,.png,.webp"
            onChange={(event) => {
              selectFiles(event.target.files);
              event.currentTarget.value = "";
            }}
          />
        </label>

        {error && <div className="dashboard-error">{error}</div>}

        <div className="upload-list">
          <div className="upload-list-heading">
            <strong>Uploaded Pages ({files.length} files ready)</strong>
            <button onClick={() => setFiles([])}>Clear all</button>
          </div>
          {files.length === 0 ? (
            <div className="upload-empty">
              No files selected. Upload real comic pages to continue.
            </div>
          ) : (
            files.map((file, index) => (
              <div className="upload-row" key={`${file.name}-${index}`}>
                <span>▣</span>
                <strong>{file.name}</strong>
                <small>({(file.size / 1024 / 1024).toFixed(1)} MB)</small>
                <em>✓ Ready for detection</em>
                <button
                  type="button"
                  className="upload-remove-btn"
                  title={`Remove ${file.name}`}
                  onClick={() => removeFile(index)}
                >
                  ✕
                </button>
              </div>
            ))
          )}
        </div>

        <div className="language-cards">
          <div>
            <strong>Source Language</strong>
            <select defaultValue="Japanese">
              <option>Japanese (Raw Manga)</option>
              <option>English</option>
            </select>
            <small>● Active Engine: MangaOCR</small>
          </div>
          <div>
            <strong>Target Language</strong>
            <select defaultValue="Vietnamese">
              <option>Vietnamese</option>
            </select>
            <small>● Translator: Gemini + Custom Glossary</small>
          </div>
        </div>

        <div className="pipeline-bar">
          <div>
            <strong>
              {message ||
                (files.length
                  ? `Ready to process ${files.length} page${files.length > 1 ? "s" : ""} in Asynchronous Queue`
                  : "Ready when pages are uploaded")}
            </strong>
            <small>
              Queue › YOLOv8 Detection › Manga OCR › Waiting Review › LaMa Inpainting › Typesetting
            </small>
          </div>
          <button
            className="create-project-button"
            disabled={!files.length || busy}
            onClick={() => void createAndUpload()}
          >
            {busy ? "Uploading..." : "Start AI Pipeline ▶"}
          </button>
        </div>
      </section>
    </AppLayout>
  );
}

export function TeamScreen({
  session,
  project,
  onNavigate,
  onLogout,
}: {
  session: AuthSession;
  project: ProjectSummary;
  onNavigate: NavigateFn;
  onLogout: () => void;
}) {
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("Translator");
  const emailInputRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const loadMembers = async () => {
    setLoading(true);
    try {
      setMembers(await getProjectMembers(project.id));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to load members.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadMembers();
  }, [project.id]);

  const isCurrentUserAdmin =
    members.some(
      (m) => String(m.user_id) === String(session.user.id) && (m.is_owner || m.role === "Project Manager")
    ) || session.user.role === "ADMIN" || session.user.role === "Owner";

  const invite = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const member = await inviteProjectMember(project.id, email, role, session.user.id);
      setMembers((current) => {
        const exists = current.some((item) => item.user_id === member.user_id);
        return exists
          ? current.map((item) => (item.user_id === member.user_id ? member : item))
          : [...current, member];
      });
      setEmail("");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to invite member.");
    } finally {
      setBusy(false);
    }
  };

  const handleRoleChange = async (memberUserId: number, newRole: string) => {
    setError("");
    try {
      const updated = await updateProjectMemberRole(project.id, memberUserId, newRole, session.user.id);
      setMembers((current) => current.map((m) => (m.user_id === memberUserId ? updated : m)));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to update member role.");
    }
  };

  const handleRemoveMember = async (memberUserId: number, memberName: string) => {
    if (!window.confirm(`Are you sure you want to remove member "${memberName}" from the project?`)) return;
    setError("");
    try {
      await removeProjectMember(project.id, memberUserId, session.user.id);
      setMembers((current) => current.filter((m) => m.user_id !== memberUserId));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to remove member.");
    }
  };

  return (
    <AppLayout
      session={session}
      activeScreen="team"
      activeProject={project}
      breadcrumbs={["Projects", project.title, "Team & Roles"]}
      onNavigate={onNavigate}
      onLogout={onLogout}
    >
      <section className="team-content">
        <button className="back-projects" onClick={() => onNavigate("workspace")}>
          ← Back to Projects
        </button>
        <div className="dashboard-title">
          <div>
            <h1>Team Workspace &amp; Roles</h1>
            <p>
              Assign roles and permissions for project: <strong>{project.title}</strong>
            </p>
          </div>
          {isCurrentUserAdmin && (
            <button
              className="create-project-button"
              type="button"
              onClick={() => emailInputRef.current?.focus()}
            >
              <AppIcon name="users" /> Invite Member
            </button>
          )}
        </div>

        <div className="team-summary">
          <div>
            <span>Total Members</span>
            <strong>{members.length}</strong>
            <small>Active workspace members</small>
          </div>
          <div>
            <span>Project Series</span>
            <strong>{project.title}</strong>
            <small>{project.total_pages} pages • Japanese → Vietnamese</small>
          </div>
          <div>
            <span>Access Level</span>
            <strong>Private Workspace</strong>
            <small>Role-based permissions</small>
          </div>
        </div>

        {isCurrentUserAdmin && (
          <form className="invite-bar" onSubmit={(event) => void invite(event)}>
            <AppIcon name="mail" />
            <input
              ref={emailInputRef}
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="colleague@studio.com"
              type="email"
              required
            />
            <select value={role} onChange={(event) => setRole(event.target.value)}>
              <option>Translator</option>
              <option>Typesetter</option>
              <option>Project Manager</option>
            </select>
            <button className="create-project-button" disabled={busy}>
              {busy ? "Sending..." : "Send Invite"}
            </button>
          </form>
        )}

        {error && <div className="dashboard-error">{error}</div>}

        <div className="members-panel">
          <div className="members-heading">
            <h2>
              Workspace Members <small>{members.length}</small>
            </h2>
          </div>
          {loading ? (
            <div className="dashboard-empty">Loading members...</div>
          ) : members.length === 0 ? (
            <div className="dashboard-empty">No registered collaborators yet.</div>
          ) : (
            <div className="member-list">
              {members.map((member) => {
                const isSelf = String(member.user_id) === String(session.user.id);
                const canManageRow = isCurrentUserAdmin && !member.is_owner && !isSelf;
                return (
                  <div className="member-row" key={member.user_id}>
                    <div className="member-identity">
                      <span>{member.name.slice(0, 2).toUpperCase()}</span>
                      <div>
                        <strong>{member.name}</strong>
                        <small>{member.email}</small>
                      </div>
                    </div>
                    {member.is_owner ? (
                      <b className="role-owner">Owner</b>
                    ) : canManageRow ? (
                      <select
                        className="member-role-select"
                        value={member.role}
                        onChange={(e) => void handleRoleChange(member.user_id, e.target.value)}
                        aria-label={`Role for ${member.name}`}
                      >
                        <option value="Translator">Translator</option>
                        <option value="Typesetter">Typesetter</option>
                        <option value="Project Manager">Project Manager</option>
                      </select>
                    ) : (
                      <b className={`role-${member.role.toLowerCase().replace(" ", "-")}`}>
                        {member.role}
                      </b>
                    )}
                    <span>{member.is_owner ? "Overall Supervision" : "Assigned project tasks"}</span>
                    <div>
                      {member.is_owner ? (
                        <small>Owner</small>
                      ) : canManageRow ? (
                        <button
                          type="button"
                          className="delete-bubble-button"
                          onClick={() => void handleRemoveMember(member.user_id, member.name)}
                          title="Remove member"
                        >
                          <AppIcon name="trash" /> Remove
                        </button>
                      ) : null}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div className="permissions-panel">
          <h2>Role Permissions Guide</h2>
          <div className="permission-grid">
            <div>
              <b>Project Manager</b>
              <p>Full pipeline control, team invites and role changes.</p>
            </div>
            <div>
              <b>Translator</b>
              <p>Review Studio access, OCR correction and translation.</p>
            </div>
            <div>
              <b>Typesetter</b>
              <p>Typesetting Studio access and bubble formatting.</p>
            </div>
          </div>
        </div>
      </section>
    </AppLayout>
  );
}

export function Kpi({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="kpi-card">
      <span>{label}</span>
      <strong>{value || "—"}</strong>
      <small>{detail}</small>
    </div>
  );
}

export function SettingsScreen({
  session,
  activeProject,
  onSyncProject,
  onNavigate,
  onLogout,
}: {
  session: AuthSession;
  activeProject: ProjectSummary | null;
  onSyncProject: (project: ProjectSummary | null) => void;
  onNavigate: NavigateFn;
  onLogout: () => void;
}) {
  const [settings, setSettings] = useState<SettingsSnapshot | null>(null);
  const [tab, setTab] = useState<"api" | "glossary" | "logs">("api");
  const [glossary, setGlossary] = useState<GlossaryTerm[]>([]);
  const [logs, setLogs] = useState<SystemLogEntry[]>([]);
  const [sourceTerm, setSourceTerm] = useState("");
  const [targetTerm, setTargetTerm] = useState("");
  const [projectId, setProjectId] = useState("");
  const [glossaryFilterProject, setGlossaryFilterProject] = useState<string>("all");
  const [glossarySearch, setGlossarySearch] = useState("");
  const [editingGlossaryId, setEditingGlossaryId] = useState<number | null>(null);
  const [editSource, setEditSource] = useState("");
  const [editTarget, setEditTarget] = useState("");
  const [logFilterProject, setLogFilterProject] = useState<string>("all");
  const [logFilterLevel, setLogFilterLevel] = useState<string>("ALL");
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const refreshSettings = async () => {
    try {
      setSettings(await getSettings(session.user.id));
    } catch (requestError) {
      setError(
        requestError instanceof Error ? requestError.message : "Unable to load settings.",
      );
    }
  };

  useEffect(() => {
    void refreshSettings();
  }, [session.user.id]);

  useEffect(() => {
    void getProjects(session.user.id)
      .then((loaded) => {
        setProjects(loaded);
        if (!activeProject && loaded[0]) {
          onSyncProject(loaded[0]);
        }
        if (!projectId && loaded[0]) {
          setProjectId(String(loaded[0].id));
        }
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Unable to load projects."));
  }, [session.user.id]);

  useEffect(() => {
    void getGlossary(session.user.id)
      .then(setGlossary)
      .catch((e) => setError(e instanceof Error ? e.message : "Unable to load glossary."));
  }, [session.user.id]);

  useEffect(() => {
    if (tab === "logs") {
      void getSettingsLogs(
        session.user.id,
        logFilterProject !== "all" ? Number(logFilterProject) : undefined,
        logFilterLevel,
      )
        .then(setLogs)
        .catch((e) => setError(e instanceof Error ? e.message : "Unable to load logs."));
    }
  }, [tab, session.user.id, logFilterProject, logFilterLevel]);

  const projectMap = useMemo(() => {
    const map = new Map<number, string>();
    projects.forEach((p) => map.set(p.id, p.title));
    return map;
  }, [projects]);

  const filteredGlossary = useMemo(() => {
    const query = glossarySearch.trim().toLowerCase();
    return glossary.filter((item) => {
      if (glossaryFilterProject !== "all" && String(item.project_id) !== glossaryFilterProject) {
        return false;
      }
      if (!query) return true;
      return (
        item.source_term.toLowerCase().includes(query) ||
        item.target_term.toLowerCase().includes(query)
      );
    });
  }, [glossary, glossaryFilterProject, glossarySearch]);

  const addTerm = async (event: FormEvent) => {
    event.preventDefault();
    if (!projectId) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const item = await createGlossary(session.user.id, Number(projectId), sourceTerm, targetTerm);
      setGlossary((items) => [item, ...items]);
      setSourceTerm("");
      setTargetTerm("");
      setShowAdd(false);
      setMessage("Glossary term added.");
      void refreshSettings();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to save glossary term.");
    } finally {
      setBusy(false);
    }
  };

  const startEditGlossary = (item: GlossaryTerm) => {
    setEditingGlossaryId(item.id);
    setEditSource(item.source_term);
    setEditTarget(item.target_term);
    setError("");
    setMessage("");
  };

  const saveEditGlossary = async (glossaryId: number) => {
    if (!editSource.trim() || !editTarget.trim()) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const updated = await updateGlossary(
        session.user.id,
        glossaryId,
        editSource.trim(),
        editTarget.trim(),
      );
      setGlossary((current) => current.map((item) => (item.id === glossaryId ? updated : item)));
      setEditingGlossaryId(null);
      setMessage("Glossary term updated.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to update glossary term.");
    } finally {
      setBusy(false);
    }
  };

  const handleDeleteGlossary = async (item: GlossaryTerm) => {
    if (!window.confirm(`Delete glossary term "${item.source_term} → ${item.target_term}"?`)) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await deleteGlossary(session.user.id, item.id);
      setGlossary((current) => current.filter((row) => row.id !== item.id));
      if (editingGlossaryId === item.id) {
        setEditingGlossaryId(null);
      }
      setMessage("Glossary term deleted.");
      void refreshSettings();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to delete glossary term.");
    } finally {
      setBusy(false);
    }
  };

  const handleClearLogs = async () => {
    const scopeLabel =
      logFilterProject === "all"
        ? "all accessible projects"
        : projectMap.get(Number(logFilterProject)) || "this project";
    if (!window.confirm(`Permanently clear system logs for ${scopeLabel}?`)) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const result = await clearSettingsLogs(
        session.user.id,
        logFilterProject !== "all" ? Number(logFilterProject) : undefined,
      );
      setLogs([]);
      setMessage(result.message);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to clear system logs.");
    } finally {
      setBusy(false);
    }
  };

  const tabTitle =
    tab === "api" ? "API Key Config" : tab === "glossary" ? "Custom Glossary" : "System Logs";

  return (
    <AppLayout
      session={session}
      activeScreen="settings"
      activeProject={activeProject ?? projects[0] ?? null}
      breadcrumbs={["Personal Settings", tabTitle]}
      onNavigate={(screen) => onNavigate(screen, activeProject ?? projects[0])}
      onLogout={onLogout}
    >
      <section className="settings-content">
        <div className="dashboard-title">
          <div>
            <h1>Personal Settings</h1>
            <p>Manage your API access, glossary and system logs.</p>
          </div>
        </div>

        <div className="settings-tabs">
          <button
            className={tab === "api" ? "active" : ""}
            onClick={() => {
              setTab("api");
              setMessage("");
              setError("");
            }}
          >
            API Key Config
          </button>
          <button
            className={tab === "glossary" ? "active" : ""}
            onClick={() => {
              setTab("glossary");
              setMessage("");
              setError("");
            }}
          >
            Custom Glossary {glossary.length ? `(${glossary.length})` : ""}
          </button>
          <button
            className={tab === "logs" ? "active" : ""}
            onClick={() => {
              setTab("logs");
              setMessage("");
              setError("");
            }}
          >
            System Logs {logs.length ? `(${logs.length})` : ""}
          </button>
        </div>

        {error && <div className="dashboard-error">{error}</div>}
        {message && <div className="typesetting-message">{message}</div>}

        {!settings ? (
          <div className="dashboard-empty">Loading settings...</div>
        ) : tab === "api" ? (
          <ApiSettings settings={settings} userId={session.user.id} projects={projects} />
        ) : tab === "glossary" ? (
          <div className="settings-section">
            <div className="settings-section-heading">
              <div>
                <h2>Custom glossary</h2>
                <p>Enforced in every translation pass across your manga projects.</p>
              </div>
              <button
                className="create-project-button"
                onClick={() => setShowAdd((prev) => !prev)}
              >
                {showAdd ? "✕ Cancel" : "＋ Add term"}
              </button>
            </div>

            {showAdd && (
              <form className="glossary-form" onSubmit={(event) => void addTerm(event)}>
                <select
                  value={projectId}
                  onChange={(event) => setProjectId(event.target.value)}
                  required
                >
                  <option value="">Select project</option>
                  {projects.map((project) => (
                    <option key={project.id} value={project.id}>
                      {project.title}
                    </option>
                  ))}
                </select>
                <input
                  value={sourceTerm}
                  onChange={(event) => setSourceTerm(event.target.value)}
                  placeholder="Source term (e.g. 先生)"
                  required
                />
                <input
                  value={targetTerm}
                  onChange={(event) => setTargetTerm(event.target.value)}
                  placeholder="Vietnamese term (e.g. Tiên sinh)"
                  required
                />
                <button className="create-project-button" disabled={busy}>
                  {busy ? "Saving..." : "Save term"}
                </button>
              </form>
            )}

            <div className="glossary-filter-bar">
              <div className="glossary-search-box">
                <AppIcon name="search" />
                <input
                  value={glossarySearch}
                  onChange={(event) => setGlossarySearch(event.target.value)}
                  placeholder="Search source or localized term..."
                />
              </div>
              <select
                value={glossaryFilterProject}
                onChange={(event) => setGlossaryFilterProject(event.target.value)}
                aria-label="Filter glossary by project"
              >
                <option value="all">All Projects ({glossary.length})</option>
                {projects.map((project) => (
                  <option key={project.id} value={String(project.id)}>
                    {project.title}
                  </option>
                ))}
              </select>
            </div>

            {filteredGlossary.length ? (
              <div className="glossary-list">
                {filteredGlossary.map((item) => {
                  const isEditing = editingGlossaryId === item.id;
                  const projTitle =
                    item.project_title || projectMap.get(item.project_id) || `Project #${item.project_id}`;
                  return (
                    <div className="glossary-row" key={item.id}>
                      <span className="glossary-project-chip">{projTitle}</span>
                      {isEditing ? (
                        <>
                          <input
                            className="glossary-inline-input"
                            value={editSource}
                            onChange={(e) => setEditSource(e.target.value)}
                            placeholder="Source term"
                          />
                          <b>→</b>
                          <input
                            className="glossary-inline-input"
                            value={editTarget}
                            onChange={(e) => setEditTarget(e.target.value)}
                            placeholder="Localized term"
                          />
                          <div className="glossary-row-actions">
                            <button
                              type="button"
                              className="glossary-action-btn save"
                              disabled={busy || !editSource.trim() || !editTarget.trim()}
                              onClick={() => void saveEditGlossary(item.id)}
                            >
                              Save
                            </button>
                            <button
                              type="button"
                              className="glossary-action-btn"
                              onClick={() => setEditingGlossaryId(null)}
                            >
                              Cancel
                            </button>
                          </div>
                        </>
                      ) : (
                        <>
                          <span className="glossary-source-term">{item.source_term}</span>
                          <b>→</b>
                          <strong className="glossary-target-term">{item.target_term}</strong>
                          <div className="glossary-row-actions">
                            <button
                              type="button"
                              className="glossary-action-btn"
                              onClick={() => startEditGlossary(item)}
                            >
                              Edit
                            </button>
                            <button
                              type="button"
                              className="delete-bubble-button"
                              disabled={busy}
                              onClick={() => void handleDeleteGlossary(item)}
                            >
                              <AppIcon name="trash" /> Delete
                            </button>
                          </div>
                        </>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="dashboard-empty">
                {glossary.length
                  ? "No glossary terms match your current search or project filter."
                  : "No glossary terms configured yet."}
              </div>
            )}
          </div>
        ) : (
          <div className="settings-section">
            <div className="settings-section-heading">
              <div>
                <h2>System logs</h2>
                <p>Errors, warnings and pipeline execution events persisted in SQLite.</p>
              </div>
              <div className="logs-toolbar-actions">
                <select
                  value={logFilterProject}
                  onChange={(e) => setLogFilterProject(e.target.value)}
                  aria-label="Filter logs by project"
                >
                  <option value="all">All Projects</option>
                  {projects.map((project) => (
                    <option key={project.id} value={String(project.id)}>
                      {project.title}
                    </option>
                  ))}
                </select>
                <select
                  value={logFilterLevel}
                  onChange={(e) => setLogFilterLevel(e.target.value)}
                  aria-label="Filter logs by level"
                >
                  <option value="ALL">All Levels</option>
                  <option value="INFO">INFO</option>
                  <option value="WARNING">WARNING</option>
                  <option value="ERROR">ERROR</option>
                </select>
                <button
                  type="button"
                  className="danger-button"
                  disabled={busy || logs.length === 0}
                  onClick={() => void handleClearLogs()}
                >
                  <AppIcon name="trash" /> Clear logs
                </button>
              </div>
            </div>
            <div className="settings-terminal">
              {logs.length ? (
                logs.map((log) => (
                  <div key={log.id}>
                    <time>
                      {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : "--:--:--"}
                    </time>
                    <b className={log.level.toLowerCase()}>{log.level}</b>
                    <span>
                      {log.project_title ? `[${log.project_title}] ` : ""}
                      {log.message}
                    </span>
                  </div>
                ))
              ) : (
                <div>No system logs available.</div>
              )}
            </div>
          </div>
        )}
      </section>
    </AppLayout>
  );
}

export function ApiSettings({
  settings,
  userId,
  projects,
}: {
  settings: SettingsSnapshot;
  userId: string;
  projects: ProjectSummary[];
}) {
  const [projectId, setProjectId] = useState(projects[0]?.id ?? 0);
  const [apiKey, setApiKey] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    if (!projectId && projects[0]) setProjectId(projects[0].id);
  }, [projectId, projects]);

  const save = async () => {
    if (!projectId || !apiKey.trim()) return;
    try {
      await saveApiKey(userId, projectId, apiKey);
      setApiKey("");
      setMessage("API key saved securely.");
      setError("");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to save API key.");
    }
  };

  const test = async () => {
    if (!projectId || (!apiKey.trim() && !settings.providers.gemini)) return;
    setTesting(true);
    setError("");
    setMessage("");
    try {
      const result = apiKey.trim()
        ? await testApiKey(projectId, apiKey)
        : await testSavedApiKey(userId, projectId);
      setMessage(result.message);
    } catch (requestError) {
      setError(
        requestError instanceof Error ? requestError.message : "Gemini connection failed.",
      );
    } finally {
      setTesting(false);
    }
  };

  const quota = settings.quota_usage ?? {
    requests_this_month: 0,
    monthly_limit: 500,
    usage_percent: 0,
    translated_bubbles: 0,
    completed_pages: 0,
    glossary_terms: 0,
  };

  return (
    <>
      <div className="settings-card api-card">
        <h2>Cloud LLM API key</h2>
        <p>Used by the translation client. Stored server-side and never exposed to the frontend.</p>
        <label>
          Project
          <select value={projectId} onChange={(event) => setProjectId(Number(event.target.value))}>
            <option value={0}>Select project</option>
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.title}
              </option>
            ))}
          </select>
        </label>
        <label>
          Provider
          <select defaultValue="gemini">
            <option value="gemini">● Gemini (Google DeepMind)</option>
          </select>
        </label>
        <label>
          API key
          <input
            type="password"
            value={apiKey}
            onChange={(event) => setApiKey(event.target.value)}
            placeholder={
              settings.providers.gemini
                ? "Enter a new key to replace the current key"
                : "Paste Gemini API key"
            }
          />
          <small>Saved encrypted on the server and used by new pipeline tasks.</small>
        </label>
        {(error || message) && (
          <div className={error ? "dashboard-error" : "typesetting-message"}>
            {error || message}
          </div>
        )}
        <div className="api-actions">
          <span className={settings.providers.gemini ? "configured" : "missing"}>
            ● {settings.providers.gemini ? "Configured" : "Not configured"}
          </span>
          <button disabled={!projectId || !apiKey.trim()} onClick={() => void save()}>
            Save key
          </button>
          <button
            disabled={!projectId || (!apiKey.trim() && !settings.providers.gemini) || testing}
            onClick={() => void test()}
          >
            {testing ? "Testing..." : "Test Connection"}
          </button>
        </div>
      </div>

      <div className="settings-card quota-card">
        <h2>Quota &amp; usage</h2>
        <p>Current billing cycle consumption across all accessible projects and chapter batches.</p>
        <div className="quota-line">
          <span>Requests &amp; bubbles processed</span>
          <b>
            {quota.requests_this_month} / {quota.monthly_limit} ({quota.usage_percent}%)
          </b>
        </div>
        <div className="quota-track">
          <i style={{ width: `${quota.usage_percent}%` }} />
        </div>
        <div className="quota-metrics-grid">
          <div>
            <span>Translated Bubbles</span>
            <strong>{quota.translated_bubbles}</strong>
          </div>
          <div>
            <span>Completed Pages</span>
            <strong>{quota.completed_pages}</strong>
          </div>
          <div>
            <span>Glossary Terms</span>
            <strong>{quota.glossary_terms}</strong>
          </div>
        </div>
        <small>
          Calculated live from SQLite translation regions, completed pages and pipeline tasks.
        </small>
      </div>
    </>
  );
}

export function CreateProjectModal({
  userId,
  project,
  onClose,
  onCreated,
}: {
  userId: string;
  project?: ProjectSummary;
  onClose: () => void;
  onCreated: (project: ProjectSummary) => void;
}) {
  const isEdit = Boolean(project);
  const [title, setTitle] = useState(project?.title ?? "");
  const [description, setDescription] = useState(project?.description ?? "");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      onCreated(
        project
          ? await updateProject(project.id, title, description, userId)
          : await createProject(userId, title, description),
      );
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : isEdit
            ? "Unable to update project."
            : "Unable to create project.",
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="modal-backdrop" onMouseDown={onClose}>
      <form
        className="project-modal"
        onSubmit={(event) => void submit(event)}
        onMouseDown={(event) => event.stopPropagation()}
      >
        <button type="button" className="modal-close" onClick={onClose}>
          ×
        </button>
        <h2>{isEdit ? "Edit Project" : "Create New Project"}</h2>
        <p>
          {isEdit
            ? "Update the name and description of this project."
            : "Set up a new comic series or chapter bundle for your localization team."}
        </p>
        {error && <div className="dashboard-error">{error}</div>}
        <label>Project / Series Name *</label>
        <input value={title} onChange={(event) => setTitle(event.target.value)} required />
        <label>
          Description <small>(optional)</small>
        </label>
        <textarea
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          rows={3}
        />
        <div className="language-row">
          <div>
            <label>Source Language</label>
            <select defaultValue="Japanese">
              <option>Japanese (Raw Manga)</option>
              <option>English</option>
            </select>
          </div>
          <div>
            <label>Target Language</label>
            <select defaultValue="Vietnamese">
              <option>Vietnamese</option>
            </select>
          </div>
        </div>
        <div className="pipeline-note">
          Default pipeline: YOLOv8 Text Detection → MangaOCR → LaMa Inpainting → Cloud LLM
          Translation.
        </div>
        <div className="modal-footer">
          <button type="button" onClick={onClose}>
            Cancel
          </button>
          <button className="create-project-button" disabled={busy}>
            {busy ? (isEdit ? "Saving..." : "Creating...") : isEdit ? "Save Changes" : "Create Project"}
          </button>
        </div>
      </form>
    </div>
  );
}
