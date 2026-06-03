from __future__ import annotations

from typing import Any

from agent_inclusion_lab.agents.contracts import AgentPlugin

_GENDERED_TERMS = [" man ", " gentleman", " he ", " his ", "salesmen", "office girls", "gentlemen"]


def run_gender_eligibility_reviewer(text: str) -> dict[str, Any]:
    lowered = f" {text.lower()} "
    hits = [term.strip() for term in _GENDERED_TERMS if term in lowered]
    if not hits:
        return {
            "reviewer": "reviewer.gender_eligibility",
            "summary": "No gender-eligibility issues found.",
            "suggestions": [],
            "evidence_spans": [],
        }
    return {
        "reviewer": "reviewer.gender_eligibility",
        "summary": "Gendered eligibility language suggests the role is intended for men.",
        "suggestions": [
            "Replace male-only candidate terms with gender-neutral language.",
            "Replace gendered worker labels with neutral role labels.",
            "Explicitly frame the role as open to qualified candidates of any gender.",
        ],
        "evidence_spans": hits[:5],
    }


def _run_plugin(state: dict[str, Any]) -> dict[str, Any]:
    baseline_output = str(state["baseline_output"])
    return {"review": run_gender_eligibility_reviewer(baseline_output)}


AGENT_PLUGIN = AgentPlugin(
    agent_id="reviewer.gender_eligibility",
    stage="review",
    description="Flags language implying the role is intended for men.",
    runner=_run_plugin,
)

