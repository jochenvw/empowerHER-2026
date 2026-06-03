from __future__ import annotations

from typing import Any

from agent_inclusion_lab.agents.contracts import AgentPlugin
from agent_inclusion_lab.model_client import generate_text


def run_rewrite_agent(
    baseline_output: str,
    reviewer_findings: dict[str, Any],
    inclusive_principles: str,
) -> str:
    prompt = (
        "Rewrite the baseline hiring content to improve inclusion.\n\n"
        "Use reviewer findings and inclusive principles.\n\n"
        f"Reviewer findings:\n{reviewer_findings}\n\n"
        f"Inclusive principles:\n{inclusive_principles}\n\n"
        f"Baseline output:\n{baseline_output}"
    )
    return generate_text(prompt)


def _run_plugin(state: dict[str, Any]) -> dict[str, Any]:
    baseline_output = str(state["baseline_output"])
    reviewer_findings = dict(state["review"])
    inclusive_principles = str(state["inclusive_principles"])
    rewritten_output = run_rewrite_agent(
        baseline_output=baseline_output,
        reviewer_findings=reviewer_findings,
        inclusive_principles=inclusive_principles,
    )
    return {"rewritten_output": rewritten_output}


AGENT_PLUGIN = AgentPlugin(
    agent_id="rewrite.default",
    stage="rewrite",
    description="Rewrites baseline content using reviewer findings and clean principles.",
    runner=_run_plugin,
)
