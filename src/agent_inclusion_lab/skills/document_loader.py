from __future__ import annotations

from pathlib import Path


def load_text(path: str | Path) -> str:
    file_path = Path(path)
    return file_path.read_text(encoding="utf-8")

