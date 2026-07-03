from __future__ import annotations

import argparse
import shutil
from importlib import resources
from pathlib import Path

from db_snooper import profiler, schema_linker

SKILL_NAME = "db-snooper-context"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Snoop through databases and generate LLM-ready SQL context.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("profile", help="Generate a SQL profile for a database.")
    subparsers.add_parser("links", help="Generate Markdown schema join links for a database.")
    skill_parser = subparsers.add_parser("skill", help="Show or install the bundled agent skill.")
    skill_subparsers = skill_parser.add_subparsers(dest="skill_command", required=True)
    skill_subparsers.add_parser("path", help="Print the bundled skill file path.")
    install_parser = skill_subparsers.add_parser("install", help="Copy the bundled skill into a skills directory.")
    install_parser.add_argument("target_dir", help="Directory that contains agent skill folders.")
    install_parser.add_argument("--force", action="store_true", help="Overwrite an existing db-snooper skill folder.")
    return parser


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        import sys

        argv = sys.argv[1:]
    if argv and argv[0] == "profile":
        return profiler.main(argv[1:], prog="db-snooper profile")
    if argv and argv[0] == "links":
        return schema_linker.main(argv[1:], prog="db-snooper links")
    if argv and argv[0] == "skill":
        return skill_main(argv[1:])

    parser = build_arg_parser()
    parser.parse_args(argv)
    return 0


def skill_main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(["skill", *(argv or [])])
    skill_dir = resources.files("db_snooper").joinpath("skills", SKILL_NAME)

    if args.skill_command == "path":
        print(skill_dir.joinpath("SKILL.md"))
        return 0

    target_dir = Path(args.target_dir)
    target_skill_dir = target_dir / SKILL_NAME
    if target_skill_dir.exists():
        if not args.force:
            parser.error(f"{target_skill_dir} already exists; pass --force to replace it")
        if target_skill_dir.is_dir():
            shutil.rmtree(target_skill_dir)
        else:
            target_skill_dir.unlink()
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(skill_dir, target_skill_dir)
    print(target_skill_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
