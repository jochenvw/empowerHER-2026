from __future__ import annotations

import re
from typing import Any

_REVIEWER_ID = "review.olga_age_bias_checker"
_MAX_EVIDENCE_SPANS = 6

_AGE_BIAS_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"\b(?:young|youthful|junior)\b", re.IGNORECASE),
        "Avoid age-coded terms like 'young' or 'youthful'; describe role level instead.",
    ),
    (
        re.compile(r"\b(?:digital native|recent graduate)\b", re.IGNORECASE),
        "Replace age-coded proxies with concrete skills or tool experience requirements.",
    ),
    (
        re.compile(r"\b(?:overqualified|too old)\b", re.IGNORECASE),
        "Do not imply older candidates are less suitable because of age.",
    ),
    (
        re.compile(r"\b(?:energetic|high energy)\b", re.IGNORECASE),
        "Use outcome-focused language instead of age-coded traits like 'energetic'.",
    ),
)


def run_age_bias_review(text: str) -> dict[str, Any]:
    suggestions: list[str] = []
    evidence_spans: list[str] = []

    for pattern, suggestion in _AGE_BIAS_RULES:
        matches = [match.group(0) for match in pattern.finditer(text)]
        if not matches:
            continue
        suggestions.append(suggestion)
        evidence_spans.extend(matches)

    unique_suggestions = list(dict.fromkeys(suggestions))
    unique_evidence = list(dict.fromkeys(evidence_spans))[:_MAX_EVIDENCE_SPANS]

    if unique_suggestions:
        summary = "Potential age-bias wording found; suggest neutral, skill-based phrasing."
    else:
        summary = "No age-bias wording detected."

    return {
        "reviewer": _REVIEWER_ID,
        "summary": summary,
        "suggestions": unique_suggestions,
        "evidence_spans": unique_evidence,
    }
