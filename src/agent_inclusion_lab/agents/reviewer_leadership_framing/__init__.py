from __future__ import annotations

from typing import Any

from agent_inclusion_lab.agents.contracts import AgentPlugin

_CODED_LEADERSHIP_TERMS = [
    "firm handshake",
    "command respect",
    "strong, dependable man",
    "maturity, steadiness",
    "clean-cut",
    "well-spoken",
    "traditional corporate environment",
]


def run_leadership_framing_reviewer(text: str) -> dict[str, Any]:
    lowered = text.lower()
    hits = [term for term in _CODED_LEADERSHIP_TERMS if term in lowered]
    if not hits:
        return {
            "reviewer": "reviewer.leadership_framing",
            "summary": "Leadership framing is mostly competency-based.",
            "suggestions": [],
            "evidence_spans": [],
        }
    return {
        "reviewer": "reviewer.leadership_framing",
        "summary": "Leadership is framed through stereotype-coded traits instead of observable competencies.",
        "suggestions": [
            "Replace style/appearance language with observable leadership competencies.",
            "Define suitability using decision-making, team management, and operational outcomes.",
            "Remove dominance-coded suitability proxies not tied to job results.",
        ],
        "evidence_spans": hits[:5],
    }


def _run_plugin(state: dict[str, Any]) -> dict[str, Any]:
    baseline_output = str(state["baseline_output"])
    return {"review": run_leadership_framing_reviewer(baseline_output)}


AGENT_PLUGIN = AgentPlugin(
    agent_id="reviewer.leadership_framing",
    stage="review",
    description="Flags stereotype-based leadership framing and coded suitability traits.",
    runner=_run_plugin,
)
