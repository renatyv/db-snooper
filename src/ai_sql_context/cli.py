from __future__ import annotations

import argparse
import os
from pathlib import Path

from ai_sql_context.connectors import ConnectionConfig, create_db_engine
from ai_sql_context.inspectors import DatabaseInspector
from ai_sql_context.render import write_context


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "profile":
        profile(args)
        return 0
    parser.print_help()
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-sql-context")
    subparsers = parser.add_subparsers(dest="command")
    profile_parser = subparsers.add_parser("profile", help="Profile a database into a SQL context file")
    profile_parser.add_argument("--dialect", default=os.getenv("DB_DIALECT", "mysql"), choices=["mysql", "mariadb"])
    profile_parser.add_argument("--host", default=os.getenv("DB_HOST", "localhost"))
    profile_parser.add_argument("--port", type=int, default=int(os.getenv("DB_PORT", "3306")))
    profile_parser.add_argument("--database", default=os.getenv("DB_NAME"))
    profile_parser.add_argument("--user", default=os.getenv("DB_USER"))
    profile_parser.add_argument("--password", default=None, help="Database password. Prefer --password-env.")
    profile_parser.add_argument("--password-env", default="DB_PASSWORD", help="Environment variable containing DB password")
    profile_parser.add_argument("--output", default=os.getenv("AI_SQL_CONTEXT_OUTPUT", "context/database.sql"))
    profile_parser.add_argument("--sample-rows", type=int, default=1000)
    profile_parser.add_argument("--max-tables", type=int, default=None)
    profile_parser.add_argument("--include-table", action="append", default=[])
    profile_parser.add_argument("--exclude-table", action="append", default=[])
    return parser


def profile(args: argparse.Namespace) -> None:
    password = args.password if args.password is not None else os.getenv(args.password_env)
    missing = [name for name, value in {"database": args.database, "user": args.user, "password": password}.items() if not value]
    if missing:
        raise SystemExit(f"Missing required database settings: {', '.join(missing)}")

    config = ConnectionConfig(args.dialect, args.host, args.port, args.database, args.user, password)
    engine = create_db_engine(config)
    inspector = DatabaseInspector(
        engine=engine,
        dialect=args.dialect,
        database=args.database,
        sample_rows=args.sample_rows,
        max_tables=args.max_tables,
        include_tables=set(args.include_table) if args.include_table else None,
        exclude_tables=set(args.exclude_table),
    )
    context = inspector.inspect()
    output = Path(args.output)
    write_context(output, context)
    print(f"Wrote {output}")
