from __future__ import annotations

from pathlib import Path

from agent_inclusion_lab.agents.baseline_agent import run_baseline_agent
from agent_inclusion_lab.evals.inclusion_eval import evaluate_text
from agent_inclusion_lab.skills.document_loader import load_text


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    legacy_path = root / "data" / "legacy" / "hiring_guidelines_legacy.md"
    legacy_guidance = load_text(legacy_path)

    baseline_output = run_baseline_agent(legacy_guidance)
    baseline_eval = evaluate_text(baseline_output)

    print("=== Baseline output ===")
    print(baseline_output)
    print("\n=== Inclusion score ===")
    print(
        f"overall_score={baseline_eval['overall_score']} "
        f"overall_pass={baseline_eval['overall_pass']}"
    )
    print("\n=== LLM judge evals ===")
    for item in baseline_eval["evals"]:
        print(
            f"- {item['eval_name']}: score={item['score']} pass={item['pass']} "
            f"rationale={item['rationale']}"
        )


if __name__ == "__main__":
    main()
