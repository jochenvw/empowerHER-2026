from __future__ import annotations

from typing import Any

from agent_inclusion_lab.agents.contracts import AgentPlugin
from agent_inclusion_lab.evals.inclusion_eval import evaluate_text


def run_inclusion_reviewer(text: str) -> dict[str, Any]:
    evaluation = evaluate_text(text)
    return {
        "score": evaluation["score"],
        "findings": evaluation["findings"],
        "flagged_terms": evaluation["flagged_terms"],
        "recommendation": evaluation["recommendation"],
    }


def _run_plugin(state: dict[str, Any]) -> dict[str, Any]:
    baseline_output = str(state["baseline_output"])
    return {"review": run_inclusion_reviewer(baseline_output)}


AGENT_PLUGIN = AgentPlugin(
    agent_id="reviewer.default",
    stage="review",
    description="Reviews baseline output for inclusion risk indicators.",
    runner=_run_plugin,
)
