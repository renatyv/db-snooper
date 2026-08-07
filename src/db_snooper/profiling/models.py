from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from db_snooper.database_stats import LARGE_TABLE_THRESHOLD
from db_snooper.query_timeout import DEFAULT_QUERY_TIMEOUT


@dataclass(frozen=True)
class ProfileOptions:
    small_table_threshold: int = 10
    latest_row_limit: int = 1
    random_row_limit: int = 2
    large_table_threshold: int = LARGE_TABLE_THRESHOLD
    query_timeout: int = DEFAULT_QUERY_TIMEOUT
    include_tables: frozenset[str] | None = None
    exclude_tables: frozenset[str] = frozenset()
    schema: str | None = None
    include_technical_tables: bool = False
    include_empty_tables: bool = False
    use_dump_ddl: bool = False


ProfileProgress = Callable[[int, int, str], None]
