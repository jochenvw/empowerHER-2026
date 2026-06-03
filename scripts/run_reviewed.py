from __future__ import annotations

from pathlib import Path

from agent_inclusion_lab.skills.document_loader import load_text
from agent_inclusion_lab.workflow import run_inclusion_workflow


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    legacy_path = root / "data" / "legacy" / "hiring_guidelines_legacy.md"
    clean_path = root / "data" / "clean" / "inclusive_hiring_principles.md"

    legacy_guidance = load_text(legacy_path)
    clean_principles = load_text(clean_path)

    result = run_inclusion_workflow(legacy_guidance, clean_principles)

    print("=== Baseline output ===")
    print(result.baseline_output)
    print("\n=== Rewritten output ===")
    print(result.rewritten_output)
    print("\n=== Scores ===")
    print(
        f"before={result.baseline_eval['score']} after={result.rewritten_eval['score']}"
    )


if __name__ == "__main__":
    main()

