from __future__ import annotations

import json
import logging
import re
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from sqlalchemy import ARRAY, Table, func, literal_column, select
from sqlalchemy.engine import Connection
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql.sqltypes import (
    JSON,
    BigInteger,
    Float,
    Integer,
    LargeBinary,
    Numeric,
    SmallInteger,
    String,
    Text,
)

from db_snooper import query_timeout
from db_snooper.database_stats import get_catalog_column_stats
from db_snooper.shared import is_sensitive

_logger = logging.getLogger("db_snooper")

# JSON/JSONB profiling gates: keep key extraction bounded so a single oversized
# value or a very large table cannot hang the profile.
JSON_PROFILE_ROW_LIMIT = 100_000  # don't attempt JSON key extraction above this
JSON_SAMPLE_LIMIT = 1_000  # max JSON values read for key extraction
JSON_MAX_VALUE_BYTES = 65_536  # skip individual JSON values larger than 64KB


def profile_column(
    conn: Connection,
    table: Table,
    column: Any,
    total_rows: int,
    unique_columns: set[str],
    indexed_columns: set[str],
    timeout_seconds: int,
    catalog_stat: Any = None,
) -> list[str]:
    indexed = column.name in indexed_columns
    counts_available = total_rows <= 5_000_000 or indexed
    non_nulls: int | None = None
    nulls: int | None = None
    skipped: list[str] = []
    if counts_available:
        with query_timeout.metric(conn, skipped, "null/non-null counts"):
            non_nulls = int(
                query_timeout.execute(
                    conn, select(func.count(column)).select_from(table)
                ).scalar_one()
            )
        if non_nulls is not None:
            nulls = total_rows - non_nulls
            if non_nulls == 0:
                lines = [f"-- {column.name}: all NULL"]
                lines.extend(
                    _skipped_metric_lines(column.name, skipped, timeout_seconds)
                )
                return lines

    distinct_supported = is_distinct_supported(column)
    distinct_available = distinct_supported and (
        total_rows <= 100_000 or (total_rows <= 1_000_000 and indexed)
    )
    distinct_count: int | None = None
    if distinct_available:
        with query_timeout.metric(conn, skipped, "distinct count"):
            distinct_count = int(
                query_timeout.execute(
                    conn, select(func.count(func.distinct(column))).select_from(table)
                ).scalar_one()
            )

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
    elif catalog_stat is not None and catalog_stat.null_frac is not None:
        # Exact count skipped (table too large/unindexed, or query timed out);
        # fall back to the catalog null fraction.
        catalog_nulls = round(catalog_stat.null_frac * total_rows)
        summary.extend(
            (f"nulls≈{catalog_nulls}", f"non_nulls≈{total_rows - catalog_nulls}")
        )
    if distinct_count is not None:
        summary.append(f"distinct={distinct_count}")
    elif catalog_stat is not None and catalog_stat.distinct is not None:
        summary.append(f"distinct≈{catalog_stat.distinct}")
    lines = [
        f"-- {column.name}: {', '.join(summary) if summary else 'profile metrics skipped'}"
    ]

    if is_numeric(column):
        numeric = []
        have_range = False
        if total_rows <= 5_000_000 or indexed:
            with query_timeout.metric(conn, skipped, "min/max"):
                min_value, max_value = query_timeout.execute(
                    conn, select(func.min(column), func.max(column)).select_from(table)
                ).one()
                numeric.extend(
                    (
                        f"min={format_value(min_value)}",
                        f"max={format_value(max_value)}",
                    )
                )
                have_range = True
        if (
            not have_range
            and catalog_stat is not None
            and catalog_stat.min_value is not None
            and catalog_stat.max_value is not None
        ):
            numeric.extend(
                (
                    f"min≈{format_value(catalog_stat.min_value)}",
                    f"max≈{format_value(catalog_stat.max_value)}",
                )
            )
        col_name = str(column.name)
        include_avg_median = col_name != "id" and not col_name.endswith("_id")
        if include_avg_median:
            if total_rows <= 1_000_000 or (total_rows <= 10_000_000 and indexed):
                with query_timeout.metric(conn, skipped, "average"):
                    average = query_timeout.execute(
                        conn, select(func.avg(column)).select_from(table)
                    ).scalar_one()
                    numeric.append(f"average={format_value(average)}")
            if total_rows < 100_000:
                with query_timeout.metric(conn, skipped, "median"):
                    median = median_value(conn, table, column)
                    numeric.append(f"median={format_value(median)}")
        if numeric:
            lines.append(f"-- {column.name} numeric: {', '.join(numeric)}")

    if not sensitive and not unique_identifier and distinct_supported:
        top_values: list[tuple[Any, int]] = []
        if distinct_count is not None and distinct_count < 20:
            with query_timeout.metric(conn, skipped, "value counts"):
                top_values = get_value_counts(conn, table, column, limit=None)
                lines.append(
                    f"-- {column.name} values (value=count): {format_value_counts(top_values)}"
                )
        elif total_rows <= 100_000 and indexed:
            with query_timeout.metric(conn, skipped, "top values"):
                top_values = get_value_counts(conn, table, column, limit=10)
                if top_values and top_values[0][1] > 1:
                    lines.append(
                        f"-- {column.name} top_values (value=count): {format_value_counts(top_values)}"
                    )
        elif total_rows > 100_000 and indexed:
            top_values = (
                list(catalog_stat.top_values) if catalog_stat is not None else []
            )
            if top_values:
                lines.append(
                    f"-- {column.name} top_values (from db stats, value=count): "
                    f"{format_value_counts(top_values)}"
                )
        shape_summary = get_shape_summary(column, distinct_count, top_values)
        if shape_summary:
            lines.append(
                f"-- {column.name} value_shapes (shape=count): {shape_summary}"
            )

    # Type-specific profiling for container/LOB types that cannot be DISTINCTed.
    if not sensitive and not unique_identifier:
        if is_json(column):
            json_line = profile_json_column(conn, table, column, total_rows)
            if json_line:
                lines.append(json_line)
        elif is_array(column):
            array_line = profile_array_column(conn, table, column, total_rows, indexed)
            if array_line:
                lines.append(array_line)

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
    # Delegates to the shared catalog reader, which covers PostgreSQL pg_stats,
    # MySQL singleton/equi-height histograms, and MariaDB mysql.column_stats.
    stats = get_catalog_column_stats(conn, table, total_rows)
    stat = stats.get(column.name)
    return list(stat.top_values) if stat else []


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


def is_json(column: Any) -> bool:
    # Covers base JSON, MySQL JSON, and PostgreSQL JSON/JSONB.
    return isinstance(column.type, JSON)


def is_array(column: Any) -> bool:
    return isinstance(column.type, ARRAY)


def is_lob(column: Any) -> bool:
    return isinstance(column.type, LargeBinary)


def is_distinct_supported(column: Any) -> bool:
    # JSON/JSONB, ARRAY, and binary LOBs cannot be meaningfully DISTINCTed
    # (most dialects reject it outright, and even where allowed it is too slow
    # to be informative).
    return not (is_json(column) or is_array(column) or is_lob(column))


def profile_json_column(
    conn: Connection, table: Table, column: Any, total_rows: int
) -> str | None:
    """Emit top-level JSON key frequencies, bounded by row-count and size gates."""
    if total_rows > JSON_PROFILE_ROW_LIMIT:
        return None
    key_counts: dict[str, int] = {}
    sampled = 0
    try:
        rows = query_timeout.execute(
            conn,
            select(column)
            .select_from(table)
            .where(column.is_not(None))
            .limit(JSON_SAMPLE_LIMIT),
        )
        for (value,) in rows:
            sampled += 1
            if value is None:
                continue
            if not _json_value_in_bounds(value):
                continue
            for key in _json_keys(value):
                key_counts[key] = key_counts.get(key, 0) + 1
    except query_timeout.QueryTimeout:
        return None
    except Exception as exc:
        query_timeout.recover_connection(conn)
        _logger.debug(
            "JSON key profile for %s.%s skipped: %r",
            table.name,
            column.name,
            exc,
            exc_info=True,
        )
        return None
    if not key_counts or sampled == 0:
        return None
    ordered = sorted(key_counts.items(), key=lambda item: (-item[1], item[0]))
    pairs = ", ".join(f"{key}={count}" for key, count in ordered)
    return f"-- {column.name} json_keys (key=count): {pairs}"


def profile_array_column(
    conn: Connection, table: Table, column: Any, total_rows: int, indexed: bool
) -> str | None:
    """Emit min/avg/max element counts for an ARRAY column."""
    if not (total_rows <= 5_000_000 or indexed):
        return None
    length_expr = _array_length_expr(conn, column)
    if length_expr is None:
        return None
    try:
        min_len, avg_len, max_len = query_timeout.execute(
            conn,
            select(
                func.min(length_expr),
                func.avg(length_expr),
                func.max(length_expr),
            ).select_from(table),
        ).one()
    except query_timeout.QueryTimeout:
        return None
    except Exception as exc:
        query_timeout.recover_connection(conn)
        _logger.debug(
            "array length profile for %s.%s skipped: %r",
            table.name,
            column.name,
            exc,
            exc_info=True,
        )
        return None
    if min_len is None and avg_len is None and max_len is None:
        return None
    parts = []
    if min_len is not None:
        parts.append(f"min_len={format_value(min_len)}")
    if avg_len is not None:
        parts.append(f"avg_len={format_value(avg_len)}")
    if max_len is not None:
        parts.append(f"max_len={format_value(max_len)}")
    return f"-- {column.name} array: {', '.join(parts)}" if parts else None


def _json_value_in_bounds(value: Any) -> bool:
    try:
        return len(json_dumps(value)) <= JSON_MAX_VALUE_BYTES
    except (TypeError, ValueError):
        return False


def _json_keys(value: Any) -> list[str]:
    if isinstance(value, dict):
        return [str(key) for key in value.keys()]
    return []


def _array_length_expr(conn: Connection, column: Any):
    dialect = conn.dialect.name
    if dialect == "postgresql":
        # cardinality() handles multi-dim and empty arrays for 1-D inputs.
        return func.cardinality(column)
    if dialect == "duckdb":
        return func.len(column)
    # Fallback: array_length(col, 1) works on PostgreSQL-compatible dialects.
    return func.array_length(column, 1)


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
