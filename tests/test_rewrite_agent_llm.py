from __future__ import annotations

from agent_inclusion_lab import model_client
from agent_inclusion_lab.agents.registry import (
    get_default_agent_ids_by_stage,
    resolve_agent,
)


def test_rewrite_default_stays_noop_on_main() -> None:
    defaults = get_default_agent_ids_by_stage()
    assert defaults["rewrite"] == "rewrite.default"


def test_llm_rewrite_agent_uses_agent_framework_agent(monkeypatch) -> None:
    captured: dict[str, str] = {}

    def fake_generate_text(prompt: str) -> str:
        captured["prompt"] = prompt
        return "We welcome all qualified candidates."

    monkeypatch.setattr(model_client, "generate_text", fake_generate_text)

    plugin = resolve_agent(stage="rewrite", requested_agent_id="rewrite.llm")
    state = {
        "baseline_output": "A married gentleman is preferred.",
        "inclusive_principles": "Use neutral, competency-based language.",
        "review": {"suggestions": ["Remove gendered language."]},
    }

    result = plugin.runner(state)

    assert result["rewritten_output"] == "We welcome all qualified candidates."
    assert "married gentleman" in captured["prompt"]
    assert "Remove gendered language." in captured["prompt"]
