from agent_inclusion_lab.agents.reviewer_gender_eligibility import run_gender_eligibility_reviewer


def test_gender_eligibility_reviewer_flags_gender_restrictions() -> None:
    review = run_gender_eligibility_reviewer("Applicants must be male only for this role.")

    assert review["reviewer"] == "reviewer.gender_eligibility"
    assert review["summary"].startswith("Gender eligibility bias detected.")
    assert set(review["evidence_spans"]) == {"male only", "must be male"}
    assert review["suggestions"] == [
        "Replace gender-restricted eligibility with role-based qualification criteria.",
        "Describe who is eligible using skills and experience, not gender.",
    ]


def test_gender_eligibility_reviewer_keeps_clean_text_unchanged() -> None:
    review = run_gender_eligibility_reviewer("We welcome all qualified candidates.")

    assert review["summary"] == "No gender eligibility bias detected."
    assert review["evidence_spans"] == []
    assert review["suggestions"] == []
