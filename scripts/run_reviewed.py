from __future__ import annotations

from pathlib import Path

from agent_inclusion_lab.skills.document_loader import load_text
from agent_inclusion_lab.workflow import run_inclusion_workflow


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    legacy_path = root / "data" / "legacy" / "hiring_guidelines_legacy.md"
    clean_path = root / "data" / "clean" / "inclusive_hiring_principles.md"

    clean_principles = load_text(clean_path)

    result = run_inclusion_workflow(legacy_path, clean_principles)

    print("=== Baseline output ===")
    print(result.baseline_output)
    if result.feedback_summary:
        print("\n=== Feedback summary ===")
        for item in result.feedback_summary:
            print(f"- {item}")

    print("\n=== Improved output ===")
    print(result.rewritten_output)
    print("\n=== Scores ===")
    print(
        f"before={result.baseline_eval['overall_score']} "
        f"after={result.rewritten_eval['overall_score']}"
    )
    print(
        f"before_pass={result.baseline_eval['overall_pass']} "
        f"after_pass={result.rewritten_eval['overall_pass']}"
    )


if __name__ == "__main__":
    main()
