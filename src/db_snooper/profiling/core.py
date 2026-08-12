from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import MetaData, Table, inspect
from sqlalchemy.engine import Engine

from db_snooper import query_timeout
from db_snooper._version import __version__
from db_snooper.contracts import (
    OBJECT_TABLE,
    ProfileProgress,
    SchemaProfilePlan,
)
from db_snooper.profiling.ddl import TableDdl, get_table_ddl
from db_snooper.profiling.tables import (
    COLUMNS_HEADING,
    INDEXES_HEADING,
    TableProfile,
    collect_relationships,
    format_relationships,
    profile_table,
    resolve_table_size,
)
from db_snooper.profiling.utility_dump import dump_create_table


def profile_schema(
    engine: Engine,
    plan: SchemaProfilePlan,
    progress: ProfileProgress | None = None,
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
        accessible = set(permission_report.accessible_tables)
        tables = [table for table in tables if table in accessible]
        if not tables:
            return "\n".join(lines).rstrip() + "\n"
        # Collect foreign-key relationships once (catalog metadata only, no row
        # scans) and emit a consolidated section up front. This survives the
        # small-table case where CREATE TABLE is omitted because every row is
        # dumped, so join hints stay available regardless of table size.
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

            # Resolve row count once (needs a reflected table) so the DDL and
            # profiling decisions below share it. Empty tables are skipped
            # entirely unless --include-empty-tables is set.
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

            lines.append(f"# {table_name}")
            lines.append("")

            # When every row is listed below, the CREATE TABLE is redundant: the
            # row data already exposes columns, types, and constraints.
            kind = kinds.get(table_name, OBJECT_TABLE)
            # A view's rows never reveal its SELECT definition, so always emit
            # the view DDL even when every row is listed (unlike base tables).
            skip_create_table = (
                kind == OBJECT_TABLE
                and size_info is not None
                and size_info.all_rows_listed(options)
            )

            ddl: TableDdl | None = None
            ddl_exc: Exception | None = None
            if not skip_create_table:
                if not options.use_dump_ddl and table is not None:
                    try:
                        ddl = get_table_ddl(conn, table, kind=kind)
                    # Any compiler/dialect failure should fall through to utility DDL.
                    except Exception as exc:  # noqa: BLE001
                        ddl_exc = exc

                if ddl is None:
                    fallback_schema = (
                        table.schema if table is not None else None
                    ) or options.schema
                    try:
                        ddl = dump_create_table(
                            engine.url, engine.dialect.name, table_name, fallback_schema
                        )
                    # Utility, parser, and OS failures become a per-table warning.
                    except Exception as exc:  # noqa: BLE001
                        ddl_exc = ddl_exc or exc
                        ddl = None
                    if ddl is not None:
                        lines.append(
                            f"- {table_name}: CREATE TABLE via utility fallback"
                        )

                if ddl is None:
                    exc = ddl_exc or reflect_exc
                    failed_ddl_tables.append(table_name)
                    lines.append(
                        f"- {table_name}: skipped (DDL generation failed: "
                        f"{type(exc).__name__}: {exc})"
                    )
                    lines.append("")
                    lines.append("")
                    if progress is not None:
                        progress(index, len(tables), table_name)
                    continue

                lines.append("```sql")
                lines.extend(ddl.create_table)
                lines.append("```")
                lines.append("")
                if ddl.indexes:
                    lines.append(INDEXES_HEADING)
                    lines.append("")
                    for index_ddl in ddl.indexes:
                        lines.append(f"- {index_ddl}")
                    lines.append("")

            if table is None:
                lines.append(
                    f"- {table_name}: column profiling skipped "
                    "(schema via utility fallback)"
                )
                lines.append("")
            else:

                # profile_table consumes this callback before the loop advances.
                def report_column(column_name: str) -> None:
                    if progress is not None:
                        progress(
                            index - 1,  # noqa: B023
                            len(tables),
                            f"{table_name} ({column_name})",  # noqa: B023
                        )

                table_profile: TableProfile | None = profile_table(
                    conn,
                    table,
                    options,
                    report_column=report_column,
                    size_info=size_info,
                )

                if table_profile is not None:
                    if table_profile.rows_heading:
                        lines.append(table_profile.rows_heading)
                        lines.append("")
                    if table_profile.rows_lines:
                        lines.extend(table_profile.rows_lines)
                        lines.append("")
                    if table_profile.columns_lines:
                        lines.append(COLUMNS_HEADING)
                        lines.append("")
                        lines.extend(table_profile.columns_lines)
                        lines.append("")
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
