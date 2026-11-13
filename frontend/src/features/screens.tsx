import { FormEvent, PointerEvent, useEffect, useMemo, useRef, useState } from "react";
import { createBubble, createChapter, createGlossary, createProject, deleteBubble, deleteChapter, deleteProjectData, getChapter, getGlossary, getProjectMembers, getProjectQueue, getProjects, getProjectChapters, getSettings, getSettingsLogs, inviteProjectMember, login, register, requestPasswordReset, rerunPageOcr, restoreBubble, saveApiKey, startProjectQueue, testApiKey, testSavedApiKey, translatePage, typesetPage, updateBubble, uploadPage } from "../api";
import type { ChapterSummary, GlossaryTerm, ProjectSummary, QueueSnapshot, SettingsSnapshot, SystemLogEntry, TeamMember } from "../api";
import { ReviewCanvas } from "../components/ReviewCanvas";
import { AppIcon } from "../components/AppIcon";
import { UserMenu } from "../components/UserMenu";
import { useStudioStore } from "../store";
import type { Region } from "../types";
import type { AuthSession } from "./auth/AuthScreen";

const API_ORIGIN = import.meta.env.VITE_API_ORIGIN ?? "";
export function WorkspaceScreen({ session, onOpenTeam, onOpenChapter, onOpenQueue, onOpenReview, onOpenTypesetting, onOpenSettings, onLogout }: { session: AuthSession; onOpenTeam: (project: ProjectSummary) => void; onOpenChapter: (project: ProjectSummary) => void; onOpenQueue: (project: ProjectSummary) => void; onOpenReview: (project: ProjectSummary) => void; onOpenTypesetting: (project: ProjectSummary) => void; onOpenSettings: () => void; onLogout: () => void }) {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");

  const loadProjects = async () => {
    setLoading(true);
    try {
      setProjects(await getProjects(session.user.id));
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
      [project.title, project.description, String(project.id)]
        .some((value) => (value ?? "").toLowerCase().includes(normalized))
    );
  }, [projects, query]);

  return <div className="dashboard-page">
    <aside className="dashboard-sidebar">
      <div>
        <div className="dashboard-brand"><span>A</span><strong>ACL</strong><small>v2.4 Editorial Core</small></div>
        <nav className="dashboard-nav">
          <button>▦　Dashboard</button><button className="active">▱　Projects</button><button onClick={() => projects[0] && onOpenChapter(projects[0])}>♧　Chapter Studio</button><button onClick={() => projects[0] && onOpenReview(projects[0])}>◈　Review Studio</button><button onClick={() => projects[0] && onOpenTypesetting(projects[0])}>⌁　Typesetting</button><button onClick={() => projects[0] && onOpenQueue(projects[0])}>▤　Queue Monitor</button><button onClick={onOpenSettings}>☷　Personal Settings</button>
        </nav>
      </div>
      <div className="dashboard-sidebar-bottom"><span>ⓘ　Documentation</span><div>● Core　• Online</div></div>
    </aside>
    <main className="dashboard-main">
      <header className="dashboard-header"><div><strong>ACL Studio</strong><span>/</span><b>Projects</b></div><div className="dashboard-actions"><label className="project-search"><AppIcon name="search" /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Filter batches or series..." aria-label="Filter projects" /></label><span className="gpu-pill">● Node Tokyo-01 (GPU idle)</span><UserMenu user={session.user} onLogout={onLogout} /></div></header>
      <section className="dashboard-content">
        <div className="dashboard-title"><div><h1>Projects</h1><p>Manage your ongoing comic localization series and translation pipelines.</p></div><button className="create-project-button" onClick={() => setShowCreate(true)}>＋ Create New Project</button></div>
        {error && <div className="dashboard-error">{error}</div>}
        {loading ? <div className="dashboard-empty">Loading projects...</div> : projects.length === 0 ? <div className="dashboard-empty"><h2>No projects yet</h2><p>Create a project to start localizing your first comic series.</p><button className="create-project-button" onClick={() => setShowCreate(true)}>Create New Project</button></div> : visibleProjects.length === 0 ? <div className="dashboard-empty"><h2>No matching projects</h2><p>Try another project name, description, or ID.</p></div> : <div className="project-grid">{visibleProjects.map((project) => <ProjectCard key={project.id} project={project} onOpen={() => onOpenChapter(project)} onTeam={() => onOpenTeam(project)} onQueue={() => onOpenQueue(project)} onReview={() => onOpenReview(project)} onTypesetting={() => onOpenTypesetting(project)} />)}</div>}
        {projects.length > 0 && <div className="kpi-grid"><Kpi label="Active Projects" value={String(projects.length)} detail="" /><Kpi label="In Queue" value={String(projects.reduce((sum, project) => sum + project.total_pages - project.completed_pages, 0))} detail="pages pending OCR" /><Kpi label="Storage Allocation" value="" detail="" /></div>}
      </section>
    </main>
    {showCreate && <CreateProjectModal userId={session.user.id} onClose={() => setShowCreate(false)} onCreated={(project) => { setProjects((current) => [project, ...current]); setShowCreate(false); }} />}
  </div>;
}


export function ProjectCard({ project, onOpen, onTeam, onQueue, onReview, onTypesetting }: { project: ProjectSummary; onOpen: () => void; onTeam: () => void; onQueue: () => void; onReview: () => void; onTypesetting: () => void }) {
  return <article className="project-card"><div className="project-card-title"><h3>{project.title}</h3><span>#{String(project.id).padStart(2, "0")}</span></div><p>{project.total_pages} pages • Japanese → Vietnamese</p><div className="project-status">● {project.completed_pages === project.total_pages && project.total_pages > 0 ? "Completed" : project.completed_pages > 0 ? "In review" : "Not started"}</div><div className="progress-label"><span>Progress: {project.completed_pages}/{project.total_pages} Pages</span><span>{project.progress_percent}%</span></div><div className="progress-track"><i style={{ width: `${project.progress_percent}%` }} /></div><p className="project-description">{project.description || "No project description."}</p><div className="project-card-actions"><button className="project-open-button" onClick={onOpen}>Open Project</button><details className="project-actions-menu"><summary aria-label={`More actions for ${project.title}`}><AppIcon name="more" /></summary><div><button onClick={onTeam}><AppIcon name="users" /> Team</button><button onClick={onQueue}><AppIcon name="queue" /> Queue</button><button onClick={onReview}><AppIcon name="review" /> Review</button><button onClick={onTypesetting}><AppIcon name="typesetting" /> Typeset</button></div></details></div></article>;
}


export function ReviewScreen({ session, project, onBack, onOpenQueue, onOpenTypesetting, onLogout }: { session: AuthSession; project: ProjectSummary; onBack: () => void; onOpenQueue: () => void; onOpenTypesetting: () => void; onLogout: () => void }) {
  const [chapters, setChapters] = useState<ChapterSummary[]>([]);
  const [chapterId, setChapterId] = useState<number | null>(null);
  const [chapter, setChapter] = useState<import("../types").Chapter | null>(null);
  const [pageIndex, setPageIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [imageSize, setImageSize] = useState({ width: 0, height: 0 });
  const [deletedBubble, setDeletedBubble] = useState<(Region & { page_id: number }) | null>(null);
  const [drawMode, setDrawMode] = useState(false);
  const [drawStart, setDrawStart] = useState<{ x: number; y: number } | null>(null);
  const [drawBox, setDrawBox] = useState<{ x: number; y: number; width: number; height: number } | null>(null);
  const [boxInteraction, setBoxInteraction] = useState<{ regionId: number; mode: "move" | "resize"; start: { x: number; y: number }; bbox: Region["bbox"] } | null>(null);
  useEffect(() => { void getProjectChapters(project.id).then((items) => { setChapters(items); setChapterId(items[0]?.id ?? null); }).catch((requestError) => setError(requestError instanceof Error ? requestError.message : "Unable to load chapters.")); }, []);
  useEffect(() => { if (!chapterId) { setLoading(false); return; } setLoading(true); void getChapter(chapterId).then(setChapter).catch((requestError) => setError(requestError instanceof Error ? requestError.message : "Unable to load page.")).finally(() => setLoading(false)); }, [chapterId]);
  const page = chapter?.pages[pageIndex] ?? null;
  const imageUrl = page?.original_url ?? null;
  useEffect(() => { setImageSize({ width: 0, height: 0 }); }, [imageUrl]);
  const updateOriginal = (regionId: number, text: string) => { if (!chapter || !page) return; setChapter({ ...chapter, pages: chapter.pages.map((item) => item.id === page.id ? { ...item, regions: item.regions.map((region) => region.id === regionId ? { ...region, original_text: text } : region) } : item) }); };
  const rerunOcr = async () => {
    if (!page) return;
    setSaving(true); setError(""); setMessage("");
    try {
      const updated = await rerunPageOcr(page.id);
      setChapter((current) => current ? { ...current, pages: current.pages.map((item) => item.id === updated.id ? updated : item) } : current);
      setMessage("OCR completed. Review the detected text before translating.");
    } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Unable to re-run OCR."); } finally { setSaving(false); }
  };
  const saveAndTranslate = async () => {
    if (!page) return;
    setSaving(true); setError(""); setMessage("");
    try {
      const editedText = Object.fromEntries(page.regions.filter((region) => region.original_text.trim()).map((region) => [region.id, region.original_text]));
      const updated = await translatePage(page.id, editedText);
      setChapter((current) => current ? { ...current, pages: current.pages.map((item) => item.id === updated.id ? updated : item) } : current);
      setMessage("Translation and rendering complete. Proceed to Typesetting to review the final page.");
    } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Unable to translate the reviewed OCR text."); } finally { setSaving(false); }
  };
  const addBubble = async (coordinates: [number, number, number, number]) => {
    if (!page) return;
    try {
      const region = await createBubble(page.id, coordinates as [number, number, number, number]);
      setChapter((current) => current ? { ...current, pages: current.pages.map((item) => item.id === page.id ? { ...item, regions: [...item.regions, region] } : item) } : current);
    } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Unable to add bubble."); }
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
    const x1 = Math.round(Math.min(drawStart.x, point.x) * imageSize.width / bounds.width);
    const y1 = Math.round(Math.min(drawStart.y, point.y) * imageSize.height / bounds.height);
    const x2 = Math.round(Math.max(drawStart.x, point.x) * imageSize.width / bounds.width);
    const y2 = Math.round(Math.max(drawStart.y, point.y) * imageSize.height / bounds.height);
    setDrawMode(false);
    await addBubble([x1, y1, x2, y2]);
  };
  const getImagePoint = (event: PointerEvent<HTMLElement>) => {
    const image = event.currentTarget.closest(".review-image-wrap")?.querySelector("img");
    if (!image) return null;
    const bounds = image.getBoundingClientRect();
    return {
      x: Math.max(0, Math.min(imageSize.width, (event.clientX - bounds.left) * imageSize.width / bounds.width)),
      y: Math.max(0, Math.min(imageSize.height, (event.clientY - bounds.top) * imageSize.height / bounds.height)),
    };
  };
  const updateLocalBbox = (regionId: number, bbox: Region["bbox"]) => {
    setChapter((current) => current ? { ...current, pages: current.pages.map((item) => item.id === page?.id ? { ...item, regions: item.regions.map((region) => region.id === regionId ? { ...region, bbox } : region) } : item) } : current);
  };
  const handleBoxStart = (event: PointerEvent<HTMLElement>, region: Region, mode: "move" | "resize") => {
    if (drawMode || !imageSize.width || !imageSize.height) return;
    event.stopPropagation();
    event.preventDefault();
    const point = getImagePoint(event);
    if (!point) return;
    event.currentTarget.setPointerCapture(event.pointerId);
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
    const width = x2 - x1;
    const height = y2 - y1;
    const bbox: Region["bbox"] = boxInteraction.mode === "move"
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
    const nextBbox: Region["bbox"] = boxInteraction.mode === "move"
      ? [Math.max(0, Math.min(imageSize.width - (x2 - x1), Math.round(x1 + dx))), Math.max(0, Math.min(imageSize.height - (y2 - y1), Math.round(y1 + dy))), Math.max(x2 - x1, Math.min(imageSize.width, Math.round(x2 + dx))), Math.max(y2 - y1, Math.min(imageSize.height, Math.round(y2 + dy)))]
      : [x1, y1, Math.max(x1 + 4, Math.min(imageSize.width, Math.round(point.x))), Math.max(y1 + 4, Math.min(imageSize.height, Math.round(point.y)))];
    try {
      await updateBubble(region.id, { bbox: nextBbox });
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to save bubble position.");
    }
  };
  const removeBubble = async (regionId: number) => {
    if (!window.confirm("Delete this text bubble?")) return;
    if (!page) return;
    const pageId = page.id;
    try {
      const deleted = await deleteBubble(regionId);
      setDeletedBubble({ ...deleted.region, page_id: pageId });
      setChapter((current) => current ? { ...current, pages: current.pages.map((item) => item.id === pageId ? { ...item, regions: item.regions.filter((region) => region.id !== regionId) } : item) } : current);
    } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Unable to delete bubble."); }
  };
  const undoDelete = async () => {
    if (!deletedBubble) return;
    try {
      const restored = await restoreBubble(deletedBubble);
      const pageId = deletedBubble.page_id;
      setChapter((current) => current ? { ...current, pages: current.pages.map((item) => item.id === pageId ? { ...item, regions: [...item.regions, restored].sort((a, b) => a.id - b.id) } : item) } : current);
      setDeletedBubble(null);
    } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Unable to undo bubble deletion."); }
  };
  return <div className="dashboard-page"><aside className="dashboard-sidebar"><div><div className="dashboard-brand"><span>A</span><strong>ACL</strong><small>v2.4 Editorial Core</small></div><nav className="dashboard-nav"><button onClick={onBack}>▦　Dashboard</button><button onClick={onBack}>▱　Projects</button><button onClick={onBack}>♧　Chapter Studio</button><button className="active">◈　Review Studio</button><button onClick={onOpenTypesetting}>⌁　Typesetting</button><button onClick={onOpenQueue}>▤　Queue Monitor</button><button onClick={onBack}>☷　Personal Settings</button></nav></div><div className="dashboard-sidebar-bottom"><span>ⓘ　Documentation</span><div>● Core　• Online</div></div></aside><main className="dashboard-main"><header className="dashboard-header"><div><strong>ACL Studio</strong><span>/</span><b>Review Studio</b></div><div className="dashboard-actions"><UserMenu user={session.user} onLogout={onLogout} /></div></header>  <section className="review-content">{deletedBubble && <div className="undo-bubble-banner">Bubble #{deletedBubble.id} deleted. <button onClick={() => void undoDelete()}>Undo</button></div>}<div className="dashboard-title"><div><h1>Interactive Review Studio</h1><p>{project.title} — OCR verification and text correction</p></div><select value={chapterId ?? ""} onChange={(event) => { setChapterId(Number(event.target.value)); setPageIndex(0); }}>{chapters.length ? chapters.map((item) => <option key={item.id} value={item.id}>{item.chapter_name}</option>) : <option value="">No chapters</option>}</select></div>{error &&   <div className="dashboard-error">{error}</div>}{message && <div className="typesetting-message">{message} <button onClick={onOpenTypesetting}>Go to Typesetting →</button></div>}{loading ? <div className="dashboard-empty">Loading OCR data...</div> : !page ? <div className="dashboard-empty"><h2>No OCR pages yet</h2><p>Upload and process chapter pages before reviewing OCR.</p></div> : <><div className="review-toolbar"><button disabled={pageIndex === 0} onClick={() => setPageIndex((index) => index - 1)}>← Prev Page</button><span>Page {pageIndex + 1} of {chapter?.pages.length}</span><button disabled={pageIndex >= (chapter?.pages.length ?? 1) - 1} onClick={() => setPageIndex((index) => index + 1)}>Next Page →</button>  <button className={drawMode ? "draw-bubble-active" : ""} onClick={() => { setDrawMode((current) => !current); setDrawStart(null); setDrawBox(null); }}>{drawMode ? "✕ Cancel drawing" : "＋ Draw bubble"}</button></div><div className="review-grid"><div className="review-image-panel"><h2>Original Page — Detection Preview</h2>  <div className={`review-image-wrap ${drawMode ? "draw-mode" : ""}`} onPointerDown={handleDrawStart} onPointerMove={handleDrawMove} onPointerUp={(event) => void handleDrawEnd(event)} onPointerCancel={() => { setDrawStart(null); setDrawBox(null); }}><img draggable={false} style={{ pointerEvents: drawMode ? "none" : "auto" }} src={`${API_ORIGIN}${page.original_url}`} alt={page.page_number.toString()} onLoad={(event) => setImageSize({ width: event.currentTarget.naturalWidth, height: event.currentTarget.naturalHeight })} />{imageSize.width > 0 && page.regions.map((region, index) => { const [x, y, x2, y2] = region.bbox; return   <div className={`bbox ${region.original_text ? "" : "low-confidence"}`} key={region.id} onPointerDown={(event) => handleBoxStart(event, region, "move")} onPointerMove={handleBoxMove} onPointerUp={(event) => void handleBoxEnd(event)} style={{ left: `${x / imageSize.width * 100}%`, top: `${y / imageSize.height * 100}%`, width: `${(x2 - x) / imageSize.width * 100}%`, height: `${(y2 - y) / imageSize.height * 100}%`, pointerEvents: drawMode ? "none" : "auto" }}>  <b>{region.id}</b><i className="bbox-resize-handle" onPointerDown={(event) => handleBoxStart(event, region, "resize")} /></div>; })}{drawBox && <div className="draw-bubble-preview" style={{ left: `${drawBox.x / (imageSize.width / 100)}%`, top: `${drawBox.y / (imageSize.height / 100)}%`, width: `${drawBox.width / (imageSize.width / 100)}%`, height: `${drawBox.height / (imageSize.height / 100)}%` }} />}</div></div><div className="ocr-panel"><div className="ocr-panel-title"><h2>Extracted Text (Manga OCR)</h2><button disabled={saving} onClick={() => void rerunOcr()}><AppIcon name="refresh" /> Re-run OCR</button></div>{page.regions.map((region, index) => <div className={`ocr-card ${!region.original_text ? "low-confidence" : ""}`} key={region.id}><div>  <b>Bubble #{region.id}　Text Region</b><small>Box: [{region.bbox.join(", ")}] <button className="delete-bubble-button" aria-label={`Delete bubble ${region.id}`} onClick={() => void removeBubble(region.id)}><AppIcon name="trash" /> Delete</button></small></div><textarea value={region.original_text} onChange={(event) => updateOriginal(region.id, event.target.value)} /><span>{region.original_text ? "Verified OCR text" : "Needs transcription"}</span></div>)}<button className="create-project-button review-save" disabled={saving} onClick={() => void saveAndTranslate()}>{saving ? "Translating & Rendering... (30-60s)" : "Save OCR & Re-Translate →"}</button></div></div></>}</section></main></div>;
}


export function TypesettingScreen({ session, project, onBack, onOpenReview, onOpenQueue, onLogout }: { session: AuthSession; project: ProjectSummary; onBack: () => void; onOpenReview: () => void; onOpenQueue: () => void; onLogout: () => void }) {
  const [chapters, setChapters] = useState<ChapterSummary[]>([]);
  const [chapterId, setChapterId] = useState<number | null>(null);
  const [chapter, setChapter] = useState<import("../types").Chapter | null>(null);
  const [pageIndex, setPageIndex] = useState(0);
  const [regionId, setRegionId] = useState<number | null>(null);
  const [text, setText] = useState("");
  const [fontSize, setFontSize] = useState(24);
  const [compareOriginal, setCompareOriginal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [imageSize, setImageSize] = useState({ width: 0, height: 0 });

  useEffect(() => { void getProjectChapters(project.id).then((items) => { setChapters(items); setChapterId(items[0]?.id ?? null); }).catch((requestError) => setError(requestError instanceof Error ? requestError.message : "Unable to load chapters.")); }, []);
  useEffect(() => { if (!chapterId) { setLoading(false); return; } setLoading(true); void getChapter(chapterId).then((loaded) => { setChapter(loaded); setPageIndex(0); }).catch((requestError) => setError(requestError instanceof Error ? requestError.message : "Unable to load chapter.")).finally(() => setLoading(false)); }, [chapterId]);
  const page = chapter?.pages[pageIndex] ?? null;
  const selectedRegion = page?.regions.find((region) => region.id === regionId) ?? page?.regions[0] ?? null;
  useEffect(() => { const first = page?.regions[0]; setRegionId(first?.id ?? null); setText(first?.translated_text ?? ""); setFontSize(first?.font_size ?? 24); }, [page?.id]);
  const saveAndRender = async () => {
    if (!page || !selectedRegion) return;
    setSaving(true); setError(""); setMessage("");
    try {
      const updated = await typesetPage(page.id, selectedRegion.id, text, fontSize);
      setChapter((current) => current ? { ...current, pages: current.pages.map((item) => item.id === updated.id ? updated : item) } : current);
      setMessage("Translation saved and page re-rendered.");
    } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Unable to re-render page."); } finally { setSaving(false); }
  };
  const imageUrl = page ? (compareOriginal ? page.original_url : page.rendered_url ?? page.clean_url ?? page.original_url) : null;
  useEffect(() => { setImageSize({ width: 0, height: 0 }); }, [imageUrl]);
  return <div className="dashboard-page"><aside className="dashboard-sidebar"><div><div className="dashboard-brand"><span>A</span><strong>ACL</strong><small>v2.4 Editorial Core</small></div><nav className="dashboard-nav"><button onClick={onBack}>▦　Dashboard</button>  <button onClick={onBack}>▱　Projects</button><button onClick={onBack}>♧　Chapter Studio</button><button onClick={onOpenReview}>◈　Review Studio</button><button className="active">⌁　Typesetting</button><button onClick={onOpenQueue}>▤　Queue Monitor</button><button>☷　Personal Settings</button></nav></div><div className="dashboard-sidebar-bottom"><span>ⓘ　Documentation</span><div>● Core　• Online</div></div></aside><main className="dashboard-main"><header className="dashboard-header"><div><strong>ACL Studio</strong><span>/</span><b>Typesetting Studio</b></div><div className="dashboard-actions"><UserMenu user={session.user} onLogout={onLogout} /></div></header><section className="typesetting-content"><div className="dashboard-title"><div><h1>Typesetting Studio</h1><p>{project.title} — final Vietnamese layout and page rendering</p></div><select value={chapterId ?? ""} onChange={(event) => setChapterId(Number(event.target.value))}>{chapters.length ? chapters.map((item) => <option key={item.id} value={item.id}>{item.chapter_name}</option>) : <option value="">No chapters</option>}</select></div>{error && <div className="dashboard-error">{error}</div>}{message && <div className="typesetting-message">{message}</div>}{loading ? <div className="dashboard-empty">Loading typesetting data...</div> : !page ? <div className="dashboard-empty"><h2>No pages available</h2><p>Upload and process real chapter pages before typesetting.</p></div> : <><div className="typesetting-toolbar"><button disabled={pageIndex === 0} onClick={() => setPageIndex((index) => index - 1)}>← Previous</button><span>Page {pageIndex + 1} of {chapter?.pages.length}</span><button disabled={pageIndex >= (chapter?.pages.length ?? 1) - 1} onClick={() => setPageIndex((index) => index + 1)}>Next →</button><label><input type="checkbox" checked={compareOriginal} onChange={(event) => setCompareOriginal(event.target.checked)} /> Compare with Japanese original</label></div>  <div className="typesetting-grid">  <div className="typesetting-preview"><div className="typesetting-preview-heading"><h2>{compareOriginal ? "Japanese Original" : "Rendered Vietnamese Page"}</h2><span>{page.status}</span></div>{imageUrl ? <div className="typesetting-image-wrap"><img src={`${API_ORIGIN}${imageUrl}`} alt={`Page ${page.page_number}`} onLoad={(event) => setImageSize({ width: event.currentTarget.naturalWidth, height: event.currentTarget.naturalHeight })} />{imageSize.width > 0 && page.regions.map((region, index) => { const [x, y, x2, y2] = region.bbox; return <button className={`typesetting-bbox ${region.id === selectedRegion?.id ? "selected" : ""}`} key={region.id} aria-label={`Select bubble ${index + 1}`} onClick={() => { setRegionId(region.id); setText(region.translated_text); setFontSize(region.font_size ?? 24); }} style={{ left: `${x / imageSize.width * 100}%`, top: `${y / imageSize.height * 100}%`, width: `${(x2 - x) / imageSize.width * 100}%`, height: `${(y2 - y) / imageSize.height * 100}%` }}><b>{index + 1}</b></button>; })}</div> : <div className="dashboard-empty">No rendered image available.</div>}</div><aside className="typesetting-panel"><h2>Speech Bubble</h2><label className="field-label" htmlFor="bubble-select">Select region</label><select id="bubble-select" value={selectedRegion?.id ?? ""} onChange={(event) => { const next = page.regions.find((region) => region.id === Number(event.target.value));   setRegionId(next?.id ?? null); setText(next?.translated_text ?? ""); setFontSize(next?.font_size ?? 24); }}>{page.regions.map((region, index) =>   <option key={region.id} value={region.id}>Bubble {region.id}</option>)}</select>{selectedRegion ? <><div className="typesetting-source"><span>Original OCR</span><p>{selectedRegion.original_text || "No OCR text"}</p></div><label className="field-label" htmlFor="typeset-text">Vietnamese translation</label><textarea id="typeset-text" value={text} onChange={(event) => setText(event.target.value)} rows={8} placeholder="Enter translated dialogue..." /><label className="field-label" htmlFor="font-size">Font size</label>  <input id="font-size" type="number" min="8" max="120" value={fontSize} onChange={(event) => setFontSize(Number(event.target.value))} /><button className="create-project-button full-width" disabled={saving || !text.trim()} onClick={() => void saveAndRender()}>{saving ? "Rendering..." : "⚡ Save & Re-render Now"}</button></> : <p className="muted">No speech bubbles detected on this page.</p>}</aside></div></>}</section></main></div>;
}


export function QueueScreen({ session, project, onBack, onOpenReview, onOpenTypesetting, onLogout }: { session: AuthSession; project: ProjectSummary; onBack: () => void; onOpenReview: () => void; onOpenTypesetting: () => void; onLogout: () => void }) {
  const [queue, setQueue] = useState<QueueSnapshot | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const refresh = async () => { try { setQueue(await getProjectQueue(project.id)); setError(""); } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Unable to load queue."); } finally { setLoading(false); } };
  useEffect(() => { void refresh(); const timer = window.setInterval(() => void refresh(), 5000); return () => window.clearInterval(timer); }, []);
  const start = async () => { if (!queue?.chapter_id) return; try { setQueue(await startProjectQueue(project.id, queue.chapter_id)); } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Unable to start pipeline."); } };
  const percent = queue?.task?.progress_percent ?? (queue?.total_pages ? Math.round(queue.completed_pages / queue.total_pages * 100) : 0);
  const pagePercent = queue?.total_pages ? Math.round(queue.completed_pages / queue.total_pages * 100) : 0;
  const completed = Boolean(queue?.total_pages && queue.completed_pages === queue.total_pages);
  const taskRunning = queue?.task?.status === "RUNNING" || queue?.task?.status === "QUEUED";
  const taskStatus = queue?.task?.status ?? "NOT_STARTED";
  const downloadZip = () => { window.location.href = `/api/projects/${project.id}/queue/export`; };
  return <div className="dashboard-page"><aside className="dashboard-sidebar"><div><div className="dashboard-brand"><span>A</span><strong>ACL</strong><small>v2.4 Editorial Core</small></div><nav className="dashboard-nav"><button onClick={onBack}>▦　Dashboard</button><button onClick={onBack}>▱　Projects</button><button onClick={onBack}>♧　Chapter Studio</button><button className="active">▤　Queue Monitor</button><button onClick={onOpenReview}>◈　Review Studio</button><button onClick={onOpenTypesetting}>⌁　Typesetting</button><button onClick={onBack}>☷　Personal Settings</button></nav></div><div className="dashboard-sidebar-bottom"><span>ⓘ　Documentation</span><div>● Core　• Online</div></div></aside><main className="dashboard-main"><header className="dashboard-header"><div><strong>ACL Studio</strong><span>/</span><b>Queue Monitor</b></div><div className="dashboard-actions"><span className="gpu-pill">●　Node Tokyo-01 (GPU idle)</span><UserMenu user={session.user} onLogout={onLogout} /></div></header><section className="queue-content"><div className="dashboard-title"><div><h1>Queue Monitor</h1><p>{completed ? "All chapter tasks completed successfully." : "Real-time task tracking for the asynchronous pipeline."}</p></div><div className="queue-actions"><button onClick={() => void refresh()}>↻ Auto-refresh: 5s</button><button className="create-project-button" disabled={!queue?.chapter_id || taskRunning} onClick={() => void start()}>{taskRunning ? `● ${queue?.task?.status === "QUEUED" ? "Queued" : "Running"} ${queue?.task?.progress_percent ?? 0}%` : completed || taskStatus === "FAILED" ? "↻ Re-run Pipeline" : "▶ Run Pipeline"}</button>{completed && <button onClick={downloadZip}>⇩ Download Chapter (ZIP)</button>}</div>  </div>{error && <div className="dashboard-error">{error}</div>}{loading ? <div className="dashboard-empty">Loading queue...</div> : !queue || !queue.total_pages ? <div className="dashboard-empty"><h2>No queued pages</h2><p>Upload chapter pages first. Queue data will appear here when real pages exist.</p></div> : <><div className={completed ? "queue-complete" : "queue-hero"}>{completed && <div className="complete-icon">✿</div>}  <div><strong>{completed ? "Chapter Localization 100% Complete!" : `Active Chapter: ${project.title}`}</strong><p>{completed ? `All ${queue.total_pages} pages have been detected, cleaned, translated, and typeset.` : ""}</p><b>Task status: {taskStatus} · {queue.completed_pages} / {queue.total_pages} Pages Processed ({pagePercent}%)</b></div><div className="queue-progress"><i style={{ width: `${percent}%` }} /></div><div className="stage-line"><span>● Queued</span><span>→</span><span>● Detection</span><span>→</span><span>● OCR</span><span>→</span><span>● Review</span><span>→</span><span>○ Inpainting</span><span>→</span><span>○ Typesetting</span></div></div><div className="queue-stats"><Kpi label={completed ? "Total Pages Localized" : "Worker Node"} value={completed ? `${queue.total_pages} Pages` : "Node Tokyo-01"} detail={completed ? "100% Completion" : "GPU worker status from queue"} /><Kpi label={completed ? "Average Processing Time" : "Throughput"} value="—" detail="Unavailable from current queue data" /><Kpi label={completed ? "Translation Provider" : "Review Queue"} value={completed ? "Configured backend" : String(queue.pages.filter((page) => page.status === "REVIEW" || page.status === "AWAITING_REVIEW").length)} detail={completed ? "" : "Pages awaiting review"} /></div><div className="queue-matrix"><div className="queue-matrix-head"><h2>{completed ? "Completed Chapter Artifacts" : "Pipeline Task Execution Matrix"}</h2><span>{queue.total_pages} pages total</span></div>{queue.pages.map((page) => <div className="queue-row" key={page.id}><b>Page {String(page.page_number).padStart(3, "0")}</b><span>{page.filename}</span><strong>{completed ? "Typesetting Done" : page.status}</strong><em className={page.status === "FAILED" ? "failed" : page.status === "COMPLETED" ? "done" : ""}>{page.status === "COMPLETED" ? "✓ Completed" : page.status}</em></div>)}</div><div className="queue-log"><strong>▣ {completed ? "Terminal Execution Summary" : "Live Worker Stream"}</strong>{queue.logs.length ? queue.logs.map((log, index) => <div key={`${log.timestamp}-${index}`}>[{log.timestamp}] {log.level} {log.message}</div>) : <div>No worker logs yet.</div>}</div></>}</section></main></div>;
}


export function ChapterScreen({ session, project, onBack, onOpenQueue, onOpenReview, onOpenTypesetting, onLogout }: { session: AuthSession; project: ProjectSummary; onBack: () => void; onOpenQueue: () => void; onOpenReview: () => void; onOpenTypesetting: () => void; onLogout: () => void }) {
  const [chapter, setChapter] = useState<ChapterSummary | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const selectFiles = (selected: FileList | null) => { if (!selected) return; const valid = Array.from(selected).filter((file) => /\.(jpe?g|png|webp)$/i.test(file.name)); if (valid.length !== selected.length) setError("Only JPG, JPEG, PNG and WEBP files are supported."); setFiles((current) => [...current, ...valid]); };
  const createAndUpload = async () => { if (!files.length) return; setBusy(true); setError(""); const pendingFiles = [...files]; setFiles([]); onOpenQueue(); try { const nextChapter = chapter ?? await createChapter(project.id, `${project.title} — Chapter 1`); setChapter(nextChapter); await Promise.all(pendingFiles.map((file) => uploadPage(file, nextChapter.id))); await startProjectQueue(project.id, nextChapter.id); } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Upload or pipeline start failed."); } finally { setBusy(false); } };
  const removeChapter = async () => { if (!chapter || !window.confirm("Delete this chapter, its pages, OCR, translations and rendered files?")) return; setBusy(true); setError(""); try { await deleteChapter(project.id, chapter.id); setChapter(null); setMessage("Old chapter deleted. Upload new pages to create a clean chapter."); } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Unable to delete chapter."); } finally { setBusy(false); } };
  const clearProject = async () => { if (!window.confirm("Delete ALL old chapters, pages, OCR, translations, queue logs and rendered results in this project?")) return; setBusy(true); setError(""); try { await deleteProjectData(project.id); setChapter(null); setMessage("All old project data was deleted. Upload new pages to start clean."); } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Unable to clear project data."); } finally { setBusy(false); } };
  return <div className="dashboard-page"><aside className="dashboard-sidebar"><div><div className="dashboard-brand"><span>A</span><strong>ACL</strong><small>v2.4 Editorial Core</small></div><nav className="dashboard-nav"><button onClick={onBack}>▦　Dashboard</button><button onClick={onBack}>▱　Projects</button><button className="active">♧　Chapter Studio</button><button onClick={onOpenReview}>◈　Review Studio</button><button onClick={onOpenTypesetting}>⌁　Typesetting</button><button onClick={onOpenQueue}>▤　Queue Monitor</button><button onClick={onBack}>☷　Personal Settings</button></nav></div><div className="dashboard-sidebar-bottom"><span>ⓘ　Documentation</span><div>● Core　• Online</div></div></aside><main className="dashboard-main"><header className="dashboard-header"><div><strong>ACL Studio</strong><span>/</span><b>Projects</b><span>/</span><b>Chapter Studio</b></div><div className="dashboard-actions"><span className="gpu-pill">●　Node Tokyo-01 (GPU idle)</span><UserMenu user={session.user} onLogout={onLogout} /></div></header><section className="chapter-content"><div className="chapter-heading"><div><h1>Chapter Studio</h1><p>Upload chapter raw scans and configure AI pipeline execution.</p></div><div className="chapter-heading-actions"><span className="project-chip">▣　Project: {project.title}</span><button className="danger-button" disabled={busy} onClick={() => void clearProject()}>Clear old results</button>{chapter && <button className="danger-button" disabled={busy} onClick={() => void removeChapter()}>Delete chapter</button>}</div></div><label className="dropzone"><span className="upload-cloud">☁</span><strong>Drag &amp; drop comic pages here</strong><small>Accepts JPG, PNG batches up to 50 pages • 100MB per chapter</small><span className="browse-button">▣　Browse Files from Computer</span><input type="file" multiple accept=".jpg,.jpeg,.png,.webp" onChange={(event) => selectFiles(event.target.files)} /></label>{error && <div className="dashboard-error">{error}</div>}<div className="upload-list"><div className="upload-list-heading"><strong>◈ Uploaded Pages ({files.length} files ready)</strong><button onClick={() => setFiles([])}>Clear all</button></div>{files.length === 0 ? <div className="upload-empty">No files selected. Upload real comic pages to continue.</div> : files.map((file, index) => <div className="upload-row" key={`${file.name}-${index}`}><span>▣</span><strong>{file.name}</strong><small>({(file.size / 1024 / 1024).toFixed(1)} MB)</small><em>✓ Ready for detection</em></div>)}</div><div className="language-cards"><div>⚑　<strong>Source Language</strong><select defaultValue="Japanese"><option>Japanese (Raw Manga)</option><option>English</option></select><small>◉ Active Engine: MangaOCR</small></div><div>▣　<strong>Target Language</strong><select defaultValue="Vietnamese"><option>Vietnamese</option></select><small>↗ Translator: Gemini + Custom Glossary</small></div></div><div className="pipeline-bar"><div><strong>{message || (files.length ? `Ready to process ${files.length} page${files.length > 1 ? "s" : ""} in Asynchronous Queue` : "Ready when pages are uploaded")}</strong><small>Queue　› YOLOv8 Detection　› Manga OCR　› Waiting Review　› LaMa Inpainting　› Typesetting</small></div><button className="create-project-button" disabled={!files.length || busy} onClick={() => void createAndUpload()}>{busy ? "Uploading..." : "Start AI Pipeline　▶"}</button></div></section></main></div>;
}


export function TeamScreen({ session, project, onBack, onLogout }: { session: AuthSession; project: ProjectSummary; onBack: () => void; onLogout: () => void }) {
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("Translator");
  const emailInputRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const loadMembers = async () => { setLoading(true); try { setMembers(await getProjectMembers(project.id)); } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Unable to load members."); } finally { setLoading(false); } };
  useEffect(() => { void loadMembers(); }, []);
  const invite = async (event: FormEvent) => { event.preventDefault(); setBusy(true); setError(""); try { const member = await inviteProjectMember(project.id, email, role); setMembers((current) => [...current, member]); setEmail(""); } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Unable to invite member."); } finally { setBusy(false); } };
  return <div className="dashboard-page"><aside className="dashboard-sidebar"><div><div className="dashboard-brand"><span>A</span><strong>ACL</strong><small>v2.4 Editorial Core</small></div><nav className="dashboard-nav"><button onClick={onBack}>▦　Dashboard</button><button className="active">▱　Projects</button><button>♧　Chapter Studio</button><button>◈　Review Studio</button><button>⌁　Typesetting</button><button>▤　Queue Monitor</button><button>☷　Personal Settings</button></nav></div><div className="dashboard-sidebar-bottom"><span>ⓘ　Documentation</span><div>● Core　• Online</div></div></aside><main className="dashboard-main"><header className="dashboard-header"><div><strong>ACL Studio</strong><span>/</span><b>Projects</b><span>/</span><b>Team Workspace</b></div><div className="dashboard-actions"><span className="gpu-pill">●　Node Tokyo-01 (GPU idle)</span><UserMenu user={session.user} onLogout={onLogout} /></div></header><section className="team-content"><button className="back-projects" onClick={onBack}>← Back to Projects</button><div className="dashboard-title"><div><h1>Team Workspace &amp; Roles</h1><p>Assign roles and permissions for project: <strong>{project.title}</strong></p></div><button className="create-project-button" type="button" onClick={() => emailInputRef.current?.focus()}><AppIcon name="users" /> Invite Member</button></div><div className="team-summary"><div><span>Total Members</span><strong>{members.length}</strong><small>Active workspace members</small></div><div><span>Project Series</span><strong>{project.title}</strong><small>{project.total_pages} pages • Japanese → Vietnamese</small></div><div><span>Access Level</span><strong>Private Workspace</strong><small>Encrypted</small></div></div><form className="invite-bar" onSubmit={(event) => void invite(event)}><AppIcon name="mail" /><input ref={emailInputRef} value={email} onChange={(event) => setEmail(event.target.value)} placeholder="colleague@studio.com" type="email" required /><select value={role} onChange={(event) => setRole(event.target.value)}><option>Translator</option><option>Typesetter</option><option>Project Manager</option></select><button className="create-project-button" disabled={busy}>{busy ? "Sending..." : "Send Invite"}</button></form>{error && <div className="dashboard-error">{error}</div>}<div className="members-panel"><div className="members-heading"><h2>Workspace Members <small>{members.length}</small></h2></div>{loading ? <div className="dashboard-empty">Loading members...</div> : members.length === 0 ? <div className="dashboard-empty">No registered collaborators yet.</div> : <div className="member-list">{members.map((member) => <div className="member-row" key={member.user_id}><div className="member-identity"><span>{member.name.slice(0, 2).toUpperCase()}</span><div><strong>{member.name}</strong><small>{member.email}</small></div></div><b className={`role-${member.role.toLowerCase().replace(" ", "-")}`}>{member.role}</b><span>{member.is_owner ? "Overall Supervision" : "Assigned project tasks"}</span><small>{member.is_owner ? "Owner" : ""}</small></div>)}</div>}</div><div className="permissions-panel"><h2>ⓘ Role Permissions Guide</h2><div className="permission-grid"><div><b>Project Manager</b><p>Full pipeline control, team invites and role changes.</p></div><div><b>Translator</b><p>Review Studio access, OCR correction and translation.</p></div><div><b>Typesetter</b><p>Typesetting Studio access and bubble formatting.</p></div></div></div></section></main></div>;
}


export function Kpi({ label, value, detail }: { label: string; value: string; detail: string }) {
  return <div className="kpi-card"><span>{label}</span><strong>{value || "—"}</strong><small>{detail}</small></div>;
}


export function SettingsScreen({ session, onBack, onLogout }: { session: AuthSession; onBack: () => void; onLogout: () => void }) {
  const [settings, setSettings] = useState<SettingsSnapshot | null>(null);
  const [tab, setTab] = useState<"api" | "glossary" | "logs">("api");
  const [glossary, setGlossary] = useState<GlossaryTerm[]>([]);
  const [logs, setLogs] = useState<SystemLogEntry[]>([]);
  const [sourceTerm, setSourceTerm] = useState("");
  const [targetTerm, setTargetTerm] = useState("");
  const [projectId, setProjectId] = useState("");
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => { void getSettings(session.user.id).then(setSettings).catch((requestError) => setError(requestError instanceof Error ? requestError.message : "Unable to load settings.")); }, [session.user.id]);
  useEffect(() => { void getProjects(session.user.id).then(setProjects).catch((e) => setError(e instanceof Error ? e.message : "Unable to load projects.")); }, [session.user.id]);
  useEffect(() => { if (tab === "glossary") void getGlossary(session.user.id).then(setGlossary).catch((e) => setError(e instanceof Error ? e.message : "Unable to load glossary.")); if (tab === "logs") void getSettingsLogs(session.user.id).then(setLogs).catch((e) => setError(e instanceof Error ? e.message : "Unable to load logs.")); }, [tab, session.user.id]);
  const addTerm = async (event: FormEvent) => { event.preventDefault(); if (!projectId) return; try { const item = await createGlossary(session.user.id, Number(projectId), sourceTerm, targetTerm); setGlossary((items) => [item, ...items]); setSourceTerm(""); setTargetTerm(""); setShowAdd(false); } catch (e) { setError(e instanceof Error ? e.message : "Unable to save glossary term."); } };
  return <div className="dashboard-page"><aside className="dashboard-sidebar"><div><div className="dashboard-brand"><span>A</span><strong>ACL</strong><small>v2.4 Editorial</small></div><button className="new-pipeline">＋ New Pipeline</button><nav className="dashboard-nav"><button onClick={onBack}>▦　Projects</button><button>♧　Queue</button><button>⌁　Typesetting Studio</button><button>◈　Dual Inspector</button><button className="active">☷　Settings</button></nav></div><div className="dashboard-sidebar-bottom"><span>ⓘ　Documentation</span><div>● System Status</div></div></aside><main className="dashboard-main"><header className="dashboard-header"><div><strong>ACL Studio</strong><span>/</span><b>Personal Settings</b><span>/</span><b>{tab === "api" ? "API Key Config" : tab === "glossary" ? "Custom Glossary" : "System Logs"}</b></div><div className="dashboard-actions"><span className="gpu-pill">●　Node Tokyo-01 (GPU idle)</span><UserMenu user={session.user} onLogout={onLogout} /></div></header><section className="settings-content"><div className="dashboard-title"><div><h1>Personal Settings</h1><p>Manage your API access, glossary and system logs.</p></div></div><div className="settings-tabs"><button className={tab === "api" ? "active" : ""} onClick={() => setTab("api")}>API Key Config</button><button className={tab === "glossary" ? "active" : ""} onClick={() => setTab("glossary")}>Custom Glossary {glossary.length ? `(${glossary.length})` : ""}</button><button className={tab === "logs" ? "active" : ""} onClick={() => setTab("logs")}>System Logs {logs.length ? "•" : ""}</button></div>{error && <div className="dashboard-error">{error}</div>}{!settings ? <div className="dashboard-empty">Loading settings...</div>   : tab === "api" ? <ApiSettings settings={settings} userId={session.user.id} projects={projects} /> : tab === "glossary" ? <div className="settings-section"><div className="settings-section-heading"><div><h2>Custom glossary</h2><p>Enforced in every translation pass.</p></div><button className="create-project-button" onClick={() => setShowAdd(true)}>＋ Add term</button></div>{showAdd &&   <form className="glossary-form" onSubmit={(event) => void addTerm(event)}><select value={projectId} onChange={(event) => setProjectId(event.target.value)} required><option value="">Project</option>{projects.map((project) => <option key={project.id} value={project.id}>{project.title}</option>)}</select><input value={sourceTerm} onChange={(event) => setSourceTerm(event.target.value)} placeholder="Source term" required /><input value={targetTerm} onChange={(event) => setTargetTerm(event.target.value)} placeholder="Localized term" required /><button className="create-project-button">Save term</button></form>}{glossary.length ? <div className="glossary-list">{glossary.map((item) => <div className="glossary-row" key={item.id}><span>{item.source_term}</span><b>→</b><strong>{item.target_term}</strong></div>)}</div> : <div className="dashboard-empty">No glossary terms configured.</div>}</div> : <div className="settings-section"><div className="settings-section-heading"><div><h2>System logs</h2><p>Errors and warnings from queue jobs and pipeline workers.</p></div><button onClick={() => setLogs([])}>Clear view</button></div><div className="settings-terminal">{logs.length ? logs.map((log) => <div key={log.id}><time>{log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : "--:--:--"}</time><b className={log.level.toLowerCase()}>{log.level}</b><span>{log.message}</span></div>) : <div>No system logs available.</div>}</div></div>}</section></main></div>;
}


export function ApiSettings({ settings, userId, projects }: { settings: SettingsSnapshot; userId: string; projects: ProjectSummary[] }) {
  const [projectId, setProjectId] = useState(projects[0]?.id ?? 0);
  const [apiKey, setApiKey] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [testing, setTesting] = useState(false);
  useEffect(() => { if (!projectId && projects[0]) setProjectId(projects[0].id); }, [projectId, projects]);
  const save = async () => {
    if (!projectId || !apiKey.trim()) return;
    try { await saveApiKey(userId, projectId, apiKey); setApiKey(""); setMessage("API key saved securely."); setError(""); }
    catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Unable to save API key."); }
  };
  const test = async () => {
    if (!projectId || (!apiKey.trim() && !settings.providers.gemini)) return;
    setTesting(true); setError(""); setMessage("");
    try { const result = apiKey.trim() ? await testApiKey(projectId, apiKey) : await testSavedApiKey(userId, projectId); setMessage(result.message); }
    catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Gemini connection failed."); }
    finally { setTesting(false); }
  };
  return <><div className="settings-card api-card"><h2>Cloud LLM API key</h2><p>Used by the translation client. Stored server-side and never exposed to the frontend.</p><label>Project<select value={projectId} onChange={(event) => setProjectId(Number(event.target.value))}><option value={0}>Select project</option>{projects.map((project) => <option key={project.id} value={project.id}>{project.title}</option>)}</select></label><label>Provider<select defaultValue="gemini"><option value="gemini">◉ Gemini (Google DeepMind)</option></select></label><label>API key<input type="password" value={apiKey} onChange={(event) => setApiKey(event.target.value)} placeholder={settings.providers.gemini ? "Enter a new key to replace the current key" : "Paste Gemini API key"} /><small>Saved encrypted on the server and used by new pipeline tasks.</small></label>{(error || message) && <div className={error ? "dashboard-error" : "typesetting-message"}>{error || message}</div>}<div className="api-actions"><span className={settings.providers.gemini ? "configured" : "missing"}>● {settings.providers.gemini ? "Configured" : "Not configured"}</span><button disabled={!projectId || !apiKey.trim()} onClick={() => void save()}>Save key</button><button disabled={!projectId || (!apiKey.trim() && !settings.providers.gemini) || testing} onClick={() => void test()}>{testing ? "Testing..." : "⚙ Test Connection"}</button></div></div><div className="settings-card quota-card"><h2>Quota &amp; usage</h2><p>Current billing cycle token consumption across all chapter batches.</p><div className="quota-line"><span>Requests this month</span><b>—</b></div><div className="quota-track"><i style={{ width: "0%" }} /></div><small>No usage data available.</small></div></>;
}


export function CreateProjectModal({ userId, onClose, onCreated }: { userId: string; onClose: () => void; onCreated: (project: ProjectSummary) => void }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const submit = async (event: FormEvent) => {
    event.preventDefault(); setBusy(true); setError("");
    try { onCreated(await createProject(userId, title, description)); } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Unable to create project."); } finally { setBusy(false); }
  };
  return <div className="modal-backdrop" onMouseDown={onClose}><form className="project-modal" onSubmit={(event) => void submit(event)} onMouseDown={(event) => event.stopPropagation()}><button type="button" className="modal-close" onClick={onClose}>×</button><h2>Create New Project</h2><p>Set up a new comic series or chapter bundle for your localization team.</p>{error && <div className="dashboard-error">{error}</div>}<label>Project / Series Name *</label><input value={title} onChange={(event) => setTitle(event.target.value)} required /><label>Description <small>(optional)</small></label><textarea value={description} onChange={(event) => setDescription(event.target.value)} rows={3} /><div className="language-row"><div><label>Source Language</label><select defaultValue="Japanese"><option>Japanese (Raw Manga)</option><option>English</option></select></div><div><label>Target Language</label><select defaultValue="Vietnamese"><option>Vietnamese</option></select></div></div><div className="pipeline-note">ⓘ　Default pipeline: YOLOv8 Text Detection → MangaOCR → LaMa Inpainting → Cloud LLM Translation.</div><div className="modal-footer"><button type="button" onClick={onClose}>Cancel</button><button className="create-project-button" disabled={busy}>{busy ? "Creating..." : "⊕ Create Project"}</button></div></form></div>;
}
