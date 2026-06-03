from __future__ import annotations

from pathlib import Path

from agent_inclusion_lab.skills.job_post_reader import read_job_post


def load_baseline_job_post(path: str | Path) -> str:
    return read_job_post(path)
