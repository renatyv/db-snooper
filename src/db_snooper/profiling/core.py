from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import MetaData, Table, inspect
from sqlalchemy.engine import Engine

from db_snooper import query_timeout
from db_snooper._version import __version__
from db_snooper.contracts import (
    OBJECT_MATERIALIZED_VIEW,
    OBJECT_TABLE,
    OBJECT_VIEW,
    ProfileProgress,
    SchemaProfilePlan,
)
from db_snooper.profiling.ddl import TableDdl, get_table_ddl
from db_snooper.profiling.schema_header import (
    format_columns_line,
    format_fk_line,
    format_indexes_line,
)
from db_snooper.profiling.tables import (
    TableProfile,
    _format_rows_table,
    collect_relationships,
    format_relationships,
    profile_table,
    resolve_table_size,
)
from db_snooper.profiling.utility_dump import dump_create_table
from db_snooper.query_timeout import BigQueryBudget


def profile_schema(
    engine: Engine,
    plan: SchemaProfilePlan,
    progress: ProfileProgress | None = None,
    bigquery_budget: BigQueryBudget | None = None,
) -> str:
    options = plan.options
    tables = list(plan.table_names)
    skipped_technical_tables = plan.skipped_technical_tables
    permission_report = plan.permission_report
    kinds = plan.kinds
    database = (
        engine.url.host if engine.dialect.name == "bigquery" else engine.url.database
    ) or ""
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    schema_value = (
        options.schema
        or getattr(engine.dialect, "dataset_id", None)
        or engine.dialect.default_schema_name
        or ""
    )
    lines = [
        "---",
        "generator: db-snooper",
        f"version: {__version__}",
        f"generated_at_utc: {generated_at}",
        f"dialect: {engine.dialect.name}",
        f"database: {database}",
        f"schema: {schema_value}",
    ]
    if skipped_technical_tables:
        lines.append("skipped_technical_tables:")
        for name in sorted(skipped_technical_tables):
            lines.append(f"  - {name}")
    lines.append("---")
    lines.append("")

    with engine.connect() as conn:
        query_timeout.apply_query_timeout(conn, options.query_timeout)
        query_timeout.apply_bigquery_budget(conn, bigquery_budget)
        accessible = set(permission_report.accessible_tables)
        tables = [table for table in tables if table in accessible]
        if not tables:
            return "\n".join(lines).rstrip() + "\n"
        # Collect foreign-key relationships once (catalog metadata only, no row
        # scans) and emit a consolidated section up front. This survives the
        # one-block-per-table rendering, so join hints stay available regardless
        # of table size.
        relationship_lines = format_relationships(
            collect_relationships(inspect(engine), tables, options.schema),
            options.schema,
        )
        if relationship_lines:
            lines.append("## Relationships")
            lines.append("")
            lines.extend(relationship_lines)
            lines.append("")
        metadata = MetaData()
        failed_ddl_tables: list[str] = []
        skipped_empty_tables: list[str] = []
        for index, table_name in enumerate(tables, start=1):
            if progress is not None:
                progress(index - 1, len(tables), table_name)

            table: Table | None = None
            reflect_exc: Exception | None = None
            try:
                table = Table(
                    table_name, metadata, schema=options.schema, autoload_with=conn
                )
            # Dialect plugins may raise non-SQLAlchemy errors; utility DDL is the fallback.
            except Exception as exc:  # noqa: BLE001
                reflect_exc = exc

            # Resolve row count once (needs a reflected table) so the header and
            # profiling decisions below share it. Empty tables are skipped
            # entirely unless include_empty_tables is enabled.
            size_info = (
                resolve_table_size(conn, table, options) if table is not None else None
            )
            if (
                size_info is not None
                and size_info.is_empty
                and not options.include_empty_tables
            ):
                skipped_empty_tables.append(table_name)
                if progress is not None:
                    progress(index, len(tables), table_name)
                continue

            kind = kinds.get(table_name, OBJECT_TABLE)
            table_profile, raw_ddl, fallback_note = _profile_one_table(
                conn,
                engine,
                table_name,
                table,
                reflect_exc,
                kind,
                size_info,
                options,
                progress,
                index,
                len(tables),
            )

            if table_profile is None:
                # DDL generation failed entirely; the per-table warning was
                # already recorded in _profile_one_table.
                failed_ddl_tables.append(table_name)
                continue

            _emit_table_block(
                lines,
                table_name,
                table_profile,
                table,
                conn,
                raw_ddl,
                fallback_note,
                size_info,
                options,
            )
            lines.append("")
            if progress is not None:
                progress(index, len(tables), table_name)

    if failed_ddl_tables:
        summary = (
            f"Skipped {len(failed_ddl_tables)} table(s) due to DDL generation "
            f"errors: {', '.join(failed_ddl_tables)}"
        )
        lines.append(f"- {summary}")
        lines.append("")

    if skipped_empty_tables:
        summary = f"Skipped {len(skipped_empty_tables)} empty table(s): " + ", ".join(
            sorted(skipped_empty_tables)
        )
        lines.append(f"- {summary}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _profile_one_table(
    conn,
    engine,
    table_name: str,
    table: Table | None,
    reflect_exc: Exception | None,
    kind: str,
    size_info,
    options,
    progress,
    index: int,
    total: int,
):
    """Profile a single table, returning (TableProfile, raw_ddl, fallback_note).

    Introspection produces the flattened header lines by default. The full
    ``CREATE TABLE`` DDL is only ever emitted as a last-resort fallback when
    introspection fails entirely; in that case ``raw_ddl`` carries the DDL
    block (rendered as fenced ``sql``) and the header lines in the
    ``TableProfile`` are left ``None``.
    """
    # ``raw_ddl`` is set in two cases: (1) a view/materialized view, whose
    # SELECT definition introspection cannot derive, so its CREATE VIEW DDL is
    # the header; and (2) the last-resort utility fallback when reflection of a
    # base table failed entirely.
    raw_ddl: list[str] | None = None
    fallback_note: str | None = None

    ddl: TableDdl | None = None
    ddl_exc: Exception | None = None
    if table is not None and not options.use_dump_ddl:
        try:
            ddl = get_table_ddl(conn, table, kind=kind)
        except Exception as exc:  # noqa: BLE001
            ddl_exc = exc

    # Views always need their SELECT definition, which introspection cannot
    # derive; emit the view DDL as the header in place of the flattened lines.
    if kind in {OBJECT_VIEW, OBJECT_MATERIALIZED_VIEW} and ddl is not None:
        raw_ddl = ddl.create_table

    if ddl is None and table is None:
        # Reflection failed: try the utility dump (pg_dump/mysqldump) as the
        # last-resort source of the DDL block.
        fallback_schema = options.schema
        try:
            ddl = dump_create_table(
                engine.url, engine.dialect.name, table_name, fallback_schema
            )
        except Exception as exc:  # noqa: BLE001
            ddl_exc = ddl_exc or exc
            ddl = None
        if ddl is not None:
            raw_ddl = ddl.create_table
            fallback_note = f"- {table_name}: CREATE TABLE via utility fallback"

    if table is None and raw_ddl is None:
        # Introspection and the utility fallback both failed; the caller marks
        # this table as failed and emits a summary bullet.
        return None, None, None

    # Profile the table (or note that profiling was skipped via utility DDL).
    if table is not None:
        def report_column(column_name: str) -> None:
            if progress is not None:
                progress(
                    index - 1,
                    total,
                    f"{table_name} ({column_name})",
                )

        table_profile = profile_table(
            conn,
            table,
            options,
            report_column=report_column,
            size_info=size_info,
            allow_table_sample=kind == OBJECT_TABLE,
        )
        # Flattened header lines come from introspection on the reflected base
        # table. Views/materialized views render their CREATE VIEW DDL instead
        # (via raw_ddl), so the introspection header is skipped for them.
        if raw_ddl is None:
            table_profile.columns_line = format_columns_line(table, conn)
            table_profile.indexes_line = format_indexes_line(table, conn)
            table_profile.fk_line = format_fk_line(table)
    else:
        # Introspection unavailable; only the raw DDL block remains.
        table_profile = TableProfile(
            note="column profiling skipped (schema via utility fallback)"
        )

    return table_profile, raw_ddl, fallback_note


def _emit_table_block(
    lines: list[str],
    table_name: str,
    table_profile: TableProfile,
    table: Table | None,
    conn,
    raw_ddl: list[str] | None,
    fallback_note: str | None,
    size_info,
    options,
) -> None:
    """Append the one-block-per-table rendering to ``lines``.

    Layout (blank-line-separated):
        # <table>  (rows=<N>)
        columns: ...
        indexes: ...
        fk: ...
        values:
        <col>: <inline>
        samples: / all rows:
        | column | ... |
    """
    row_display = table_profile.row_count_display
    if not row_display and size_info is not None:
        # Empty included tables: total_rows is 0.
        if size_info.total_rows is not None:
            row_display = str(size_info.total_rows)
        elif size_info.estimate is not None:
            row_display = f"≈{size_info.estimate}"
    header = f"# {table_name}"
    if row_display:
        header += f"  (rows={row_display})"
    lines.append(header)
    lines.append("")

    if fallback_note:
        lines.append(fallback_note)

    if raw_ddl is not None:
        # Last-resort: emit the raw CREATE TABLE in a fenced sql block in
        # place of the three header lines, then continue with values/samples.
        lines.append("```sql")
        lines.extend(raw_ddl)
        lines.append("```")
        lines.append("")
    else:
        for line in (
            table_profile.columns_line,
            table_profile.indexes_line,
            table_profile.fk_line,
        ):
            if line:
                lines.append(line)
        lines.append("")

    # values: block — one line per column (suppressed for included empty
    # tables, which carry no data context).
    is_empty_included = (
        size_info is not None
        and size_info.is_empty
        and options.include_empty_tables
    )
    if table_profile.column_profiles and not is_empty_included:
        lines.append("values:")
        for profile in table_profile.column_profiles:
            lines.append(f"{profile.name}: {profile.value_line}")
        lines.append("")

    # samples: / all rows: block.
    if is_empty_included:
        # Nothing to sample; emit an empty marker per spec line 14.
        lines.append("all rows:")
        lines.append("| column |  |")
    elif table_profile.sample_rows or table_profile.is_small_table_all_rows:
        if table_profile.is_small_table_all_rows:
            heading = "all rows:"
        else:
            heading = "samples:"
        lines.append(heading)
        sample_columns = table_profile.sample_columns
        if not sample_columns and table is not None:
            sample_columns = [c.name for c in table.columns]
        lines.extend(
            _format_rows_table(
                sample_columns,
                table_profile.sample_rows,
                table_profile.sample_labels,
            )
        )
        if table_profile.note:
            lines.append(f"- {table_profile.note}")
    elif table_profile.note:
        lines.append(f"- {table_profile.note}")
