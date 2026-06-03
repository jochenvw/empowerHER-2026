from __future__ import annotations

from pathlib import Path

from agent_inclusion_lab.skills.document_loader import load_text


def read_job_post(path: str | Path) -> str:
    return load_text(Path(path))

