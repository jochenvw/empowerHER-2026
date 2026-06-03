from agent_inclusion_lab.agents.registry import discover_agent_plugins, resolve_agent


def test_registry_discovers_default_stages() -> None:
    plugins = discover_agent_plugins()
    assert "baseline.default" in plugins
    assert "reviewer.default" in plugins
    assert "rewrite.default" in plugins

    assert resolve_agent("draft").agent_id == "baseline.default"
    assert resolve_agent("review").agent_id == "reviewer.default"
    assert resolve_agent("rewrite").agent_id == "rewrite.default"

