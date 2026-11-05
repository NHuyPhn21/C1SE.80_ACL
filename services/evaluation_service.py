"""Replaceable accuracy service using preview data until the API is available."""

from __future__ import annotations

from abc import ABC, abstractmethod
from functools import lru_cache

from models.evaluation import (
    DetectionClassMetric,
    EvaluationResult,
    EvaluationStatus,
    OcrMetrics,
    YoloMetrics,
)


class EvaluationService(ABC):
    @abstractmethod
    def get_result(
        self, project_name: str, state: EvaluationStatus = EvaluationStatus.COMPLETED
    ) -> EvaluationResult:
        raise NotImplementedError


class MockEvaluationService(EvaluationService):
    """Stable demo results matching the future backend response contract."""

    def get_result(
        self, project_name: str, state: EvaluationStatus = EvaluationStatus.COMPLETED
    ) -> EvaluationResult:
        if state == EvaluationStatus.EMPTY:
            return EvaluationResult(project_name=project_name, status=state)
        if state == EvaluationStatus.EVALUATING:
            return EvaluationResult(project_name=project_name, status=state, dataset_size=250)
        if state == EvaluationStatus.FAILED:
            return EvaluationResult(
                project_name=project_name,
                status=state,
                dataset_size=250,
                error_message="Evaluation worker could not load the validation dataset.",
            )

        return EvaluationResult(
            project_name=project_name,
            status=EvaluationStatus.COMPLETED,
            dataset_size=250,
            yolo=YoloMetrics(
                map50=0.942,
                map50_95=0.781,
                precision=0.916,
                recall=0.887,
                classes=(
                    DetectionClassMetric("Panel", 0.956, 0.931, 0.902),
                    DetectionClassMetric("Text Bubble", 0.928, 0.901, 0.872),
                ),
            ),
            ocr=OcrMetrics(
                character_accuracy=0.901,
                character_error_rate=0.099,
                exact_match=0.824,
                evaluated_regions=768,
            ),
            evaluated_at="28 Oct 2026, 14:20 ICT",
        )


@lru_cache(maxsize=1)
def get_evaluation_service() -> EvaluationService:
    return MockEvaluationService()
