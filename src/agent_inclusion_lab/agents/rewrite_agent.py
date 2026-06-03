from __future__ import annotations

from typing import Any

from agent_inclusion_lab.agents.contracts import AgentPlugin


def run_revision_synthesizer(
    baseline_output: str,
    reviewer_feedback: list[dict[str, Any]],
    inclusive_principles: str,
) -> str:
    _ = inclusive_principles
    has_suggestions = any(item.get("suggestions") for item in reviewer_feedback)
    if not has_suggestions:
        return baseline_output

    # Main branch intentionally keeps baseline unchanged.
    # Reference implementation can replace this with rewrite logic.
    return baseline_output


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
