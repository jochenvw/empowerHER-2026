from agent_inclusion_lab.agents.registry import discover_agent_plugins, resolve_agent


def test_olga_age_bias_checker_plugin_is_discoverable() -> None:
    plugins = discover_agent_plugins()
    assert "review.olga_age_bias_checker" in plugins
    plugin = resolve_agent(stage="review", requested_agent_id="review.olga_age_bias_checker")
    assert plugin.agent_id == "review.olga_age_bias_checker"
    assert plugin.stage == "review"
    assert plugin.description


def test_olga_age_bias_checker_flags_age_coded_terms() -> None:
    plugin = resolve_agent(stage="review", requested_agent_id="review.olga_age_bias_checker")

    result = plugin.runner(
        {
            "baseline_output": (
                "We want a young, high energy digital native with 3 years of experience."
            )
        }
    )

    assert result["review"]["reviewer"] == "review.olga_age_bias_checker"
    assert result["review"]["suggestions"]
    assert "young" in result["review"]["evidence_spans"]
    assert "high energy" in result["review"]["evidence_spans"]
    assert "digital native" in result["review"]["evidence_spans"]
