from __future__ import annotations

from typing import Any

from agent_inclusion_lab.agents.contracts import AgentPlugin


def run_rewrite_agent(
    baseline_output: str,
    reviewer_findings: dict[str, Any],
    inclusive_principles: str,
) -> str:
    return baseline_output


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
    description="Pass-through placeholder for future text improvement agents.",
    runner=_run_plugin,
)
