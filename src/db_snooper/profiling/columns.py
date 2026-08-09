from __future__ import annotations

import json
import logging
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
                lines = [f"- {column.name}: all NULL"]
                lines.extend(_skipped_metric_lines(skipped, timeout_seconds))
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

    # Low-cardinality columns: fetch the full histogram up front so the
    # value=count pairs can be inlined into the column header (replacing the
    # "N distinct" label) and so average/median can be skipped for numeric
    # columns, where the counts already are the precise distribution.
    full_histogram: list[tuple[Any, int]] | None = None
    if (
        not sensitive
        and not unique_identifier
        and distinct_supported
        and distinct_count is not None
        and distinct_count < 20
    ):
        with query_timeout.metric(conn, skipped, "value counts"):
            full_histogram = get_value_counts(conn, table, column, limit=None)

    # Numeric min/max is computed first so the range can be inlined on the
    # column header (``int 5..214``); average/median and any catalog-range
    # fallback are emitted as a supplementary ``stats`` sub-bullet.
    numeric_range: str | None = None
    numeric_stats: list[str] = []
    if is_numeric(column):
        have_range = False
        if total_rows <= 5_000_000 or indexed:
            with query_timeout.metric(conn, skipped, "min/max"):
                min_value, max_value = query_timeout.execute(
                    conn, select(func.min(column), func.max(column)).select_from(table)
                ).one()
            if min_value is not None and max_value is not None:
                numeric_range = (
                    f"{numeric_type_word(column)} "
                    f"{format_value(min_value)}..{format_value(max_value)}"
                )
                have_range = True
        if (
            not have_range
            and catalog_stat is not None
            and catalog_stat.min_value is not None
            and catalog_stat.max_value is not None
        ):
            numeric_stats.append(
                f"min≈{format_value(catalog_stat.min_value)}, "
                f"max≈{format_value(catalog_stat.max_value)}"
            )
        col_name = str(column.name)
        include_avg_median = (
            col_name != "id"
            and not col_name.endswith("_id")
            # The full histogram is the exact distribution, so average/median
            # would only restate it.
            and full_histogram is None
        )
        if include_avg_median:
            if total_rows <= 1_000_000 or (total_rows <= 10_000_000 and indexed):
                with query_timeout.metric(conn, skipped, "average"):
                    average = query_timeout.execute(
                        conn, select(func.avg(column)).select_from(table)
                    ).scalar_one()
                    numeric_stats.append(f"average={format_value(average)}")
            if total_rows < 100_000:
                with query_timeout.metric(conn, skipped, "median"):
                    median = median_value(conn, table, column)
                    numeric_stats.append(f"median={format_value(median)}")

    summary: list[str] = []
    if unique_identifier:
        summary.append("unique identifier")
    if full_histogram is not None:
        # The histogram inlines the distribution; "N distinct" is implied, so
        # it is omitted to avoid restating the obvious.
        summary.append(format_value_counts(full_histogram))
    elif distinct_count is not None:
        # "all distinct" means every present (non-null) value is unique. The
        # right baseline is the non-null count; we only fall back to total rows
        # when the null/non-null query was skipped or timed out (distinct ==
        # total then still correctly implies no nulls). Any nulls are reported
        # normally, e.g. ``all distinct, nulls=8``. It is implied by
        # "unique identifier", so it is suppressed there to avoid restating it.
        distinct_base = non_nulls if non_nulls is not None else total_rows
        if distinct_count == distinct_base:
            if not unique_identifier:
                summary.append("all distinct")
        else:
            summary.append(f"{distinct_count} distinct")
    elif catalog_stat is not None and catalog_stat.distinct is not None:
        summary.append(f"≈{catalog_stat.distinct} distinct")
    if nulls is not None:
        if nulls > 0:
            summary.append(f"nulls={nulls}")
    elif catalog_stat is not None and catalog_stat.null_frac is not None:
        # Exact count skipped (table too large/unindexed, or query timed out);
        # fall back to the catalog null fraction.
        catalog_nulls = round(catalog_stat.null_frac * total_rows)
        if catalog_nulls > 0:
            summary.append(f"nulls≈{catalog_nulls}")
    # The min..max range is redundant when the full histogram already lists
    # every value: with two distinct values the range endpoints are exactly
    # those two values, so the range just restates them.
    if numeric_range and (full_histogram is None or len(full_histogram) > 2):
        summary.append(numeric_range)
    lines = [
        f"- {column.name}: {', '.join(summary) if summary else 'profile metrics skipped'}"
    ]
    if numeric_stats:
        lines.append(continuation_line("stats", ", ".join(numeric_stats)))

    if not sensitive and not unique_identifier and distinct_supported:
        top_values: list[tuple[Any, int]] = []
        if full_histogram is not None:
            # Already inlined on the column header; no separate line.
            top_values = full_histogram
        elif total_rows <= 100_000 and indexed:
            with query_timeout.metric(conn, skipped, "top values"):
                top_values = get_value_counts(conn, table, column, limit=10)
                if top_values and top_values[0][1] > 1:
                    lines.append(
                        continuation_line(
                            "top_values", format_value_counts(top_values)
                        )
                    )
        elif total_rows > 100_000 and indexed:
            top_values = (
                list(catalog_stat.top_values) if catalog_stat is not None else []
            )
            if top_values:
                lines.append(
                    continuation_line(
                        "top_values", format_value_counts(top_values)
                    )
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

    lines.extend(_skipped_metric_lines(skipped, timeout_seconds))
    return lines


def _skipped_metric_lines(
    skipped: list[str], timeout_seconds: int
) -> list[str]:
    if not skipped or timeout_seconds <= 0:
        return []
    return [
        continuation_line(metric, f"skipped (query timeout > {timeout_seconds}s)")
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


def is_numeric(column: Any) -> bool:
    return isinstance(column.type, (Integer, BigInteger, SmallInteger, Numeric, Float))


def numeric_type_word(column: Any) -> str:
    """Short type label for inline numeric ranges: ``int`` vs ``num``."""
    if isinstance(column.type, (Integer, BigInteger, SmallInteger)):
        return "int"
    return "num"


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
    return continuation_line("json_keys", pairs)


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
    return continuation_line("array", ", ".join(parts)) if parts else None


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


def continuation_line(label: str, body: str) -> str:
    """A metric line that belongs to the column header above it.

    Rendered as a nested markdown bullet: the parent list item (the column
    header ``- col: ...`` line) already names the column, so continuation lines
    omit the repeated column name and indent under it. The ``label`` makes the
    metric self-describing.
    """
    return f"  - {label}: {body}"


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
