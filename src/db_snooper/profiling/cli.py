from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from db_snooper.application import run_profiles
from db_snooper.connection import (
    add_connection_arguments,
    resolve_database_url,
    resolve_schema,
)
from db_snooper.contracts import ProfileOptions
from db_snooper.profiling.suggestions import format_suggestions
from db_snooper.progress import ProgressBar
from db_snooper.shared import default_output_path, output_component, parse_table_set

_logger = logging.getLogger("db_snooper")
_DEFAULTS = ProfileOptions()


def build_arg_parser(prog: str | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a SQL profile for a database.", prog=prog
    )
    add_connection_arguments(parser)
    parser.add_argument("--output", help="Output directory. Defaults to <database>/.")
    parser.add_argument(
        "--small-table-threshold",
        type=int,
        default=_DEFAULTS.small_table_threshold,
        help="Tables with this many rows or fewer are dumped in full.",
    )
    parser.add_argument(
        "--latest-row-limit",
        type=int,
        default=_DEFAULTS.latest_row_limit,
        help="Most-recent rows (by key) shown for tables above the small-table threshold.",
    )
    parser.add_argument(
        "--random-row-limit",
        type=int,
        default=_DEFAULTS.random_row_limit,
        help="Random rows shown for tables above the small-table threshold.",
    )
    parser.add_argument(
        "--large-table-threshold",
        type=int,
        default=_DEFAULTS.large_table_threshold,
        help=(
            "Tables whose catalog row estimate is at/above this count are profiled "
            "from internal stats only; COUNT(*) and per-column queries are skipped. "
            f"Default {_DEFAULTS.large_table_threshold}."
        ),
    )
    parser.add_argument(
        "--query-timeout",
        type=int,
        default=_DEFAULTS.query_timeout,
        help=(
            "Abort any profiling query that runs longer than this many seconds, skip the "
            "affected metric, and continue. 0 disables. Applies to PostgreSQL/MySQL/MariaDB "
            f"(SQLite/DuckDB have no native support). Default {_DEFAULTS.query_timeout}."
        ),
    )
    parser.add_argument(
        "--per-table",
        action="store_true",
        help="Write one .md profile per table instead of one schema profile.",
    )
    parser.add_argument("--include-tables", help="Comma-separated table allowlist.")
    parser.add_argument("--exclude-tables", help="Comma-separated table denylist.")
    parser.add_argument(
        "--include-technical-tables",
        action="store_true",
        help=(
            "Profile migration/framework tables (e.g. schema_migrations, "
            "alembic_version, flyway_schema_history) that are skipped by default."
        ),
    )
    parser.add_argument(
        "--include-empty-tables",
        action="store_true",
        help=(
            "Profile tables with zero rows (emitting their CREATE TABLE). "
            "By default empty tables are skipped entirely."
        ),
    )
    parser.add_argument(
        "--use-dump-ddl",
        action="store_true",
        help=(
            "Always emit CREATE TABLE via pg_dump/mysqldump instead of SQLAlchemy "
            "reflection (testing aid for the utility fallback)."
        ),
    )
    return parser


def main(argv: list[str] | None = None, prog: str | None = None) -> int:
    logging.basicConfig(level=logging.WARNING, format="%(message)s", stream=sys.stderr)
    parser = build_arg_parser(prog=prog)
    args = parser.parse_args(argv)
    if args.large_table_threshold < 1:
        parser.error("--large-table-threshold must be a positive integer")
    if args.query_timeout < 0:
        parser.error("--query-timeout must be a non-negative integer")
    url = resolve_database_url(args, parser)

    options = ProfileOptions(
        small_table_threshold=args.small_table_threshold,
        latest_row_limit=args.latest_row_limit,
        random_row_limit=args.random_row_limit,
        large_table_threshold=args.large_table_threshold,
        query_timeout=args.query_timeout,
        include_tables=parse_table_set(args.include_tables),
        exclude_tables=parse_table_set(args.exclude_tables) or frozenset(),
        schema=resolve_schema(args),
        include_technical_tables=args.include_technical_tables,
        include_empty_tables=args.include_empty_tables,
        use_dump_ddl=args.use_dump_ddl,
    )
    engine = create_engine(url)
    progress_bar = ProgressBar("Profiling", 0)

    def show_progress(current: int, total: int, item: str) -> None:
        nonlocal progress_bar
        if progress_bar.total != total:
            progress_bar = ProgressBar("Profiling", total)
            progress_bar.start(f"profiling {item}")
            return
        progress_bar.update(
            current,
            f"profiling {item}" if current < total else f"profiled {item}",
        )

    output_dir = (
        Path(args.output)
        if args.output
        else default_output_path(args.database or os.environ["DB_SNOOPER_DATABASE"])
    )
    try:
        run = run_profiles(engine, options, args.per_table, show_progress)
        for warning in run.warnings:
            _logger.warning(warning)
        for document in run.documents:
            if document.table is not None:
                schema_dir = output_dir / output_component(document.schema)
                schema_dir.mkdir(parents=True, exist_ok=True)
                (schema_dir / f"{output_component(document.table)}.md").write_text(
                    document.markdown, encoding="utf-8"
                )
            else:
                output_dir.mkdir(parents=True, exist_ok=True)
                (output_dir / f"{output_component(document.schema)}.md").write_text(
                    document.markdown, encoding="utf-8"
                )
    except SQLAlchemyError as exc:
        progress_bar.finish()
        reason = str(getattr(exc, "orig", exc)).splitlines()[0]
        print(f"Database error: {reason}", file=sys.stderr)
        return 1
    except Exception:
        progress_bar.finish()
        raise
    else:
        progress_bar.finish("Profiling complete")
        suggestions = format_suggestions(run.suggestions)
        if suggestions:
            print(suggestions, file=sys.stderr)
    finally:
        engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
