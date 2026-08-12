from __future__ import annotations

import argparse
import getpass
import os
import subprocess
from pathlib import Path
from typing import Any

from sqlalchemy import inspect
from sqlalchemy.engine import URL, Engine

DRIVER_NAMES = {
    "bigquery": "bigquery",
    "sqlite": "sqlite",
    "postgres": "postgresql+psycopg",
    "mysql": "mysql+pymysql",
    "mariadb": "mysql+pymysql",
    "duckdb": "duckdb",
}

DEFAULT_PORTS = {
    "postgres": 5432,
    "mysql": 3306,
    "mariadb": 3306,
}


def add_connection_arguments(parser: argparse.ArgumentParser) -> None:
    connection = parser.add_argument_group("connection")
    authentication = parser.add_argument_group("authentication")
    rds = parser.add_argument_group("Amazon RDS IAM")
    connection.add_argument(
        "--db-type",
        choices=sorted(DRIVER_NAMES),
        default=None,
        help="Database type. Defaults to DB_SNOOPER_DB_TYPE.",
    )
    connection.add_argument(
        "--database",
        default=None,
        help=(
            "Database name, BigQuery project ID, or file path for SQLite/DuckDB. "
            "Defaults to DB_SNOOPER_DATABASE."
        ),
    )
    connection.add_argument(
        "--host",
        default=None,
        help="Database host. Defaults to DB_SNOOPER_DB_HOST or localhost.",
    )
    connection.add_argument(
        "--port",
        type=int,
        default=None,
        help="Database port. Defaults to DB_SNOOPER_DB_PORT or the database server default.",
    )
    authentication.add_argument(
        "--user", default=None, help="Database user. Defaults to DB_SNOOPER_DB_USER."
    )
    authentication.add_argument(
        "--password",
        default=None,
        help="Database password. Defaults to DB_SNOOPER_DB_PASSWORD, then a secure prompt for server databases.",
    )
    authentication.add_argument(
        "--ask-password",
        action="store_true",
        help="Prompt securely for the database password.",
    )
    authentication.add_argument(
        "--ssl-ca",
        default=None,
        help="CA bundle for verified PostgreSQL/MySQL/MariaDB TLS. Defaults to DB_SNOOPER_SSL_CA.",
    )
    rds.add_argument(
        "--rds-iam",
        action="store_true",
        help="Use Amazon RDS IAM authentication via the AWS CLI instead of a password.",
    )
    rds.add_argument(
        "--aws-region",
        default=None,
        help="AWS Region for RDS IAM authentication. Defaults to AWS CLI configuration.",
    )
    rds.add_argument(
        "--aws-profile",
        default=None,
        help="AWS CLI profile for RDS IAM authentication.",
    )
    connection.add_argument(
        "--schema",
        default=None,
        help="Schema to inspect. Defaults to DB_SNOOPER_SCHEMA; without either, all user schemas are inspected.",
    )


def resolve_database_url(
    args: argparse.Namespace, parser: argparse.ArgumentParser
) -> URL:
    db_type = _value(args, "db_type", "DB_SNOOPER_DB_TYPE")
    if not db_type:
        parser.error(
            "database connection is required. Use friendly flags like "
            "--db-type sqlite --database path/to.db, or set DB_SNOOPER_DB_TYPE and DB_SNOOPER_DATABASE."
        )
    if db_type not in DRIVER_NAMES:
        parser.error(
            f"unsupported --db-type {db_type!r}; choose one of: {', '.join(sorted(DRIVER_NAMES))}"
        )

    database = _value(args, "database", "DB_SNOOPER_DATABASE")
    if not database:
        parser.error("--database or DB_SNOOPER_DATABASE is required")

    ssl_ca = _value(args, "ssl_ca", "DB_SNOOPER_SSL_CA")
    if args.rds_iam and db_type not in {"postgres", "mysql", "mariadb"}:
        parser.error("--rds-iam requires PostgreSQL, MySQL, or MariaDB")
    if ssl_ca and db_type not in {"postgres", "mysql", "mariadb"}:
        parser.error("--ssl-ca requires PostgreSQL, MySQL, or MariaDB")
    if ssl_ca and not Path(ssl_ca).is_file():
        parser.error(f"SSL CA bundle does not exist: {ssl_ca}")

    if db_type in {"sqlite", "duckdb"}:
        return URL.create(DRIVER_NAMES[db_type], database=database)
    if db_type == "bigquery":
        return URL.create(DRIVER_NAMES[db_type], host=database)

    host = _value(args, "host", "DB_SNOOPER_DB_HOST") or "localhost"
    port = (
        _optional_int(_value(args, "port", "DB_SNOOPER_DB_PORT"), parser)
        or DEFAULT_PORTS[db_type]
    )
    user = _value(args, "user", "DB_SNOOPER_DB_USER")
    if args.rds_iam:
        if not user:
            parser.error("--user is required with --rds-iam")
        if host == "localhost":
            parser.error("--host must be an Amazon RDS endpoint with --rds-iam")
        if not ssl_ca:
            parser.error("--ssl-ca is required with --rds-iam")
        password = _rds_iam_token(args, parser, host, port, user)
    else:
        password = _value(args, "password", "DB_SNOOPER_DB_PASSWORD")
    if not args.rds_iam and (args.ask_password or password is None):
        password = getpass.getpass("Database password: ")

    query: dict[str, str] = {}
    if ssl_ca:
        if db_type == "postgres":
            query = {"sslmode": "verify-full", "sslrootcert": ssl_ca}
        else:
            query = {
                "ssl_ca": ssl_ca,
                "ssl_verify_cert": "true",
                "ssl_verify_identity": "true",
            }
    return URL.create(
        DRIVER_NAMES[db_type],
        username=user,
        password=password,
        host=host,
        port=port,
        database=database,
        query=query,
    )


def _rds_iam_token(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
    host: str,
    port: int,
    user: str,
) -> str:
    command = [
        "aws",
        "rds",
        "generate-db-auth-token",
        "--hostname",
        host,
        "--port",
        str(port),
        "--username",
        user,
    ]
    if args.aws_region:
        command.extend(("--region", args.aws_region))
    if args.aws_profile:
        command.extend(("--profile", args.aws_profile))
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError:
        parser.error("--rds-iam requires the AWS CLI")
    except subprocess.CalledProcessError as exc:
        parser.error(f"could not generate an RDS IAM token: {exc.stderr.strip()}")
    token = result.stdout.strip()
    if not token:
        parser.error("AWS CLI returned an empty RDS IAM token")
    return token


def resolve_schema(args: argparse.Namespace) -> str | None:
    """Return an explicitly selected schema, if any."""
    return _value(args, "schema", "DB_SNOOPER_SCHEMA")


def list_schemas(engine: Engine, selected_schema: str | None = None) -> list[str]:
    """List non-system schemas that contain tables for this database connection."""
    if selected_schema:
        return [selected_schema]

    dialect = engine.dialect.name
    if dialect == "sqlite":
        return ["main"]
    if dialect == "bigquery" and engine.dialect.dataset_id:
        return [engine.dialect.dataset_id]
    if dialect in {"mysql", "mariadb"}:
        return [engine.dialect.default_schema_name or engine.url.database or "main"]

    system_schemas = {"information_schema", "pg_catalog", "pg_toast"}
    inspector = inspect(engine)
    schemas = [
        schema
        for schema in inspector.get_schema_names()
        if schema not in system_schemas and inspector.get_table_names(schema=schema)
    ]
    return sorted(schemas)


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
