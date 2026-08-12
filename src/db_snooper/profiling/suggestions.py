from __future__ import annotations

from collections.abc import Iterable

from db_snooper.contracts import PermissionReport
from db_snooper.profiling.utility_dump import (
    dump_utility_available,
    dump_utility_name,
)


def profile_suggestions(
    reports: Iterable[PermissionReport], dialect_name: str
) -> list[str]:
    """Return actionable ways the user can make a future profile more complete."""
    suggestions: list[str] = []
    seen: set[str] = set()

    for report in reports:
        if report.inaccessible_tables:
            names = ", ".join(name for name, _ in report.inaccessible_tables)
            schema = report.schema or "<schema>"
            if report.dialect == "postgresql":
                action = (
                    f"Grant table read access: GRANT SELECT ON ALL TABLES IN SCHEMA "
                    f"{schema} TO <role>; Missing: {names}."
                )
            elif report.dialect in {"mysql", "mariadb"}:
                action = (
                    f"Grant table read access: GRANT SELECT ON `{schema}`.* TO "
                    f"'<user>'@'<host>'; Missing: {names}."
                )
            else:
                action = f"Grant SELECT access to the inaccessible tables: {names}."
            _append_once(suggestions, seen, action)

        missing_stats = sorted(
            name for name, accessible in report.stats_access.items() if not accessible
        )
        if not missing_stats:
            continue
        names = ", ".join(missing_stats)
        if report.dialect == "sqlite" and missing_stats == ["sqlite_stat1"]:
            action = (
                "Run ANALYZE on the SQLite database to populate sqlite_stat1 and "
                "improve estimates for large tables."
            )
        else:
            action = (
                f"Make database statistics readable ({names}) so large-table profiles "
                "can include estimated nulls, distinct values, ranges, and top values."
            )
        _append_once(suggestions, seen, action)

    utility = dump_utility_name(dialect_name)
    if utility is not None and not dump_utility_available(dialect_name):
        _append_once(
            suggestions,
            seen,
            f"Install {utility} and add it to PATH. It lets db-snooper recover "
            "CREATE TABLE DDL when SQLAlchemy reflection fails.",
        )

    return suggestions


def format_suggestions(suggestions: Iterable[str]) -> str:
    items = list(suggestions)
    if not items:
        return ""
    lines = ["Suggestions to improve this profile:"]
    lines.extend(f"  - {suggestion}" for suggestion in items)
    return "\n".join(lines)


def _append_once(items: list[str], seen: set[str], value: str) -> None:
    if value not in seen:
        seen.add(value)
        items.append(value)
