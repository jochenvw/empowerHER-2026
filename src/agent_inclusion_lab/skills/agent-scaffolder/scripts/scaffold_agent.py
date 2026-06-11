from __future__ import annotations

import argparse
from pathlib import Path

from agent_inclusion_lab.skills.agent_scaffolder import scaffold_agent_from_issue


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold a new agent from a GitHub issue body.")
    parser.add_argument("--issue-body-file", required=True, help="Path to a text file containing the issue body.")
    parser.add_argument("--root", default=None, help="Repository root. Defaults to the current working directory.")
    args = parser.parse_args()

    issue_body = Path(args.issue_body_file).read_text(encoding="utf-8")
    agent_dir = scaffold_agent_from_issue(issue_body, root=args.root)
    print(agent_dir)


if __name__ == "__main__":
    main()
