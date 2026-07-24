from __future__ import annotations

import argparse
import shutil
from importlib.resources import files
from pathlib import Path

SKILLS_PACKAGE_ROOT = files("db_snooper") / "skills"

TARGET_DIRS = {
    "opencode": "~/.config/opencode/skills",
    "claude": "~/.claude/skills",
    "agents": "~/.agents/skills",
}


def _bundled_skills_root() -> Path:
    return Path(str(SKILLS_PACKAGE_ROOT))


def iter_bundled_skills() -> list[tuple[str, Path]]:
    root = _bundled_skills_root()
    skills: list[tuple[str, Path]] = []
    for entry in sorted(root.iterdir()):
        skill_md = entry / "SKILL.md"
        if entry.is_dir() and skill_md.is_file():
            skills.append((entry.name, skill_md))
    return skills


def parse_frontmatter(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end: int | None = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}
    meta: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip("'\"")
    return meta


def list_skills() -> int:
    skills = iter_bundled_skills()
    if not skills:
        print("No bundled skills found.")
        return 1
    print(f"Bundled skills ({len(skills)}):")
    for name, skill_md in skills:
        description = parse_frontmatter(skill_md).get("description", "")
        print(f"\n  {name}")
        if description:
            print(f"    {description}")
    return 0


def _resolve_destinations(target: str, dest_dir: str | None) -> list[Path]:
    if dest_dir:
        return [Path(dest_dir).expanduser()]
    if target == "all":
        return [Path(path).expanduser() for path in TARGET_DIRS.values()]
    return [Path(TARGET_DIRS[target]).expanduser()]


def install_skills(target: str, dest_dir: str | None, force: bool) -> int:
    skills = iter_bundled_skills()
    if not skills:
        print("No bundled skills found.")
        return 1
    destinations = _resolve_destinations(target, dest_dir)
    installed = 0
    skipped = 0
    for dest in destinations:
        dest.mkdir(parents=True, exist_ok=True)
        for name, src in skills:
            out_dir = dest / name
            if out_dir.exists() and not force:
                print(f"  skipped   {name} -> {out_dir} (exists; use --force to overwrite)")
                skipped += 1
                continue
            if out_dir.exists():
                shutil.rmtree(out_dir)
            out_dir.mkdir(parents=True)
            shutil.copy2(src, out_dir / "SKILL.md")
            print(f"  installed {name} -> {out_dir}")
            installed += 1
    print(f"\nDone: {installed} installed, {skipped} skipped.")
    return 0


def build_arg_parser(prog: str | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=prog,
        description="Install or list the bundled agent skills that ship with db-snooper.",
    )
    sub = parser.add_subparsers(dest="skills_command", required=True)
    sub.add_parser("list", help="List bundled skills.")
    install = sub.add_parser("install", help="Copy bundled skills into an agent discovery directory.")
    install.add_argument(
        "--target",
        choices=[*TARGET_DIRS.keys(), "all"],
        default="opencode",
        help="Which agent discovery directory to install into. Default: opencode (~/.config/opencode/skills).",
    )
    install.add_argument(
        "--dir",
        help="Custom destination directory. Overrides --target.",
    )
    install.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing skill folders. By default existing folders are skipped.",
    )
    return parser


def main(argv: list[str] | None = None, prog: str | None = None) -> int:
    parser = build_arg_parser(prog=prog)
    args = parser.parse_args(argv)
    if args.skills_command == "list":
        return list_skills()
    if args.skills_command == "install":
        return install_skills(args.target, args.dir, args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
