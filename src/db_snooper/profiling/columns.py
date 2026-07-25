from __future__ import annotations

import csv
import json
import re
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from sqlalchemy import Table, func, literal_column, select, text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql.sqltypes import (
    BigInteger,
    Float,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
)

from db_snooper import query_timeout
from db_snooper.shared import is_sensitive


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
                query_timeout.execute(
                    conn, select(func.count(column)).select_from(table)
                ).scalar_one()
            )
        except query_timeout.QueryTimeout:
            non_nulls = None
            skipped.append("null/non-null counts")
        if non_nulls is not None:
            nulls = total_rows - non_nulls
            if non_nulls == 0:
                lines = [f"-- {column.name}: all NULL"]
                lines.extend(
                    _skipped_metric_lines(column.name, skipped, timeout_seconds)
                )
                return lines

    distinct_available = total_rows <= 100_000 or (
        total_rows <= 1_000_000 and indexed
    )
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
    lines = [
        f"-- {column.name}: {', '.join(summary) if summary else 'profile metrics skipped'}"
    ]

    if is_numeric(column):
        numeric = []
        if total_rows <= 5_000_000 or indexed:
            try:
                min_value, max_value = query_timeout.execute(
                    conn, select(func.min(column), func.max(column)).select_from(table)
                ).one()
                numeric.extend(
                    (
                        f"min={format_value(min_value)}",
                        f"max={format_value(max_value)}",
                    )
                )
            except query_timeout.QueryTimeout:
                skipped.append("min/max")
        if total_rows <= 1_000_000 or (
            total_rows <= 10_000_000 and indexed
        ):
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
                lines.append(
                    f"-- {column.name} values: {format_value_counts(top_values)}"
                )
            except query_timeout.QueryTimeout:
                skipped.append("value counts")
        elif total_rows <= 100_000 and indexed:
            try:
                top_values = get_value_counts(conn, table, column, limit=10)
                if top_values and top_values[0][1] > 1:
                    lines.append(
                        f"-- {column.name} top_values: {format_value_counts(top_values)}"
                    )
            except query_timeout.QueryTimeout:
                skipped.append("top values")
        elif total_rows > 100_000 and indexed:
            top_values = get_catalog_top_values(conn, table, column, total_rows)
            if top_values:
                lines.append(
                    f"-- {column.name} top_values (catalog): "
                    f"{format_value_counts(top_values)}"
                )
        shape_summary = get_shape_summary(column, distinct_count, top_values)
        if shape_summary:
            lines.append(f"-- {column.name} shape: {shape_summary}")
    lines.extend(_skipped_metric_lines(column.name, skipped, timeout_seconds))
    return lines


def _skipped_metric_lines(
    column_name: str, skipped: list[str], timeout_seconds: int
) -> list[str]:
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
            select(func.percentile_cont(0.5).within_group(column)).where(
                column.is_not(None)
            ),
        ).scalar_one()
    if conn.dialect.name == "mariadb":
        percentile = func.percentile_cont(0.5).within_group(column).over()
        return query_timeout.execute(
            conn,
            select(percentile)
            .select_from(table)
            .where(column.is_not(None))
            .limit(1),
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
                [
                    func.floor((ordered.c.n + 1) / 2),
                    func.floor((ordered.c.n + 2) / 2),
                ]
            )
        ),
    ).scalar_one()


def get_value_counts(
    conn: Connection, table: Table, column: Any, limit: int | None
) -> list[tuple[Any, int]]:
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
                        "schema": table.schema
                        or conn.dialect.default_schema_name,
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
                        "WHERE SCHEMA_NAME = :schema AND TABLE_NAME = :table "
                        "AND COLUMN_NAME = :column"
                    ),
                    {
                        "schema": table.schema
                        or conn.dialect.default_schema_name,
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
    return next(
        csv.reader([value[1:-1]], delimiter=",", quotechar='"', escapechar="\\")
    )


def mysql_histogram_values(
    histogram: Any, total_rows: int
) -> list[tuple[Any, int]]:
    if isinstance(histogram, str):
        histogram = json.loads(histogram)
    if (
        not isinstance(histogram, dict)
        or histogram.get("histogram-type") != "singleton"
    ):
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


def get_shape_summary(
    column: Any,
    distinct_count: int | None,
    top_values: list[tuple[Any, int]],
) -> str | None:
    if (
        not isinstance(column.type, (String, Text))
        or distinct_count is None
        or distinct_count <= 1
    ):
        return None
    values = [
        value for value, _count in top_values[:10] if isinstance(value, str)
    ]
    if not values:
        return None
    shapes: dict[str, int] = {}
    for value in values:
        shape = value_shape(value)
        if shape and shape != "text":
            shapes[shape] = shapes.get(shape, 0) + 1
    if not shapes:
        return None
    return ", ".join(
        f"{shape}={count}"
        for shape, count in sorted(
            shapes.items(), key=lambda item: (-item[1], item[0])
        )[:5]
    )


def value_shape(value: str) -> str | None:
    if not value:
        return "empty"
    if re.fullmatch(r"[A-Z]{2,}\d+", value):
        return "UPPER+digits"
    if re.fullmatch(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", value
    ):
        return "email"
    if re.fullmatch(r"\+?[\d .()/-]{7,}", value):
        return "phone"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}.*", value):
        return "date-like"
    if re.search(r"\d", value) and re.search(r"[A-Za-z]", value):
        return "letters+digits"
    return "text"


def is_numeric(column: Any) -> bool:
    return isinstance(
        column.type, (Integer, BigInteger, SmallInteger, Numeric, Float)
    )


def is_identifier_name(column_name: str) -> bool:
    lower_name = column_name.lower()
    return (
        lower_name == "id"
        or lower_name.endswith("_id")
        or lower_name.endswith("id")
    )


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
