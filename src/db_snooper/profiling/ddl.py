from __future__ import annotations

import re
from dataclasses import dataclass

from sqlalchemy import Table, text
from sqlalchemy.engine import Connection
from sqlalchemy.schema import CreateIndex, CreateTable

from db_snooper.contracts import (
    OBJECT_MATERIALIZED_VIEW,
    OBJECT_TABLE,
    OBJECT_VIEW,
)
from db_snooper.shared import bigquery_table_id


@dataclass
class TableDdl:
    create_table: list[str]
    indexes: list[str]


_INDEX_PREFIX_RE = re.compile(
    r"^\s*CREATE\s+"
    r"(?P<unique>UNIQUE\s+)?"
    r"INDEX\s+"
    r"(?:\"[^\"]+\"|`[^`]+`|\[[^\]]+\]|\S+)\s+"
    r"ON\s+"
    r"(?:\"[^\"]+\"|`[^`]+`|\[[^\]]+\]|[\w.]+)\s*",
    re.IGNORECASE,
)


def compact_index_sql(sql: str) -> str:
    match = _INDEX_PREFIX_RE.match(sql)
    if match is None:
        return sql.strip().rstrip(";").strip()
    unique = (match.group("unique") or "").strip()
    rest = sql[match.end() :].strip().rstrip(";").strip()
    return f"{unique} {rest}".strip() if unique else rest


def get_table_ddl(conn: Connection, table: Table, kind: str = OBJECT_TABLE) -> TableDdl:
    if kind in {OBJECT_VIEW, OBJECT_MATERIALIZED_VIEW}:
        return get_view_ddl(conn, table, kind)
    dialect_name = conn.dialect.name
    if dialect_name == "sqlite":
        return get_sqlite_ddl(conn, table.name)
    if dialect_name in {"mysql", "mariadb"}:
        return get_mysql_ddl(conn, table)
    return get_reflected_ddl(conn, table)


def get_view_ddl(conn: Connection, table: Table, kind: str) -> TableDdl:
    dialect_name = conn.dialect.name
    if dialect_name == "postgresql":
        return _postgres_view_ddl(conn, table, kind)
    if dialect_name == "sqlite":
        return _sqlite_view_ddl(conn, table.name)
    if dialect_name == "duckdb":
        return _duckdb_view_ddl(conn, table)
    if dialect_name in {"mysql", "mariadb"}:
        return _mysql_view_ddl(conn, table)
    if dialect_name == "bigquery":
        return _bigquery_view_ddl(conn, table, kind)
    return get_reflected_ddl(conn, table)


def _view_keyword(kind: str) -> str:
    return (
        "CREATE MATERIALIZED VIEW"
        if kind == OBJECT_MATERIALIZED_VIEW
        else "CREATE VIEW"
    )


def _materialized_view_indexes(conn: Connection, table: Table) -> list[str]:
    return [
        compact_index_sql(ensure_semicolon(str(CreateIndex(index).compile(conn))))
        for index in sorted(table.indexes, key=lambda item: item.name or "")
    ]


def _postgres_view_ddl(conn: Connection, table: Table, kind: str) -> TableDdl:
    body = conn.execute(
        text(
            "SELECT pg_get_viewdef(c.oid, true) FROM pg_class c "
            "JOIN pg_namespace n ON n.oid = c.relnamespace "
            "WHERE n.nspname = :schema AND c.relname = :name"
        ),
        {"schema": table.schema, "name": table.name},
    ).scalar_one_or_none()
    qualified = conn.dialect.identifier_preparer.format_table(table)
    keyword = _view_keyword(kind)
    create_table = [
        ensure_semicolon(f"{keyword} {qualified} AS\n{body.strip().rstrip(';')}")
        if body
        else ensure_semicolon(f"{keyword} {qualified} AS SELECT *")
    ]
    indexes = (
        _materialized_view_indexes(conn, table)
        if kind == OBJECT_MATERIALIZED_VIEW
        else []
    )
    return TableDdl(create_table=create_table, indexes=indexes)


def _sqlite_view_ddl(conn: Connection, table_name: str) -> TableDdl:
    sql = conn.execute(
        text("SELECT sql FROM sqlite_master WHERE type = 'view' AND name = :name"),
        {"name": table_name},
    ).scalar_one_or_none()
    return TableDdl(
        create_table=[ensure_semicolon(str(sql))] if sql else [], indexes=[]
    )


def _duckdb_view_ddl(conn: Connection, table: Table) -> TableDdl:
    sql = conn.execute(
        text(
            "SELECT sql FROM duckdb_views() "
            "WHERE schema_name = :schema AND view_name = :name"
        ),
        {"schema": table.schema or "main", "name": table.name},
    ).scalar_one_or_none()
    return TableDdl(
        create_table=[ensure_semicolon(str(sql))] if sql else [], indexes=[]
    )


def _mysql_view_ddl(conn: Connection, table: Table) -> TableDdl:
    body = conn.execute(
        text(
            "SELECT view_definition FROM information_schema.views "
            "WHERE table_schema = :schema AND table_name = :name"
        ),
        {
            "schema": table.schema or conn.dialect.default_schema_name,
            "name": table.name,
        },
    ).scalar_one_or_none()
    qualified = conn.dialect.identifier_preparer.format_table(table)
    create_table = (
        [ensure_semicolon(f"CREATE VIEW {qualified} AS {body.strip().rstrip(';')}")]
        if body is not None
        else []
    )
    return TableDdl(create_table=create_table, indexes=[])


def _bigquery_view_ddl(conn: Connection, table: Table, kind: str) -> TableDdl:
    client = conn.connection.driver_connection._client
    project = getattr(conn.dialect, "project_id", None) or client.project
    remote_table = client.get_table(
        bigquery_table_id(project, table.schema, table.name)
    )
    materialized = remote_table.table_type == "MATERIALIZED_VIEW"
    body = remote_table.mview_query if materialized else remote_table.view_query
    qualified = conn.dialect.identifier_preparer.format_table(table)
    keyword = "CREATE MATERIALIZED VIEW" if materialized else _view_keyword(kind)
    return TableDdl(
        create_table=[
            ensure_semicolon(f"{keyword} {qualified} AS\n{body.rstrip(';')}")
        ],
        indexes=[],
    )


def get_sqlite_ddl(conn: Connection, table_name: str) -> TableDdl:
    table_sql = conn.execute(
        text("select sql from sqlite_master where type = 'table' and name = :name"),
        {"name": table_name},
    ).scalar_one_or_none()
    index_sql = conn.execute(
        text(
            "select sql from sqlite_master "
            "where type = 'index' and tbl_name = :name and sql is not null "
            "order by name"
        ),
        {"name": table_name},
    ).scalars()
    return TableDdl(
        create_table=[ensure_semicolon(str(table_sql))] if table_sql else [],
        indexes=[compact_index_sql(ensure_semicolon(str(sql))) for sql in index_sql],
    )


_MYSQL_INDEX_NAME_RE = re.compile(
    r"\b((?:UNIQUE|FULLTEXT|SPATIAL)\s+)?KEY\s+(?:`[^`]+`|\w+)(?=\s*\()",
    re.IGNORECASE,
)


def _strip_mysql_noise(sql: str) -> str:
    sql = re.sub(r"\s+DEFAULT\s+NULL\b", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s+CHARACTER\s+SET\s+\w+", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s+COLLATE\s+\w+", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s*ENGINE\s*=\s*\w+", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s*(?:DEFAULT\s+)?CHARSET\s*=\s*\w+", "", sql, flags=re.IGNORECASE)
    sql = re.sub(
        r"\s*(?:DEFAULT\s+)?COLL(?:ATE|ATION)\s*=\s*\w+",
        "",
        sql,
        flags=re.IGNORECASE,
    )
    return _MYSQL_INDEX_NAME_RE.sub(r"\1KEY", sql)


def get_mysql_ddl(conn: Connection, table: Table) -> TableDdl:
    quoted_table = conn.dialect.identifier_preparer.format_table(table)
    row = conn.exec_driver_sql(f"SHOW CREATE TABLE {quoted_table}").first()
    if row is None:
        return TableDdl(create_table=[], indexes=[])
    return TableDdl(
        create_table=[ensure_semicolon(_strip_mysql_noise(str(row[1])))], indexes=[]
    )


def get_reflected_ddl(conn: Connection, table: Table) -> TableDdl:
    return TableDdl(
        create_table=[ensure_semicolon(str(CreateTable(table).compile(conn)))],
        indexes=[
            compact_index_sql(ensure_semicolon(str(CreateIndex(index).compile(conn))))
            for index in sorted(table.indexes, key=lambda item: item.name or "")
        ],
    )


def ensure_semicolon(sql: str) -> str:
    sql = sql.rstrip()
    return sql if sql.endswith(";") else sql + ";"
