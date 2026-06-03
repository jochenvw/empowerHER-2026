from __future__ import annotations

from typing import Any

from agent_inclusion_lab.agents.contracts import AgentPlugin
from agent_inclusion_lab.model_client import generate_text


def run_revision_synthesizer(
    baseline_output: str,
    reviewer_feedback: list[dict[str, Any]],
    inclusive_principles: str,
) -> str:
    has_suggestions = any(item.get("suggestions") for item in reviewer_feedback)
    if not has_suggestions:
        return baseline_output

    panel_notes = []
    for item in reviewer_feedback:
        suggestions = item.get("suggestions", [])
        if suggestions:
            joined = "; ".join(str(s) for s in suggestions)
            panel_notes.append(f"- {item.get('reviewer')}: {joined}")
    panel_text = "\n".join(panel_notes)

    prompt = (
        "You are revising a job posting to reduce bias and improve equal access.\n"
        "Keep core business intent and responsibilities intact.\n"
        "Do not invent facts.\n"
        "Return revised posting text only.\n\n"
        "Improver panel guidance:\n"
        f"{panel_text}\n\n"
        "Inclusive principles:\n"
        f"{inclusive_principles}\n\n"
        "Original posting:\n"
        f"{baseline_output}"
    )
    return generate_text(prompt)


def _run_plugin(state: dict[str, Any]) -> dict[str, Any]:
    baseline_output = str(state["baseline_output"])
    reviewer_feedback = list(state.get("reviews", []))
    inclusive_principles = str(state["inclusive_principles"])
    rewritten_output = run_revision_synthesizer(
        baseline_output=baseline_output,
        reviewer_feedback=reviewer_feedback,
        inclusive_principles=inclusive_principles,
    )
    return {"rewritten_output": rewritten_output}


AGENT_PLUGIN = AgentPlugin(
    agent_id="rewrite.default",
    stage="rewrite",
    description="Revision synthesizer placeholder (no-op on main).",
    runner=_run_plugin,
)
