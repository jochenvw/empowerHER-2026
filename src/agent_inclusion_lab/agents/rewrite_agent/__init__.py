from __future__ import annotations

from typing import Any

from agent_inclusion_lab.agents.contracts import AgentPlugin


def run_rewrite_agent(baseline_output: str, review: dict[str, Any]) -> str:
    """Main-branch placeholder rewriter.

    It returns the draft unchanged. Workshop participants replace this with a
    plugin that consumes ``review`` suggestions and the inclusive principles to
    produce improved text, which then scores higher in the reviewed flow.
    """
    _ = review
    return baseline_output


def _run_plugin(state: dict[str, Any]) -> dict[str, Any]:
    baseline_output = str(state.get("baseline_output", ""))
    review = state.get("review")
    review_dict = review if isinstance(review, dict) else {}
    return {"rewritten_output": run_rewrite_agent(baseline_output, review_dict)}


AGENT_PLUGIN = AgentPlugin(
    agent_id="rewrite.default",
    stage="rewrite",
    description="Main-branch placeholder rewriter that returns the draft unchanged.",
    runner=_run_plugin,
)
