from __future__ import annotations

from dataclasses import replace

from sqlalchemy.engine import Engine

from db_snooper.connection import list_schemas
from db_snooper.contracts import (
    ProfileDocument,
    ProfileOptions,
    ProfileProgress,
    ProfileRun,
    SchemaProfilePlan,
)
from db_snooper.permissions import check_permissions
from db_snooper.profiling.core import profile_schema, profile_schema_with_toc
from db_snooper.profiling.discovery import list_schema_tables
from db_snooper.profiling.suggestions import profile_suggestions
from db_snooper.query_timeout import BigQueryBudget


def build_schema_plan(engine: Engine, options: ProfileOptions) -> SchemaProfilePlan:
    tables, skipped_technical, kinds = list_schema_tables(engine, options)
    with engine.connect() as conn:
        permissions = check_permissions(
            conn, engine.dialect.name, options.schema, tables
        )
    return SchemaProfilePlan(
        options=options,
        table_names=tuple(tables),
        skipped_technical_tables=tuple(skipped_technical),
        permission_report=permissions,
        kinds=kinds,
    )


def profile_database(
    engine: Engine,
    options: ProfileOptions,
    progress: ProfileProgress | None = None,
) -> str:
    markdown, _ = profile_database_with_toc(engine, options, progress)
    return markdown


def profile_database_with_toc(
    engine: Engine,
    options: ProfileOptions,
    progress: ProfileProgress | None = None,
) -> tuple[str, str | None]:
    """Profile the single resolved schema, returning ``(markdown, toc | None)``."""
    budget = BigQueryBudget(options.max_bytes_billed)
    return profile_schema_with_toc(
        engine, build_schema_plan(engine, options), progress, bigquery_budget=budget
    )


def run_profiles(
    engine: Engine,
    options: ProfileOptions,
    per_table: bool,
    progress: ProfileProgress | None = None,
) -> ProfileRun:
    documents: list[ProfileDocument] = []
    warnings: list[str] = []
    reports = []
    bigquery_budget = BigQueryBudget(options.max_bytes_billed)
    for schema in list_schemas(engine, options.schema):
        schema_options = replace(options, schema=schema)
        plan = build_schema_plan(engine, schema_options)
        reports.append(plan.permission_report)
        if plan.skipped_technical_tables:
            warnings.append(
                f"Skipped technical tables in {schema}: "
                + ", ".join(sorted(plan.skipped_technical_tables))
            )

        # profile_schema consumes this callback before the loop advances.
        def schema_progress(current: int, total: int, item: str) -> None:
            if progress is not None:
                progress(current, total, f"{schema}: {item}")  # noqa: B023

        accessible = set(plan.permission_report.accessible_tables)
        if per_table:
            for table_name in plan.table_names:
                if table_name not in accessible:
                    continue
                table_plan = replace(
                    plan,
                    table_names=(table_name,),
                    skipped_technical_tables=(),
                )
                documents.append(
                    ProfileDocument(
                        schema=schema,
                        table=table_name,
                        markdown=profile_schema(
                            engine,
                            table_plan,
                            schema_progress,
                            bigquery_budget=bigquery_budget,
                        ),
                    )
                )
        else:
            # Schema-level profile: attach the TOC sidecar (None when disabled
            # or nothing to index). Per-table documents intentionally get no
            # TOC — each file holds exactly one table block.
            markdown, toc = profile_schema_with_toc(
                engine,
                plan,
                schema_progress,
                bigquery_budget=bigquery_budget,
            )
            documents.append(
                ProfileDocument(
                    schema=schema,
                    table=None,
                    markdown=markdown,
                    toc=toc,
                )
            )

    return ProfileRun(
        documents=tuple(documents),
        warnings=tuple(warnings),
        suggestions=tuple(profile_suggestions(reports, engine.dialect.name)),
    )
