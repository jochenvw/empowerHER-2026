from __future__ import annotations

from pathlib import Path

from agent_inclusion_lab.agents.contracts import AgentPlugin
from agent_inclusion_lab.skills.job_post_reader import read_job_post


def run_baseline_agent(job_post_path: str | Path) -> str:
    return read_job_post(job_post_path).strip()


def _run_plugin(state: dict[str, object]) -> dict[str, object]:
    job_post_path = str(state["job_post_path"])
    return {"baseline_output": run_baseline_agent(job_post_path)}


AGENT_PLUGIN = AgentPlugin(
    agent_id="baseline.default",
    stage="draft",
    description="Reads the job post via skill and returns it verbatim as baseline.",
    runner=_run_plugin,
)
