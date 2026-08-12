from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from typing import Any

from sqlalchemy import Table, text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.schema import UniqueConstraint

from db_snooper.contracts import DEFAULT_LARGE_TABLE_THRESHOLD
from db_snooper.shared import bigquery_table_id

# Tables whose catalog row estimate is at/above this count are profiled from
# internal database stats only: COUNT(*) and all per-column aggregations are
# skipped because they would be far too slow. "Hundreds of millions or more".
LARGE_TABLE_THRESHOLD = DEFAULT_LARGE_TABLE_THRESHOLD


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
        if dialect == "bigquery":
            return _bigquery_row_count(conn, table.name, schema)
    except SQLAlchemyError:
        return None
    return None


def _postgres_row_estimate(
    conn: Connection, table_name: str, schema: str | None
) -> int | None:
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


def _mysql_row_estimate(
    conn: Connection, table_name: str, schema: str | None
) -> int | None:
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


def _duckdb_row_estimate(
    conn: Connection, table_name: str, schema: str | None
) -> int | None:
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


def _bigquery_row_count(
    conn: Connection, table_name: str, schema: str | None
) -> int | None:
    try:
        client = conn.connection.driver_connection._client
        project = getattr(conn.dialect, "project_id", None) or client.project
        table = client.get_table(bigquery_table_id(project, schema, table_name))
        return int(table.num_rows)
    except Exception:  # BigQuery client errors are not SQLAlchemy exceptions.
        return None


@dataclass(frozen=True)
class ColumnStat:
    """Per-column statistics read from a database's internal catalog.

    Every field is an *estimate* derived from catalog metadata, never the
    result of scanning the table. ``top_values`` holds ``(value, row_count)``
    pairs whose counts are likewise estimated.
    """

    null_frac: float | None = None
    distinct: int | None = None
    min_value: Any | None = None
    max_value: Any | None = None
    top_values: tuple[tuple[Any, int], ...] = ()


def get_catalog_column_stats(
    conn: Connection, table: Table, estimate: int | None
) -> dict[str, ColumnStat]:
    """Return cheap catalog-derived :class:`ColumnStat` per column, by name.

    Enriches profiles of very large tables (where scans are unaffordable) and
    backfills metrics skipped on medium-large tables. Any failure — missing
    stats table, permission denied, parse error — collapses to ``{}`` so callers
    always fall back gracefully.
    """
    dialect = conn.dialect.name
    try:
        if dialect == "postgresql":
            return _postgres_column_stats(conn, table, estimate)
        if dialect in {"mysql", "mariadb"}:
            # MariaDB connects through the pymysql driver, so dialect.name is
            # "mysql"; ``is_mariadb`` distinguishes the two at runtime.
            if getattr(conn.dialect, "is_mariadb", False):
                return _mariadb_column_stats(conn, table, estimate)
            return _mysql_column_stats(conn, table, estimate)
    except SQLAlchemyError:
        return {}
    return {}


def _postgres_column_stats(
    conn: Connection, table: Table, estimate: int | None
) -> dict[str, ColumnStat]:
    schema = table.schema or conn.dialect.default_schema_name or "public"
    rows = conn.execute(
        text(
            "SELECT attname, null_frac, n_distinct, "
            "histogram_bounds::text, most_common_vals::text, most_common_freqs "
            "FROM pg_stats WHERE schemaname = :schema AND tablename = :table "
            "AND NOT inherited"
        ),
        {"schema": schema, "table": table.name},
    )
    stats: dict[str, ColumnStat] = {}
    for attname, null_frac, n_distinct, bounds_text, mcv_text, mcf in rows:
        min_value = max_value = None
        bounds = parse_postgres_array(bounds_text) if bounds_text else []
        if bounds:
            min_value, max_value = bounds[0], bounds[-1]
        stats[attname] = ColumnStat(
            null_frac=_safe_frac(null_frac),
            distinct=_postgres_distinct(n_distinct, estimate),
            min_value=min_value,
            max_value=max_value,
            top_values=_postgres_top_values(mcv_text, mcf, estimate),
        )
    return stats


def _postgres_distinct(n_distinct: Any, estimate: int | None) -> int | None:
    if n_distinct is None:
        return None
    value = float(n_distinct)
    if value >= 0:
        return max(1, round(value))
    if estimate and estimate > 0:
        # Negative n_distinct is a fraction of rows (e.g. -1 == unique).
        return max(1, round(abs(value) * estimate))
    return None


def _postgres_top_values(
    mcv_text: str | None, mcf: list[float] | None, estimate: int | None
) -> tuple[tuple[Any, int], ...]:
    if not mcv_text or not mcf or not estimate or estimate <= 0:
        return ()
    values = parse_postgres_array(mcv_text)
    return tuple(
        (value, max(1, round(float(frequency) * estimate)))
        for value, frequency in zip(values, mcf)
    )[:10]


def _mysql_column_stats(
    conn: Connection, table: Table, estimate: int | None
) -> dict[str, ColumnStat]:
    schema = table.schema or conn.dialect.default_schema_name
    if not schema:
        return {}
    rows = conn.execute(
        text(
            "SELECT COLUMN_NAME, HISTOGRAM "
            "FROM information_schema.COLUMN_STATISTICS "
            "WHERE SCHEMA_NAME = :schema AND TABLE_NAME = :table"
        ),
        {"schema": schema, "table": table.name},
    )
    stats: dict[str, ColumnStat] = {}
    for column_name, histogram in rows:
        stat = mysql_histogram_summary(histogram, estimate)
        if stat is not None:
            stats[column_name] = stat
    return stats


def mysql_histogram_summary(histogram: Any, estimate: int | None) -> ColumnStat | None:
    """Parse a MySQL ``COLUMN_STATISTICS`` histogram JSON into a ColumnStat.

    Handles both histogram types:
    - ``singleton``: buckets are ``[value, cumulative_frequency]`` → yields
      distinct count, exact top values, and min/max from the value ordering.
    - ``equi-height``: buckets are ``[lower, upper, cumulative_frequency, ndv]``
      → yields min/max from the first/last bounds and a distinct estimate.
    The top-level ``null-values`` field gives the NULL fraction for both types.
    """
    if isinstance(histogram, (bytes, bytearray)):
        histogram = histogram.decode("utf-8", "replace")
    if isinstance(histogram, str):
        try:
            histogram = json.loads(histogram)
        except (TypeError, ValueError):
            return None
    if not isinstance(histogram, dict):
        return None

    null_frac = _safe_frac(histogram.get("null-values"))
    htype = histogram.get("histogram-type")
    buckets = histogram.get("buckets") or []
    min_value = max_value = None
    distinct: int | None = None
    top_values: tuple[tuple[Any, int], ...] = ()

    if htype == "singleton":
        distinct = len(buckets)
        if buckets:
            values = [bucket[0] for bucket in buckets]
            min_value, max_value = values[0], values[-1]
        if estimate and estimate > 0:
            previous = 0.0
            counts: list[tuple[Any, float]] = []
            for bucket in buckets:
                cumulative = float(bucket[1])
                counts.append((bucket[0], cumulative - previous))
                previous = cumulative
            top_values = tuple(
                sorted(
                    (
                        (value, max(1, round(frequency * estimate)))
                        for value, frequency in counts
                    ),
                    key=lambda item: (-item[1], str(item[0])),
                )
            )[:10]
    elif htype == "equi-height":
        ndv_total = 0
        for bucket in buckets:
            if len(bucket) >= 4 and bucket[3] is not None:
                try:
                    ndv_total += int(bucket[3])
                except (TypeError, ValueError):
                    pass
        distinct = ndv_total if ndv_total else None
        if buckets:
            min_value = buckets[0][0]
            max_value = buckets[-1][1]

    return ColumnStat(
        null_frac=null_frac,
        distinct=distinct,
        min_value=_decode_catalog_value(min_value),
        max_value=_decode_catalog_value(max_value),
        top_values=tuple(
            (_decode_catalog_value(value), count) for value, count in top_values
        ),
    )


def _mariadb_column_stats(
    conn: Connection, table: Table, estimate: int | None
) -> dict[str, ColumnStat]:
    schema = table.schema or conn.dialect.default_schema_name
    if not schema:
        return {}
    rows = conn.execute(
        text(
            "SELECT column_name, min_value, max_value, nulls_ratio, "
            "avg_frequency, histogram "
            "FROM mysql.column_stats "
            "WHERE db_name = :schema AND table_name = :table"
        ),
        {"schema": schema, "table": table.name},
    )
    stats: dict[str, ColumnStat] = {}
    for (
        column_name,
        min_value,
        max_value,
        nulls_ratio,
        avg_frequency,
        histogram,
    ) in rows:
        null_frac = _safe_frac(nulls_ratio)
        stats[column_name] = ColumnStat(
            null_frac=null_frac,
            distinct=_mariadb_distinct(avg_frequency, null_frac, estimate),
            min_value=_decode_catalog_value(min_value),
            max_value=_decode_catalog_value(max_value),
            top_values=_mariadb_top_values(histogram, null_frac, estimate),
        )
    return stats


def _mariadb_distinct(
    avg_frequency: Any, null_frac: float | None, estimate: int | None
) -> int | None:
    # avg_frequency is the average number of non-null rows sharing a value.
    if not avg_frequency or float(avg_frequency) <= 0 or not estimate or estimate <= 0:
        return None
    non_null_frac = 1.0 - (null_frac or 0.0)
    return max(1, round(estimate * non_null_frac / float(avg_frequency)))


def _mariadb_top_values(
    histogram: Any, null_frac: float | None, estimate: int | None
) -> tuple[tuple[Any, int], ...]:
    if isinstance(histogram, (bytes, bytearray)):
        histogram = histogram.decode("utf-8", "replace")
    if isinstance(histogram, str):
        try:
            histogram = json.loads(histogram)
        except (TypeError, ValueError):
            return ()
    if not isinstance(histogram, dict) or not estimate or estimate <= 0:
        return ()
    non_null_count = estimate * (1.0 - (null_frac or 0.0))
    counts: list[tuple[Any, float]] = []
    for bucket in histogram.get("histogram_hb", []):
        # Only singleton buckets (ndv == 1) name an individual value.
        if bucket.get("ndv") != 1:
            continue
        value = bucket.get("start")
        if value is None:
            continue
        counts.append((value, float(bucket.get("size", 0.0))))
    return tuple(
        sorted(
            (
                (
                    _decode_catalog_value(value),
                    max(1, round(frequency * non_null_count)),
                )
                for value, frequency in counts
            ),
            key=lambda item: (-item[1], str(item[0])),
        )
    )[:10]


def _safe_frac(value: Any) -> float | None:
    return float(value) if value is not None else None


def _decode_catalog_value(value: Any) -> Any:
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", "replace")
    return value


def parse_postgres_array(value: str) -> list[str]:
    # pg_stats exposes anyarray, which drivers cannot decode without knowing the
    # underlying type. Its text form uses standard PostgreSQL array quoting.
    if not (value.startswith("{") and value.endswith("}")):
        return []
    return next(
        csv.reader([value[1:-1]], delimiter=",", quotechar='"', escapechar="\\")
    )


def get_indexed_column_names(table: Table) -> set[str]:
    indexed = {column.name for column in table.primary_key.columns}
    for index in table.indexes:
        indexed.update(column.name for column in index.columns)
    for constraint in table.constraints:
        if isinstance(constraint, UniqueConstraint):
            indexed.update(column.name for column in constraint.columns)
    return indexed
