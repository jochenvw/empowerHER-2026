from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_inclusion_lab import workflow
from agent_inclusion_lab.skills.document_loader import load_text
from agent_inclusion_lab.workflow import run_inclusion_workflow


def test_workflow_smoke_verbatim_baseline_flow(monkeypatch) -> None:
    async def fake_run_review_panel(
        baseline_output: str, inclusive_principles: str
    ) -> list[dict[str, Any]]:
        _ = baseline_output
        _ = inclusive_principles
        return [
            {
                "reviewer": "reviewer.noop",
                "summary": "No improvements suggested.",
                "suggestions": [],
                "evidence_spans": [],
            }
        ]

    async def fake_run_editor_agent(
        baseline_output: str,
        review_panel: list[dict[str, Any]],
        inclusive_principles: str,
    ) -> tuple[list[str], str]:
        _ = review_panel
        _ = inclusive_principles
        return (["No improvements suggested."], baseline_output)

    def fake_eval(text: str) -> dict[str, object]:
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

    monkeypatch.setattr(workflow, "run_review_panel", fake_run_review_panel)
    monkeypatch.setattr(workflow, "run_editor_agent", fake_run_editor_agent)
    monkeypatch.setattr(workflow, "evaluate_text", fake_eval)

    root = Path(__file__).resolve().parents[1]
    legacy_path = root / "data" / "legacy" / "hiring_guidelines_legacy.md"
    legacy = load_text(legacy_path)
    clean = load_text(root / "data" / "clean" / "inclusive_hiring_principles.md")

    result = run_inclusion_workflow(legacy_path, clean)
    assert result.baseline_output == legacy.strip()
    assert result.rewritten_output == result.baseline_output
    assert result.baseline_eval["overall_score"] == result.rewritten_eval["overall_score"]
