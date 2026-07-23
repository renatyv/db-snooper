from __future__ import annotations

import argparse
import csv
import json
import os
import re
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import date, datetime, time, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import MetaData, Table, create_engine, desc, func, inspect, literal_column, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.schema import CreateIndex, CreateTable, UniqueConstraint
from sqlalchemy.sql.sqltypes import BigInteger, Float, Integer, Numeric, SmallInteger, String, Text

from db_snooper import __version__
from db_snooper import query_timeout
from db_snooper.connection import add_connection_arguments, list_schemas, resolve_database_url, resolve_schema
from db_snooper.progress import ProgressBar
from db_snooper.query_timeout import DEFAULT_QUERY_TIMEOUT

SENSITIVE_NAME_PARTS = ("password", "passwd", "pwd", "hash", "salt", "secret", "token")

# Tables whose catalog row estimate is at/above this count are profiled from
# internal database stats only: COUNT(*) and all per-column aggregations are
# skipped because they would be far too slow. "Hundreds of millions or more".
LARGE_TABLE_THRESHOLD = 100_000_000


@dataclass(frozen=True)
class ProfileOptions:
    small_table_threshold: int = 50
    sample_row_limit: int = 50
    large_table_threshold: int = LARGE_TABLE_THRESHOLD
    query_timeout: int = DEFAULT_QUERY_TIMEOUT
    include_tables: frozenset[str] | None = None
    exclude_tables: frozenset[str] = frozenset()
    schema: str | None = None


ProfileProgress = Callable[[int, int, str], None]


def list_schema_tables(engine: Engine, options: ProfileOptions) -> list[str]:
    inspector = inspect(engine)
    tables = sorted(inspector.get_table_names(schema=options.schema))
    if options.include_tables is not None:
        tables = [table for table in tables if table in options.include_tables]
    tables = [table for table in tables if table not in options.exclude_tables]
    return tables


def profile_database(
    engine: Engine,
    options: ProfileOptions,
    progress: ProfileProgress | None = None,
    table_names: list[str] | None = None,
) -> str:
    tables = table_names if table_names is not None else list_schema_tables(engine, options)

    database = engine.url.database or ""
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    lines = [
        "-- db-snooper",
        f"-- version: {__version__}",
        f"-- generated_at_utc: {generated_at}",
        f"-- dialect: {engine.dialect.name}",
        f"-- database: {database}",
        f"-- schema: {options.schema or engine.dialect.default_schema_name or ''}",
        "",
    ]

    with engine.connect() as conn:
        query_timeout.apply_query_timeout(conn, options.query_timeout)
        metadata = MetaData()
        for index, table_name in enumerate(tables, start=1):
            if progress is not None:
                progress(index - 1, len(tables), table_name)
            table = Table(table_name, metadata, schema=options.schema, autoload_with=conn)
            ddl = get_table_ddl(conn, table)
            lines.extend(ddl)
            if lines[-1] != "":
                lines.append("")
            def report_column(column_name: str) -> None:
                if progress is not None:
                    progress(index - 1, len(tables), f"{table_name} ({column_name})")

            lines.extend(profile_table(conn, table, options, report_column=report_column))
            lines.append("")
            lines.append("")
            if progress is not None:
                progress(index, len(tables), table_name)

    return "\n".join(lines).rstrip() + "\n"


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


def estimate_row_count(conn: Connection, table: Table) -> int | None:
    """Return a cheap catalog row-count estimate, or ``None`` if unavailable.

    Used to decide whether a full ``COUNT(*)`` scan is affordable. Any failure
    (missing stats table, stale/unknown marker, parse error) collapses to
    ``None`` so the caller falls back to an exact count.
    """
    dialect = conn.dialect.name
    schema = table.schema or conn.dialect.default_schema_name
    try:
        if dialect == "postgresql":
            return _postgres_row_estimate(conn, table.name, schema)
        if dialect in {"mysql", "mariadb"}:
            return _mysql_row_estimate(conn, table.name, schema)
        if dialect == "duckdb":
            return _duckdb_row_estimate(conn, table.name, schema)
        if dialect == "sqlite":
            return _sqlite_row_estimate(conn, table.name)
    except SQLAlchemyError:
        return None
    return None


def _postgres_row_estimate(conn: Connection, table_name: str, schema: str | None) -> int | None:
    row = conn.execute(
        text(
            "SELECT c.reltuples::bigint FROM pg_class c "
            "JOIN pg_namespace n ON n.oid = c.relnamespace "
            "WHERE c.relname = :table AND n.nspname = :schema"
        ),
        {"table": table_name, "schema": schema or "public"},
    ).one_or_none()
    if not row or row[0] is None or int(row[0]) < 0:
        return None
    return int(row[0])


def _mysql_row_estimate(conn: Connection, table_name: str, schema: str | None) -> int | None:
    schema_name = schema or conn.dialect.default_schema_name
    if not schema_name:
        return None
    value = conn.execute(
        text(
            "SELECT TABLE_ROWS FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA = :schema AND TABLE_NAME = :table"
        ),
        {"schema": schema_name, "table": table_name},
    ).scalar_one_or_none()
    if value is None:
        return None
    return int(value)


def _duckdb_row_estimate(conn: Connection, table_name: str, schema: str | None) -> int | None:
    schema_name = schema or "main"
    value = conn.execute(
        text(
            "SELECT estimated_size FROM duckdb_tables() "
            "WHERE schema_name = :schema AND table_name = :table"
        ),
        {"schema": schema_name, "table": table_name},
    ).scalar_one_or_none()
    if value is None or int(value) < 0:
        return None
    return int(value)


def _sqlite_row_estimate(conn: Connection, table_name: str) -> int | None:
    # sqlite_stat1 only exists after ANALYZE. The stat string is "N d1 d2 ..."
    # where N is the estimated number of rows in the table.
    stat = conn.execute(
        text("SELECT stat FROM sqlite_stat1 WHERE tbl = :table LIMIT 1"),
        {"table": table_name},
    ).scalar_one_or_none()
    if not stat:
        return None
    first = str(stat).split()[0]
    try:
        count = int(first)
    except ValueError:
        return None
    return count if count >= 0 else None


def profile_table_from_stats(table: Table, estimate: int) -> list[str]:
    # DDL (emitted separately by profile_database) already lists the columns,
    # so no further queries are needed here.
    return [
        f"-- total rows\u2248{estimate} "
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
        total_rows = query_timeout.execute(conn, select(func.count()).select_from(table)).scalar_one()
    except query_timeout.QueryTimeout:
        return [f"-- {table.name}: skipped (row count query timeout)"]
    lines = [f"-- total rows={total_rows}"]
    if total_rows <= options.small_table_threshold:
        marker = "ALL_ROWS" if total_rows <= options.sample_row_limit else "SAMPLED_ROWS"
        lines.append(f"-- {marker}: {table.name}")
        try:
            sampled = sample_rows(conn, table, options.sample_row_limit)
        except query_timeout.QueryTimeout:
            sampled = []
        for row in sampled:
            lines.append(f"-- row: {json_dumps(row)}")
        return lines

    lines.append(f"-- LATEST_ROWS: {table.name}")
    try:
        latest = latest_rows(conn, table, 3)
    except query_timeout.QueryTimeout:
        latest = []
    for row in latest:
        lines.append(f"-- row: {json_dumps(row)}")

    lines.append(f"-- RANDOM_ROWS: {table.name}")
    try:
        random_sample = random_rows(conn, table, 5)
    except query_timeout.QueryTimeout:
        random_sample = []
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
    statement = select(table).order_by(*(desc(column) for column in order_columns)).limit(limit)
    return rows_for_statement(conn, table, statement)


def random_rows(conn: Connection, table: Table, limit: int) -> list[dict[str, Any]]:
    random_function = func.rand() if conn.dialect.name in {"mysql", "mariadb"} else func.random()
    statement = select(table).order_by(random_function).limit(limit)
    return rows_for_statement(conn, table, statement)


def rows_for_statement(conn: Connection, table: Table, statement: Any) -> list[dict[str, Any]]:
    rows = []
    for row in query_timeout.execute(conn, statement).mappings():
        output: dict[str, Any] = {}
        for column in table.columns:
            value = row[column.name]
            output[column.name] = "[REDACTED]" if is_sensitive(column.name) else jsonable(value)
        rows.append(output)
    return rows


def profile_column(
    conn: Connection,
    table: Table,
    column: Any,
    total_rows: int,
    unique_columns: set[str],
    indexed_columns: set[str],
    timeout_seconds: int,
) -> list[str]:
    indexed = column.name in indexed_columns
    counts_available = total_rows <= 5_000_000 or indexed
    non_nulls: int | None = None
    nulls: int | None = None
    skipped: list[str] = []
    if counts_available:
        try:
            non_nulls = int(
                query_timeout.execute(conn, select(func.count(column)).select_from(table)).scalar_one()
            )
        except query_timeout.QueryTimeout:
            non_nulls = None
            skipped.append("null/non-null counts")
        if non_nulls is not None:
            nulls = total_rows - non_nulls
            if non_nulls == 0:
                lines = [f"-- {column.name}: all NULL"]
                lines.extend(_skipped_metric_lines(column.name, skipped, timeout_seconds))
                return lines

    distinct_available = total_rows <= 100_000 or (total_rows <= 1_000_000 and indexed)
    distinct_count: int | None = None
    if distinct_available:
        try:
            distinct_count = int(
                query_timeout.execute(
                    conn, select(func.count(func.distinct(column))).select_from(table)
                ).scalar_one()
            )
        except query_timeout.QueryTimeout:
            distinct_count = None
            skipped.append("distinct count")

    unique_identifier = column.name in unique_columns or (
        distinct_count is not None
        and nulls == 0
        and non_nulls is not None
        and distinct_count == non_nulls
        and is_identifier_name(column.name)
    )
    sensitive = is_sensitive(column.name)

    summary = []
    if unique_identifier:
        summary.append("unique identifier")
    if non_nulls is not None:
        summary.extend((f"nulls={nulls}", f"non_nulls={non_nulls}"))
    if distinct_count is not None:
        summary.append(f"distinct={distinct_count}")
    lines = [f"-- {column.name}: {', '.join(summary) if summary else 'profile metrics skipped'}"]

    if is_numeric(column):
        numeric = []
        if total_rows <= 5_000_000 or indexed:
            try:
                min_value, max_value = query_timeout.execute(
                    conn, select(func.min(column), func.max(column)).select_from(table)
                ).one()
                numeric.extend((f"min={format_value(min_value)}", f"max={format_value(max_value)}"))
            except query_timeout.QueryTimeout:
                skipped.append("min/max")
        if total_rows <= 1_000_000 or (total_rows <= 10_000_000 and indexed):
            try:
                average = query_timeout.execute(
                    conn, select(func.avg(column)).select_from(table)
                ).scalar_one()
                numeric.append(f"average={format_value(average)}")
            except query_timeout.QueryTimeout:
                skipped.append("average")
        if total_rows < 100_000:
            try:
                median = median_value(conn, table, column)
                numeric.append(f"median={format_value(median)}")
            except query_timeout.QueryTimeout:
                skipped.append("median")
        if numeric:
            lines.append(f"-- {column.name} numeric: {', '.join(numeric)}")

    if not sensitive and not unique_identifier:
        top_values: list[tuple[Any, int]] = []
        if distinct_count is not None and distinct_count < 20:
            try:
                top_values = get_value_counts(conn, table, column, limit=None)
                lines.append(f"-- {column.name} values: {format_value_counts(top_values)}")
            except query_timeout.QueryTimeout:
                skipped.append("value counts")
        elif total_rows <= 100_000 and indexed:
            try:
                top_values = get_value_counts(conn, table, column, limit=10)
                if top_values and top_values[0][1] > 1:
                    lines.append(f"-- {column.name} top_values: {format_value_counts(top_values)}")
            except query_timeout.QueryTimeout:
                skipped.append("top values")
        elif total_rows > 100_000 and indexed:
            top_values = get_catalog_top_values(conn, table, column, total_rows)
            if top_values:
                lines.append(f"-- {column.name} top_values (catalog): {format_value_counts(top_values)}")
        shape_summary = get_shape_summary(column, distinct_count, top_values)
        if shape_summary:
            lines.append(f"-- {column.name} shape: {shape_summary}")
    lines.extend(_skipped_metric_lines(column.name, skipped, timeout_seconds))
    return lines


def _skipped_metric_lines(column_name: str, skipped: list[str], timeout_seconds: int) -> list[str]:
    if not skipped or timeout_seconds <= 0:
        return []
    return [
        f"-- {column_name} {metric}: skipped (query timeout > {timeout_seconds}s)"
        for metric in skipped
    ]


def median_value(conn: Connection, table: Table, column: Any) -> Any:
    if conn.dialect.name == "postgresql":
        return query_timeout.execute(
            conn,
            select(func.percentile_cont(0.5).within_group(column)).where(column.is_not(None)),
        ).scalar_one()
    if conn.dialect.name == "mariadb":
        percentile = func.percentile_cont(0.5).within_group(column).over()
        return query_timeout.execute(
            conn,
            select(percentile).select_from(table).where(column.is_not(None)).limit(1),
        ).scalar_one()

    ordered = (
        select(
            column.label("value"),
            func.row_number().over(order_by=column).label("rn"),
            func.count().over().label("n"),
        )
        .where(column.is_not(None))
        .subquery()
    )
    return query_timeout.execute(
        conn,
        select(func.avg(ordered.c.value)).where(
            ordered.c.rn.in_(
                [func.floor((ordered.c.n + 1) / 2), func.floor((ordered.c.n + 2) / 2)]
            )
        ),
    ).scalar_one()


def get_value_counts(conn: Connection, table: Table, column: Any, limit: int | None) -> list[tuple[Any, int]]:
    statement = (
        select(column, func.count().label("value_count"))
        .select_from(table)
        .where(column.is_not(None))
        .group_by(column)
        .order_by(literal_column("value_count").desc(), column.asc())
    )
    if limit is not None:
        statement = statement.limit(limit)
    rows = query_timeout.execute(conn, statement)
    return [(row[0], int(row[1])) for row in rows]


def get_catalog_top_values(
    conn: Connection, table: Table, column: Any, total_rows: int
) -> list[tuple[Any, int]]:
    try:
        with conn.begin_nested():
            if conn.dialect.name == "postgresql":
                row = conn.execute(
                    text(
                        "SELECT most_common_vals::text, most_common_freqs "
                        "FROM pg_stats WHERE schemaname = :schema AND tablename = :table "
                        "AND attname = :column"
                    ),
                    {
                        "schema": table.schema or conn.dialect.default_schema_name,
                        "table": table.name,
                        "column": column.name,
                    },
                ).one_or_none()
                if not row or not row[0] or not row[1]:
                    return []
                values = parse_postgres_array(row[0])
                return [
                    (value, max(1, round(float(frequency) * total_rows)))
                    for value, frequency in zip(values, row[1])
                ][:10]
            if conn.dialect.name == "mysql":
                histogram = conn.execute(
                    text(
                        "SELECT HISTOGRAM FROM information_schema.COLUMN_STATISTICS "
                        "WHERE SCHEMA_NAME = :schema AND TABLE_NAME = :table AND COLUMN_NAME = :column"
                    ),
                    {
                        "schema": table.schema or conn.dialect.default_schema_name,
                        "table": table.name,
                        "column": column.name,
                    },
                ).scalar_one_or_none()
                return mysql_histogram_values(histogram, total_rows)
    except SQLAlchemyError:
        return []
    return []


def parse_postgres_array(value: str) -> list[str]:
    # pg_stats exposes anyarray, which drivers cannot decode without knowing the
    # underlying type. Its text form uses standard PostgreSQL array quoting.
    if not (value.startswith("{") and value.endswith("}")):
        return []
    return next(csv.reader([value[1:-1]], delimiter=",", quotechar='"', escapechar="\\"))


def mysql_histogram_values(histogram: Any, total_rows: int) -> list[tuple[Any, int]]:
    if isinstance(histogram, str):
        histogram = json.loads(histogram)
    if not isinstance(histogram, dict) or histogram.get("histogram-type") != "singleton":
        return []
    previous = 0.0
    values = []
    for value, cumulative_frequency in histogram.get("buckets", []):
        frequency = float(cumulative_frequency) - previous
        previous = float(cumulative_frequency)
        values.append((value, max(1, round(frequency * total_rows))))
    return sorted(values, key=lambda item: (-item[1], str(item[0])))[:10]


def get_unique_column_names(table: Table) -> set[str]:
    primary_key_columns = list(table.primary_key.columns)
    unique_columns = (
        {primary_key_columns[0].name} if len(primary_key_columns) == 1 else set()
    )
    for constraint in table.constraints:
        if isinstance(constraint, UniqueConstraint) and len(constraint.columns) == 1:
            unique_columns.update(column.name for column in constraint.columns)
    for index in table.indexes:
        if index.unique and len(index.columns) == 1:
            unique_columns.update(column.name for column in index.columns)
    return unique_columns


def get_indexed_column_names(table: Table) -> set[str]:
    indexed = {column.name for column in table.primary_key.columns}
    for index in table.indexes:
        indexed.update(column.name for column in index.columns)
    for constraint in table.constraints:
        if isinstance(constraint, UniqueConstraint):
            indexed.update(column.name for column in constraint.columns)
    return indexed


def get_shape_summary(
    column: Any,
    distinct_count: int | None,
    top_values: list[tuple[Any, int]],
) -> str | None:
    if not isinstance(column.type, (String, Text)) or distinct_count is None or distinct_count <= 1:
        return None
    values = [value for value, _count in top_values[:10] if isinstance(value, str)]
    if not values:
        return None
    shapes: dict[str, int] = {}
    for value in values:
        shape = value_shape(value)
        if shape and shape != "text":
            shapes[shape] = shapes.get(shape, 0) + 1
    if not shapes:
        return None
    return ", ".join(f"{shape}={count}" for shape, count in sorted(shapes.items(), key=lambda item: (-item[1], item[0]))[:5])


def value_shape(value: str) -> str | None:
    if not value:
        return "empty"
    if re.fullmatch(r"[A-Z]{2,}\d+", value):
        return "UPPER+digits"
    if re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", value):
        return "email"
    if re.fullmatch(r"\+?[\d .()/-]{7,}", value):
        return "phone"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}.*", value):
        return "date-like"
    if re.search(r"\d", value) and re.search(r"[A-Za-z]", value):
        return "letters+digits"
    return "text"


def is_numeric(column: Any) -> bool:
    return isinstance(column.type, (Integer, BigInteger, SmallInteger, Numeric, Float))


def is_sensitive(column_name: str) -> bool:
    lower_name = column_name.lower()
    return any(part in lower_name for part in SENSITIVE_NAME_PARTS)


def is_identifier_name(column_name: str) -> bool:
    lower_name = column_name.lower()
    return lower_name == "id" or lower_name.endswith("_id") or lower_name.endswith("id")


def format_value_counts(values: list[tuple[Any, int]]) -> str:
    return ", ".join(f"{format_value(value)}={count}" for value, count in values)


def format_value(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, float):
        return f"{value:g}"
    if isinstance(value, Decimal):
        return f"{value:g}"
    return str(value)


def jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.hex()
    return value


def json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, default=str)


def ensure_semicolon(sql: str) -> str:
    sql = sql.rstrip()
    if not sql.endswith(";"):
        return sql + ";"
    return sql


def parse_table_set(value: str | None) -> frozenset[str] | None:
    if not value:
        return None
    return frozenset(table.strip() for table in value.split(",") if table.strip())


def default_output_path(database: str) -> Path:
    name = Path(database).name
    db_name = Path(name).stem or name
    return Path(db_name)


def output_component(value: str) -> str:
    """Map database object names to a single safe output path component."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip(".") or "unnamed"


def build_arg_parser(prog: str | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a SQL profile for a database.", prog=prog)
    add_connection_arguments(parser)
    parser.add_argument("--output", help="Output directory. Defaults to <database>/.")
    parser.add_argument("--sample-row-limit", type=int, default=50, help="Maximum sampled rows for small tables.")
    parser.add_argument("--small-table-threshold", type=int, default=50, help="Rows at or below this count are sampled.")
    parser.add_argument(
        "--large-table-threshold",
        type=int,
        default=LARGE_TABLE_THRESHOLD,
        help=(
            "Tables whose catalog row estimate is at/above this count are profiled "
            "from internal stats only; COUNT(*) and per-column queries are skipped. "
            f"Default {LARGE_TABLE_THRESHOLD}."
        ),
    )
    parser.add_argument(
        "--query-timeout",
        type=int,
        default=DEFAULT_QUERY_TIMEOUT,
        help=(
            "Abort any profiling query that runs longer than this many seconds, skip the "
            "affected metric, and continue. 0 disables. Applies to PostgreSQL/MySQL/MariaDB "
            f"(SQLite/DuckDB have no native support). Default {DEFAULT_QUERY_TIMEOUT}."
        ),
    )
    parser.add_argument("--per-table", action="store_true", help="Write one .sql profile per table instead of one schema profile.")
    parser.add_argument("--include-tables", help="Comma-separated table allowlist.")
    parser.add_argument("--exclude-tables", help="Comma-separated table denylist.")
    return parser


def main(argv: list[str] | None = None, prog: str | None = None) -> int:
    parser = build_arg_parser(prog=prog)
    args = parser.parse_args(argv)
    if args.large_table_threshold < 1:
        parser.error("--large-table-threshold must be a positive integer")
    if args.query_timeout < 0:
        parser.error("--query-timeout must be a non-negative integer")
    url = resolve_database_url(args, parser)

    options = ProfileOptions(
        small_table_threshold=args.small_table_threshold,
        sample_row_limit=args.sample_row_limit,
        large_table_threshold=args.large_table_threshold,
        query_timeout=args.query_timeout,
        include_tables=parse_table_set(args.include_tables),
        exclude_tables=parse_table_set(args.exclude_tables) or frozenset(),
        schema=resolve_schema(args),
    )
    engine = create_engine(url)
    progress_bar = ProgressBar("Profiling", 0)
    active_schema = ""

    def show_progress(current: int, total: int, table_name: str) -> None:
        nonlocal progress_bar
        item = f"{active_schema}: {table_name}"
        if progress_bar.total != total:
            progress_bar = ProgressBar("Profiling", total)
            progress_bar.start(f"profiling {item}")
            return
        progress_bar.update(current, f"profiling {item}" if current < total else f"profiled {item}")

    schemas = list_schemas(engine, options.schema)
    output_dir = Path(args.output) if args.output else default_output_path(args.database or os.environ["DB_SNOOPER_DATABASE"])
    try:
        for schema in schemas:
            active_schema = schema
            schema_options = replace(options, schema=schema)
            tables = list_schema_tables(engine, schema_options)
            schema_dir = output_dir / output_component(schema)
            if args.per_table:
                schema_dir.mkdir(parents=True, exist_ok=True)
                for table_name in tables:
                    table_output = profile_database(engine, schema_options, progress=show_progress, table_names=[table_name])
                    (schema_dir / f"{output_component(table_name)}.sql").write_text(table_output, encoding="utf-8")
            else:
                output = profile_database(engine, schema_options, progress=show_progress, table_names=tables)
                output_dir.mkdir(parents=True, exist_ok=True)
                (output_dir / f"{output_component(schema)}.sql").write_text(output, encoding="utf-8")
    except Exception:
        progress_bar.finish()
        raise
    else:
        progress_bar.finish("Profiling complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
