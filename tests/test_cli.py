from __future__ import annotations

import os
import subprocess
import sys


def test_cli_help() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "agent_inclusion_lab.cli", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0
    assert "usage: eh" in completed.stdout
    assert "ui" in completed.stdout


def test_cli_no_args_shows_help() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "agent_inclusion_lab.cli"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0
    assert "usage: eh" in completed.stdout


def test_cli_health() -> None:
    env = dict(os.environ)
    env.update(
        {
        "FOUNDRY_MODEL_DEPLOYMENT": "demo-deployment",
        "FOUNDRY_PROJECT_ENDPOINT": "https://example.services.ai.azure.com/api/projects/demo",
        "FOUNDRY_API_KEY": "demo-key",
        }
    )
    completed = subprocess.run(
        [sys.executable, "-m", "agent_inclusion_lab.cli", "health"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "Inclusion Lab Health Check" in completed.stdout
