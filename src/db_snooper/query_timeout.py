from __future__ import annotations

from contextlib import contextmanager

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import OperationalError, SQLAlchemyError

_TIMEOUT_DIALECTS = {"postgresql", "mysql"}

_MYSQL_TIMEOUT_STATEMENTS = (
    "SET SESSION MAX_EXECUTION_TIME = {ms}",
    "SET SESSION MAX_STATEMENT_TIME = {seconds}",
)


class QueryTimeout(Exception):
    """Raised when a profiling query exceeds the configured statement timeout."""


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
    if _orig_error_code(orig) in {"3024", "1969", "1317"}:
        return True
    return False


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
    caller can skip the affected metric and continue. All other errors propagate.
    """
    try:
        return conn.execute(statement)
    except OperationalError as exc:
        if not is_query_timeout(exc):
            raise
        conn.rollback()
        _set_session_timeout(conn, timeout_seconds)
        raise QueryTimeout(f"query exceeded timeout: {exc.orig!r}") from exc


@contextmanager
def metric(skipped: list[str], metric_name: str):
    """Record expected query timeouts; unexpected errors bubble to the workflow."""
    try:
        yield
    except QueryTimeout:
        skipped.append(metric_name)
