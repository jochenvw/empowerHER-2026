from __future__ import annotations

import re
from typing import Any

from agent_inclusion_lab.agents.contracts import AgentPlugin

_BIAS_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r"\b(?:male|female|men|women|gentlemen|ladies)\s+(?:only|required|preferred)\b",
            re.IGNORECASE,
        ),
        "Replace gender-restricted eligibility with role-based qualification criteria.",
    ),
    (
        re.compile(r"\b(?:only|must be)\s+(?:male|female|men|women)\b", re.IGNORECASE),
        "Describe who is eligible using skills and experience, not gender.",
    ),
)


def run_gender_eligibility_reviewer(text: str) -> dict[str, Any]:
    evidence_spans: list[str] = []
    seen_evidence: set[str] = set()
    suggestions: list[str] = []

    for pattern, suggestion in _BIAS_RULES:
        matched_rule = False
        for match in pattern.finditer(text):
            value = match.group(0).strip()
            if value in seen_evidence:
                continue
            evidence_spans.append(value)
            seen_evidence.add(value)
            matched_rule = True
        if matched_rule and suggestion not in suggestions:
            suggestions.append(suggestion)

    if evidence_spans:
        summary = (
            "Gender eligibility bias detected. Use gender-neutral requirements so all "
            "qualified candidates can apply."
        )
    else:
        summary = "No gender eligibility bias detected."

    return {
        "reviewer": "reviewer.gender_eligibility",
        "summary": summary,
        "suggestions": suggestions,
        "evidence_spans": evidence_spans,
    }


def _run_plugin(state: dict[str, Any]) -> dict[str, Any]:
    baseline_output = str(state.get("baseline_output", ""))
    return {"review": run_gender_eligibility_reviewer(baseline_output)}


AGENT_PLUGIN = AgentPlugin(
    agent_id="reviewer.gender_eligibility",
    stage="review",
    description="Flags gender-based eligibility restrictions and suggests inclusive alternatives.",
    runner=_run_plugin,
)
