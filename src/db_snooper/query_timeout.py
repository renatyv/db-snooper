from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError

_TIMEOUT_DIALECTS = {"postgresql", "mysql"}

_MYSQL_TIMEOUT_STATEMENTS = (
    "SET SESSION MAX_EXECUTION_TIME = {ms}",
    "SET SESSION MAX_STATEMENT_TIME = {seconds}",
)


class QueryTimeout(Exception):
    """Raised when a profiling query exceeds the configured statement timeout."""


class QueryBudgetExceeded(Exception):
    """Raised before a BigQuery query would exceed the configured scan budget."""


@dataclass
class BigQueryBudget:
    max_bytes: int
    used_bytes: int = 0

    @property
    def remaining_bytes(self) -> int:
        return max(0, self.max_bytes - self.used_bytes)


_BIGQUERY_BUDGET_KEY = "db_snooper_bigquery_budget"


def apply_bigquery_budget(conn: Connection, budget: BigQueryBudget | None) -> None:
    if conn.dialect.name == "bigquery" and budget is not None and budget.max_bytes > 0:
        conn.execution_options(**{_BIGQUERY_BUDGET_KEY: budget})


def apply_query_timeout(conn: Connection, seconds: int) -> None:
    """Best-effort server-side statement timeout for this connection."""
    _set_session_timeout(conn, seconds)


def _set_session_timeout(conn: Connection, seconds: int) -> None:
    if seconds <= 0:
        return
    dialect = conn.dialect.name
    if dialect not in _TIMEOUT_DIALECTS:
        return
    try:
        if dialect == "postgresql":
            conn.execute(text(f"SET statement_timeout = {seconds * 1000}"))
        else:
            _apply_mysql_timeout(conn, seconds)
    except SQLAlchemyError:
        pass


def _apply_mysql_timeout(conn: Connection, seconds: int) -> None:
    context = {"ms": seconds * 1000, "seconds": seconds}
    for template in _MYSQL_TIMEOUT_STATEMENTS:
        try:
            conn.execute(text(template.format(**context)))
            return
        except SQLAlchemyError:
            continue


def is_query_timeout(exc: SQLAlchemyError) -> bool:
    """Return True if ``exc`` represents a server-side statement-timeout abort."""
    message = str(exc).lower()
    if (
        "statement timeout" in message
        or "canceling statement due to statement timeout" in message
    ):
        return True
    if "maximum statement execution time" in message or "max_statement_time" in message:
        return True
    orig = getattr(exc, "orig", None)
    sqlstate = getattr(orig, "sqlstate", None) or getattr(orig, "pgcode", None)
    if sqlstate == "57014":
        return True
    return _orig_error_code(orig) in {"3024", "1969", "1317"}


def _orig_error_code(orig: object | None) -> str | None:
    for attr in ("errno", "args"):
        value = getattr(orig, attr, None)
        if isinstance(value, tuple) and value and isinstance(value[0], int):
            return str(value[0])
        if isinstance(value, int):
            return str(value)
    return None


def execute(conn: Connection, statement: object, timeout_seconds: int = 0):
    """Execute ``statement`` via the connection.

    On a server-side timeout the (read-only) transaction is rolled back, the
    statement timeout is restored, and :class:`QueryTimeout` is raised so the
    caller can skip the affected metric and continue. BigQuery queries are dry-run
    and capped when a scan budget is attached. All other errors propagate.
    """
    budget = conn.get_execution_options().get(_BIGQUERY_BUDGET_KEY)
    if budget is not None:
        return _execute_bigquery_budgeted(conn, statement, budget)
    try:
        return conn.execute(statement)
    except SQLAlchemyError as exc:
        if not is_query_timeout(exc):
            raise
        conn.rollback()
        _set_session_timeout(conn, timeout_seconds)
        raise QueryTimeout(f"query timeout > {timeout_seconds}s") from exc


def _execute_bigquery_budgeted(
    conn: Connection, statement: object, budget: BigQueryBudget
):
    from google.cloud.bigquery import QueryJobConfig

    remaining = budget.remaining_bytes
    if remaining <= 0:
        raise QueryBudgetExceeded(
            f"BigQuery scan budget exhausted ({budget.max_bytes} bytes)"
        )

    dry_result = conn.execute(
        statement.execution_options(job_config=QueryJobConfig(dry_run=True))
    )
    estimated = _bigquery_result_bytes(dry_result)
    dry_result.close()
    if estimated > remaining:
        raise QueryBudgetExceeded(
            f"BigQuery scan budget exceeded: estimated {estimated} bytes, "
            f"{remaining} remaining"
        )

    try:
        result = conn.execute(
            statement.execution_options(
                job_config=QueryJobConfig(maximum_bytes_billed=remaining)
            )
        )
    except SQLAlchemyError as exc:
        if "maximum bytes billed" not in str(exc).lower():
            raise
        raise QueryBudgetExceeded(
            f"BigQuery scan budget exceeded ({remaining} bytes remaining)"
        ) from exc
    budget.used_bytes += _bigquery_result_bytes(result) or estimated
    return result


def _bigquery_result_bytes(result: object) -> int:
    cursor = getattr(result, "cursor", None)
    rows = getattr(cursor, "_query_rows", None)
    return int(getattr(rows, "total_bytes_processed", 0) or 0)


@contextmanager
def metric(skipped: list[tuple[str, str]], metric_name: str):
    """Record expected timeout/budget skips; unexpected errors bubble up."""
    try:
        yield
    except (QueryTimeout, QueryBudgetExceeded) as exc:
        skipped.append((metric_name, str(exc)))
