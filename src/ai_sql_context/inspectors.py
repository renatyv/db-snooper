from __future__ import annotations

from collections import defaultdict
from typing import Any

from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection, Engine

from ai_sql_context.models import (
    ColumnInfo,
    ColumnProfile,
    DatabaseContext,
    ForeignKeyInfo,
    IndexInfo,
    LikelyJoin,
    TableProfile,
)
from ai_sql_context.profiling import compact_value, is_numeric_type, is_string_type, normalize_scalar, value_shape


class DatabaseInspector:
    def __init__(
        self,
        engine: Engine,
        dialect: str,
        database: str,
        sample_rows: int = 1000,
        max_tables: int | None = None,
        include_tables: set[str] | None = None,
        exclude_tables: set[str] | None = None,
    ) -> None:
        self.engine = engine
        self.dialect = dialect
        self.database = database
        self.sample_rows = sample_rows
        self.max_tables = max_tables
        self.include_tables = include_tables
        self.exclude_tables = exclude_tables or set()

    def inspect(self) -> DatabaseContext:
        with self.engine.connect() as conn:
            tables = self._table_names(conn)
            profiles = [self._inspect_table(conn, table) for table in tables]
        joins = declared_joins(profiles) + likely_name_joins(profiles)
        return DatabaseContext(self.dialect, self.database, profiles, sorted_joins(joins))

    def _table_names(self, conn: Connection) -> list[str]:
        names = sorted(inspect(conn).get_table_names())
        if self.include_tables:
            names = [name for name in names if name in self.include_tables]
        names = [name for name in names if name not in self.exclude_tables]
        if self.max_tables is not None:
            names = names[: self.max_tables]
        return names

    def _inspect_table(self, conn: Connection, table: str) -> TableProfile:
        row_count = scalar_int(conn, f"SELECT COUNT(*) FROM {quote_identifier(table)}")
        columns = self._columns(conn, table)
        profile = TableProfile(
            name=table,
            row_count=row_count,
            columns=columns,
            create_table_sql=self._create_table_sql(conn, table),
            primary_key=self._primary_key(conn, table),
            foreign_keys=self._foreign_keys(conn, table),
            indexes=self._indexes(conn, table),
        )
        profile.sample_rows = self._sample_rows(conn, table, columns, row_count)
        profile.column_profiles = [self._column_profile(conn, table, column, row_count) for column in columns]
        return profile

    def _columns(self, conn: Connection, table: str) -> list[ColumnInfo]:
        rows = conn.execute(
            text(
                """
                SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, EXTRA
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = :database AND TABLE_NAME = :table
                ORDER BY ORDINAL_POSITION
                """
            ),
            {"database": self.database, "table": table},
        ).mappings()
        return [
            ColumnInfo(
                name=row["COLUMN_NAME"],
                data_type=row["COLUMN_TYPE"],
                nullable=row["IS_NULLABLE"] == "YES",
                default=row["COLUMN_DEFAULT"],
                extra=row["EXTRA"] or None,
            )
            for row in rows
        ]

    def _create_table_sql(self, conn: Connection, table: str) -> str:
        row = conn.execute(text(f"SHOW CREATE TABLE {quote_identifier(table)}")).first()
        if row is None:
            return ""
        return str(row[1]).strip()

    def _primary_key(self, conn: Connection, table: str) -> tuple[str, ...]:
        rows = conn.execute(
            text(
                """
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = :database
                  AND TABLE_NAME = :table
                  AND CONSTRAINT_NAME = 'PRIMARY'
                ORDER BY ORDINAL_POSITION
                """
            ),
            {"database": self.database, "table": table},
        )
        return tuple(row[0] for row in rows)

    def _foreign_keys(self, conn: Connection, table: str) -> list[ForeignKeyInfo]:
        rows = conn.execute(
            text(
                """
                SELECT CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME, ORDINAL_POSITION
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = :database
                  AND TABLE_NAME = :table
                  AND REFERENCED_TABLE_NAME IS NOT NULL
                ORDER BY CONSTRAINT_NAME, ORDINAL_POSITION
                """
            ),
            {"database": self.database, "table": table},
        ).mappings()
        grouped: dict[str, dict[str, Any]] = {}
        for row in rows:
            name = row["CONSTRAINT_NAME"]
            item = grouped.setdefault(
                name,
                {
                    "columns": [],
                    "referenced_table": row["REFERENCED_TABLE_NAME"],
                    "referenced_columns": [],
                },
            )
            item["columns"].append(row["COLUMN_NAME"])
            item["referenced_columns"].append(row["REFERENCED_COLUMN_NAME"])
        return [
            ForeignKeyInfo(name, tuple(value["columns"]), value["referenced_table"], tuple(value["referenced_columns"]))
            for name, value in sorted(grouped.items())
        ]

    def _indexes(self, conn: Connection, table: str) -> list[IndexInfo]:
        rows = conn.execute(
            text(
                """
                SELECT INDEX_NAME, COLUMN_NAME, NON_UNIQUE, SEQ_IN_INDEX
                FROM INFORMATION_SCHEMA.STATISTICS
                WHERE TABLE_SCHEMA = :database AND TABLE_NAME = :table
                ORDER BY INDEX_NAME, SEQ_IN_INDEX
                """
            ),
            {"database": self.database, "table": table},
        ).mappings()
        grouped: dict[str, dict[str, Any]] = {}
        for row in rows:
            name = row["INDEX_NAME"]
            item = grouped.setdefault(name, {"columns": [], "unique": row["NON_UNIQUE"] == 0})
            item["columns"].append(row["COLUMN_NAME"])
        return [IndexInfo(name, tuple(value["columns"]), value["unique"]) for name, value in sorted(grouped.items())]

    def _sample_rows(self, conn: Connection, table: str, columns: list[ColumnInfo], row_count: int) -> list[dict[str, Any]]:
        if row_count >= 50 or not columns:
            return []
        order = order_by_clause(columns)
        rows = conn.execute(text(f"SELECT * FROM {quote_identifier(table)} {order} LIMIT 50")).mappings()
        return [{key: normalize_scalar(value) for key, value in row.items()} for row in rows]

    def _column_profile(self, conn: Connection, table: str, column: ColumnInfo, row_count: int) -> ColumnProfile:
        table_sql = quote_identifier(table)
        column_sql = quote_identifier(column.name)
        counts = conn.execute(
            text(
                f"""
                SELECT
                    SUM(CASE WHEN {column_sql} IS NULL THEN 1 ELSE 0 END) AS null_count,
                    SUM(CASE WHEN {column_sql} IS NOT NULL THEN 1 ELSE 0 END) AS non_null_count,
                    COUNT(DISTINCT {column_sql}) AS distinct_count
                FROM {table_sql}
                """
            )
        ).mappings().one()
        null_count = int(counts["null_count"] or 0)
        non_null_count = int(counts["non_null_count"] or 0)
        distinct_count = int(counts["distinct_count"] or 0)
        profile = ColumnProfile(column.name, null_count, non_null_count, distinct_count)

        value_list_limit = 50 if is_string_type(column.data_type) and distinct_count <= 50 else 20
        values_with_counts = self._values_with_counts(conn, table, column.name, limit=value_list_limit if distinct_count <= value_list_limit else 10)
        if distinct_count <= value_list_limit:
            profile.low_cardinality_values = values_with_counts
        else:
            profile.top_values = values_with_counts[:10]

        if is_numeric_type(column.data_type):
            profile.numeric_min, profile.numeric_max = self._min_max(conn, table, column.name)
            profile.numeric_median = self._median(conn, table, column.name, non_null_count)

        if is_string_type(column.data_type) or distinct_count < 20:
            sample_values = self._sample_column_values(conn, table, column.name)
            profile.shape = value_shape(sample_values)
        else:
            profile.shape = {"profiled": False, "reason": "non-string high-cardinality column"}
        return profile

    def _values_with_counts(self, conn: Connection, table: str, column: str, limit: int) -> list[tuple[Any, int]]:
        rows = conn.execute(
            text(
                f"""
                SELECT {quote_identifier(column)} AS value, COUNT(*) AS count
                FROM {quote_identifier(table)}
                GROUP BY {quote_identifier(column)}
                ORDER BY count DESC, value ASC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        )
        return [(normalize_scalar(row[0]), int(row[1])) for row in rows]

    def _min_max(self, conn: Connection, table: str, column: str) -> tuple[Any | None, Any | None]:
        row = conn.execute(
            text(f"SELECT MIN({quote_identifier(column)}), MAX({quote_identifier(column)}) FROM {quote_identifier(table)}")
        ).one()
        return normalize_scalar(row[0]), normalize_scalar(row[1])

    def _median(self, conn: Connection, table: str, column: str, non_null_count: int) -> Any | None:
        if non_null_count == 0:
            return None
        offset = (non_null_count - 1) // 2
        row = conn.execute(
            text(
                f"""
                SELECT {quote_identifier(column)}
                FROM {quote_identifier(table)}
                WHERE {quote_identifier(column)} IS NOT NULL
                ORDER BY {quote_identifier(column)}
                LIMIT 1 OFFSET :offset
                """
            ),
            {"offset": offset},
        ).first()
        return normalize_scalar(row[0]) if row else None

    def _sample_column_values(self, conn: Connection, table: str, column: str) -> list[Any]:
        rows = conn.execute(
            text(
                f"""
                SELECT {quote_identifier(column)}
                FROM {quote_identifier(table)}
                WHERE {quote_identifier(column)} IS NOT NULL
                LIMIT :limit
                """
            ),
            {"limit": self.sample_rows},
        )
        return [row[0] for row in rows]


def quote_identifier(name: str) -> str:
    return "`" + name.replace("`", "``") + "`"


def scalar_int(conn: Connection, sql: str) -> int:
    value = conn.execute(text(sql)).scalar_one()
    return int(value or 0)


def order_by_clause(columns: list[ColumnInfo]) -> str:
    if not columns:
        return ""
    pk_like = [column.name for column in columns if column.name == "id"]
    selected = pk_like or [columns[0].name]
    return "ORDER BY " + ", ".join(quote_identifier(name) for name in selected)


def declared_joins(tables: list[TableProfile]) -> list[LikelyJoin]:
    joins: list[LikelyJoin] = []
    for table in tables:
        for fk in table.foreign_keys:
            joins.append(
                LikelyJoin(
                    table.name,
                    ",".join(fk.columns),
                    fk.referenced_table,
                    ",".join(fk.referenced_columns),
                    "declared",
                    f"foreign key {fk.name}",
                )
            )
    return joins


def likely_name_joins(tables: list[TableProfile]) -> list[LikelyJoin]:
    table_by_name = {table.name: table for table in tables}
    pk_by_table = {table.name: table.primary_key for table in tables if len(table.primary_key) == 1}
    existing = {(join.left_table, join.left_column, join.right_table, join.right_column) for join in declared_joins(tables)}
    joins: list[LikelyJoin] = []
    column_types: dict[tuple[str, str], str] = {
        (table.name, column.name): column.data_type for table in tables for column in table.columns
    }
    for table in tables:
        for column in table.columns:
            if not column.name.endswith("_id"):
                continue
            target_table_name = column.name[:-3]
            if target_table_name not in table_by_name or target_table_name not in pk_by_table:
                continue
            target_column = pk_by_table[target_table_name][0]
            key = (table.name, column.name, target_table_name, target_column)
            if key in existing:
                continue
            if column_types[(table.name, column.name)].split("(", 1)[0] != column_types[(target_table_name, target_column)].split("(", 1)[0]:
                continue
            joins.append(
                LikelyJoin(
                    table.name,
                    column.name,
                    target_table_name,
                    target_column,
                    "medium",
                    "*_id column name matches table primary key",
                )
            )
    return joins


def sorted_joins(joins: list[LikelyJoin]) -> list[LikelyJoin]:
    deduped = {(join.left_table, join.left_column, join.right_table, join.right_column, join.confidence): join for join in joins}
    return sorted(deduped.values(), key=lambda join: (join.left_table, join.left_column, join.right_table, join.right_column))


def render_value_for_comment(value: Any) -> str:
    return compact_value(value)
