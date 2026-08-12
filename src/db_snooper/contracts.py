from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

DEFAULT_LARGE_TABLE_THRESHOLD = 100_000_000
DEFAULT_QUERY_TIMEOUT = 10
DEFAULT_BIGQUERY_MAX_BYTES_BILLED = 1_073_741_824
DEFAULT_RANDOM_SAMPLE_PERCENT = 0.1

OBJECT_TABLE = "table"
OBJECT_VIEW = "view"
OBJECT_MATERIALIZED_VIEW = "materialized_view"


@dataclass(frozen=True)
class ProfileOptions:
    small_table_threshold: int = 10
    latest_row_limit: int = 1
    random_row_limit: int = 2
    large_table_threshold: int = DEFAULT_LARGE_TABLE_THRESHOLD
    query_timeout: int = DEFAULT_QUERY_TIMEOUT
    max_bytes_billed: int = DEFAULT_BIGQUERY_MAX_BYTES_BILLED
    random_sample_percent: float = DEFAULT_RANDOM_SAMPLE_PERCENT
    metadata_only: bool = False
    include_tables: frozenset[str] | None = None
    exclude_tables: frozenset[str] = frozenset()
    schema: str | None = None
    include_technical_tables: bool = False
    include_empty_tables: bool = False
    use_dump_ddl: bool = False


ProfileProgress = Callable[[int, int, str], None]


@dataclass(frozen=True)
class PermissionReport:
    dialect: str
    schema: str | None
    accessible_tables: list[str]
    inaccessible_tables: list[tuple[str, str]]
    stats_access: dict[str, bool]

    @property
    def has_select_access(self) -> bool:
        return bool(self.accessible_tables)


@dataclass(frozen=True)
class SchemaProfilePlan:
    options: ProfileOptions
    table_names: tuple[str, ...]
    skipped_technical_tables: tuple[str, ...]
    permission_report: PermissionReport
    kinds: dict[str, str]


@dataclass(frozen=True)
class ProfileDocument:
    schema: str
    table: str | None
    markdown: str


@dataclass(frozen=True)
class ProfileRun:
    documents: tuple[ProfileDocument, ...]
    warnings: tuple[str, ...]
    suggestions: tuple[str, ...]
