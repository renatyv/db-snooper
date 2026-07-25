from __future__ import annotations

import argparse

from db_snooper.linking import cli as linking_cli
from db_snooper.profiling import cli as profiling_cli


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Snoop through databases and generate LLM-ready SQL context.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("profile", help="Generate a SQL profile for a database.")
    subparsers.add_parser("links", help="Generate Markdown schema join links for a database.")
    subparsers.add_parser("skills", help="Install or list bundled agent skills.")
    return parser


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        import sys

        argv = sys.argv[1:]
    if argv and argv[0] == "profile":
        return profiling_cli.main(argv[1:], prog="db-snooper profile")
    if argv and argv[0] == "links":
        return linking_cli.main(argv[1:], prog="db-snooper links")
    if argv and argv[0] == "skills":
        from db_snooper import agent_skills

        return agent_skills.main(argv[1:], prog="db-snooper skills")
    parser = build_arg_parser()
    parser.parse_args(argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
