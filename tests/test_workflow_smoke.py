from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from agent_inclusion_lab.skills.document_loader import load_text
from agent_inclusion_lab.workflow import run_inclusion_workflow


def test_workflow_smoke_dry_run(monkeypatch) -> None:
    monkeypatch.setenv("DRY_RUN", "true")
    monkeypatch.delenv("FOUNDRY_ENDPOINT", raising=False)
    monkeypatch.delenv("FOUNDRY_API_KEY", raising=False)
    monkeypatch.delenv("FOUNDRY_MODEL_DEPLOYMENT", raising=False)
    monkeypatch.delenv("FOUNDRY_PROJECT_ENDPOINT", raising=False)

    root = Path(__file__).resolve().parents[1]
    legacy = load_text(root / "data" / "legacy" / "hiring_guidelines_legacy.md")
    clean = load_text(root / "data" / "clean" / "inclusive_hiring_principles.md")

    result = run_inclusion_workflow(legacy, clean)
    assert result.baseline_eval["score"] < result.rewritten_eval["score"]


def test_scripts_execute_in_dry_run() -> None:
    root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    env["DRY_RUN"] = "true"
    env["PYTHONPATH"] = str(root / "src")

    baseline = subprocess.run(
        [sys.executable, str(root / "scripts" / "run_baseline.py")],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    reviewed = subprocess.run(
        [sys.executable, str(root / "scripts" / "run_reviewed.py")],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert baseline.returncode == 0, baseline.stderr
    assert reviewed.returncode == 0, reviewed.stderr
    assert "score=" in baseline.stdout
    assert "before=" in reviewed.stdout

