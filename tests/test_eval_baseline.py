import json
from pathlib import Path

from agent_inclusion_lab.evals import inclusion_eval
from agent_inclusion_lab.skills.document_loader import load_text


def _fake_judge_response(prompt: str) -> str:
    eval_name = prompt.split("Evaluation name: ", 1)[1].split("\n", 1)[0].strip()
    text = prompt.split("Text to evaluate:\n", 1)[1].lower()

    if eval_name == "Gender Eligibility Bias":
        terms = ["man", "gentleman", "he ", " his", "salesmen", "office girls"]
    elif eval_name == "Gender Stereotype and Leadership Framing":
        terms = ["firm handshake", "command respect", "strong, dependable man", "clean-cut"]
    else:
        terms = ["between 30 and 45", "married gentleman", "family obligations", "clean-cut"]

    hits = sum(1 for term in terms if term in text)
    score = 1 if hits >= 2 else (3 if hits == 1 else 5)
    return json.dumps(
        {
            "eval_name": eval_name,
            "score": score,
            "rationale": "Mock judge rationale.",
            "evidence_spans": [term for term in terms if term in text][:4],
            "improvement_advice": "Mock advice.",
        }
    )


def test_legacy_scores_lower_than_clean(monkeypatch) -> None:
    monkeypatch.setattr(inclusion_eval, "generate_text", _fake_judge_response)
    root = Path(__file__).resolve().parents[1]
    legacy = load_text(root / "data" / "legacy" / "hiring_guidelines_legacy.md")
    clean = load_text(root / "data" / "clean" / "inclusive_hiring_principles.md")
    legacy_eval = inclusion_eval.evaluate_text(legacy)
    clean_eval = inclusion_eval.evaluate_text(clean)
    assert legacy_eval["overall_score"] < clean_eval["overall_score"]


def test_biased_sample_fails_and_neutral_passes(monkeypatch) -> None:
    monkeypatch.setattr(inclusion_eval, "generate_text", _fake_judge_response)
    biased = (
        "He should command the room and be always available. "
        "A married gentleman with a firm handshake is preferred."
    )
    neutral = (
        "Use observable competencies, structured interview rubrics, and inclusive language."
    )
    assert inclusion_eval.evaluate_text(biased)["overall_pass"] is False
    assert inclusion_eval.evaluate_text(neutral)["overall_pass"] is True
