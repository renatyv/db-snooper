from __future__ import annotations

import hashlib
from dataclasses import dataclass

from db_snooper._version import __version__


@dataclass(frozen=True)
class TocEntry:
    """One indexed top-level section: label plus its line range in the profile."""

    label: str
    start_line: int
    end_line: int


class TocTracker:
    """Record section line ranges from the writer's own append positions.

    The profile is assembled as a flat list of lines and finalized as
    ``"\\n".join(lines).rstrip() + "\\n"``, so a section whose first line is
    about to be appended starts at 1-based line ``len(lines) + 1``, and its
    end is the section's last non-blank line (trailing blank separators are
    excluded so ranges survive the final ``rstrip``). Positions are captured
    while emitting — the finished markdown is never re-parsed — which makes
    the line numbers correct by construction.
    """

    def __init__(self, lines: list[str]) -> None:
        self._lines = lines
        self.entries: list[TocEntry] = []

    def start(self) -> int:
        """Line number the next appended line will occupy."""
        return len(self._lines) + 1

    def finish(self, label: str, start_line: int) -> None:
        """Close the section opened at ``start_line`` after its last append."""
        end_line = len(self._lines)
        while end_line > start_line and not self._lines[end_line - 1].strip():
            end_line -= 1
        if end_line >= start_line:
            self.entries.append(TocEntry(label, start_line, end_line))


def render_toc(
    entries: list[TocEntry],
    *,
    generated_at_utc: str,
    dialect: str,
    database: str,
    schema: str,
    profile_markdown: str,
) -> str:
    """Render the ``<profile>.toc.md`` sidecar for a finished profile.

    One line per top-level section — ``Relationships``, each table block,
    the trailing summary — with its exact line range. The frontmatter pins
    the indexed file by sha256 so consumers can fail fast on a stale TOC
    instead of reading line ranges that no longer match.
    """
    lines = [
        "---",
        "generator: db-snooper",
        f"version: {__version__}",
        f"generated_at_utc: {generated_at_utc}",
        f"dialect: {dialect}",
        f"database: {database}",
        f"schema: {schema}",
        f"profile_lines: {len(profile_markdown.splitlines())}",
        f"profile_sha256: {hashlib.sha256(profile_markdown.encode('utf-8')).hexdigest()}",
        "---",
        "",
    ]
    lines.extend(
        f"{entry.label}: lines {entry.start_line}-{entry.end_line}" for entry in entries
    )
    return "\n".join(lines).rstrip() + "\n"
