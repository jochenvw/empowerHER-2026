from __future__ import annotations

from typing import Any

from agent_inclusion_lab.agents.contracts import AgentPlugin

from .tools import run_age_bias_review

_REVIEWER_ID = "review.olga_age_bias_checker"


def _run_plugin(state: dict[str, Any]) -> dict[str, Any]:
    baseline_output = str(state.get("baseline_output", ""))
    return {"review": run_age_bias_review(baseline_output)}


AGENT_PLUGIN = AgentPlugin(
    agent_id=_REVIEWER_ID,
    stage="review",
    description=(
        "Review-stage checker for age-biased language so young and older "
        "candidates are treated equally."
    ),
    runner=_run_plugin,
)
