from __future__ import annotations

from pathlib import Path

from agent_inclusion_lab.skills.document_loader import load_text
from agent_inclusion_lab.workflow import run_inclusion_workflow


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    legacy_path = root / "data" / "legacy" / "hiring_guidelines_legacy.md"
    clean_text = load_text(root / "data" / "clean" / "inclusive_hiring_principles.md")

    workflow = run_inclusion_workflow(legacy_path, clean_text)

    baseline_eval = workflow.baseline_eval
    rewritten_eval = workflow.rewritten_eval

    print("version,overall_score,overall_pass")
    print(
        f"baseline,{baseline_eval['overall_score']},{baseline_eval['overall_pass']}"
    )
    print(
        f"rewritten,{rewritten_eval['overall_score']},{rewritten_eval['overall_pass']}"
    )
    print("")
    print("version,eval_name,score,pass")
    for version, report in [("baseline", baseline_eval), ("rewritten", rewritten_eval)]:
        for item in report["evals"]:
            print(f"{version},{item['eval_name']},{item['score']},{item['pass']}")


if __name__ == "__main__":
    main()
