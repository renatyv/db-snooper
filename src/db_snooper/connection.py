from __future__ import annotations

import argparse
import getpass
import os
from typing import Any

from sqlalchemy.engine import URL

DRIVER_NAMES = {
    "sqlite": "sqlite",
    "postgres": "postgresql+psycopg",
    "mysql": "mysql+pymysql",
    "mariadb": "mariadb+mariadbconnector",
    "duckdb": "duckdb",
}

def add_connection_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--db-type",
        choices=sorted(DRIVER_NAMES),
        default=None,
        help="Database type. Defaults to DB_SNOOPER_DB_TYPE.",
    )
    parser.add_argument(
        "--database",
        default=None,
        help="Database name, or file path for SQLite/DuckDB. Defaults to DB_SNOOPER_DATABASE.",
    )
    parser.add_argument("--host", default=None, help="Database host. Defaults to DB_SNOOPER_DB_HOST or localhost.")
    parser.add_argument("--port", type=int, default=None, help="Database port. Defaults to DB_SNOOPER_DB_PORT.")
    parser.add_argument("--user", default=None, help="Database user. Defaults to DB_SNOOPER_DB_USER.")
    parser.add_argument(
        "--password",
        default=None,
        help="Database password. Prefer DB_SNOOPER_DB_PASSWORD or --ask-password to avoid shell history.",
    )
    parser.add_argument("--ask-password", action="store_true", help="Prompt securely for the database password.")


def resolve_database_url(args: argparse.Namespace, parser: argparse.ArgumentParser) -> URL:
    db_type = _value(args, "db_type", "DB_SNOOPER_DB_TYPE")
    if not db_type:
        parser.error(
            "database connection is required. Use friendly flags like "
            "--db-type sqlite --database path/to.db, or set DB_SNOOPER_DB_TYPE and DB_SNOOPER_DATABASE."
        )
    if db_type not in DRIVER_NAMES:
        parser.error(f"unsupported --db-type {db_type!r}; choose one of: {', '.join(sorted(DRIVER_NAMES))}")

    database = _value(args, "database", "DB_SNOOPER_DATABASE")
    if not database:
        parser.error("--database or DB_SNOOPER_DATABASE is required")

    password = _value(args, "password", "DB_SNOOPER_DB_PASSWORD")
    if args.ask_password:
        password = getpass.getpass("Database password: ")

    if db_type in {"sqlite", "duckdb"}:
        return URL.create(DRIVER_NAMES[db_type], database=database)

    host = _value(args, "host", "DB_SNOOPER_DB_HOST") or "localhost"
    port = _optional_int(_value(args, "port", "DB_SNOOPER_DB_PORT"), parser)
    user = _value(args, "user", "DB_SNOOPER_DB_USER")
    return URL.create(DRIVER_NAMES[db_type], username=user, password=password, host=host, port=port, database=database)


def _value(args: argparse.Namespace, arg_name: str, env_name: str) -> Any:
    value = getattr(args, arg_name)
    if value is not None:
        return value
    return os.environ.get(env_name)


def _optional_int(value: Any, parser: argparse.ArgumentParser) -> int | None:
    if value in (None, ""):
        return None
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except ValueError:
        parser.error("DB_SNOOPER_DB_PORT must be an integer")
