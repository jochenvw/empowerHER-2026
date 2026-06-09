from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 2:
        raise RuntimeError("Usage: read_job_post.py <path>")
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    sys.stdout.buffer.write(text.encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
