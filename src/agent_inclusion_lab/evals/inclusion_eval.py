from __future__ import annotations

from typing import Any

from agent_inclusion_lab.skills.bias_checks import analyze_bias

PASS_THRESHOLD = 75


def evaluate_text(text: str) -> dict[str, Any]:
    result = analyze_bias(text)
    score = int(result["score"])
    recommendation = "pass" if score >= PASS_THRESHOLD else "fail"
    return {
        "score": score,
        "findings": result["findings"],
        "flagged_terms": result["flagged_terms"],
        "recommendation": recommendation,
    }

