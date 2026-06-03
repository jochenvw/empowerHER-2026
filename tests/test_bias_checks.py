from agent_inclusion_lab.skills.bias_checks import analyze_bias


def test_bias_checks_find_expected_terms() -> None:
    text = (
        "He is a natural leader with executive presence. "
        "Candidates should be always available and visible in the office."
    )
    result = analyze_bias(text)
    assert result["score"] < 100
    terms = {item["term"] for item in result["flagged_terms"]}
    assert "he" in terms
    assert "always available" in terms
    assert "executive presence" in terms

