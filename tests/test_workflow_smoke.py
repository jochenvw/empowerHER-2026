from __future__ import annotations

from pathlib import Path
from typing import Any
from types import SimpleNamespace

from agent_inclusion_lab import workflow
from agent_inclusion_lab.skills.document_loader import load_text
from agent_inclusion_lab.workflow import run_inclusion_workflow


def test_workflow_smoke_verbatim_baseline_flow(monkeypatch) -> None:
    async def fake_eval_async(text: str) -> dict[str, object]:
        score = 1 if "gentleman" in text.lower() else 5
        return {
            "overall_score": float(score),
            "overall_pass": score >= 4,
            "evals": [
                {
                    "eval_name": "Gender Eligibility Bias",
                    "score": score,
                    "pass": score >= 4,
                    "rationale": "mock",
                    "evidence_spans": [],
                    "improvement_advice": "mock",
                }
            ],
        }

    def fake_resolve_agent(stage: str, requested_agent_id: str | None = None):
        _ = requested_agent_id
        if stage == "draft":
            return SimpleNamespace(
                runner=lambda state: {
                    "baseline_output": load_text(Path(state["job_post_path"])).strip()
                }
            )
        if stage == "rewrite":
            return SimpleNamespace(
                runner=lambda state: {"rewritten_output": str(state["baseline_output"])}
            )
        raise AssertionError(f"Unexpected stage: {stage}")

    def fake_discover():
        return {
            "reviewer.default": SimpleNamespace(
                agent_id="reviewer.default",
                stage="review",
                runner=lambda _state: {
                    "review": {
                        "reviewer": "reviewer.default",
                        "summary": "No improvements suggested.",
                        "suggestions": [],
                        "evidence_spans": [],
                    }
                },
            )
        }

    monkeypatch.setattr(workflow, "resolve_agent", fake_resolve_agent)
    monkeypatch.setattr(workflow, "discover_agent_plugins", fake_discover)
    monkeypatch.setattr(workflow, "evaluate_text_async", fake_eval_async)

    root = Path(__file__).resolve().parents[1]
    legacy_path = root / "data" / "legacy" / "hiring_guidelines_legacy.md"
    legacy = load_text(legacy_path)
    clean = load_text(root / "data" / "clean" / "inclusive_hiring_principles.md")

    result = run_inclusion_workflow(legacy_path, clean)
    assert result.baseline_output == legacy.strip()
    assert result.rewritten_output == result.baseline_output
    assert result.baseline_eval["overall_score"] == result.rewritten_eval["overall_score"]
    assert len(result.review_panel) == 1
    assert result.review_panel[0]["reviewer"] == "reviewer.default"


def test_workflow_rewrite_plugin_improves_after_score(monkeypatch) -> None:
    """A rewrite plugin that changes the text is evaluated separately and can
    raise the after-score, without editing workflow logic."""

    async def fake_eval_async(text: str) -> dict[str, object]:
        score = 1 if "gentleman" in text.lower() else 5
        return {
            "overall_score": float(score),
            "overall_pass": score >= 4,
            "evals": [],
        }

    def fake_resolve_agent(stage: str, requested_agent_id: str | None = None):
        _ = requested_agent_id
        if stage == "draft":
            return SimpleNamespace(
                runner=lambda _state: {"baseline_output": "A married gentleman is preferred."}
            )
        if stage == "rewrite":
            return SimpleNamespace(
                runner=lambda state: {
                    "rewritten_output": "We welcome all qualified candidates.",
                    "_review_seen": state.get("review", {}).get("summary"),
                    "_panel_size": len(state.get("review_panel", [])),
                }
            )
        raise AssertionError(f"Unexpected stage: {stage}")

    def fake_discover():
        return {
            "reviewer.gender": SimpleNamespace(
                agent_id="reviewer.gender",
                stage="review",
                runner=lambda _state: {
                    "review": {
                        "reviewer": "reviewer.gender",
                        "summary": "Remove gendered language.",
                        "suggestions": ["Use neutral candidate framing."],
                        "evidence_spans": ["married gentleman"],
                    }
                },
            ),
            "reviewer.access": SimpleNamespace(
                agent_id="reviewer.access",
                stage="review",
                runner=lambda _state: {
                    "review": {
                        "reviewer": "reviewer.access",
                        "summary": "Marital status is not job-related.",
                        "suggestions": ["Drop marital status preference."],
                        "evidence_spans": ["married"],
                    }
                },
            ),
        }

    monkeypatch.setattr(workflow, "resolve_agent", fake_resolve_agent)
    monkeypatch.setattr(workflow, "discover_agent_plugins", fake_discover)
    monkeypatch.setattr(workflow, "evaluate_text_async", fake_eval_async)

    result = run_inclusion_workflow("ignored.md", "principles")
    assert result.rewritten_output != result.baseline_output
    assert result.baseline_eval["overall_score"] < result.rewritten_eval["overall_score"]
    assert result.rewritten_eval["overall_pass"] is True
    assert len(result.review_panel) == 2
    assert {item["reviewer"] for item in result.review_panel} == {
        "reviewer.gender",
        "reviewer.access",
    }
