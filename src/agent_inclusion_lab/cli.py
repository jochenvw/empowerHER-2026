from __future__ import annotations

import argparse
import importlib
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable

from agent_inclusion_lab.agents.baseline_agent import run_baseline_agent
from agent_inclusion_lab.evals.inclusion_eval import evaluate_text
from agent_inclusion_lab.skills.document_loader import load_text
from agent_inclusion_lab.workflow import run_inclusion_workflow


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="eh",
        description="CLI for the agent inclusion workshop.",
    )
    subparsers = parser.add_subparsers(dest="command", required=False)

    subparsers.add_parser("health", help="Run environment health checks.")
    subparsers.add_parser("baseline", help="Run baseline draft and score.")
    subparsers.add_parser("reviewed", help="Run baseline and review stages and compare baseline vs reviewed scores.")
    subparsers.add_parser("evals", help="Run LLM judge evaluation checks.")
    ui_parser = subparsers.add_parser("ui", help="Launch Chainlit UI.")
    ui_parser.add_argument("--host", default="127.0.0.1", help="Chainlit host (default: 127.0.0.1)")
    ui_parser.add_argument("--port", default="8000", help="Chainlit port (default: 8000)")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        raise SystemExit(0)

    handlers: dict[str, Callable[[], int]] = {
        "health": _run_health,
        "baseline": _run_baseline,
        "reviewed": _run_reviewed,
        "evals": _run_evals,
        "ui": lambda: _run_ui(host=args.host, port=args.port),
    }
    exit_code = handlers[args.command]()
    raise SystemExit(exit_code)


def _resolve_project_root() -> Path:
    cwd = Path.cwd()
    if (cwd / "data" / "legacy" / "hiring_guidelines_legacy.md").exists():
        return cwd
    return Path(__file__).resolve().parents[2]


def _load_sources() -> tuple[Path, str]:
    root = _resolve_project_root()
    legacy = root / "data" / "legacy" / "hiring_guidelines_legacy.md"
    clean = load_text(root / "data" / "clean" / "inclusive_hiring_principles.md")
    return legacy, clean


def _run_baseline() -> int:
    legacy, _ = _load_sources()
    baseline_output = run_baseline_agent(legacy)
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
    return 0


def _run_reviewed() -> int:
    legacy, clean = _load_sources()
    result = run_inclusion_workflow(legacy, clean)

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
    return 0


def _run_evals() -> int:
    legacy, clean = _load_sources()
    result = run_inclusion_workflow(legacy, clean)
    baseline_eval = result.baseline_eval
    rewritten_eval = result.rewritten_eval

    print("version,overall_score,overall_pass")
    print(f"baseline,{baseline_eval['overall_score']},{baseline_eval['overall_pass']}")
    print(f"rewritten,{rewritten_eval['overall_score']},{rewritten_eval['overall_pass']}")
    print("")
    print("version,eval_name,score,pass")
    for version, report in [("baseline", baseline_eval), ("rewritten", rewritten_eval)]:
        for item in report["evals"]:
            print(f"{version},{item['eval_name']},{item['score']},{item['pass']}")
    return 0


def _run_health() -> int:
    symbols = _health_symbols()
    root = _resolve_project_root()
    remediation = {
        "python_version": "Install Python 3.11+ and retry.",
        "uv_installed": "Install uv: https://docs.astral.sh/uv/getting-started/installation/",
        "env_example_exists": "Restore .env.example from repository root.",
        "legacy_data_exists": "Ensure data/legacy/hiring_guidelines_legacy.md exists.",
        "clean_data_exists": "Ensure data/clean/inclusive_hiring_principles.md exists.",
        "package_import": "Run `uv sync` to install project dependencies.",
        "chainlit_import": "Run `uv sync` to install Chainlit.",
        "foundry_config": "Set FOUNDRY_MODEL_DEPLOYMENT and one endpoint variable in .env.",
        "foundry_auth_config": "Set FOUNDRY_API_KEY or configure Azure Identity credentials.",
    }
    checks: list[tuple[str, bool, str]] = [
        (
            "python_version",
            sys.version_info >= (3, 11),
            f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        ),
        ("uv_installed", shutil.which("uv") is not None, "uv in PATH"),
        ("env_example_exists", (root / ".env.example").exists(), str(root / ".env.example")),
        (
            "legacy_data_exists",
            (root / "data" / "legacy" / "hiring_guidelines_legacy.md").exists(),
            "data/legacy/hiring_guidelines_legacy.md",
        ),
        (
            "clean_data_exists",
            (root / "data" / "clean" / "inclusive_hiring_principles.md").exists(),
            "data/clean/inclusive_hiring_principles.md",
        ),
    ]

    checks.append(_import_check("agent_inclusion_lab", "package_import"))
    checks.append(_import_check("chainlit", "chainlit_import"))

    deployment_present = bool(os.getenv("FOUNDRY_MODEL_DEPLOYMENT"))
    endpoint_present = bool(
        os.getenv("FOUNDRY_OPENAI_ENDPOINT")
        or os.getenv("FOUNDRY_PROJECT_ENDPOINT")
        or os.getenv("FOUNDRY_ENDPOINT")
    )
    checks.append(
        (
            "foundry_config",
            deployment_present and endpoint_present,
            "deployment + endpoint present"
            if deployment_present and endpoint_present
            else "missing FOUNDRY_MODEL_DEPLOYMENT or endpoint config",
        )
    )
    checks.append(
        (
            "foundry_auth_config",
            bool(os.getenv("FOUNDRY_API_KEY")) or bool(os.getenv("AZURE_CLIENT_ID")),
            "API key or Azure Identity hints present"
            if (bool(os.getenv("FOUNDRY_API_KEY")) or bool(os.getenv("AZURE_CLIENT_ID")))
            else "set FOUNDRY_API_KEY or configure Azure Identity credentials",
        )
    )

    print(f"{symbols['title']} Inclusion Lab Health Check")
    print("--------------------------------")
    for name, ok, details in checks:
        icon = symbols["pass"] if ok else symbols["fail"]
        status = "PASS" if ok else "FAIL"
        print(f"{icon} {name}: {status} - {details}")

    failed = [(name, details) for name, ok, details in checks if not ok]
    if not failed:
        print(f"\n{symbols['success']} All checks passed. You're ready to run the workflow.")
        return 0

    print(f"\n{symbols['fix']} Remediation steps:")
    for name, _details in failed:
        hint = remediation.get(name, "Review the configuration and retry.")
        print(f"- {name}: {hint}")
    return 1


def _print_ui_banner() -> None:
    banner = r"""
  ______                                        _   _ _____ ____
 |  ____|                                      | | | | ____|  _ \
 | |__   _ __ ___  _ __   _____      _____ _ __| |_| |  _| | |_) |
 |  __| | '_ ` _ \| '_ \ / _ \ \ /\ / / _ \ '__|  _  | |___|  _ <
 | |____| | | | | | |_) | (_) \ V  V /  __/ |  | | | |_____| | \ \
 |______|_| |_| |_| .__/ \___/ \_/\_/ \___|_|  |_| |_|     |_|  \_\
                   | |
                   |_|        * * *  2 0 2 6  * * *
"""
    print(banner)
    print("        EmpowerHER 2026 - Inclusion Lab Web UI\n")


def _run_ui(host: str, port: str) -> int:
    _print_ui_banner()
    root = _resolve_project_root()
    app_path = root / "chainlit_app.py"
    if not app_path.exists():
        print(f"[FAIL] chainlit_app.py not found at {app_path}")
        return 1
    command = [
        sys.executable,
        "-m",
        "chainlit",
        "run",
        str(app_path),
        "--host",
        host,
        "--port",
        str(port),
        "-w",
    ]
    return subprocess.call(command)


def _import_check(module_name: str, check_name: str) -> tuple[str, bool, str]:
    try:
        importlib.import_module(module_name)
        return (check_name, True, f"{module_name} importable")
    except Exception as exc:
        return (check_name, False, str(exc))


def _health_symbols() -> dict[str, str]:
    preferred = {
        "title": "🩺",
        "pass": "✅",
        "fail": "❌",
        "success": "🎉",
        "fix": "🛠️",
    }
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        for symbol in preferred.values():
            symbol.encode(encoding)
    except Exception:
        return {
            "title": "[HEALTH]",
            "pass": "[OK]",
            "fail": "[FAIL]",
            "success": "[READY]",
            "fix": "[FIX]",
        }
    return preferred


if __name__ == "__main__":
    main()
