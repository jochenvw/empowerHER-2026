from __future__ import annotations

import importlib
import os
import shutil
import sys
from pathlib import Path


def _is_true(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def run_checks() -> list[tuple[str, bool, str]]:
    root = Path(__file__).resolve().parents[1]
    dry_run = _is_true(os.getenv("DRY_RUN", "true"))

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

    if dry_run:
        checks.append(("foundry_config", True, "DRY_RUN=true (credentials not required)"))
    else:
        required = [
            "FOUNDRY_ENDPOINT",
            "FOUNDRY_API_KEY",
            "FOUNDRY_MODEL_DEPLOYMENT",
            "FOUNDRY_PROJECT_ENDPOINT",
        ]
        missing = [name for name in required if not os.getenv(name)]
        checks.append(
            (
                "foundry_config",
                len(missing) == 0,
                "all foundry env vars present" if not missing else f"missing: {', '.join(missing)}",
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

