from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import MetaData, Table, create_engine, func, inspect, literal_column, select, text
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.schema import CreateIndex, CreateTable, UniqueConstraint
from sqlalchemy.sql.sqltypes import BigInteger, Float, Integer, Numeric, SmallInteger, String, Text

from ai_sql_context import __version__

SENSITIVE_NAME_PARTS = ("password", "passwd", "pwd", "hash", "salt", "secret", "token")


@dataclass(frozen=True)
class ProfileOptions:
    small_table_threshold: int = 50
    sample_row_limit: int = 50
    include_tables: frozenset[str] | None = None
    exclude_tables: frozenset[str] = frozenset()


def profile_database(engine: Engine, options: ProfileOptions) -> str:
    inspector = inspect(engine)
    tables = sorted(inspector.get_table_names())
    if options.include_tables is not None:
        tables = [table for table in tables if table in options.include_tables]
    tables = [table for table in tables if table not in options.exclude_tables]

    url = engine.url.render_as_string(hide_password=True)
    database = engine.url.database or ""
    lines = [
        "-- ai-sql-context",
        f"-- version: {__version__}",
        f"-- dialect: {engine.dialect.name}",
        f"-- database: {database}",
        f"-- url: {url}",
        "",
    ]

    with engine.connect() as conn:
        metadata = MetaData()
        for table_name in tables:
            table = Table(table_name, metadata, autoload_with=conn)
            ddl = get_table_ddl(conn, table)
            lines.extend(ddl)
            if lines[-1] != "":
                lines.append("")
            lines.extend(profile_table(conn, table, options))
            lines.append("")
            lines.append("")

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


def profile_table(conn: Connection, table: Table, options: ProfileOptions) -> list[str]:
    total_rows = conn.execute(select(func.count()).select_from(table)).scalar_one()
    lines = [f"-- total rows={total_rows}"]
    if total_rows <= options.small_table_threshold:
        marker = "ALL_ROWS" if total_rows <= options.sample_row_limit else "SAMPLED_ROWS"
        lines.append(f"-- {marker}: {table.name}")
        for row in sample_rows(conn, table, options.sample_row_limit):
            lines.append(f"-- row: {json_dumps(row)}")
        return lines

    unique_columns = get_unique_column_names(table)
    for column in table.columns:
        lines.extend(profile_column(conn, table, column, int(total_rows), unique_columns))
    return lines


def sample_rows(conn: Connection, table: Table, limit: int) -> list[dict[str, Any]]:
    order_columns = list(table.primary_key.columns) or list(table.columns)
    statement = select(table).order_by(*order_columns).limit(limit)
    rows = []
    for row in conn.execute(statement).mappings():
        output: dict[str, Any] = {}
        for column in table.columns:
            value = row[column.name]
            output[column.name] = "[REDACTED]" if is_sensitive(column.name) else jsonable(value)
        rows.append(output)
    return rows


def profile_column(conn: Connection, table: Table, column: Any, total_rows: int, unique_columns: set[str]) -> list[str]:
    non_nulls = conn.execute(select(func.count(column)).select_from(table)).scalar_one()
    nulls = total_rows - int(non_nulls)
    if non_nulls == 0:
        return [f"-- {column.name}: all NULL"]

    distinct_count = conn.execute(select(func.count(func.distinct(column))).select_from(table)).scalar_one()
    distinct_count = int(distinct_count)
    unique_identifier = column.name in unique_columns or (
        nulls == 0 and distinct_count == non_nulls and is_identifier_name(column.name)
    )
    sensitive = is_sensitive(column.name)

    if unique_identifier:
        line = f"-- {column.name}: unique values={distinct_count}"
        if is_numeric(column):
            min_value, max_value = conn.execute(select(func.min(column), func.max(column)).select_from(table)).one()
            line += f", range={format_value(min_value)}..{format_value(max_value)}"
        return [line]

    lines = [f"-- {column.name}: nulls={nulls}, non_nulls={non_nulls}, distinct={distinct_count}"]
    if is_numeric(column):
        min_value, max_value = conn.execute(select(func.min(column), func.max(column)).select_from(table)).one()
        median = median_value(conn, table, column, int(non_nulls))
        lines.append(
            f"-- {column.name} numeric: min={format_value(min_value)}, "
            f"median={format_value(median)}, max={format_value(max_value)}"
        )

    if not sensitive:
        top_values = get_top_values(conn, table, column)
        if distinct_count < 20:
            lines.append(f"-- {column.name} values: {format_value_counts(top_values)}")
        elif top_values and top_values[0][1] > 1:
            lines.append(f"-- {column.name} top_values: {format_value_counts(top_values)}")
        shape_summary = get_shape_summary(column, distinct_count, top_values)
        if shape_summary:
            lines.append(f"-- {column.name} shape: {shape_summary}")
    return lines


def median_value(conn: Connection, table: Table, column: Any, non_nulls: int) -> Any:
    ordered = (
        select(
            column.label("value"),
            func.row_number().over(order_by=column).label("rn"),
        )
        .where(column.is_not(None))
        .subquery()
    )
    lower = (non_nulls + 1) // 2
    upper = (non_nulls + 2) // 2
    return conn.execute(
        select(func.avg(ordered.c.value)).where(ordered.c.rn.in_([lower, upper]))
    ).scalar_one()


def get_top_values(conn: Connection, table: Table, column: Any) -> list[tuple[Any, int]]:
    rows = conn.execute(
        select(column, func.count().label("count"))
        .select_from(table)
        .where(column.is_not(None))
        .group_by(column)
        .order_by(literal_column("count").desc(), column.asc())
        .limit(10)
    )
    return [(row[0], int(row[1])) for row in rows]


def get_unique_column_names(table: Table) -> set[str]:
    unique_columns = {column.name for column in table.primary_key.columns}
    for constraint in table.constraints:
        if isinstance(constraint, UniqueConstraint) and len(constraint.columns) == 1:
            unique_columns.update(column.name for column in constraint.columns)
    for index in table.indexes:
        if index.unique and len(index.columns) == 1:
            unique_columns.update(column.name for column in index.columns)
    return unique_columns


def get_shape_summary(
    column: Any,
    distinct_count: int,
    top_values: list[tuple[Any, int]],
) -> str | None:
    if not isinstance(column.type, (String, Text)) or distinct_count <= 1:
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


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a SQL profile for a database.")
    parser.add_argument("--url", default=None, help="SQLAlchemy database URL. Defaults to AI_SQL_CONTEXT_DB_URL.")
    parser.add_argument("--output", help="Output .sql file. Defaults to stdout.")
    parser.add_argument("--sample-row-limit", type=int, default=50, help="Maximum sampled rows for small tables.")
    parser.add_argument("--small-table-threshold", type=int, default=50, help="Rows at or below this count are sampled.")
    parser.add_argument("--include-tables", help="Comma-separated table allowlist.")
    parser.add_argument("--exclude-tables", help="Comma-separated table denylist.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    url = args.url
    if url is None:
        import os

        url = os.environ.get("AI_SQL_CONTEXT_DB_URL")
    if not url:
        parser.error("--url or AI_SQL_CONTEXT_DB_URL is required")

    options = ProfileOptions(
        small_table_threshold=args.small_table_threshold,
        sample_row_limit=args.sample_row_limit,
        include_tables=parse_table_set(args.include_tables),
        exclude_tables=parse_table_set(args.exclude_tables) or frozenset(),
    )
    engine = create_engine(url)
    output = profile_database(engine, options)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
