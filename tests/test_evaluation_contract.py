from __future__ import annotations

import pytest
from pydantic import ValidationError

from models import CategoryScore, EvaluationData, Scores


def _scores() -> dict[str, dict[str, object]]:
    return {
        "open_source": {"score": 20, "max": 35, "evidence": "Community work"},
        "self_projects": {"score": 20, "max": 30, "evidence": "Complex project"},
        "production": {"score": 15, "max": 25, "evidence": "Internship"},
        "technical_skills": {"score": 8, "max": 10, "evidence": "Technical breadth"},
    }


def _evaluation(**overrides: object) -> dict[str, object]:
    evaluation: dict[str, object] = {
        "scores": _scores(),
        "bonus_points": {"total": 5, "breakdown": "Portfolio"},
        "deductions": {"total": 0, "reasons": "None"},
        "key_strengths": ["Projects"],
        "areas_for_improvement": ["Documentation"],
    }
    evaluation.update(overrides)
    return evaluation


def test_evaluation_contract_accepts_valid_rubric_output() -> None:
    evaluation = EvaluationData(**_evaluation())

    assert evaluation.scores.open_source.max == 35
    assert evaluation.bonus_points.total == 5


def test_category_score_rejects_score_above_declared_max() -> None:
    with pytest.raises(ValidationError, match="score cannot exceed category maximum"):
        CategoryScore(score=36, max=35, evidence="invalid")


def test_scores_rejects_non_rubric_category_maximum() -> None:
    categories = _scores()
    categories["open_source"]["max"] = 40

    with pytest.raises(ValidationError, match="maximum must be 35"):
        Scores(**categories)


def test_evaluation_contract_limits_improvement_items_to_three() -> None:
    with pytest.raises(ValidationError):
        EvaluationData(
            **_evaluation(areas_for_improvement=["one", "two", "three", "four"])
        )
