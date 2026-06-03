from __future__ import annotations

import importlib
import os
import shutil
import sys
from pathlib import Path


def run_checks() -> list[tuple[str, bool, str]]:
    root = Path(__file__).resolve().parents[1]

    checks: list[tuple[str, bool, str]] = []
    checks.append(
        (
            "python_version",
            sys.version_info >= (3, 11),
            f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        )
    )
    checks.append(("uv_installed", shutil.which("uv") is not None, "uv in PATH"))
    checks.append(
        (
            "env_example_exists",
            (root / ".env.example").exists(),
            str(root / ".env.example"),
        )
    )
    checks.append(
        (
            "legacy_data_exists",
            (root / "data" / "legacy" / "hiring_guidelines_legacy.md").exists(),
            "data/legacy/hiring_guidelines_legacy.md",
        )
    )
    checks.append(
        (
            "clean_data_exists",
            (root / "data" / "clean" / "inclusive_hiring_principles.md").exists(),
            "data/clean/inclusive_hiring_principles.md",
        )
    )

    try:
        importlib.import_module("agent_inclusion_lab")
        checks.append(("package_import", True, "agent_inclusion_lab importable"))
    except Exception as exc:
        checks.append(("package_import", False, str(exc)))

    try:
        importlib.import_module("chainlit")
        checks.append(("chainlit_import", True, "chainlit importable"))
    except Exception as exc:
        checks.append(("chainlit_import", False, str(exc)))

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

    return checks


def main() -> None:
    checks = run_checks()
    print("check,result,details")
    for name, ok, details in checks:
        print(f"{name},{'PASS' if ok else 'FAIL'},{details}")

    if not all(ok for _, ok, _ in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
