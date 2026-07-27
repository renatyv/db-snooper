from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import MetaData, Table, inspect
from sqlalchemy.engine import Engine

from db_snooper import __version__, query_timeout
from db_snooper.permissions import PermissionReport, check_permissions, format_warnings
from db_snooper.profiling.models import ProfileOptions, ProfileProgress
from db_snooper.profiling.tables import get_table_ddl, profile_table
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
    lines = [
        "-- db-snooper",
        f"-- version: {__version__}",
        f"-- generated_at_utc: {generated_at}",
        f"-- dialect: {engine.dialect.name}",
        f"-- database: {database}",
        f"-- schema: {options.schema or engine.dialect.default_schema_name or ''}",
    ]
    if table_names is None:
        tables, computed_skipped = list_schema_tables(engine, options)
        if skipped_technical_tables is None:
            skipped_technical_tables = computed_skipped
    if skipped_technical_tables:
        lines.append(
            "-- skipped technical tables: "
            + ", ".join(sorted(skipped_technical_tables))
        )
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
        for index, table_name in enumerate(tables, start=1):
            if progress is not None:
                progress(index - 1, len(tables), table_name)
            table = Table(
                table_name, metadata, schema=options.schema, autoload_with=conn
            )
            try:
                ddl = get_table_ddl(conn, table)
            except Exception as exc:
                _logger.warning(
                    "Skipped table '%s': could not generate DDL (%s: %s)",
                    table_name,
                    type(exc).__name__,
                    exc,
                )
                failed_ddl_tables.append(table_name)
                lines.append(
                    f"-- {table_name}: skipped (DDL generation failed: "
                    f"{type(exc).__name__}: {exc})"
                )
                lines.append("")
                lines.append("")
                if progress is not None:
                    progress(index, len(tables), table_name)
                continue
            lines.extend(ddl)
            if lines[-1] != "":
                lines.append("")

            def report_column(column_name: str) -> None:
                if progress is not None:
                    progress(
                        index - 1, len(tables), f"{table_name} ({column_name})"
                    )
            try:
                table_prodile_strings = profile_table(conn, table, options, report_column=report_column)
                lines.extend(
                    table_prodile_strings
                )
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
        lines.append(f"-- {summary}")
        lines.append("")

    if failed_profile_tables:
        summary = (
            f"Skipped {len(failed_profile_tables)} table(s) due to Profile generation "
            f"errors: {', '.join(failed_profile_tables)}"
        )
        _logger.warning(summary)
        lines.append(f"-- {summary}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
