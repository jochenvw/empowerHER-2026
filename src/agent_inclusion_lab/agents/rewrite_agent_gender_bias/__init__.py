"""Gender eligibility bias rewrite agent.

Rewrites job postings to remove gender eligibility bias and represent equal
opportunity for all genders.  Opt in with::

    INCLUSION_REWRITE_AGENT=rewrite.gender_bias uv run eh reviewed
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_inclusion_lab.agents.contracts import AgentPlugin

from .tools import rewrite_with_agent

_SYSTEM_PROMPT = (Path(__file__).resolve().parent / "system_prompt.md").read_text(encoding="utf-8")


def _build_user_request(state: dict[str, Any]) -> str:
    baseline = str(state.get("baseline_output", "")).strip()
    principles = str(state.get("inclusive_principles", "")).strip()
    review = state.get("review")
    suggestions = review.get("suggestions", []) if isinstance(review, dict) else []
    suggestion_text = "\n".join(f"- {item}" for item in suggestions) if suggestions else "- (none provided)"
    return (
        "Inclusive hiring principles:\n"
        f"{principles}\n\n"
        "Reviewer suggestions:\n"
        f"{suggestion_text}\n\n"
        "Job posting to rewrite:\n"
        f"{baseline}"
    )


def _run_plugin(state: dict[str, Any]) -> dict[str, Any]:
    rewritten = rewrite_with_agent(_SYSTEM_PROMPT, _build_user_request(state))
    return {"rewritten_output": rewritten}


AGENT_PLUGIN = AgentPlugin(
    agent_id="rewrite.gender_bias",
    stage="rewrite",
    description=(
        "Rewrites job postings to remove gender eligibility bias and represent "
        "equal opportunity; opt in via INCLUSION_REWRITE_AGENT=rewrite.gender_bias."
    ),
    runner=_run_plugin,
)
