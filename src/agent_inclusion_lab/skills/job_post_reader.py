from __future__ import annotations

import asyncio
import subprocess
import sys
import warnings
from functools import lru_cache
from pathlib import Path
from threading import Thread
from typing import Any

from agent_framework import FileSkill, FileSkillScript, FileSkillsSource

_SKILL_NAME = "job-post-reader"
_SCRIPT_NAME = "scripts/read_job_post.py"


def _skill_dir() -> Path:
    return Path(__file__).resolve().parent / "job-post-reader"


def _run_script(skill: FileSkill, script: FileSkillScript, args: dict[str, Any] | list[str] | None = None) -> str:
    if isinstance(args, dict):
        path_value = args.get("path")
        if path_value is None:
            raise ValueError("Script args dict must include 'path'.")
        cli_args = [str(path_value)]
    elif isinstance(args, list):
        cli_args = [str(value) for value in args]
    else:
        cli_args = []

    command = [sys.executable, script.full_path, *cli_args]
    completed = subprocess.run(
        command, capture_output=True, text=True, encoding="utf-8", check=False
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or "Unknown script error."
        raise RuntimeError(f"File-based skill script failed: {stderr}")
    return completed.stdout


def _run_async(coro):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    result: dict[str, Any] = {}
    error: dict[str, BaseException] = {}

    def _target() -> None:
        try:
            result["value"] = asyncio.run(coro)
        except BaseException as exc:  # noqa: BLE001
            error["value"] = exc

    thread = Thread(target=_target, daemon=True)
    thread.start()
    thread.join()
    if "value" in error:
        raise error["value"]
    return result["value"]


@lru_cache(maxsize=1)
def _load_file_skill() -> tuple[FileSkill, FileSkillScript]:
    source = FileSkillsSource(
        skill_paths=[_skill_dir()],
        script_runner=_run_script,
    )
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*\\[SKILLS\\].*")
        skills = _run_async(source.get_skills())
    if not skills:
        raise RuntimeError("No file-based skills were discovered for job post reader.")

    skill = next((item for item in skills if item.frontmatter.name == _SKILL_NAME), None)
    if skill is None or not isinstance(skill, FileSkill):
        raise RuntimeError(f"Expected FileSkill '{_SKILL_NAME}' was not discovered.")

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*\\[SKILLS\\].*")
        script = _run_async(skill.get_script(_SCRIPT_NAME))
    if script is None or not isinstance(script, FileSkillScript):
        raise RuntimeError(f"Expected script '{_SCRIPT_NAME}' was not discovered for '{_SKILL_NAME}'.")
    return skill, script


def read_job_post(path: str | Path) -> str:
    skill, script = _load_file_skill()
    return _run_script(skill, script, [str(path)])
