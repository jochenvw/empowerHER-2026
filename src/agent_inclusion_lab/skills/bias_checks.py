from __future__ import annotations

import re
from typing import Any

GENDERED_TERMS = ["he", "him", "his", "manpower"]
RISK_PHRASES = [
    "culture fit",
    "aggressive",
    "dominant",
    "command the room",
    "always available",
    "flexible schedules may struggle",
    "visible in the office",
    "young and energetic",
    "native speaker",
]
VAGUE_TERMS = ["executive presence", "rockstar", "high potential", "natural leader"]


def _count_occurrences(text: str, term: str) -> int:
    escaped = re.escape(term)
    pattern = rf"\b{escaped}\b"
    return len(re.findall(pattern, text, flags=re.IGNORECASE))


def _scan_terms(text: str, terms: list[str], category: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for term in terms:
        count = _count_occurrences(text, term)
        if count:
            findings.append({"category": category, "term": term, "count": count})
    return findings


def analyze_bias(text: str) -> dict[str, Any]:
    gendered = _scan_terms(text, GENDERED_TERMS, "gendered_language")
    phrase_risks = _scan_terms(text, RISK_PHRASES, "exclusionary_phrase")
    vague = _scan_terms(text, VAGUE_TERMS, "vague_criteria")

    flagged_terms = [*gendered, *phrase_risks, *vague]
    total_hits = sum(item["count"] for item in flagged_terms)

    score = max(0, 100 - (total_hits * 8))
    findings = []
    if gendered:
        findings.append("Gendered language was detected.")
    if phrase_risks:
        findings.append("Potentially exclusionary phrases were detected.")
    if vague:
        findings.append("Vague leadership criteria were detected.")
    if not findings:
        findings.append("No tracked bias indicators were detected.")

    return {
        "score": score,
        "findings": findings,
        "flagged_terms": flagged_terms,
        "counts": {
            "gendered_language_hits": sum(item["count"] for item in gendered),
            "exclusionary_phrase_hits": sum(item["count"] for item in phrase_risks),
            "vague_criteria_hits": sum(item["count"] for item in vague),
        },
    }

