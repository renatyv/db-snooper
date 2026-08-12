from __future__ import annotations

import os
import re
import shutil
import subprocess

from sqlalchemy.engine import URL

from db_snooper.profiling.ddl import TableDdl, compact_index_sql

_UTILITY_FOR_DIALECT: dict[str, str] = {
    "postgresql": "pg_dump",
    "mysql": "mysqldump",
    "mariadb": "mysqldump",
}

_DUMP_TIMEOUT_SECONDS = 60


def dump_utility_name(dialect_name: str) -> str | None:
    """Return the optional DDL fallback utility used for a dialect."""
    return _UTILITY_FOR_DIALECT.get(dialect_name)


def dump_utility_available(dialect_name: str) -> bool:
    """Return whether the dialect's optional DDL fallback is on PATH."""
    binary_name = dump_utility_name(dialect_name)
    return binary_name is None or shutil.which(binary_name) is not None


def dump_create_table(
    url: URL,
    dialect_name: str,
    table_name: str,
    schema: str | None,
) -> TableDdl | None:
    """Return normalized CREATE TABLE DDL + compact indexes when available."""
    binary_name = dump_utility_name(dialect_name)
    if binary_name is None:
        return None
    binary = shutil.which(binary_name)
    if binary is None:
        return None
    cmd = (
        _build_pg_dump_cmd(binary, url, table_name, schema)
        if binary_name == "pg_dump"
        else _build_mysqldump_cmd(binary, url, table_name)
    )
    sql = _run(cmd, url, binary_name)
    return _normalize(sql)


def _compact_indexes(raw_indexes: list[str]) -> list[str]:
    return [compact_index_sql(idx) for idx in raw_indexes if idx.strip()]


def _build_pg_dump_cmd(
    binary: str, url: URL, table_name: str, schema: str | None
) -> list[str]:
    cmd = [
        binary,
        "--schema-only",
        "--no-owner",
        "--no-privileges",
        "--no-comments",
        "--no-password",
    ]
    # pg_dump matches reliably only with a schema-qualified table pattern on
    # PostgreSQL 18+; a separate --schema flag yields "no matching tables".
    if schema:
        cmd.append(f"--table={schema}.{table_name}")
    else:
        cmd.append(f"--table={table_name}")
    if url.host:
        cmd.extend(["-h", url.host])
    if url.port:
        cmd.extend(["-p", str(url.port)])
    if url.username:
        cmd.extend(["-U", url.username])
    if url.database:
        cmd.extend(["-d", url.database])
    return cmd


def _build_mysqldump_cmd(binary: str, url: URL, table_name: str) -> list[str]:
    cmd = [
        binary,
        "--no-data",
        "--no-tablespaces",
        "--skip-comments",
        "--skip-add-drop-table",
        "--compact",
    ]
    if url.host:
        cmd.extend(["-h", url.host])
    if url.port:
        cmd.extend(["-P", str(url.port)])
    if url.username:
        cmd.extend(["-u", url.username])
    if url.database:
        cmd.append(url.database)
    cmd.append(table_name)
    return cmd


def _run(cmd: list[str], url: URL, binary_name: str) -> str:
    env = dict(os.environ)
    password = url.password
    if password is not None:
        if binary_name == "pg_dump":
            env["PGPASSWORD"] = password
        else:
            env["MYSQL_PWD"] = password
    completed = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=_DUMP_TIMEOUT_SECONDS,
        env=env,
    )
    completed.check_returncode()
    return completed.stdout


def _normalize(sql: str) -> TableDdl | None:
    create_table = _extract_create_table_block(sql)
    if create_table is None:
        return None
    indexes = _compact_indexes(_extract_indexes(sql))
    return TableDdl(create_table=[create_table], indexes=indexes)


def _extract_create_table_block(sql: str) -> str | None:
    lines = sql.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        if re.match(r"^CREATE (UNLOGGED )?TABLE\b", line):
            start = index
            break
    if start is None:
        return None
    block: list[str] = []
    for line in lines[start:]:
        block.append(line)
        if line.rstrip().endswith(";"):
            break
    text = "\n".join(block).strip()
    return text if text.endswith(";") else text + ";"


def _extract_indexes(sql: str) -> list[str]:
    indexes: list[str] = []
    for line in sql.splitlines():
        stripped = line.strip()
        if re.match(r"^CREATE (UNIQUE )?INDEX\b", stripped):
            indexes.append(_ensure_semicolon(stripped))
    return indexes


def _ensure_semicolon(text: str) -> str:
    text = text.rstrip()
    return text if text.endswith(";") else text + ";"
