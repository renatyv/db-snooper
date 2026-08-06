from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import MetaData, Table, inspect
from sqlalchemy.engine import Engine

from db_snooper import __version__, query_timeout
from db_snooper.permissions import PermissionReport, check_permissions, format_warnings
from db_snooper.profiling.models import ProfileOptions, ProfileProgress
from db_snooper.profiling.tables import (
    TableDdl,
    get_table_ddl,
    profile_table,
    resolve_table_size,
)
from db_snooper.profiling.utility_dump import dump_create_table
from db_snooper.shared import is_technical_table

_logger = logging.getLogger("db_snooper")


def list_schema_tables(
    engine: Engine, options: ProfileOptions
) -> tuple[list[str], list[str]]:
    """Return ``(tables, skipped_technical)`` for the schema.

    Migration/DB-internal tables are excluded by default unless
    ``options.include_technical_tables`` is set; the excluded names are returned
    so the profile can record which tables were skipped.
    """
    inspector = inspect(engine)
    all_tables = sorted(inspector.get_table_names(schema=options.schema))
    if not options.include_technical_tables:
        skipped_technical = [t for t in all_tables if is_technical_table(t)]
        tables = [t for t in all_tables if not is_technical_table(t)]
    else:
        skipped_technical = []
        tables = list(all_tables)
    if options.include_tables is not None:
        tables = [table for table in tables if table in options.include_tables]
    tables = [table for table in tables if table not in options.exclude_tables]
    return tables, skipped_technical


def profile_database(
    engine: Engine,
    options: ProfileOptions,
    progress: ProfileProgress | None = None,
    table_names: list[str] | None = None,
    skipped_technical_tables: list[str] | None = None,
    permission_report: PermissionReport | None = None,
) -> str:
    tables = table_names if table_names is not None else []
    database = engine.url.database or ""
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    schema_value = options.schema or engine.dialect.default_schema_name or ""
    lines = [
        "---",
        "generator: db-snooper",
        f"version: {__version__}",
        f"generated_at_utc: {generated_at}",
        f"dialect: {engine.dialect.name}",
        f"database: {database}",
        f"schema: {schema_value}",
    ]
    if table_names is None:
        tables, computed_skipped = list_schema_tables(engine, options)
        if skipped_technical_tables is None:
            skipped_technical_tables = computed_skipped
    if skipped_technical_tables:
        lines.append("skipped_technical_tables:")
        for name in sorted(skipped_technical_tables):
            lines.append(f"  - {name}")
    lines.append("---")
    lines.append("")

    with engine.connect() as conn:
        query_timeout.apply_query_timeout(conn, options.query_timeout)
        if permission_report is None:
            permission_report = check_permissions(
                conn, engine.dialect.name, options.schema, tables
            )
            for warning in format_warnings(permission_report):
                _logger.warning(warning)
        accessible = set(permission_report.accessible_tables)
        tables = [table for table in tables if table in accessible]
        if not tables:
            _logger.warning("No accessible tables to profile; skipping schema.")
            return "\n".join(lines).rstrip() + "\n"
        metadata = MetaData()
        failed_ddl_tables: list[str] = []
        failed_profile_tables: list[str] = []
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
            except Exception as exc:
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

            lines.append(f"## {table_name}")
            lines.append("")

            # When every row is listed below, the CREATE TABLE is redundant: the
            # row data already exposes columns, types, and constraints.
            skip_create_table = size_info is not None and size_info.all_rows_listed(
                options
            )

            ddl: TableDdl | None = None
            ddl_exc: Exception | None = None
            if not skip_create_table:
                if not options.use_dump_ddl and table is not None:
                    try:
                        ddl = get_table_ddl(conn, table)
                    except Exception as exc:
                        ddl_exc = exc

                if ddl is None:
                    reason = (
                        "forced (--use-dump-ddl)"
                        if options.use_dump_ddl
                        else f"SQLAlchemy DDL failed ({type((ddl_exc or reflect_exc)).__name__})"
                    )
                    _logger.info("Utility fallback for '%s': %s", table_name, reason)
                    fallback_schema = (
                        table.schema if table is not None else None
                    ) or options.schema
                    try:
                        ddl = dump_create_table(
                            engine.url, engine.dialect.name, table_name, fallback_schema
                        )
                    except Exception as exc:
                        _logger.warning(
                            "utility fallback errored for '%s': %r", table_name, exc
                        )
                        ddl = None
                    if ddl is not None:
                        lines.append(
                            f"- {table_name}: CREATE TABLE via utility fallback"
                        )

                if ddl is None:
                    exc = ddl_exc or reflect_exc
                    _logger.warning(
                        "Skipped table '%s': could not generate DDL (%s: %s)",
                        table_name,
                        type(exc).__name__,
                        exc,
                    )
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
                    lines.append("- indexes:")
                    for index_ddl in ddl.indexes:
                        lines.append(f"  - {index_ddl}")
                    lines.append("")

            if table is None:
                lines.append(
                    f"- {table_name}: column profiling skipped "
                    "(schema via utility fallback)"
                )
            else:

                def report_column(column_name: str) -> None:
                    if progress is not None:
                        progress(
                            index - 1, len(tables), f"{table_name} ({column_name})"
                        )

                try:
                    table_prodile_strings = profile_table(
                        conn,
                        table,
                        options,
                        report_column=report_column,
                        size_info=size_info,
                    )
                    lines.extend(table_prodile_strings)
                except Exception as exc:
                    _logger.warning(
                        "Skipped table '%s': could not generate profile (%s: %s)",
                        table_name,
                        type(exc).__name__,
                        exc,
                    )
                    failed_profile_tables.append(table_name)
            lines.append("")
            lines.append("")
            if progress is not None:
                progress(index, len(tables), table_name)

    if failed_ddl_tables:
        summary = (
            f"Skipped {len(failed_ddl_tables)} table(s) due to DDL generation "
            f"errors: {', '.join(failed_ddl_tables)}"
        )
        _logger.warning(summary)
        lines.append(f"- {summary}")
        lines.append("")

    if failed_profile_tables:
        summary = (
            f"Skipped {len(failed_profile_tables)} table(s) due to Profile generation "
            f"errors: {', '.join(failed_profile_tables)}"
        )
        _logger.warning(summary)
        lines.append(f"- {summary}")
        lines.append("")

    if skipped_empty_tables:
        summary = f"Skipped {len(skipped_empty_tables)} empty table(s): " + ", ".join(
            sorted(skipped_empty_tables)
        )
        _logger.info(summary)
        lines.append(f"- {summary}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
