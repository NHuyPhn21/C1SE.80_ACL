"""Frontend models for displaying AI accuracy evaluation results."""

from dataclasses import dataclass, field
from enum import StrEnum


class EvaluationStatus(StrEnum):
    EMPTY = "empty"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class DetectionClassMetric:
    name: str
    map50: float
    precision: float
    recall: float


@dataclass(frozen=True)
class YoloMetrics:
    map50: float
    map50_95: float
    precision: float
    recall: float
    classes: tuple[DetectionClassMetric, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class OcrMetrics:
    character_accuracy: float
    character_error_rate: float
    exact_match: float
    evaluated_regions: int


@dataclass(frozen=True)
class EvaluationResult:
    project_name: str
    status: EvaluationStatus
    dataset_size: int = 0
    yolo: YoloMetrics | None = None
    ocr: OcrMetrics | None = None
    evaluated_at: str | None = None
    error_message: str | None = None
    is_mock: bool = True
