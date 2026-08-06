from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from sqlalchemy import Table, desc, func, select, text
from sqlalchemy.engine import Connection
from sqlalchemy.schema import CreateIndex, CreateTable

from db_snooper import query_timeout
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
from db_snooper.profiling.models import ProfileOptions
from db_snooper.shared import is_sensitive


def get_table_ddl(conn: Connection, table: Table) -> list[str]:
    dialect_name = conn.dialect.name
    if dialect_name == "sqlite":
        return get_sqlite_ddl(conn, table.name)
    if dialect_name in {"mysql", "mariadb"}:
        return get_mysql_ddl(conn, table)
    return get_reflected_ddl(conn, table)


def get_sqlite_ddl(conn: Connection, table_name: str) -> list[str]:
    table_sql = conn.execute(
        text("select sql from sqlite_master where type = 'table' and name = :name"),
        {"name": table_name},
    ).scalar_one_or_none()
    index_sql = conn.execute(
        text(
            "select sql from sqlite_master "
            "where type = 'index' and tbl_name = :name and sql is not null "
            "order by name"
        ),
        {"name": table_name},
    ).scalars()

    lines: list[str] = []
    if table_sql:
        lines.append(ensure_semicolon(str(table_sql)))
    lines.extend(ensure_semicolon(str(sql)) for sql in index_sql)
    return lines


def get_mysql_ddl(conn: Connection, table: Table) -> list[str]:
    quoted_table = conn.dialect.identifier_preparer.format_table(table)
    row = conn.exec_driver_sql(f"SHOW CREATE TABLE {quoted_table}").first()
    if row is None:
        return []
    return [ensure_semicolon(str(row[1]))]


def get_reflected_ddl(conn: Connection, table: Table) -> list[str]:
    lines = [ensure_semicolon(str(CreateTable(table).compile(conn)))]
    for index in sorted(table.indexes, key=lambda idx: idx.name or ""):
        lines.append(ensure_semicolon(str(CreateIndex(index).compile(conn))))
    return lines


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
        return self.total_rows <= min(
            options.small_table_threshold, options.sample_row_limit
        )


def resolve_table_size(
    conn: Connection, table: Table, options: ProfileOptions
) -> TableSizeInfo:
    """Determine a table's row count once so DDL and profiling decisions share it."""
    estimate = estimate_row_count(conn, table)
    if estimate is not None and estimate >= options.large_table_threshold:
        return TableSizeInfo(
            total_rows=None, estimate=estimate, is_large=True, timed_out=False
        )
    try:
        total_rows = query_timeout.execute(
            conn, select(func.count()).select_from(table)
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
) -> list[str]:
    # The table is too large to scan, but its catalog stats are free. Emit a
    # per-column summary derived entirely from those stats.
    lines = [
        f"-- total rows≈{estimate} "
        "(estimated from db stats; row/column profiling skipped)"
    ]
    catalog = get_catalog_column_stats(conn, table, estimate)
    for column in table.columns:
        stat = catalog.get(column.name)
        if stat is None:
            continue
        lines.extend(_catalog_column_lines(column, stat, estimate))
    return lines


def _catalog_column_lines(column: Any, stat: Any, estimate: int) -> list[str]:
    parts: list[str] = []
    if stat.null_frac is not None:
        nulls = round(stat.null_frac * estimate)
        parts.extend((f"nulls≈{nulls}", f"non_nulls≈{estimate - nulls}"))
    if stat.distinct is not None:
        parts.append(f"distinct≈{stat.distinct}")
    has_numeric = (
        is_numeric(column)
        and stat.min_value is not None
        and stat.max_value is not None
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
            f"-- {column.name} (from db stats): {', '.join(parts)}"
            if parts
            else f"-- {column.name} (from db stats):"
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


def profile_table(
    conn: Connection,
    table: Table,
    options: ProfileOptions,
    report_column: Callable[[str], None] | None = None,
    size_info: TableSizeInfo | None = None,
) -> list[str]:
    if size_info is None:
        size_info = resolve_table_size(conn, table, options)
    if size_info.is_large:
        return profile_table_from_stats(conn, table, size_info.estimate)
    if size_info.timed_out:
        return [f"-- {table.name}: skipped (row count query timeout)"]
    total_rows = size_info.total_rows
    if total_rows is None:
        # Unreachable: is_large/timed_out return early above.
        return [f"-- {table.name}: skipped (row count unavailable)"]
    if total_rows <= options.small_table_threshold:
        if total_rows <= options.sample_row_limit:
            # Every row is listed below, so the rows themselves expose both the
            # count and the schema: the CREATE TABLE is omitted and no row count
            # is printed. Lead with the table name as a header (no DDL here).
            lines = [f"-- {table.name}", "-- all rows"]
        else:
            # More rows than the sample cap: only the first rows are listed, so
            # keep the total count. The CREATE TABLE above already names the
            # table.
            lines = [f"-- first {options.sample_row_limit} of {total_rows} rows"]
        sampled: list[dict[str, Any]] = []
        with query_timeout.metric(conn, [], "sampled rows"):
            sampled = sample_rows(conn, table, options.sample_row_limit)
        for row in sampled:
            lines.append(f"-- row: {json_dumps(row)}")
        return lines

    lines = [f"-- total rows={total_rows}"]
    lines.append(f"-- LATEST_ROWS: {table.name} (most recent rows listed below)")
    latest: list[dict[str, Any]] = []
    with query_timeout.metric(conn, [], "latest rows"):
        latest = latest_rows(conn, table, 3)
    for row in latest:
        lines.append(f"-- row: {json_dumps(row)}")

    lines.append(f"-- RANDOM_ROWS: {table.name} (random sample listed below)")
    random_sample: list[dict[str, Any]] = []
    with query_timeout.metric(conn, [], "random rows"):
        random_sample = random_rows(conn, table, 5)
    for row in random_sample:
        lines.append(f"-- row: {json_dumps(row)}")

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
    for column in table.columns:
        if report_column is not None:
            report_column(column.name)
        lines.extend(
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
    return lines


def sample_rows(conn: Connection, table: Table, limit: int) -> list[dict[str, Any]]:
    order_columns = list(table.primary_key.columns) or list(table.columns)
    statement = select(table).order_by(*order_columns).limit(limit)
    return rows_for_statement(conn, table, statement)


def latest_rows(conn: Connection, table: Table, limit: int) -> list[dict[str, Any]]:
    order_columns = list(table.primary_key.columns) or list(table.columns)
    statement = (
        select(table).order_by(*(desc(column) for column in order_columns)).limit(limit)
    )
    return rows_for_statement(conn, table, statement)


def random_rows(conn: Connection, table: Table, limit: int) -> list[dict[str, Any]]:
    random_function = (
        func.rand() if conn.dialect.name in {"mysql", "mariadb"} else func.random()
    )
    statement = select(table).order_by(random_function).limit(limit)
    return rows_for_statement(conn, table, statement)


def rows_for_statement(
    conn: Connection, table: Table, statement: Any
) -> list[dict[str, Any]]:
    rows = []
    for row in query_timeout.execute(conn, statement).mappings():
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


def ensure_semicolon(sql: str) -> str:
    sql = sql.rstrip()
    if not sql.endswith(";"):
        return sql + ";"
    return sql
