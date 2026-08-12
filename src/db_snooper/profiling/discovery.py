from __future__ import annotations

from typing import Any

from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from db_snooper.contracts import (
    OBJECT_MATERIALIZED_VIEW,
    OBJECT_TABLE,
    OBJECT_VIEW,
    ProfileOptions,
)
from db_snooper.shared import is_technical_table


def list_schema_tables(
    engine: Engine, options: ProfileOptions
) -> tuple[list[str], list[str], dict[str, str]]:
    inspector = inspect(engine)
    base_tables = sorted(inspector.get_table_names(schema=options.schema))
    kinds: dict[str, str] = {name: OBJECT_TABLE for name in base_tables}
    for name, kind in _list_views(
        inspector, engine.dialect.name, options.schema
    ).items():
        kinds.setdefault(name, kind)

    all_objects = sorted(kinds)
    skipped_technical = (
        [name for name in all_objects if is_technical_table(name)]
        if not options.include_technical_tables
        else []
    )
    objects = [name for name in all_objects if name not in skipped_technical]
    if options.include_tables is not None:
        objects = [name for name in objects if name in options.include_tables]
    return (
        [name for name in objects if name not in options.exclude_tables],
        skipped_technical,
        kinds,
    )


def _list_views(inspector: Any, dialect: str, schema: str | None) -> dict[str, str]:
    kinds: dict[str, str] = {}
    try:
        for name in inspector.get_view_names(schema=schema):
            kinds[name] = OBJECT_VIEW
    except (SQLAlchemyError, NotImplementedError):
        pass
    if dialect == "postgresql":
        for name in _postgres_materialized_view_names(inspector, schema):
            kinds[name] = OBJECT_MATERIALIZED_VIEW
    return kinds


def _postgres_materialized_view_names(inspector: Any, schema: str | None) -> list[str]:
    method = getattr(inspector, "get_materialized_view_names", None)
    if method is None:
        return []
    try:
        return list(method(schema=schema))
    except (SQLAlchemyError, NotImplementedError):
        return []
