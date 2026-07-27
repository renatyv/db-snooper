from __future__ import annotations

from collections.abc import Callable
from typing import Any

from sqlalchemy import Table, desc, func, select, text
from sqlalchemy.engine import Connection
from sqlalchemy.schema import CreateIndex, CreateTable

from db_snooper import query_timeout
from db_snooper.database_stats import estimate_row_count, get_indexed_column_names
from db_snooper.profiling.columns import (
    JSON_MAX_VALUE_BYTES,
    get_unique_column_names,
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


def profile_table_from_stats(table: Table, estimate: int) -> list[str]:
    # DDL (emitted separately by profile_database) already lists the columns,
    # so no further queries are needed here.
    return [
        f"-- total rows≈{estimate} "
        "(estimated from catalog stats; row/column profiling skipped)"
    ]


def profile_table(
    conn: Connection,
    table: Table,
    options: ProfileOptions,
    report_column: Callable[[str], None] | None = None,
) -> list[str]:
    estimate = estimate_row_count(conn, table)
    if estimate is not None and estimate >= options.large_table_threshold:
        return profile_table_from_stats(table, estimate)
    try:
        total_rows = query_timeout.execute(
            conn, select(func.count()).select_from(table)
        ).scalar_one()
    except query_timeout.QueryTimeout:
        return [f"-- {table.name}: skipped (row count query timeout)"]
    lines = [f"-- total rows={total_rows}"]
    if total_rows <= options.small_table_threshold:
        marker = (
            "ALL_ROWS" if total_rows <= options.sample_row_limit else "SAMPLED_ROWS"
        )
        lines.append(f"-- {marker}: {table.name}")
        sampled: list[dict[str, Any]] = []
        with query_timeout.metric(conn, [], "sampled rows"):
            sampled = sample_rows(conn, table, options.sample_row_limit)
        for row in sampled:
            lines.append(f"-- row: {json_dumps(row)}")
        return lines

    lines.append(f"-- LATEST_ROWS: {table.name}")
    latest: list[dict[str, Any]] = []
    with query_timeout.metric(conn, [], "latest rows"):
        latest = latest_rows(conn, table, 3)
    for row in latest:
        lines.append(f"-- row: {json_dumps(row)}")

    lines.append(f"-- RANDOM_ROWS: {table.name}")
    random_sample: list[dict[str, Any]] = []
    with query_timeout.metric(conn, [], "random rows"):
        random_sample = random_rows(conn, table, 5)
    for row in random_sample:
        lines.append(f"-- row: {json_dumps(row)}")

    unique_columns = get_unique_column_names(table)
    indexed_columns = get_indexed_column_names(table)
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
