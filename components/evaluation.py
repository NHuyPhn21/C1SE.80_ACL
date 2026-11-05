"""HTML renderer for the Queue Monitor accuracy evaluation panel."""

from html import escape

from models.evaluation import EvaluationResult, EvaluationStatus


def render_accuracy_panel(result: EvaluationResult) -> str:
    if result.status == EvaluationStatus.EMPTY:
        return _state_panel(
            icon="analytics",
            title="No evaluation result yet",
            message="Run an evaluation after the pipeline has produced validation artifacts.",
            action="Run Evaluation",
        )
    if result.status == EvaluationStatus.EVALUATING:
        return _state_panel(
            icon="progress_activity",
            title="Evaluating model accuracy",
            message=f"Processing {result.dataset_size} validation images and OCR transcripts.",
            action="Evaluation Running",
            loading=True,
        )
    if result.status == EvaluationStatus.FAILED:
        return _state_panel(
            icon="error",
            title="Evaluation failed",
            message=result.error_message or "Accuracy metrics are temporarily unavailable.",
            action="Retry Evaluation",
            error=True,
        )

    if result.yolo is None or result.ocr is None:
        return _state_panel(
            icon="warning",
            title="Incomplete evaluation response",
            message="The evaluation result is missing YOLO or OCR metrics.",
            action="Retry Evaluation",
            error=True,
        )

    yolo = result.yolo
    ocr = result.ocr
    class_rows = "".join(
        f"""
        <div class="grid grid-cols-[1.4fr_2fr_auto] items-center gap-3 py-2.5 border-b border-[#E4DFD6] last:border-0">
          <span class="text-xs font-semibold text-on-surface">{escape(metric.name)}</span>
          <div class="h-2 rounded-full bg-surface-container overflow-hidden">
            <div class="h-full rounded-full bg-primary-container" style="width:{_percent(metric.map50)}%"></div>
          </div>
          <span class="font-code text-xs font-bold text-primary-container">{_percent(metric.map50):.1f}%</span>
        </div>
        """
        for metric in yolo.classes
    )

    return f"""
    <section id="accuracy-evaluation" class="bg-surface-container-lowest rounded-2xl border border-outline-variant/50 shadow-sm overflow-hidden">
      <div class="px-5 py-4 border-b border-outline-variant/50 flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-primary-fixed text-primary-container flex items-center justify-center">
            <span class="material-symbols-outlined">model_training</span>
          </div>
          <div>
            <div class="flex items-center gap-2 flex-wrap">
              <h3 class="font-headline text-base font-bold text-on-surface">Accuracy Evaluation</h3>
              <span class="px-2 py-0.5 rounded-full bg-[#FFF1D6] text-[#805700] font-code text-[10px] font-bold uppercase tracking-wider">Preview Data</span>
            </div>
            <p class="text-xs text-on-surface-variant mt-0.5">YOLO detection and Manga OCR quality on a held-out validation set.</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span id="evaluation-status" class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-secondary-container/60 text-secondary font-code text-xs font-semibold">
            <span class="material-symbols-outlined text-[15px]">verified</span> Completed
          </span>
          <button onclick="simulateAccuracyEvaluation()" class="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full border border-primary-container/30 bg-white text-primary-container text-xs font-bold hover:bg-primary-fixed/40 transition-colors cursor-pointer">
            <span class="material-symbols-outlined text-[16px]">refresh</span> Re-run
          </button>
        </div>
      </div>

      <div id="evaluation-loading" class="hidden p-8 text-center">
        <div class="w-10 h-10 mx-auto rounded-full border-4 border-primary-fixed border-t-primary-container animate-spin"></div>
        <p class="font-semibold text-on-surface mt-3">Evaluating validation samples...</p>
        <p class="text-xs text-on-surface-variant mt-1">Calculating detection and recognition metrics.</p>
      </div>

      <div id="evaluation-results" class="p-5 space-y-5">
        <div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
          <article class="rounded-xl border border-[#DDE2FF] bg-[#F7F8FF] p-4">
            <div class="flex items-center justify-between mb-4">
              <div>
                <p class="font-code text-[10px] uppercase tracking-widest text-primary-container font-bold">YOLOv8 Detection</p>
                <h4 class="font-headline text-lg font-bold text-on-surface mt-1">Bubble localization</h4>
              </div>
              <span class="px-2.5 py-1 rounded-full bg-secondary-container text-secondary text-xs font-bold">Excellent</span>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {_metric("mAP@0.5", yolo.map50, "Primary")}
              {_metric("mAP@0.5:0.95", yolo.map50_95)}
              {_metric("Precision", yolo.precision)}
              {_metric("Recall", yolo.recall)}
            </div>
            <div class="mt-4 pt-3 border-t border-[#DDE2FF]">
              <div class="flex items-center justify-between mb-1.5">
                <span class="font-code text-[10px] uppercase tracking-wider text-on-surface-variant font-bold">Per-class mAP@0.5</span>
                <span class="text-[10px] text-on-surface-variant">2 classes</span>
              </div>
              {class_rows}
            </div>
          </article>

          <article class="rounded-xl border border-[#DCE8C6] bg-[#FAFCF5] p-4">
            <div class="flex items-center justify-between mb-4">
              <div>
                <p class="font-code text-[10px] uppercase tracking-widest text-secondary font-bold">Manga OCR Recognition</p>
                <h4 class="font-headline text-lg font-bold text-on-surface mt-1">Japanese text extraction</h4>
              </div>
              <span class="px-2.5 py-1 rounded-full bg-[#EAF3D9] text-secondary text-xs font-bold">Good</span>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
              {_metric("Character Accuracy", ocr.character_accuracy, "Primary", green=True)}
              {_metric("CER", ocr.character_error_rate, "Lower is better", inverse=True)}
              {_metric("Exact Match", ocr.exact_match)}
            </div>
            <div class="mt-4 rounded-xl bg-white border border-[#DCE8C6] p-3">
              <div class="flex items-center justify-between text-xs mb-2">
                <span class="font-semibold text-on-surface">Recognition coverage</span>
                <span class="font-code font-bold text-secondary">{ocr.evaluated_regions:,} regions</span>
              </div>
              <div class="h-2 rounded-full bg-surface-container overflow-hidden">
                <div class="h-full rounded-full bg-secondary" style="width:{_percent(ocr.character_accuracy)}%"></div>
              </div>
              <p class="text-[11px] text-on-surface-variant mt-2">CER is used for Japanese OCR because character-level comparison is more reliable than word tokenization.</p>
            </div>
          </article>
        </div>

        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pt-1 text-[11px] text-on-surface-variant">
          <div class="flex items-center gap-4 flex-wrap">
            <span class="inline-flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">dataset</span>{result.dataset_size} validation images</span>
            <span class="inline-flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">schedule</span>{escape(result.evaluated_at or 'Not available')}</span>
          </div>
          <span class="font-code">Backend adapter pending · Mock contract v1</span>
        </div>
      </div>
    </section>
    """


def _metric(
    label: str,
    value: float,
    note: str = "",
    *,
    green: bool = False,
    inverse: bool = False,
) -> str:
    accent = "text-secondary" if green else "text-primary-container"
    displayed = _percent(value)
    return f"""
    <div class="rounded-xl bg-white border border-[#E4DFD6] px-3 py-3 min-w-0">
      <p class="text-[10px] uppercase tracking-wider text-on-surface-variant font-bold truncate">{escape(label)}</p>
      <p class="font-headline text-2xl font-bold {accent} mt-1">{displayed:.1f}%</p>
      <p class="text-[9px] text-on-surface-variant mt-0.5">{escape(note or ('Error rate' if inverse else 'Validation'))}</p>
    </div>
    """


def _state_panel(
    *, icon: str, title: str, message: str, action: str, loading: bool = False, error: bool = False
) -> str:
    tone = "text-error bg-error-container/40" if error else "text-primary-container bg-primary-fixed/50"
    spin = " animate-spin" if loading else ""
    disabled_class = " opacity-60 cursor-not-allowed" if loading else ""
    disabled_attr = " disabled" if loading else ""
    return f"""
    <section id="accuracy-evaluation" class="bg-surface-container-lowest rounded-2xl border border-outline-variant/50 shadow-sm p-8 text-center">
      <div class="w-12 h-12 mx-auto rounded-2xl {tone} flex items-center justify-center">
        <span class="material-symbols-outlined text-[28px]{spin}">{escape(icon)}</span>
      </div>
      <h3 class="font-headline text-lg font-bold text-on-surface mt-3">{escape(title)}</h3>
      <p class="text-sm text-on-surface-variant mt-1 max-w-lg mx-auto">{escape(message)}</p>
      <button onclick="simulateAccuracyEvaluation()" class="mt-4 px-4 py-2 rounded-full bg-primary-container text-on-primary text-xs font-bold{disabled_class}"{disabled_attr}>{escape(action)}</button>
    </section>
    """


def _percent(value: float) -> float:
    return max(0.0, min(value * 100, 100.0))
