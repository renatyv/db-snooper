from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ai_sql_context import __version__
from ai_sql_context.models import ColumnProfile, DatabaseContext, TableProfile
from ai_sql_context.profiling import compact_value


def render_context(context: DatabaseContext) -> str:
    lines: list[str] = []
    lines.append("-- ai-sql-context")
    lines.append(f"-- version: {__version__}")
    lines.append(f"-- dialect: {context.dialect}")
    lines.append(f"-- database: {context.database}")
    lines.append("-- deterministic: true")
    lines.append("")
    lines.append("-- RELATIONSHIPS")
    if context.likely_joins:
        for join in context.likely_joins:
            lines.append(
                f"-- {join.left_table}.{join.left_column} -> {join.right_table}.{join.right_column} "
                f"[{join.confidence}; {join.evidence}]"
            )
    else:
        lines.append("-- none detected")
    lines.append("")

    for table in sorted(context.tables, key=lambda item: item.name):
        render_table(lines, table)
    return "\n".join(lines).rstrip() + "\n"


def write_context(path: Path, context: DatabaseContext) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_context(context), encoding="utf-8")


def render_table(lines: list[str], table: TableProfile) -> None:
    lines.append(f"-- TABLE: {table.name}")
    lines.append(f"-- row_count: {table.row_count}")
    if table.primary_key:
        lines.append(f"-- primary_key: {', '.join(table.primary_key)}")
    for fk in table.foreign_keys:
        lines.append(
            f"-- foreign_key {fk.name}: ({', '.join(fk.columns)}) -> "
            f"{fk.referenced_table}({', '.join(fk.referenced_columns)})"
        )
    for index in table.indexes:
        kind = "unique_index" if index.unique else "index"
        lines.append(f"-- {kind} {index.name}: ({', '.join(index.columns)})")
    lines.append(table.create_table_sql + ";")
    lines.append("")
    lines.append(f"-- PROFILE: {table.name}")
    for profile in sorted(table.column_profiles, key=lambda item: item.name):
        render_column_profile(lines, profile)
    if table.sample_rows:
        lines.append(f"-- ALL_ROWS: {table.name}")
        for row in table.sample_rows:
            encoded = {key: compact_value(value) for key, value in sorted(row.items())}
            lines.append(f"-- row: {json.dumps(encoded, sort_keys=True)}")
    lines.append("")


def render_column_profile(lines: list[str], profile: ColumnProfile) -> None:
    lines.append(
        f"-- column {profile.name}: nulls={profile.null_count}, non_nulls={profile.non_null_count}, "
        f"distinct={profile.distinct_count}"
    )
    if profile.numeric_min is not None or profile.numeric_max is not None or profile.numeric_median is not None:
        lines.append(
            f"-- column {profile.name} numeric: min={compact_value(profile.numeric_min)}, "
            f"median={compact_value(profile.numeric_median)}, max={compact_value(profile.numeric_max)}"
        )
    if profile.low_cardinality_values:
        lines.append(f"-- column {profile.name} values: {format_value_counts(profile.low_cardinality_values)}")
    elif profile.top_values:
        lines.append(f"-- column {profile.name} top_values: {format_value_counts(profile.top_values)}")
    if profile.shape:
        lines.append(f"-- column {profile.name} shape: {json.dumps(json_safe(profile.shape), sort_keys=True)}")


def format_value_counts(values: list[tuple[Any, int]]) -> str:
    return ", ".join(f"{compact_value(value)}={count}" for value, count in values)


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)
