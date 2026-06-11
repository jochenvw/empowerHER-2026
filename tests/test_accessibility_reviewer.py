from __future__ import annotations

import json

import pytest

from agent_inclusion_lab import model_client
from agent_inclusion_lab.agents.registry import discover_agent_plugins, resolve_agent

# Clear the lru_cache between tests so registry picks up the real plugins.
@pytest.fixture(autouse=True)
def clear_plugin_cache() -> None:
    discover_agent_plugins.cache_clear()
    yield
    discover_agent_plugins.cache_clear()


def test_accessibility_reviewer_is_discoverable() -> None:
    plugins = discover_agent_plugins()
    assert "reviewer.accessibility" in plugins

    plugin = resolve_agent(stage="review", requested_agent_id="reviewer.accessibility")
    assert plugin.agent_id == "reviewer.accessibility"
    assert plugin.stage == "review"


def test_accessibility_reviewer_returns_structured_findings(monkeypatch) -> None:
    findings = {
        "summary": (
            "Job posting contains physical and transportation requirements "
            "that may exclude candidates with disabilities."
        ),
        "suggestions": [
            (
                'Replace "must be able to lift 50 lbs" with '
                '"may occasionally need to move items; accommodations are available."'
            ),
            (
                'Replace "valid driver\'s license required" with '
                '"must be able to travel to client sites; accommodations are available."'
            ),
        ],
        "evidence_spans": [
            "must be able to lift 50 lbs",
            "valid driver's license required",
        ],
    }

    def fake_generate_text(prompt: str) -> str:
        assert "lift 50 lbs" in prompt
        return json.dumps(findings)

    monkeypatch.setattr(model_client, "generate_text", fake_generate_text)

    plugin = resolve_agent(stage="review", requested_agent_id="reviewer.accessibility")
    state = {
        "baseline_output": (
            "Must be able to lift 50 lbs regularly. "
            "Valid driver's license required. "
            "Fast-paced standing role."
        ),
    }

    result = plugin.runner(state)

    review = result["review"]
    assert review["reviewer"] == "reviewer.accessibility"
    assert "disabilities" in review["summary"]
    assert len(review["suggestions"]) == 2
    assert "must be able to lift 50 lbs" in review["evidence_spans"]
    assert "valid driver's license required" in review["evidence_spans"]


def test_accessibility_reviewer_degrades_gracefully_on_bad_json(monkeypatch) -> None:
    def fake_generate_text(prompt: str) -> str:
        return "This posting has some accessibility concerns worth addressing."

    monkeypatch.setattr(model_client, "generate_text", fake_generate_text)

    plugin = resolve_agent(stage="review", requested_agent_id="reviewer.accessibility")
    state = {"baseline_output": "Must be able to lift 50 lbs regularly."}

    result = plugin.runner(state)

    review = result["review"]
    assert review["reviewer"] == "reviewer.accessibility"
    assert "accessibility" in review["summary"].lower()
    assert isinstance(review["suggestions"], list)
    assert isinstance(review["evidence_spans"], list)


def test_accessibility_reviewer_handles_empty_posting(monkeypatch) -> None:
    findings = {
        "summary": "No accessibility barriers found.",
        "suggestions": [],
        "evidence_spans": [],
    }

    def fake_generate_text(prompt: str) -> str:
        return json.dumps(findings)

    monkeypatch.setattr(model_client, "generate_text", fake_generate_text)

    plugin = resolve_agent(stage="review", requested_agent_id="reviewer.accessibility")
    result = plugin.runner({"baseline_output": ""})

    review = result["review"]
    assert review["reviewer"] == "reviewer.accessibility"
    assert review["suggestions"] == []
    assert review["evidence_spans"] == []
