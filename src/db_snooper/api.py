from __future__ import annotations

from collections.abc import Callable

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, URL

from db_snooper.profiler import ProfileOptions, ProfileProgress, profile_database
from db_snooper.schema_linker import SchemaLinkOptions, SchemaLinkProgress, link_schema

DatabaseInput = Engine | URL | str


def generate_profile(
    database: DatabaseInput,
    options: ProfileOptions | None = None,
    progress: ProfileProgress | None = None,
) -> str:
    """Generate a SQL profile from a SQLAlchemy engine or database URL."""
    return _generate_with_engine(database, lambda engine: profile_database(engine, options or ProfileOptions(), progress))


def generate_schema_links(
    database: DatabaseInput,
    options: SchemaLinkOptions | None = None,
    progress: SchemaLinkProgress | None = None,
) -> str:
    """Generate Markdown schema links from a SQLAlchemy engine or database URL."""
    return _generate_with_engine(database, lambda engine: link_schema(engine, options or SchemaLinkOptions(), progress))


def _generate_with_engine(database: DatabaseInput, generate: Callable[[Engine], str]) -> str:
    if isinstance(database, Engine):
        return generate(database)

    engine = create_engine(database)
    try:
        return generate(engine)
    finally:
        engine.dispose()
