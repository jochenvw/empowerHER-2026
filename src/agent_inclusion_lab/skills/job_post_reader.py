from __future__ import annotations

from pathlib import Path
import warnings

warnings.filterwarnings(
    "ignore",
    message=".*experimental.*",
    module="agent_framework.*",
)

from agent_framework import ClassSkill, SkillFrontmatter
from agent_inclusion_lab.skills.document_loader import load_text


class JobPostReaderSkill(ClassSkill):
    def __init__(self) -> None:
        super().__init__(
            frontmatter=SkillFrontmatter(
                name="job-post-reader",
                description="Reads a workshop job-post markdown file as plain text.",
            )
        )

    @property
    def instructions(self) -> str:
        return "Use read-job-post to load a job posting from disk."

    @ClassSkill.script(
        name="read-job-post",
        description="Read a job posting file from disk and return its text content.",
    )
    def read_job_post(self, path: str) -> str:
        return load_text(Path(path))


def read_job_post(path: str | Path) -> str:
    skill = JobPostReaderSkill()
    return skill.read_job_post(str(path))
