from __future__ import annotations

import json
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
from db_snooper.profiling.models import ColumnProfile
from db_snooper.shared import is_sensitive

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
) -> ColumnProfile:
    """Profile a single column and return its inline ``columns:`` profile text.

    All metrics for the column — distinct count, full histogram, nulls, numeric
    range, average/median, top values, JSON/array summaries, skip reasons —
    collapse onto :attr:`ColumnProfile.value_line` as a single comma-separated
    string. The one-line-per-column rendering is what the compact output format
    requires; there are no indented continuation lines.
    """
    sensitive = is_sensitive(column.name)
    if sensitive:
        # Never dump values for sensitive fields: emit ``redacted`` and stop.
        return ColumnProfile(
            name=column.name,
            value_line="redacted",
            is_sensitive=True,
            is_unique_identifier=False,
            dropped_from_samples=False,
        )

    indexed = column.name in indexed_columns
    counts_available = total_rows <= 5_000_000 or indexed
    non_nulls: int | None = None
    nulls: int | None = None
    skipped: list[tuple[str, str]] = []
    if counts_available:
        with query_timeout.metric(skipped, "null/non-null counts"):
            non_nulls = int(
                query_timeout.execute(
                    conn,
                    select(func.count(column)).select_from(table),
                    timeout_seconds,
                ).scalar_one()
            )
        if non_nulls is not None:
            nulls = total_rows - non_nulls
            if non_nulls == 0:
                return _column_profile(column, "all NULL", skipped=skipped)

    distinct_supported = is_distinct_supported(column)
    distinct_available = distinct_supported and (
        conn.dialect.name == "bigquery"
        or total_rows <= 100_000
        or (total_rows <= 1_000_000 and indexed)
    )
    distinct_count: int | None = None
    approximate_top_values: list[tuple[Any, int]] = []
    if distinct_available:
        with query_timeout.metric(skipped, "distinct count"):
            if conn.dialect.name == "bigquery":
                expressions = [func.approx_count_distinct(column)]
                if not sensitive:
                    expressions.append(func.approx_top_count(column, 20))
                row = query_timeout.execute(
                    conn,
                    select(*expressions)
                    .select_from(table)
                    .where(column.is_not(None)),
                    timeout_seconds,
                ).one()
                distinct_count = int(row[0])
                if not sensitive:
                    approximate_top_values = _bigquery_value_counts(row[1])
            else:
                distinct_count = int(
                    query_timeout.execute(
                        conn,
                        select(func.count(func.distinct(column))).select_from(table),
                        timeout_seconds,
                    ).scalar_one()
                )

    unique_identifier = column.name in unique_columns or (
        conn.dialect.name != "bigquery"
        and distinct_count is not None
        and nulls == 0
        and non_nulls is not None
        and distinct_count == non_nulls
        and is_identifier_name(column.name)
    )
    # Low-cardinality columns: fetch the full (or BigQuery approximate) histogram
    # up front so the value=count pairs can be inlined into the value line
    # (replacing the "N distinct" label) and so average/median can be skipped
    # for numeric columns, where the counts already are the precise distribution.
    full_histogram: list[tuple[Any, int]] | None = None
    if (
        not sensitive
        and not unique_identifier
        and distinct_supported
        and distinct_count is not None
        and distinct_count < 20
    ):
        if conn.dialect.name == "bigquery":
            full_histogram = approximate_top_values or None
        else:
            with query_timeout.metric(skipped, "value counts"):
                full_histogram = get_value_counts(
                    conn, table, column, limit=None, timeout_seconds=timeout_seconds
                )

    # Numeric min/max is inlined (``5..214`` — the type token on the merged
    # columns: line already says int/float/numeric); average/median and the
    # catalog-range fallback join the same line.
    numeric_range: str | None = None
    numeric_stats: list[str] = []
    if is_numeric(column):
        have_range = False
        if total_rows <= 5_000_000 or indexed:
            with query_timeout.metric(skipped, "min/max"):
                min_value, max_value = query_timeout.execute(
                    conn,
                    select(func.min(column), func.max(column)).select_from(table),
                    timeout_seconds,
                ).one()
            if min_value is not None and max_value is not None:
                numeric_range = (
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
            # The histogram already describes the distribution, so average/median
            # would only restate it.
            and full_histogram is None
        )
        if include_avg_median:
            if total_rows <= 1_000_000 or (total_rows <= 10_000_000 and indexed):
                with query_timeout.metric(skipped, "average"):
                    average = query_timeout.execute(
                        conn,
                        select(func.avg(column)).select_from(table),
                        timeout_seconds,
                    ).scalar_one()
                    numeric_stats.append(f"avg={format_value(average)}")
            if total_rows < 100_000:
                with query_timeout.metric(skipped, "median"):
                    median = median_value(
                        conn, table, column, timeout_seconds=timeout_seconds
                    )
                    marker = "≈" if conn.dialect.name == "bigquery" else "="
                    numeric_stats.append(f"median{marker}{format_value(median)}")

    summary: list[str] = []
    if unique_identifier:
        summary.append("unique identifier")
    if full_histogram is not None:
        # The histogram inlines the distribution; "N distinct" is implied, so
        # it is omitted to avoid restating the obvious.
        values = format_value_counts(full_histogram)
        summary.append(f"≈{values}" if conn.dialect.name == "bigquery" else values)
    elif distinct_count is not None:
        # "all distinct" means every present (non-null) value is unique. The
        # right baseline is the non-null count; we only fall back to total rows
        # when the null/non-null query was skipped or timed out (distinct ==
        # total then still correctly implies no nulls). Any nulls are reported
        # normally, e.g. ``all distinct, nulls=8``. It is implied by
        # "unique identifier", so it is suppressed there to avoid restating it.
        if conn.dialect.name == "bigquery":
            summary.append(f"≈{distinct_count} distinct")
        else:
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
    # Average/median and catalog min/max ride on the same line.
    summary.extend(numeric_stats)

    # Top values for high-cardinality columns: inline on the same line. The
    # full-histogram case is already in ``summary`` above.
    top_inline: str | None = None
    if not sensitive and not unique_identifier and distinct_supported:
        if full_histogram is not None:
            # Already inlined above.
            pass
        elif conn.dialect.name == "bigquery" and approximate_top_values:
            top_inline = f"≈{format_value_counts(approximate_top_values[:10])}"
        elif total_rows <= 100_000 and indexed:
            with query_timeout.metric(skipped, "top values"):
                top_values = get_value_counts(
                    conn, table, column, limit=10, timeout_seconds=timeout_seconds
                )
                if top_values and top_values[0][1] > 1:
                    top_inline = (
                        "≈" if conn.dialect.name == "bigquery" else ""
                    ) + format_value_counts(top_values)
        elif total_rows > 100_000 and indexed:
            top_values = (
                list(catalog_stat.top_values) if catalog_stat is not None else []
            )
            if top_values:
                top_inline = format_value_counts(top_values)
    if top_inline:
        summary.append(top_inline)

    # Type-specific profiling for container/LOB types that cannot be DISTINCTed.
    # These render as a trailing annotation on the same line.
    dropped_from_samples = False
    trailing: list[str] = []
    if not sensitive and not unique_identifier:
        if is_json(column):
            json_annotation = profile_json_column(
                conn, table, column, total_rows, timeout_seconds
            )
            if json_annotation:
                trailing.append(json_annotation)
            # JSON values are per-row diagnostics that don't belong in samples.
            dropped_from_samples = True
        elif is_array(column):
            array_annotation = profile_array_column(
                conn, table, column, total_rows, indexed, timeout_seconds
            )
            if array_annotation:
                trailing.append(array_annotation)
            dropped_from_samples = True
        elif is_lob(column):
            dropped_from_samples = True

    if not summary and not trailing:
        summary.append("profile metrics skipped")
    value_line = ", ".join(summary)
    if trailing:
        value_line = (value_line + "  " if value_line else "") + "  ".join(
            f"← {t}" for t in trailing
        ).lstrip()
    # Re-append a skip-reason tail so timeouts remain visible without breaking
    # the one-line invariant.
    if skipped:
        skip_tail = "; ".join(f"{metric} skipped ({reason})" for metric, reason in skipped)
        value_line = f"{value_line}  [{skip_tail}]" if value_line else f"[{skip_tail}]"
    return ColumnProfile(
        name=column.name,
        value_line=value_line,
        is_sensitive=False,
        is_unique_identifier=unique_identifier,
        dropped_from_samples=dropped_from_samples,
    )


def _column_profile(
    column: Any,
    value_line: str,
    skipped: list[tuple[str, str]] | None = None,
    dropped_from_samples: bool = False,
) -> ColumnProfile:
    text = value_line
    if skipped:
        skip_tail = "; ".join(f"{metric} skipped ({reason})" for metric, reason in skipped)
        text = f"{text}  [{skip_tail}]"
    return ColumnProfile(
        name=column.name,
        value_line=text,
        is_sensitive=False,
        is_unique_identifier=False,
        dropped_from_samples=dropped_from_samples,
    )


def median_value(
    conn: Connection, table: Table, column: Any, timeout_seconds: int = 0
) -> Any:
    if conn.dialect.name == "bigquery":
        quantiles = query_timeout.execute(
            conn,
            select(func.approx_quantiles(column, 2)).where(column.is_not(None)),
            timeout_seconds,
        ).scalar_one()
        return quantiles[1] if quantiles else None
    if conn.dialect.name == "postgresql":
        return query_timeout.execute(
            conn,
            select(func.percentile_cont(0.5).within_group(column)).where(
                column.is_not(None)
            ),
            timeout_seconds,
        ).scalar_one()
    if conn.dialect.name == "mariadb":
        percentile = func.percentile_cont(0.5).within_group(column).over()
        return query_timeout.execute(
            conn,
            select(percentile).select_from(table).where(column.is_not(None)).limit(1),
            timeout_seconds,
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
        timeout_seconds,
    ).scalar_one()


def get_value_counts(
    conn: Connection,
    table: Table,
    column: Any,
    limit: int | None,
    timeout_seconds: int = 0,
) -> list[tuple[Any, int]]:
    if conn.dialect.name == "bigquery":
        values = query_timeout.execute(
            conn,
            select(func.approx_top_count(column, limit or 20)).where(
                column.is_not(None)
            ),
            timeout_seconds,
        ).scalar_one()
        return _bigquery_value_counts(values)
    statement = (
        select(column, func.count().label("value_count"))
        .select_from(table)
        .where(column.is_not(None))
        .group_by(column)
        .order_by(literal_column("value_count").desc(), column.asc())
    )
    if limit is not None:
        statement = statement.limit(limit)
    rows = query_timeout.execute(conn, statement, timeout_seconds)
    return [(row[0], int(row[1])) for row in rows]


def _bigquery_value_counts(values: Any) -> list[tuple[Any, int]]:
    return [
        (item["value"], int(item["count"]))
        if isinstance(item, dict)
        else (item[0], int(item[1]))
        for item in (values or [])
    ]


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
    conn: Connection,
    table: Table,
    column: Any,
    total_rows: int,
    timeout_seconds: int = 0,
) -> str | None:
    """Return top-level JSON key frequencies as an inline annotation body.

    Bounded by row-count and size gates. The returned string (e.g.
    ``json_keys: a=10, b=3``) is appended to the column's ``value_line`` as a
    trailing annotation rather than emitted as a child line.
    """
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
            timeout_seconds,
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
    if not key_counts or sampled == 0:
        return None
    ordered = sorted(key_counts.items(), key=lambda item: (-item[1], item[0]))
    pairs = ", ".join(f"{key}={count}" for key, count in ordered)
    return f"json: {pairs}"


def profile_array_column(
    conn: Connection,
    table: Table,
    column: Any,
    total_rows: int,
    indexed: bool,
    timeout_seconds: int = 0,
) -> str | None:
    """Return min/avg/max element counts for an ARRAY column as an annotation body."""
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
            timeout_seconds,
        ).one()
    except query_timeout.QueryTimeout:
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
    return f"array: {', '.join(parts)}" if parts else None


def _json_value_in_bounds(value: Any) -> bool:
    try:
        return len(json_dumps(value)) <= JSON_MAX_VALUE_BYTES
    except (TypeError, ValueError):
        return False


def _json_keys(value: Any) -> list[str]:
    if isinstance(value, dict):
        return [str(key) for key in value]
    return []


def _array_length_expr(conn: Connection, column: Any):
    dialect = conn.dialect.name
    if dialect == "postgresql":
        # cardinality() handles multi-dim and empty arrays for 1-D inputs.
        return func.cardinality(column)
    if dialect == "duckdb":
        return func.len(column)
    if dialect == "bigquery":
        return func.array_length(column)
    # Fallback: array_length(col, 1) works on PostgreSQL-compatible dialects.
    return func.array_length(column, 1)


def is_identifier_name(column_name: str) -> bool:
    return column_name.lower().endswith("id")


def format_value_counts(values: list[tuple[Any, int]]) -> str:
    parts = []
    for value, count in values:
        text = format_value(value)
        if isinstance(value, str):
            # Quote strings so they are distinguishable from numbers and from
            # the value separator, and can't run into the count that follows.
            text = f'"{text}"'
        parts.append(f"{text}={count}")
    return ", ".join(parts)


def format_value(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, float):
        return f"{value:g}"
    if isinstance(value, Decimal):
        # PostgreSQL NUMERIC aggregates carry full scale (e.g.
        # ``4.0000000000000000``); render through float with 12 significant
        # digits so the inline value line stays compact while preserving enough
        # precision for avg/median.
        return f"{float(value):.12g}"
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
