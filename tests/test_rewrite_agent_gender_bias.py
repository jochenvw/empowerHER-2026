from __future__ import annotations

from agent_inclusion_lab import model_client
from agent_inclusion_lab.agents.registry import (
    discover_agent_plugins,
    resolve_agent,
)


def test_gender_bias_plugin_is_discoverable() -> None:
    plugins = discover_agent_plugins()
    assert "rewrite.gender_bias" in plugins
    plugin = resolve_agent(stage="rewrite", requested_agent_id="rewrite.gender_bias")
    assert plugin.agent_id == "rewrite.gender_bias"
    assert plugin.stage == "rewrite"
    assert plugin.description


def test_gender_bias_agent_rewrites_via_agent_framework(monkeypatch) -> None:
    captured: dict[str, str] = {}

    def fake_generate_text(prompt: str) -> str:
        captured["prompt"] = prompt
        return "We welcome all qualified candidates regardless of gender."

    monkeypatch.setattr(model_client, "generate_text", fake_generate_text)

    plugin = resolve_agent(stage="rewrite", requested_agent_id="rewrite.gender_bias")
    state = {
        "baseline_output": "A gentleman is preferred for this chairman role.",
        "inclusive_principles": "Use neutral, competency-based language.",
        "review": {"suggestions": ["Remove gendered job titles and pronouns."]},
    }

    result = plugin.runner(state)

    assert result["rewritten_output"] == "We welcome all qualified candidates regardless of gender."
    assert "gentleman" in captured["prompt"]
    assert "Remove gendered job titles" in captured["prompt"]


def test_rewrite_default_unchanged_by_gender_bias_agent() -> None:
    """The no-op default on main must still be the first-discovered rewrite plugin."""
    from agent_inclusion_lab.agents.registry import get_default_agent_ids_by_stage

    defaults = get_default_agent_ids_by_stage()
    assert defaults["rewrite"] == "rewrite.default"
