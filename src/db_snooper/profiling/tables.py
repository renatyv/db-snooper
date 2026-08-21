from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from random import randint
from typing import Any

from sqlalchemy import (
    Column,
    Float,
    Integer,
    Numeric,
    Table,
    desc,
    func,
    select,
    text,
)
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.elements import Label
from sqlalchemy.sql.sqltypes import NullType

from db_snooper import query_timeout
from db_snooper.contracts import ProfileOptions
from db_snooper.database_stats import (
    estimate_row_count,
    get_catalog_column_stats,
    get_indexed_column_names,
)
from db_snooper.profiling.columns import (
    JSON_MAX_VALUE_BYTES,
    format_value,
    format_value_counts,
    get_unique_column_names,
    is_numeric,
    json_dumps,
    jsonable,
    profile_column,
    truncate_text,
)
from db_snooper.profiling.models import ColumnProfile
from db_snooper.shared import is_sensitive, quote_ident


@dataclass
class TableProfile:
    """Structured profile for a single table, rendered as one compact block.

    The normal path fills ``column_tokens`` (``(name, '"name" type[ flags]')``
    pairs merged with ``column_profiles`` into the ``columns:`` block) plus
    ``indexes_line``/``fk_line``. When introspection fully fails, ``raw_ddl``
    holds the last-resort CREATE TABLE block (rendered as a fenced ``sql``
    block), the header fields are ``None``, and column profiling is skipped.
    ``sample_*`` fields drive ``samples:``/``all rows:``.
    """

    column_tokens: list[tuple[str, str]] | None = None
    indexes_line: str | None = None
    fk_line: str | None = None
    raw_ddl: list[str] | None = None
    fallback_note: str | None = None
    column_profiles: list[ColumnProfile] = field(default_factory=list)
    sample_columns: list[str] = field(default_factory=list)
    sample_rows: list[dict[str, Any]] = field(default_factory=list)
    sample_labels: list[str] = field(default_factory=list)
    is_small_table_all_rows: bool = False
    row_count_display: str = ""
    # When True, catalog estimates are tagged "(from db stats)" per spec line 18.
    from_db_stats: bool = False
    # Skip/diagnostic note rendered as a trailing bullet under the table block
    # (e.g. a timed-out row count). Empty when the table profiled cleanly.
    note: str | None = None


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
    relationships: list[Relationship], schema: str | None, dialect_name: str
) -> list[str]:
    """Render foreign keys as ``- "parent"."col" ← "child"."col"`` bullets.

    The parent (referenced) column leads each line and the arrow points back
    at the children that reference it, so a column referenced by many tables
    reads as ``- "parent"."col" ← "child1"."col", "child2"."col"``. The arrow
    always points parent ← child regardless of how many children there are,
    keeping the section's direction consistent. Lines are sorted by parent,
    turning the section into an index of "what references each parent column".

    Table and column names are delimited (see
    :func:`db_snooper.shared.quote_ident`), so each side reads like the
    qualified column reference to use in a join. Composite keys render as
    ``"table".("c1", "c2")``. The parent table is schema-qualified only when
    it lives in a different schema than the one being profiled, keeping the
    common single-schema case compact.
    """
    groups: dict[str, list[Relationship]] = {}
    for rel in relationships:
        groups.setdefault(_parent_display(rel, schema, dialect_name), []).append(
            rel
        )

    lines: list[str] = []
    for parent, rels in sorted(groups.items()):
        rels.sort(key=lambda r: (r.constrained_table, r.constrained_columns))
        children: list[str] = []
        for rel in rels:
            child = _format_relationship_side(
                (rel.constrained_table,), rel.constrained_columns, dialect_name
            )
            if child not in children:
                children.append(child)
        lines.append(f"- {parent} ← {', '.join(children)}")
    return lines


def _format_relationship_side(
    table_parts: tuple[str, ...], columns: tuple[str, ...], dialect_name: str
) -> str:
    qualified = ".".join(quote_ident(part, dialect_name) for part in table_parts)
    if len(columns) == 1:
        return f"{qualified}.{quote_ident(columns[0], dialect_name)}"
    quoted = ", ".join(quote_ident(col, dialect_name) for col in columns)
    return f"{qualified}.({quoted})"


def _parent_display(rel: Relationship, schema: str | None, dialect_name: str) -> str:
    """Render the parent (referred) side of ``rel``, schema-qualifying it only
    when it lives outside the schema being profiled."""
    parts = (rel.referred_table,)
    if rel.referred_schema and rel.referred_schema != schema:
        parts = (rel.referred_schema, rel.referred_table)
    return _format_relationship_side(parts, rel.referred_columns, dialect_name)


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
    skip_reason: str | None = None

    @property
    def is_empty(self) -> bool:
        return self.total_rows == 0

    def all_rows_listed(self, options: ProfileOptions) -> bool:
        """True when the table is small enough that every row is dumped.

        Empty tables return False: with no rows dumped, nothing reveals the
        schema, so the CREATE TABLE is still required (when the table is
        included at all).
        """
        if self.total_rows is None or self.is_large or self.skip_reason:
            return False
        if self.total_rows == 0:
            return False
        return self.total_rows <= options.small_table_threshold


def resolve_table_size(
    conn: Connection, table: Table, options: ProfileOptions
) -> TableSizeInfo:
    """Determine a table's row count once so DDL and profiling decisions share it."""
    estimate = estimate_row_count(conn, table)
    if options.metadata_only:
        if estimate is None:
            return TableSizeInfo(
                total_rows=None,
                estimate=None,
                is_large=False,
                skip_reason="metadata-only; catalog row estimate unavailable",
            )
        return TableSizeInfo(total_rows=None, estimate=estimate, is_large=True)
    if estimate is not None and estimate >= options.large_table_threshold:
        return TableSizeInfo(total_rows=None, estimate=estimate, is_large=True)
    if conn.dialect.name == "bigquery" and estimate is not None:
        return TableSizeInfo(total_rows=estimate, estimate=estimate, is_large=False)
    try:
        total_rows = query_timeout.execute(
            conn, select(func.count()).select_from(table), options.query_timeout
        ).scalar_one()
    except query_timeout.QueryTimeout:
        return TableSizeInfo(
            total_rows=None,
            estimate=estimate,
            is_large=False,
            skip_reason=f"row count query timeout > {options.query_timeout}s",
        )
    except query_timeout.QueryBudgetExceeded as exc:
        return TableSizeInfo(
            total_rows=None, estimate=estimate, is_large=False, skip_reason=str(exc)
        )
    return TableSizeInfo(total_rows=total_rows, estimate=estimate, is_large=False)


def profile_table_from_stats(
    conn: Connection, table: Table, estimate: int
) -> TableProfile:
    """Profile a too-large-to-scan table entirely from catalog statistics.

    Every metric is an estimate; per spec line 18 each value line is tagged
    ``(from db stats)`` and counts use the ``≈`` marker so they are
    distinguishable from exact metrics. Sensitive columns emit ``redacted``.
    """
    column_profiles: list[ColumnProfile] = []
    catalog = get_catalog_column_stats(conn, table, estimate)
    for column in table.columns:
        sensitive = is_sensitive(column.name)
        if sensitive:
            column_profiles.append(
                ColumnProfile(
                    name=column.name,
                    value_line="redacted",
                    is_sensitive=True,
                    is_unique_identifier=False,
                    dropped_from_samples=False,
                )
            )
            continue
        stat = catalog.get(column.name)
        body = _catalog_value_line(column, stat, estimate)
        if body is None:
            # No catalog stats for this column: nothing to say inline.
            continue
        column_profiles.append(
            ColumnProfile(
                name=column.name,
                value_line=f"{body} (from db stats)",
                is_sensitive=False,
                is_unique_identifier=False,
                dropped_from_samples=False,
            )
        )
    return TableProfile(
        row_count_display=f"≈{estimate}",
        column_profiles=column_profiles,
        from_db_stats=True,
    )


def _catalog_value_line(column: Any, stat: Any, estimate: int) -> str | None:
    """Build the inline metric body (without the ``(from db stats)`` tag) from
    one column's catalog statistics."""
    if stat is None:
        return None
    parts: list[str] = []
    if stat.null_frac is not None:
        nulls = round(stat.null_frac * estimate)
        parts.append(f"nulls≈{nulls}")
    if stat.distinct is not None:
        parts.append(f"distinct≈{stat.distinct}")
    if (
        is_numeric(column)
        and stat.min_value is not None
        and stat.max_value is not None
    ):
        parts.append(
            f"min≈{format_value(stat.min_value)}, max≈{format_value(stat.max_value)}"
        )
    if stat.top_values:
        parts.append(format_value_counts(list(stat.top_values)))
    return ", ".join(parts) if parts else None


def _format_cell(value: Any) -> str:
    """Render a sampled value as a markdown-table cell.

    ``None`` becomes ``null``; booleans become lowercase ``true``/``false``;
    containers use compact JSON. Values are capped (with ``…``) so a long
    string or JSON blob cannot stretch the table. Pipes are escaped and
    newlines collapsed so a value can never break the surrounding table row.
    """
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        try:
            text_value = json_dumps(value)
        except (TypeError, ValueError):
            text_value = str(value)
    else:
        text_value = format_value(value)
    return truncate_text(str(text_value)).replace("|", "\\|").replace("\n", " ")


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
        return ["| column | " + " | ".join(column_labels) + " |"]
    width = 1 + len(column_labels)
    lines = [
        "| column | " + " | ".join(column_labels) + " |",
        "|" + "|".join(["---"] * width) + "|",
    ]
    for name in column_names:
        cells = [_format_cell(row.get(name)) for row in rows]
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    return lines


def select_sample_columns(column_profiles: list[ColumnProfile]) -> list[str]:
    """Pick which columns appear in the ``samples:`` table.

    Excluded: sensitive columns (redacted elsewhere) and columns flagged
    ``dropped_from_samples`` (per-row JSON/array/TEXT diagnostics whose concrete
    values don't add information). Everything else is kept — identifiers,
    numeric ranges, timestamps, foreign keys, and any column whose value line
    is merely ``N distinct`` all benefit from showing actual values.
    """
    return [
        profile.name
        for profile in column_profiles
        if not profile.is_sensitive and not profile.dropped_from_samples
    ]


def profile_table(
    conn: Connection,
    table: Table,
    options: ProfileOptions,
    report_column: Callable[[str], None] | None = None,
    size_info: TableSizeInfo | None = None,
    allow_table_sample: bool = True,
) -> TableProfile:
    if size_info is None:
        size_info = resolve_table_size(conn, table, options)
    if size_info.is_large:
        profile = profile_table_from_stats(conn, table, size_info.estimate)
        # Header lines are derived from the reflected table introspection.
        return profile
    if size_info.skip_reason:
        return TableProfile(
            row_count_display="",
            note=f"skipped ({size_info.skip_reason})",
        )
    total_rows = size_info.total_rows
    if total_rows is None:
        # Unreachable: is_large/skip_reason return early above.
        return TableProfile(
            row_count_display="",
            note="skipped (row count unavailable)",
        )

    if total_rows <= options.small_table_threshold:
        sampled: list[dict[str, Any]] = []
        note: str | None = None
        try:
            with query_timeout.metric([], "sampled rows"):
                sampled = sample_rows(
                    conn, table, options.small_table_threshold, options.query_timeout
                )
        except (TypeError, ValueError):
            # Result-processor crash (e.g. a date-typed SQLite column holding
            # garbage text): keep profiling, drop only the row dump.
            sampled = []
            note = "sampled rows skipped (unreadable values)"
        labels = [f"row {index + 1}" for index in range(len(sampled))]
        column_profiles = _profile_all_columns(
            conn, table, options, int(total_rows), report_column
        )
        # Small tables (<10 rows) emit both the columns: profiles and all
        # rows: per spec.
        sample_columns = select_sample_columns(column_profiles)
        return TableProfile(
            column_profiles=column_profiles,
            sample_columns=sample_columns,
            sample_rows=sampled,
            sample_labels=labels,
            is_small_table_all_rows=True,
            row_count_display=str(total_rows),
            note=note,
        )

    # Larger table: latest + random rows, then per-column profiles.
    row_skips: list[tuple[str, str]] = []
    latest: list[dict[str, Any]] = []
    try:
        with query_timeout.metric(row_skips, "latest rows"):
            latest = latest_rows(
                conn, table, options.latest_row_limit, options.query_timeout
            )
    except (TypeError, ValueError):
        latest = []
        row_skips.append(("latest rows", "unreadable values"))
    random_sample: list[dict[str, Any]] = []
    dialect = conn.dialect.name
    if dialect in {"mysql", "mariadb", "bigquery", "postgresql"} and not allow_table_sample:
        row_skips.append(
            ("random rows", "native table sampling is unavailable for views")
        )
    elif options.random_sample_percent <= 0:
        row_skips.append(
            ("random rows", "disabled by ProfileOptions(random_sample_percent=0)")
        )
    else:
        try:
            with query_timeout.metric(row_skips, "random rows"):
                random_sample = random_rows(
                    conn,
                    table,
                    options.random_row_limit,
                    options.query_timeout,
                    options.random_sample_percent,
                    total_rows,
                )
        except (TypeError, ValueError):
            random_sample = []
            row_skips.append(("random rows", "unreadable values"))

    combined = list(latest) + list(random_sample)
    labels = ["latest"] * len(latest) + ["sample"] * len(random_sample)
    column_profiles = _profile_all_columns(
        conn, table, options, int(total_rows), report_column
    )
    sample_columns = select_sample_columns(column_profiles)
    note = None
    if row_skips:
        note = "; ".join(f"{m} skipped ({r})" for m, r in row_skips)
    return TableProfile(
        column_profiles=column_profiles,
        sample_columns=sample_columns,
        sample_rows=combined,
        sample_labels=labels,
        is_small_table_all_rows=False,
        row_count_display=str(total_rows),
        note=note,
    )


def _profile_all_columns(
    conn: Connection,
    table: Table,
    options: ProfileOptions,
    total_rows: int,
    report_column: Callable[[str], None] | None,
) -> list[ColumnProfile]:
    """Profile every column of ``table`` in declared order."""
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
    profiles: list[ColumnProfile] = []
    for column in table.columns:
        if report_column is not None:
            report_column(column.name)
        profiles.append(
            profile_column(
                conn,
                table,
                column,
                total_rows,
                unique_columns,
                indexed_columns,
                options.query_timeout,
                catalog_stat=catalog_stats.get(column.name),
            )
        )
    return profiles


def _sample_select(conn: Connection, table: Table) -> Any:
    """SELECT over every column, neutralizing SQLite's numeric processors.

    REAL/NUMERIC affinity keeps non-convertible text, and SQLAlchemy's Decimal
    result processor then raises while fetching the row. NullType labels fetch
    raw values for those columns (SQLite only — other dialects enforce their
    numeric types).
    """
    if conn.dialect.name != "sqlite":
        return select(table)
    columns = [
        Label(column.name, column, type_=NullType())
        if isinstance(column.type, (Float, Numeric))
        else column
        for column in table.columns
    ]
    return select(*columns)


def sample_rows(
    conn: Connection, table: Table, limit: int, timeout_seconds: int = 0
) -> list[dict[str, Any]]:
    order_columns = _order_columns(conn, table)
    statement = _sample_select(conn, table).order_by(*order_columns).limit(limit)
    return rows_for_statement(conn, table, statement, timeout_seconds)


def latest_rows(
    conn: Connection, table: Table, limit: int, timeout_seconds: int = 0
) -> list[dict[str, Any]]:
    order_columns = _order_columns(conn, table)
    statement = (
        _sample_select(conn, table)
        .order_by(*(desc(column) for column in order_columns))
        .limit(limit)
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
    conn: Connection,
    table: Table,
    limit: int,
    timeout_seconds: int = 0,
    sample_percent: float = 0.1,
    total_rows: int = 0,
) -> list[dict[str, Any]]:
    if conn.dialect.name == "bigquery":
        qualified = conn.dialect.identifier_preparer.format_table(table)
        statement = text(
            f"SELECT * FROM {qualified} TABLESAMPLE SYSTEM "
            f"({sample_percent:g} PERCENT) LIMIT {limit}"
        )
        return rows_for_statement(conn, table, statement, timeout_seconds)
    if conn.dialect.name == "postgresql":
        sampled = table.tablesample(sample_percent)
        statement = select(
            *(sampled.c[column.name].label(column.name) for column in table.columns)
        ).limit(limit)
        return rows_for_statement(conn, table, statement, timeout_seconds)
    if conn.dialect.name in {"mysql", "mariadb"}:
        return _mysql_random_rows(conn, table, limit, timeout_seconds, total_rows)
    statement = _sample_select(conn, table).order_by(func.random()).limit(limit)
    return rows_for_statement(conn, table, statement, timeout_seconds)


# Below this size an ORDER BY RAND() filesort is cheap; above it, keyless
# tables stream through a RAND() filter instead of sorting.
_MYSQL_SORT_ROW_LIMIT = 10_000
# Keep-rate multiplier for the filter: rows arrive with probability p, so a
# p of safety*limit/total_rows expects to fill the limit after ~total/safety
# rows read and to over-deliver by the safety factor.
_MYSQL_FILTER_SAFETY = 10.0


def _mysql_random_rows(
    conn: Connection,
    table: Table,
    limit: int,
    timeout_seconds: int,
    total_rows: int,
) -> list[dict[str, Any]]:
    """Random rows on MySQL/MariaDB, which have no TABLESAMPLE clause.

    With a numeric single-column primary key, read MIN/MAX (two index dives)
    and seek to a random key value in between — the optimizer cannot shortcut
    an SQL-side ``FLOOR(MIN(pk) + (MAX(pk) - MIN(pk)) * RAND())`` to index
    dives, so the threshold is drawn here. Spans [MIN, MAX] so keys that
    don't start near 0 (shard offsets, snowflake ids) don't collapse onto
    the table head; rows after id gaps are somewhat more likely to be
    picked, which sample rows tolerate.

    Without such a key, stream rows through a RAND() filter that stops after
    ``limit`` matches (biased toward the storage-order prefix; the statement
    timeout bounds the scan), and only sort the whole table with
    ``ORDER BY RAND`` when it is small enough for that to be trivial.
    """
    key = _random_seek_key(table)
    if key is not None:
        bounds = query_timeout.execute(
            conn, select(func.min(key), func.max(key)), timeout_seconds
        ).one_or_none()
        if bounds is not None and bounds[0] is not None:
            threshold = randint(int(bounds[0]), int(bounds[1]))
            statement = (
                _sample_select(conn, table)
                .where(key >= threshold)
                .order_by(key)
                .limit(limit)
            )
            return rows_for_statement(conn, table, statement, timeout_seconds)
    elif total_rows > _MYSQL_SORT_ROW_LIMIT:
        fraction = min(1.0, _MYSQL_FILTER_SAFETY * limit / total_rows)
        statement = _sample_select(conn, table).where(func.rand() < fraction).limit(limit)
        return rows_for_statement(conn, table, statement, timeout_seconds)
    statement = _sample_select(conn, table).order_by(func.rand()).limit(limit)
    return rows_for_statement(conn, table, statement, timeout_seconds)


def _random_seek_key(table: Table) -> Column | None:
    """The single integer primary-key column a random seek can index, if any."""
    columns = list(table.primary_key.columns)
    if len(columns) == 1 and isinstance(columns[0].type, Integer):
        return columns[0]
    return None


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
    """Cap oversized container values (per spec: truncated with a trailing
    ``…``) so sampled-row output cannot be dominated by a single huge
    JSON/ARRAY value."""
    encoded = jsonable(value)
    if isinstance(encoded, (dict, list)):
        try:
            serialized = json_dumps(encoded)
        except (TypeError, ValueError):
            return encoded
        if len(serialized) > JSON_MAX_VALUE_BYTES:
            return truncate_text(serialized)
    return encoded
