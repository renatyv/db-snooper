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
        description="Generate a SQL profile for a database.",
        prog=prog,
        usage="%(prog)s [connection options] [profile options]",
    )
    add_connection_arguments(parser)
    profile = parser.add_argument_group("profile")
    filters = parser.add_argument_group("table filters")
    safety = parser.add_argument_group("safety limits")
    profile.add_argument("--output", help="Output directory. Defaults to <database>/.")
    profile.add_argument(
        "--metadata-only",
        action="store_true",
        help=(
            "Emit schema, row estimates, and catalog statistics without scanning rows."
        ),
    )
    profile.add_argument(
        "--per-table",
        action="store_true",
        help="Write one .md profile per table instead of one schema profile.",
    )
    filters.add_argument("--include-tables", help="Comma-separated table allowlist.")
    filters.add_argument("--exclude-tables", help="Comma-separated table denylist.")
    safety.add_argument(
        "--query-timeout",
        type=int,
        default=_DEFAULTS.query_timeout,
        help=(
            "Abort any profiling query that runs longer than this many seconds, skip the "
            "affected metric, and continue. 0 disables. Applies to PostgreSQL/MySQL/MariaDB "
            "(SQLite/DuckDB/BigQuery have no native support). "
            f"Default {_DEFAULTS.query_timeout}."
        ),
    )
    safety.add_argument(
        "--max-bytes-billed",
        type=int,
        default=_DEFAULTS.max_bytes_billed,
        help=(
            "Cumulative BigQuery scan budget in bytes. Queries are dry-run first and "
            "skipped when they would exceed the remaining budget; 0 disables. "
            f"Default {_DEFAULTS.max_bytes_billed}."
        ),
    )
    return parser


def main(argv: list[str] | None = None, prog: str | None = None) -> int:
    logging.basicConfig(level=logging.WARNING, format="%(message)s", stream=sys.stderr)
    parser = build_arg_parser(prog=prog)
    args = parser.parse_args(argv)
    if args.query_timeout < 0:
        parser.error("--query-timeout must be a non-negative integer")
    if args.max_bytes_billed < 0:
        parser.error("--max-bytes-billed must be a non-negative integer")
    url = resolve_database_url(args, parser)

    options = ProfileOptions(
        query_timeout=args.query_timeout,
        max_bytes_billed=args.max_bytes_billed,
        metadata_only=args.metadata_only,
        include_tables=parse_table_set(args.include_tables),
        exclude_tables=parse_table_set(args.exclude_tables) or frozenset(),
        schema=resolve_schema(args),
    )
    engine = create_engine(url)
    progress_bar = ProgressBar("Profiling", 0)

    def show_progress(current: int, total: int, item: str) -> None:
        # The total isn't known until the first callback (after table
        # discovery), so seed it once and start the live display.
        if progress_bar.total != total:
            progress_bar.total = total
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
