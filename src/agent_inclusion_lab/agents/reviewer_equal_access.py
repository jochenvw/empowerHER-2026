from __future__ import annotations

from typing import Any

from agent_inclusion_lab.agents.contracts import AgentPlugin

_BARRIER_TERMS = [
    "between 30 and 45",
    "married gentleman",
    "family obligations interfering",
    "clean-cut",
    "military service",
    "traditional corporate environment",
]


def run_equal_access_reviewer(text: str) -> dict[str, Any]:
    lowered = text.lower()
    hits = [term for term in _BARRIER_TERMS if term in lowered]
    if not hits:
        return {
            "reviewer": "reviewer.equal_access",
            "summary": "Requirements appear job-related and broadly accessible.",
            "suggestions": [],
            "evidence_spans": [],
        }
    return {
        "reviewer": "reviewer.equal_access",
        "summary": "The posting includes non-job-related barriers tied to demographics or life situation.",
        "suggestions": [
            "Remove age, marital status, and family-situation preferences.",
            "State travel and availability requirements neutrally and job-relevantly.",
            "Separate required qualifications from optional preferences using role-related criteria only.",
        ],
        "evidence_spans": hits[:5],
    }


def _run_plugin(state: dict[str, Any]) -> dict[str, Any]:
    baseline_output = str(state["baseline_output"])
    return {"review": run_equal_access_reviewer(baseline_output)}


AGENT_PLUGIN = AgentPlugin(
    agent_id="reviewer.equal_access",
    stage="review",
    description="Flags non-job-related barriers affecting equal access.",
    runner=_run_plugin,
)

