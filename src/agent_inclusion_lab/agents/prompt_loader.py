from __future__ import annotations

from pathlib import Path

_AGENT_DIR_BY_ID: dict[str, str] = {
    "baseline.default": "baseline_agent",
    "reviewer.default": "inclusion_reviewer",
    "rewrite.default": "rewrite_agent",
    "reviewer.gender_eligibility": "reviewer_gender_eligibility",
    "reviewer.leadership_framing": "reviewer_leadership_framing",
    "reviewer.equal_access": "reviewer_equal_access",
    "editor.synthesizer": "editor_synthesizer",
}


def _agents_root() -> Path:
    return Path(__file__).resolve().parent


def agent_dir(agent_id: str) -> Path:
    folder = _AGENT_DIR_BY_ID.get(agent_id)
    if folder is None:
        raise KeyError(f"Unknown agent id: {agent_id}")
    return _agents_root() / folder


def load_system_prompt(agent_id: str) -> str:
    prompt_path = agent_dir(agent_id) / "system_prompt.md"
    if not prompt_path.exists():
        raise RuntimeError(f"Missing system prompt file for {agent_id}: {prompt_path}")
    prompt = prompt_path.read_text(encoding="utf-8").strip()
    if not prompt:
        raise RuntimeError(f"System prompt file is empty for {agent_id}: {prompt_path}")
    return prompt


def load_skills_markdown(agent_id: str) -> str:
    skills_path = agent_dir(agent_id) / "skills.md"
    if not skills_path.exists():
        return ""
    return skills_path.read_text(encoding="utf-8").strip()


def build_agent_instructions(agent_id: str) -> str:
    system_prompt = load_system_prompt(agent_id)
    skills = load_skills_markdown(agent_id)
    if not skills:
        return system_prompt
    return f"{system_prompt}\n\nSkills reference:\n{skills}"
