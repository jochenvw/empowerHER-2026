from pathlib import Path

from agent_inclusion_lab.evals.inclusion_eval import evaluate_text
from agent_inclusion_lab.skills.document_loader import load_text


def test_legacy_scores_lower_than_clean() -> None:
    root = Path(__file__).resolve().parents[1]
    legacy = load_text(root / "data" / "legacy" / "hiring_guidelines_legacy.md")
    clean = load_text(root / "data" / "clean" / "inclusive_hiring_principles.md")
    legacy_eval = evaluate_text(legacy)
    clean_eval = evaluate_text(clean)
    assert legacy_eval["score"] < clean_eval["score"]


def test_biased_sample_fails_and_neutral_passes() -> None:
    biased = (
        "He should command the room and be always available. "
        "Culture fit and executive presence are required."
    )
    neutral = (
        "Use observable competencies, structured interview rubrics, and "
        "inclusive language across collaboration styles."
    )
    assert evaluate_text(biased)["recommendation"] == "fail"
    assert evaluate_text(neutral)["recommendation"] == "pass"

