from __future__ import annotations

import re
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

# Kind of a schema object, used to choose the right DDL emitter. These are
# imported by profiling.core (importing core here would be circular).
OBJECT_TABLE = "table"
OBJECT_VIEW = "view"
OBJECT_MATERIALIZED_VIEW = "materialized_view"

# Section headings emitted inside each table profile. The table name is the
# top-level heading, so these nest one level below it.
ROWS_HEADING = "## Rows"
ALL_ROWS_HEADING = "## All rows"
COLUMNS_HEADING = "## Columns"
INDEXES_HEADING = "## Indexes"


@dataclass
class TableProfile:
    """Structured profile for a single table, split into renderable sections.

    ``rows_heading``/``rows_lines`` carry the sampled-rows section (``## Rows``
    for larger tables with a total + latest/sample table, ``## All rows`` for
    small tables that dump every row). ``columns_lines`` carries the per-column
    profile section (``## Columns``); it is empty for small tables and for
    tables whose column profiling was skipped.
    """

    rows_heading: str | None
    rows_lines: list[str]
    columns_lines: list[str]


@dataclass
class TableDdl:
    """CREATE TABLE DDL split from a table's index definitions.

    ``create_table`` holds the full CREATE TABLE statement (and any DDL that is
    not a standalone index). ``indexes`` holds *compact* index descriptors:
    the verbose ``CREATE [UNIQUE] INDEX <name> ON <table>`` prefix is stripped
    because an LLM building queries already knows the table (it is the section
    heading) and rarely needs the index name. The column list and any clauses
    (USING, WHERE, operator classes, ...) are kept, since those are what make
    an index relevant to query construction.
    """

    create_table: list[str]
    indexes: list[str]


# Matches the ``CREATE [UNIQUE] INDEX <name> ON [<schema>.]<table>`` prefix of
# an index DDL statement, capturing whether it was UNIQUE. Quoted ("...", `...`,
# [...]) or bare identifiers are accepted for both the index and table names.
_INDEX_PREFIX_RE = re.compile(
    r"^\s*CREATE\s+"
    r"(?P<unique>UNIQUE\s+)?"
    r"INDEX\s+"
    r"(?:\"[^\"]+\"|`[^`]+`|\[[^\]]+\]|\S+)\s+"
    r"ON\s+"
    r"(?:\"[^\"]+\"|`[^`]+`|\[[^\]]+\]|[\w.]+)\s*",
    re.IGNORECASE,
)


def compact_index_sql(sql: str) -> str:
    """Strip the ``CREATE [UNIQUE] INDEX <name> ON <table>`` prefix from DDL.

    ``(ival)`` and ``UNIQUE (fval)`` survive; ``USING gin (col)``, ``WHERE``
    predicates and operator classes are preserved. If the prefix can't be
    matched the input is returned unchanged (only trimmed of a trailing
    semicolon) so nothing is lost.
    """
    match = _INDEX_PREFIX_RE.match(sql)
    if match is None:
        return sql.strip().rstrip(";").strip()
    unique = (match.group("unique") or "").strip()
    rest = sql[match.end():].strip().rstrip(";").strip()
    return f"{unique} {rest}".strip() if unique else rest


def get_table_ddl(
    conn: Connection, table: Table, kind: str = OBJECT_TABLE
) -> TableDdl:
    if kind in {OBJECT_VIEW, OBJECT_MATERIALIZED_VIEW}:
        return get_view_ddl(conn, table, kind)
    dialect_name = conn.dialect.name
    if dialect_name == "sqlite":
        return get_sqlite_ddl(conn, table.name)
    if dialect_name in {"mysql", "mariadb"}:
        return get_mysql_ddl(conn, table)
    return get_reflected_ddl(conn, table)


def get_view_ddl(conn: Connection, table: Table, kind: str) -> TableDdl:
    """Return DDL for a view or materialized view.

    A view cannot be reconstructed from its reflected columns, so each dialect
    reads the stored definition (``pg_get_viewdef``, ``sqlite_master``,
    ``information_schema.views``, ``duckdb_views()``). Materialized views also
    expose their indexes, reflected from the catalog.
    """
    dialect_name = conn.dialect.name
    if dialect_name == "postgresql":
        return _postgres_view_ddl(conn, table, kind)
    if dialect_name == "sqlite":
        return _sqlite_view_ddl(conn, table.name)
    if dialect_name == "duckdb":
        return _duckdb_view_ddl(conn, table)
    if dialect_name in {"mysql", "mariadb"}:
        return _mysql_view_ddl(conn, table)
    # Unrecognized dialect: fall back to reflected columns so the object still
    # surfaces with its column shape rather than disappearing from the profile.
    return get_reflected_ddl(conn, table)


def _view_keyword(kind: str) -> str:
    return (
        "CREATE MATERIALIZED VIEW"
        if kind == OBJECT_MATERIALIZED_VIEW
        else "CREATE VIEW"
    )


def _materialized_view_indexes(conn: Connection, table: Table) -> list[str]:
    indexes: list[str] = []
    for index in sorted(table.indexes, key=lambda idx: idx.name or ""):
        full = ensure_semicolon(str(CreateIndex(index).compile(conn)))
        indexes.append(compact_index_sql(full))
    return indexes


def _postgres_view_ddl(conn: Connection, table: Table, kind: str) -> TableDdl:
    # pg_get_viewdef takes the relation OID and returns just the SELECT body;
    # joining pg_class avoids the ``::regclass`` cast that collides with
    # SQLAlchemy's ``:param`` bind syntax. Works for both views ('v') and
    # materialized views ('m').
    body = conn.execute(
        text(
            "SELECT pg_get_viewdef(c.oid, true) FROM pg_class c "
            "JOIN pg_namespace n ON n.oid = c.relnamespace "
            "WHERE n.nspname = :schema AND c.relname = :name"
        ),
        {"schema": table.schema, "name": table.name},
    ).scalar_one_or_none()
    qualified = conn.dialect.identifier_preparer.format_table(table)
    keyword = _view_keyword(kind)
    create_table: list[str] = []
    if body:
        create_table.append(
            ensure_semicolon(f"{keyword} {qualified} AS\n{body.strip().rstrip(';')}")
        )
    else:
        create_table.append(ensure_semicolon(f"{keyword} {qualified} AS SELECT *"))
    indexes = (
        _materialized_view_indexes(conn, table)
        if kind == OBJECT_MATERIALIZED_VIEW
        else []
    )
    return TableDdl(create_table=create_table, indexes=indexes)


def _sqlite_view_ddl(conn: Connection, table_name: str) -> TableDdl:
    # sqlite_master stores the full ``CREATE VIEW ... AS SELECT ...`` text.
    sql = conn.execute(
        text("SELECT sql FROM sqlite_master WHERE type = 'view' AND name = :name"),
        {"name": table_name},
    ).scalar_one_or_none()
    create_table = [ensure_semicolon(str(sql))] if sql else []
    return TableDdl(create_table=create_table, indexes=[])


def _duckdb_view_ddl(conn: Connection, table: Table) -> TableDdl:
    schema = table.schema or "main"
    sql = conn.execute(
        text(
            "SELECT sql FROM duckdb_views() "
            "WHERE schema_name = :schema AND view_name = :name"
        ),
        {"schema": schema, "name": table.name},
    ).scalar_one_or_none()
    create_table = [ensure_semicolon(str(sql))] if sql else []
    return TableDdl(create_table=create_table, indexes=[])


def _mysql_view_ddl(conn: Connection, table: Table) -> TableDdl:
    schema = table.schema or conn.dialect.default_schema_name
    body = conn.execute(
        text(
            "SELECT view_definition FROM information_schema.views "
            "WHERE table_schema = :schema AND table_name = :name"
        ),
        {"schema": schema, "name": table.name},
    ).scalar_one_or_none()
    qualified = conn.dialect.identifier_preparer.format_table(table)
    create_table: list[str] = []
    if body is not None:
        create_table.append(
            ensure_semicolon(f"CREATE VIEW {qualified} AS {body.strip().rstrip(';')}")
        )
    return TableDdl(create_table=create_table, indexes=[])


def get_sqlite_ddl(conn: Connection, table_name: str) -> TableDdl:
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

    create_table: list[str] = []
    if table_sql:
        create_table.append(ensure_semicolon(str(table_sql)))
    indexes = [compact_index_sql(ensure_semicolon(str(sql))) for sql in index_sql]
    return TableDdl(create_table=create_table, indexes=indexes)


# Matches a secondary/unique/fulltext/spatial index definition and captures its
# leading keyword (e.g. ``UNIQUE ``) so the generated index name can be dropped
# while keeping the indexed column list. ``PRIMARY KEY`` and ``CONSTRAINT ...
# FOREIGN KEY`` are not matched: no name sits between their ``KEY`` and ``(``.
_MYSQL_INDEX_NAME_RE = re.compile(
    r"\b((?:UNIQUE|FULLTEXT|SPATIAL)\s+)?KEY\s+(?:`[^`]+`|\w+)(?=\s*\()",
    re.IGNORECASE,
)


def _strip_mysql_noise(sql: str) -> str:
    """Normalize a MySQL ``SHOW CREATE TABLE`` statement for compact LLM context.

    Strips engine-specific noise: the no-op ``DEFAULT NULL`` column default,
    column/table ``CHARACTER SET``/``CHARSET`` and ``COLLATE``/``COLLATION``
    clauses, the ``ENGINE=`` table option, and the generated names on secondary
    and unique indexes (``KEY name (cols)`` -> ``KEY (cols)``). Primary keys,
    foreign keys (with their constraint names), ``UNIQUE`` constraints, and the
    indexed column lists are all preserved.
    """
    sql = re.sub(r"\s+DEFAULT\s+NULL\b", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s+CHARACTER\s+SET\s+\w+", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s+COLLATE\s+\w+", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s*ENGINE\s*=\s*\w+", "", sql, flags=re.IGNORECASE)
    sql = re.sub(
        r"\s*(?:DEFAULT\s+)?CHARSET\s*=\s*\w+", "", sql, flags=re.IGNORECASE
    )
    sql = re.sub(
        r"\s*(?:DEFAULT\s+)?COLL(?:ATE|ATION)\s*=\s*\w+", "", sql, flags=re.IGNORECASE
    )
    sql = _MYSQL_INDEX_NAME_RE.sub(r"\1KEY", sql)
    return sql


def get_mysql_ddl(conn: Connection, table: Table) -> TableDdl:
    quoted_table = conn.dialect.identifier_preparer.format_table(table)
    row = conn.exec_driver_sql(f"SHOW CREATE TABLE {quoted_table}").first()
    if row is None:
        return TableDdl(create_table=[], indexes=[])
    # MySQL embeds secondary indexes (KEY/UNIQUE KEY) inside CREATE TABLE, so
    # there are no separate index statements to extract. SHOW CREATE TABLE also
    # pads the statement with engine-specific noise (DEFAULT NULL, ENGINE,
    # CHARSET, COLLATE, generated index names); strip it for a compact profile.
    create_table = _strip_mysql_noise(str(row[1]))
    return TableDdl(create_table=[ensure_semicolon(create_table)], indexes=[])


def get_reflected_ddl(conn: Connection, table: Table) -> TableDdl:
    create_table = [ensure_semicolon(str(CreateTable(table).compile(conn)))]
    indexes: list[str] = []
    for index in sorted(table.indexes, key=lambda idx: idx.name or ""):
        full = ensure_semicolon(str(CreateIndex(index).compile(conn)))
        indexes.append(compact_index_sql(full))
    return TableDdl(create_table=create_table, indexes=indexes)


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
        return self.total_rows <= options.small_table_threshold


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
) -> TableProfile:
    # The table is too large to scan, but its catalog stats are free. Emit a
    # per-column summary derived entirely from those stats.
    rows_lines = [
        f"- total≈{estimate} (estimated from db stats; row/column profiling skipped)"
    ]
    columns_lines: list[str] = []
    catalog = get_catalog_column_stats(conn, table, estimate)
    for column in table.columns:
        stat = catalog.get(column.name)
        if stat is None:
            continue
        columns_lines.extend(_catalog_column_lines(column, stat, estimate))
    return TableProfile(
        rows_heading=ROWS_HEADING,
        rows_lines=rows_lines,
        columns_lines=columns_lines,
    )


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
            f"- {column.name} (from db stats): {', '.join(parts)}"
            if parts
            else f"- {column.name} (from db stats):"
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


def _format_cell(value: Any) -> str:
    """Render a sampled value as a markdown-table cell.

    ``None`` becomes ``null``; booleans become lowercase ``true``/``false``;
    containers use compact JSON. Pipes are escaped and newlines collapsed so a
    value can never break the surrounding table row.
    """
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        try:
            text = json_dumps(value)
        except (TypeError, ValueError):
            text = str(value)
    else:
        text = format_value(value)
    return str(text).replace("|", "\\|").replace("\n", " ")


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
        return ["- (no rows sampled)"]
    width = 1 + len(column_labels)
    lines = [
        "| column | " + " | ".join(column_labels) + " |",
        "|" + "|".join(["---"] * width) + "|",
    ]
    for name in column_names:
        cells = [_format_cell(row.get(name)) for row in rows]
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    return lines


def profile_table(
    conn: Connection,
    table: Table,
    options: ProfileOptions,
    report_column: Callable[[str], None] | None = None,
    size_info: TableSizeInfo | None = None,
) -> TableProfile:
    if size_info is None:
        size_info = resolve_table_size(conn, table, options)
    if size_info.is_large:
        return profile_table_from_stats(conn, table, size_info.estimate)
    if size_info.timed_out:
        return TableProfile(
            rows_heading=None,
            rows_lines=[f"- {table.name}: skipped (row count query timeout)"],
            columns_lines=[],
        )
    total_rows = size_info.total_rows
    if total_rows is None:
        # Unreachable: is_large/timed_out return early above.
        return TableProfile(
            rows_heading=None,
            rows_lines=[f"- {table.name}: skipped (row count unavailable)"],
            columns_lines=[],
        )

    column_names = [column.name for column in table.columns]

    if total_rows <= options.small_table_threshold:
        sampled: list[dict[str, Any]] = []
        with query_timeout.metric(conn, [], "sampled rows"):
            sampled = sample_rows(conn, table, options.small_table_threshold)
        labels = [f"row {index + 1}" for index in range(len(sampled))]
        rows_lines = _format_rows_table(column_names, sampled, labels)
        # Every row fits: we only reach here when total_rows <= threshold, and
        # the LIMIT is that same threshold, so the rows alone expose the count
        # and schema. No total is printed and the section is labelled "All
        # rows". The length guard is defensive against rows vanishing between
        # the COUNT and the SELECT.
        if sampled and len(sampled) >= total_rows:
            return TableProfile(
                rows_heading=ALL_ROWS_HEADING,
                rows_lines=rows_lines,
                columns_lines=[],
            )
        return TableProfile(
            rows_heading=ROWS_HEADING,
            rows_lines=[f"- total={total_rows}", "", *rows_lines],
            columns_lines=[],
        )

    # Larger table: total + latest + random rows in one transposed table,
    # then per-column profiles.
    rows_lines = [f"- total={total_rows}"]
    latest: list[dict[str, Any]] = []
    with query_timeout.metric(conn, [], "latest rows"):
        latest = latest_rows(conn, table, options.latest_row_limit)
    random_sample: list[dict[str, Any]] = []
    with query_timeout.metric(conn, [], "random rows"):
        random_sample = random_rows(conn, table, options.random_row_limit)

    combined = list(latest) + list(random_sample)
    labels = ["latest"] * len(latest) + ["sample"] * len(random_sample)
    rows_lines.append("")
    if combined:
        rows_lines.extend(_format_rows_table(column_names, combined, labels))
    else:
        rows_lines.append("- (no rows sampled)")

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
    columns_lines: list[str] = []
    for column in table.columns:
        if report_column is not None:
            report_column(column.name)
        columns_lines.extend(
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
    return TableProfile(
        rows_heading=ROWS_HEADING,
        rows_lines=rows_lines,
        columns_lines=columns_lines,
    )


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
