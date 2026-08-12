from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from sqlalchemy import Table, desc, func, select
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError

from db_snooper import query_timeout
from db_snooper.contracts import ProfileOptions
from db_snooper.database_stats import (
    estimate_row_count,
    get_catalog_column_stats,
    get_indexed_column_names,
)
from db_snooper.profiling.columns import (
    JSON_MAX_VALUE_BYTES,
    continuation_line,
    format_value,
    format_value_counts,
    get_unique_column_names,
    is_numeric,
    json_dumps,
    jsonable,
    profile_column,
)
from db_snooper.shared import is_sensitive

# Section headings emitted inside each table profile. The table name is the
# top-level heading, so these nest one level below it.
ROWS_HEADING = "## Rows"
ALL_ROWS_HEADING = "## All rows"
COLUMNS_HEADING = "## Columns"
INDEXES_HEADING = "## Indexes"


@dataclass
class TableProfile:
    """Structured profile for a single table, split into renderable sections.

    ``rows_heading``/``rows_lines`` carry the sampled-rows section (``## Rows``
    for larger tables with a total + latest/sample table, ``## All rows`` for
    small tables that dump every row). ``columns_lines`` carries the per-column
    profile section (``## Columns``); it is empty for small tables and for
    tables whose column profiling was skipped.
    """

    rows_heading: str | None
    rows_lines: list[str]
    columns_lines: list[str]


@dataclass(frozen=True)
class Relationship:
    """One foreign-key edge in the schema graph.

    ``constrained_*`` is the local (child) side and ``referred_*`` is the remote
    (parent) side. ``referred_schema`` is the parent table's schema, or ``None``
    when it matches the child's schema or the dialect omits it.
    """

    constrained_table: str
    constrained_columns: tuple[str, ...]
    referred_table: str
    referred_columns: tuple[str, ...]
    referred_schema: str | None

    @property
    def is_composite(self) -> bool:
        return len(self.constrained_columns) > 1


def collect_relationships(
    inspector: Any, tables: list[str], schema: str | None
) -> list[Relationship]:
    """Gather every foreign key declared on ``tables`` (catalog metadata only).

    No row scans: this reads each table's FK catalog entry. A table whose FK
    metadata can't be read is skipped so one unreadable table never hides the
    rest of the relationships section. Only outgoing edges from the profiled
    tables are returned; incoming edges from non-profiled tables are not.
    """
    relationships: list[Relationship] = []
    for table_name in tables:
        try:
            foreign_keys = inspector.get_foreign_keys(table_name, schema=schema)
        except (SQLAlchemyError, NotImplementedError):
            continue
        for fk in foreign_keys:
            constrained = tuple(fk.get("constrained_columns") or ())
            referred = tuple(fk.get("referred_columns") or ())
            referred_table = fk.get("referred_table") or ""
            if not constrained or not referred or not referred_table:
                continue
            relationships.append(
                Relationship(
                    constrained_table=table_name,
                    constrained_columns=constrained,
                    referred_table=referred_table,
                    referred_columns=referred,
                    referred_schema=fk.get("referred_schema"),
                )
            )
    return relationships


def format_relationships(
    relationships: list[Relationship], schema: str | None
) -> list[str]:
    """Render foreign keys as ``- parent.col ← child.col`` bullets.

    The parent (referenced) column leads each line and the arrow points back
    at the children that reference it, so a column referenced by many tables
    reads as ``- parent.col ← child1.col, child2.col``. The arrow always
    points parent ← child regardless of how many children there are, keeping
    the section's direction consistent. Lines are sorted by parent, turning
    the section into an index of "what references each parent column".

    Composite keys render as ``table.(c1, c2)``. The parent table is
    schema-qualified only when it lives in a different schema than the one
    being profiled, keeping the common single-schema case compact.
    """
    groups: dict[str, list[Relationship]] = {}
    for rel in relationships:
        groups.setdefault(_parent_display(rel, schema), []).append(rel)

    lines: list[str] = []
    for parent, rels in sorted(groups.items()):
        rels.sort(key=lambda r: (r.constrained_table, r.constrained_columns))
        children: list[str] = []
        for rel in rels:
            child = _format_relationship_side(
                rel.constrained_table, rel.constrained_columns
            )
            if child not in children:
                children.append(child)
        lines.append(f"- {parent} ← {', '.join(children)}")
    return lines


def _format_relationship_side(table: str, columns: tuple[str, ...]) -> str:
    if len(columns) == 1:
        return f"{table}.{columns[0]}"
    return f"{table}.({', '.join(columns)})"


def _parent_display(rel: Relationship, schema: str | None) -> str:
    """Render the parent (referred) side of ``rel``, schema-qualifying it only
    when it lives outside the schema being profiled."""
    parent_table = rel.referred_table
    if rel.referred_schema and rel.referred_schema != schema:
        parent_table = f"{rel.referred_schema}.{rel.referred_table}"
    return _format_relationship_side(parent_table, rel.referred_columns)


@dataclass
class TableSizeInfo:
    """Resolved row-count information for a table.

    ``total_rows`` is an exact ``COUNT(*)`` when available; it is ``None`` for
    catalog-profiled large tables (where the count query is skipped) and for
    timed-out count queries.
    """

    total_rows: int | None
    estimate: int | None
    is_large: bool
    timed_out: bool

    @property
    def is_empty(self) -> bool:
        return self.total_rows == 0

    def all_rows_listed(self, options: ProfileOptions) -> bool:
        """True when the table is small enough that every row is dumped.

        Empty tables return False: with no rows dumped, nothing reveals the
        schema, so the CREATE TABLE is still required (when the table is
        included at all).
        """
        if self.total_rows is None or self.is_large or self.timed_out:
            return False
        if self.total_rows == 0:
            return False
        return self.total_rows <= options.small_table_threshold


def resolve_table_size(
    conn: Connection, table: Table, options: ProfileOptions
) -> TableSizeInfo:
    """Determine a table's row count once so DDL and profiling decisions share it."""
    estimate = estimate_row_count(conn, table)
    if estimate is not None and estimate >= options.large_table_threshold:
        return TableSizeInfo(
            total_rows=None, estimate=estimate, is_large=True, timed_out=False
        )
    if conn.dialect.name == "bigquery" and estimate is not None:
        return TableSizeInfo(
            total_rows=estimate, estimate=estimate, is_large=False, timed_out=False
        )
    try:
        total_rows = query_timeout.execute(
            conn, select(func.count()).select_from(table), options.query_timeout
        ).scalar_one()
    except query_timeout.QueryTimeout:
        return TableSizeInfo(
            total_rows=None, estimate=estimate, is_large=False, timed_out=True
        )
    return TableSizeInfo(
        total_rows=total_rows, estimate=estimate, is_large=False, timed_out=False
    )


def profile_table_from_stats(
    conn: Connection, table: Table, estimate: int
) -> TableProfile:
    # The table is too large to scan, but its catalog stats are free. Emit a
    # per-column summary derived entirely from those stats.
    rows_lines = [
        f"- total≈{estimate} (estimated from db stats; row/column profiling skipped)"
    ]
    columns_lines: list[str] = []
    catalog = get_catalog_column_stats(conn, table, estimate)
    for column in table.columns:
        stat = catalog.get(column.name)
        if stat is None:
            continue
        columns_lines.extend(_catalog_column_lines(column, stat, estimate))
    return TableProfile(
        rows_heading=ROWS_HEADING,
        rows_lines=rows_lines,
        columns_lines=columns_lines,
    )


def _catalog_column_lines(column: Any, stat: Any, estimate: int) -> list[str]:
    parts: list[str] = []
    if stat.null_frac is not None:
        nulls = round(stat.null_frac * estimate)
        parts.extend((f"nulls≈{nulls}", f"non_nulls≈{estimate - nulls}"))
    if stat.distinct is not None:
        parts.append(f"distinct≈{stat.distinct}")
    has_numeric = (
        is_numeric(column) and stat.min_value is not None and stat.max_value is not None
    )
    # Top values can expose real column values, so suppress them for sensitive
    # columns (mirrors the exact profiling path).
    has_top_values = bool(stat.top_values) and not is_sensitive(column.name)
    lines: list[str] = []
    if parts or has_numeric or has_top_values:
        # Emit a header so the continuation lines below are never orphaned,
        # even when null/distinct stats are absent but min/max or top_values
        # are available.
        lines.append(
            f"- {column.name} (from db stats): {', '.join(parts)}"
            if parts
            else f"- {column.name} (from db stats):"
        )
    if has_numeric:
        lines.append(
            continuation_line(
                "numeric",
                f"min≈{format_value(stat.min_value)}, max≈{format_value(stat.max_value)}",
            )
        )
    if has_top_values:
        lines.append(
            continuation_line("top_values", format_value_counts(list(stat.top_values)))
        )
    return lines


def _format_cell(value: Any) -> str:
    """Render a sampled value as a markdown-table cell.

    ``None`` becomes ``null``; booleans become lowercase ``true``/``false``;
    containers use compact JSON. Pipes are escaped and newlines collapsed so a
    value can never break the surrounding table row.
    """
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        try:
            text = json_dumps(value)
        except (TypeError, ValueError):
            text = str(value)
    else:
        text = format_value(value)
    return str(text).replace("|", "\\|").replace("\n", " ")


def _format_rows_table(
    column_names: list[str],
    rows: list[dict[str, Any]],
    column_labels: list[str],
) -> list[str]:
    """Render sampled rows as a transposed markdown table.

    Each table column becomes a row; each sampled row becomes a column. The
    first header cell is ``column`` and the rest are ``column_labels`` (e.g.
    ``latest``/``sample`` for larger tables or ``row 1``..``row N`` for small
    tables that dump every row).
    """
    if not rows:
        return ["- (no rows sampled)"]
    width = 1 + len(column_labels)
    lines = [
        "| column | " + " | ".join(column_labels) + " |",
        "|" + "|".join(["---"] * width) + "|",
    ]
    for name in column_names:
        cells = [_format_cell(row.get(name)) for row in rows]
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    return lines


def profile_table(
    conn: Connection,
    table: Table,
    options: ProfileOptions,
    report_column: Callable[[str], None] | None = None,
    size_info: TableSizeInfo | None = None,
) -> TableProfile:
    if size_info is None:
        size_info = resolve_table_size(conn, table, options)
    if size_info.is_large:
        return profile_table_from_stats(conn, table, size_info.estimate)
    if size_info.timed_out:
        return TableProfile(
            rows_heading=None,
            rows_lines=[f"- {table.name}: skipped (row count query timeout)"],
            columns_lines=[],
        )
    total_rows = size_info.total_rows
    if total_rows is None:
        # Unreachable: is_large/timed_out return early above.
        return TableProfile(
            rows_heading=None,
            rows_lines=[f"- {table.name}: skipped (row count unavailable)"],
            columns_lines=[],
        )

    column_names = [column.name for column in table.columns]

    if total_rows <= options.small_table_threshold:
        sampled: list[dict[str, Any]] = []
        with query_timeout.metric([], "sampled rows"):
            sampled = sample_rows(
                conn, table, options.small_table_threshold, options.query_timeout
            )
        labels = [f"row {index + 1}" for index in range(len(sampled))]
        rows_lines = _format_rows_table(column_names, sampled, labels)
        # Every row fits: we only reach here when total_rows <= threshold, and
        # the LIMIT is that same threshold, so the rows alone expose the count
        # and schema. No total is printed and the section is labelled "All
        # rows". The length guard is defensive against rows vanishing between
        # the COUNT and the SELECT.
        if sampled and len(sampled) >= total_rows:
            return TableProfile(
                rows_heading=ALL_ROWS_HEADING,
                rows_lines=rows_lines,
                columns_lines=[],
            )
        return TableProfile(
            rows_heading=ROWS_HEADING,
            rows_lines=[f"- total={total_rows}", "", *rows_lines],
            columns_lines=[],
        )

    # Larger table: total + latest + random rows in one transposed table,
    # then per-column profiles.
    rows_lines = [f"- total={total_rows}"]
    latest: list[dict[str, Any]] = []
    with query_timeout.metric([], "latest rows"):
        latest = latest_rows(
            conn, table, options.latest_row_limit, options.query_timeout
        )
    random_sample: list[dict[str, Any]] = []
    with query_timeout.metric([], "random rows"):
        random_sample = random_rows(
            conn, table, options.random_row_limit, options.query_timeout
        )

    combined = list(latest) + list(random_sample)
    labels = ["latest"] * len(latest) + ["sample"] * len(random_sample)
    rows_lines.append("")
    if combined:
        rows_lines.extend(_format_rows_table(column_names, combined, labels))
    else:
        rows_lines.append("- (no rows sampled)")

    unique_columns = get_unique_column_names(table)
    indexed_columns = get_indexed_column_names(table)
    # Catalog stats are fetched once per table (a single cheap catalog read) and
    # reused across columns: for catalog top_values on large indexed columns and
    # as a labeled fallback when an exact metric is skipped.
    catalog_stats = (
        get_catalog_column_stats(conn, table, total_rows)
        if total_rows > 100_000
        else {}
    )
    columns_lines: list[str] = []
    for column in table.columns:
        if report_column is not None:
            report_column(column.name)
        columns_lines.extend(
            profile_column(
                conn,
                table,
                column,
                int(total_rows),
                unique_columns,
                indexed_columns,
                options.query_timeout,
                catalog_stat=catalog_stats.get(column.name),
            )
        )
    return TableProfile(
        rows_heading=ROWS_HEADING,
        rows_lines=rows_lines,
        columns_lines=columns_lines,
    )


def sample_rows(
    conn: Connection, table: Table, limit: int, timeout_seconds: int = 0
) -> list[dict[str, Any]]:
    order_columns = _order_columns(conn, table)
    statement = select(table).order_by(*order_columns).limit(limit)
    return rows_for_statement(conn, table, statement, timeout_seconds)


def latest_rows(
    conn: Connection, table: Table, limit: int, timeout_seconds: int = 0
) -> list[dict[str, Any]]:
    order_columns = _order_columns(conn, table)
    statement = (
        select(table).order_by(*(desc(column) for column in order_columns)).limit(limit)
    )
    return rows_for_statement(conn, table, statement, timeout_seconds)


def _order_columns(conn: Connection, table: Table) -> list[Any]:
    columns = list(table.primary_key.columns) or list(table.columns)
    if conn.dialect.name != "bigquery":
        return columns
    unsupported = {"ARRAY", "GEOGRAPHY", "JSON", "STRUCT"}
    return [
        column
        for column in columns
        if type(column.type).__name__.upper() not in unsupported
    ]


def random_rows(
    conn: Connection, table: Table, limit: int, timeout_seconds: int = 0
) -> list[dict[str, Any]]:
    random_function = (
        func.rand()
        if conn.dialect.name in {"bigquery", "mysql", "mariadb"}
        else func.random()
    )
    statement = select(table).order_by(random_function).limit(limit)
    return rows_for_statement(conn, table, statement, timeout_seconds)


def rows_for_statement(
    conn: Connection, table: Table, statement: Any, timeout_seconds: int = 0
) -> list[dict[str, Any]]:
    rows = []
    for row in query_timeout.execute(conn, statement, timeout_seconds).mappings():
        output: dict[str, Any] = {}
        for column in table.columns:
            value = row[column.name]
            if is_sensitive(column.name):
                output[column.name] = "[REDACTED]"
            else:
                output[column.name] = bounded_value(value)
        rows.append(output)
    return rows


def bounded_value(value: Any) -> Any:
    """JSON-encode and cap oversized container values so sampled-row output
    cannot be dominated by a single huge JSON/ARRAY value."""
    encoded = jsonable(value)
    if isinstance(encoded, (dict, list)):
        try:
            serialized = json_dumps(encoded)
        except (TypeError, ValueError):
            return encoded
        if len(serialized) > JSON_MAX_VALUE_BYTES:
            return f"[LARGE_JSON:{len(serialized)}]"
    return encoded
