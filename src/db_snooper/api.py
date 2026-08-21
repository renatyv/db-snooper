from __future__ import annotations

from collections.abc import Callable

from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine

from db_snooper.application import profile_database_with_toc
from db_snooper.contracts import ProfileOptions, ProfileProgress

DatabaseInput = Engine | URL | str


def generate_profile(
    database: DatabaseInput,
    options: ProfileOptions | None = None,
    progress: ProfileProgress | None = None,
) -> str:
    """Generate a SQL profile from a SQLAlchemy engine or database URL."""
    markdown, _ = generate_profile_with_toc(database, options, progress)
    return markdown


def generate_profile_with_toc(
    database: DatabaseInput,
    options: ProfileOptions | None = None,
    progress: ProfileProgress | None = None,
) -> tuple[str, str | None]:
    """Generate a profile plus its TOC sidecar content.

    Returns ``(markdown, toc_markdown)``; ``toc_markdown`` is the content to
    write as ``<profile>.toc.md`` next to the profile file, or ``None`` when
    TOC emission is disabled (``ProfileOptions(emit_toc=False)``) or the
    profile has no sections to index.
    """
    return _generate_with_engine(
        database,
        lambda engine: profile_database_with_toc(
            engine, options or ProfileOptions(), progress
        ),
    )


def _generate_with_engine(
    database: DatabaseInput, generate: Callable[[Engine], str]
) -> str:
    if isinstance(database, Engine):
        return generate(database)

    engine = create_engine(database)
    try:
        return generate(engine)
    finally:
        engine.dispose()
