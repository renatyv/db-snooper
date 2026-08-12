from sqlalchemy.engine import Engine

from db_snooper.contracts import ProfileOptions, ProfileProgress
from db_snooper.profiling.discovery import list_schema_tables


def profile_database(
    engine: Engine,
    options: ProfileOptions,
    progress: ProfileProgress | None = None,
) -> str:
    from db_snooper.application import profile_database as run

    return run(engine, options, progress)


__all__ = [
    "ProfileOptions",
    "ProfileProgress",
    "list_schema_tables",
    "profile_database",
]
