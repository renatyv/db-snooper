from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ColumnInfo:
    name: str
    data_type: str
    nullable: bool
    default: str | None = None
    extra: str | None = None


@dataclass(frozen=True)
class IndexInfo:
    name: str
    columns: tuple[str, ...]
    unique: bool


@dataclass(frozen=True)
class ForeignKeyInfo:
    name: str
    columns: tuple[str, ...]
    referenced_table: str
    referenced_columns: tuple[str, ...]


@dataclass
class ColumnProfile:
    name: str
    null_count: int
    non_null_count: int
    distinct_count: int
    low_cardinality_values: list[tuple[Any, int]] = field(default_factory=list)
    top_values: list[tuple[Any, int]] = field(default_factory=list)
    numeric_min: Any | None = None
    numeric_max: Any | None = None
    numeric_median: Any | None = None
    shape: dict[str, Any] = field(default_factory=dict)


@dataclass
class TableProfile:
    name: str
    row_count: int
    columns: list[ColumnInfo]
    create_table_sql: str
    primary_key: tuple[str, ...] = ()
    foreign_keys: list[ForeignKeyInfo] = field(default_factory=list)
    indexes: list[IndexInfo] = field(default_factory=list)
    column_profiles: list[ColumnProfile] = field(default_factory=list)
    sample_rows: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class LikelyJoin:
    left_table: str
    left_column: str
    right_table: str
    right_column: str
    confidence: str
    evidence: str


@dataclass
class DatabaseContext:
    dialect: str
    database: str
    tables: list[TableProfile]
    likely_joins: list[LikelyJoin] = field(default_factory=list)
