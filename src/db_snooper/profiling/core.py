from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import MetaData, Table, inspect
from sqlalchemy.engine import Engine

from db_snooper import __version__, query_timeout
from db_snooper.permissions import PermissionReport, check_permissions, format_warnings
from db_snooper.profiling.models import ProfileOptions, ProfileProgress
from db_snooper.profiling.tables import get_table_ddl, profile_table

_logger = logging.getLogger("db_snooper")


def list_schema_tables(engine: Engine, options: ProfileOptions) -> list[str]:
    inspector = inspect(engine)
    tables = sorted(inspector.get_table_names(schema=options.schema))
    if options.include_tables is not None:
        tables = [table for table in tables if table in options.include_tables]
    tables = [table for table in tables if table not in options.exclude_tables]
    return tables


def profile_database(
    engine: Engine,
    options: ProfileOptions,
    progress: ProfileProgress | None = None,
    table_names: list[str] | None = None,
    permission_report: PermissionReport | None = None,
) -> str:
    tables = table_names if table_names is not None else list_schema_tables(engine, options)

    database = engine.url.database or ""
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    lines = [
        "-- db-snooper",
        f"-- version: {__version__}",
        f"-- generated_at_utc: {generated_at}",
        f"-- dialect: {engine.dialect.name}",
        f"-- database: {database}",
        f"-- schema: {options.schema or engine.dialect.default_schema_name or ''}",
        "",
    ]

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
        for index, table_name in enumerate(tables, start=1):
            if progress is not None:
                progress(index - 1, len(tables), table_name)
            table = Table(
                table_name, metadata, schema=options.schema, autoload_with=conn
            )
            ddl = get_table_ddl(conn, table)
            lines.extend(ddl)
            if lines[-1] != "":
                lines.append("")

            def report_column(column_name: str) -> None:
                if progress is not None:
                    progress(
                        index - 1, len(tables), f"{table_name} ({column_name})"
                    )

            lines.extend(
                profile_table(conn, table, options, report_column=report_column)
            )
            lines.append("")
            lines.append("")
            if progress is not None:
                progress(index, len(tables), table_name)

    return "\n".join(lines).rstrip() + "\n"
