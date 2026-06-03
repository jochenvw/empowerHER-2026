from __future__ import annotations

from pathlib import Path

from agent_inclusion_lab.evals.inclusion_eval import evaluate_text
from agent_inclusion_lab.skills.document_loader import load_text


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    legacy_text = load_text(root / "data" / "legacy" / "hiring_guidelines_legacy.md")
    clean_text = load_text(root / "data" / "clean" / "inclusive_hiring_principles.md")

    biased_sample = (
        "He is a natural leader with executive presence. "
        "Candidates should be always available and visible in the office."
    )
    neutral_sample = (
        "This role requires measurable coaching outcomes, clear stakeholder communication, "
        "and collaboration across remote and in-office teams."
    )

    legacy_eval = evaluate_text(legacy_text)
    clean_eval = evaluate_text(clean_text)
    biased_eval = evaluate_text(biased_sample)
    neutral_eval = evaluate_text(neutral_sample)

    checks = [
        ("legacy_lower_than_clean", legacy_eval["score"] < clean_eval["score"]),
        ("biased_sample_fails", biased_eval["recommendation"] == "fail"),
        ("neutral_sample_passes", neutral_eval["recommendation"] == "pass"),
    ]

    print("name,result")
    for name, ok in checks:
        print(f"{name},{'PASS' if ok else 'FAIL'}")

    if not all(ok for _, ok in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

