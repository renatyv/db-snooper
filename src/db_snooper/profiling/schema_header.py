from __future__ import annotations

import re
from typing import Any

from sqlalchemy import Table
from sqlalchemy.engine import Connection
from sqlalchemy.schema import ForeignKeyConstraint, UniqueConstraint

from db_snooper.shared import quote_ident

# The one-block-per-table format flattens a table's shape into a merged
# ``columns:`` block (one ``"name" type[ flags]`` line per column, see
# core.py) plus the ``indexes:``/``fk:`` one-liners, all derived from SQLAlchemy
# introspection. These helpers replace the historical ``CREATE TABLE`` DDL block
# in the normal path; DDL survives only as a last-resort fallback (see core.py).


def format_column_tokens(
    table: Table,
    conn: Connection,
    type_overrides: dict[str, str] | None = None,
) -> list[tuple[str, str]]:
    """Render every column as a ``"name" type[ flags]`` token, in table order.

    The name is always delimited (see :func:`db_snooper.shared.quote_ident`) so
    the name/type boundary stays unambiguous even when the name contains
    spaces or parentheses. Returns ``(column_name, token)`` pairs so the caller
    can join each token with the column's profile by name (the catalog-stats
    path may skip columns, so a positional zip with the profile list is not
    safe).

    Flags, emitted only when they apply and in this order: ``PK`` (primary-key
    member), ``UNIQ`` (single-column UNIQUE), ``NOTNULL`` (NOT NULL, not already
    PK), ``FK`` (single-column foreign key). The type token is the dialect-
    specific SQL type, compacted (see :func:`compact_type_string`), unless
    ``type_overrides`` supplies a data-derived replacement for the column (see
    :func:`db_snooper.profiling.columns.sqlite_storage_info` — SQLite storage
    classes can contradict or replace the declared type).
    """
    dialect_name = conn.dialect.name
    pk_names = {column.name for column in table.primary_key.columns}
    single_uniques = _single_column_unique_names(table)
    single_fks = _single_column_fk_names(table)
    overrides = type_overrides or {}
    tokens: list[tuple[str, str]] = []
    for column in table.columns:
        type_token = overrides.get(column.name) or compact_type_string(
            column, conn.dialect
        )
        flags = []
        if column.name in pk_names:
            flags.append("PK")
        if column.name in single_uniques:
            flags.append("UNIQ")
        if not column.nullable and column.name not in pk_names:
            flags.append("NOTNULL")
        if column.name in single_fks:
            flags.append("FK")
        suffix = " " + " ".join(flags) if flags else ""
        name = quote_ident(column.name, dialect_name)
        tokens.append((column.name, f"{name} {type_token}{suffix}"))
    return tokens


def format_indexes_line(table: Table, conn: Connection) -> str:
    """Render non-PK indexes as parenthesized column lists.

    Column names are delimited (same rule as the ``columns:`` block).
    Multi-column indexes keep their declared column order. Partial/conditional
    indexes append ``WHERE <predicate>``. Returns ``none`` when there are no
    non-PK indexes. The primary-key index is never repeated here.
    """
    pk_columns = {tuple(column.name for column in table.primary_key.columns)}
    entries: list[str] = []
    for index in sorted(table.indexes, key=lambda item: item.name or ""):
        cols = tuple(column.name for column in index.columns)
        # Skip an index that exactly mirrors the primary key.
        if cols and cols in pk_columns:
            continue
        entry = _join_columns(list(cols), conn.dialect.name)
        predicate = _index_predicate(index, conn.dialect.name)
        if predicate:
            entry += f" WHERE {predicate}"
        prefix = "UNIQUE " if index.unique else ""
        entries.append(prefix + entry)
    if not entries:
        return "indexes: none"
    return "indexes: " + ", ".join(entries)


def format_fk_line(table: Table, dialect_name: str) -> str:
    """Render foreign keys as ``"col"→"ref_table"."ref_col"``.

    Composite FKs render as ``("c1","c2")→"ref_table".("r1","r2")``. ``none``
    when the table has no foreign keys.
    """
    entries: list[str] = []
    for constraint in table.constraints:
        if not isinstance(constraint, ForeignKeyConstraint):
            continue
        elements = list(constraint.elements)
        if not elements:
            continue
        local = [element.parent.name for element in elements]
        ref_cols = []
        ref_table = ""
        for element in elements:
            ref_table = element.column.table.name
            ref_cols.append(element.column.name)
        local_side = _join_columns(local, dialect_name)
        ref_side = _join_columns(ref_cols, dialect_name)
        quoted_table = quote_ident(ref_table, dialect_name)
        entries.append(f"{local_side}→{quoted_table}.{ref_side}")
    if not entries:
        return "fk: none"
    return "fk: " + ", ".join(entries)


def _join_columns(cols: list[str], dialect_name: str) -> str:
    if len(cols) == 1:
        return quote_ident(cols[0], dialect_name)
    return "(" + ",".join(quote_ident(col, dialect_name) for col in cols) + ")"


def _single_column_unique_names(table: Table) -> set[str]:
    names: set[str] = set()
    for constraint in table.constraints:
        if isinstance(constraint, UniqueConstraint) and len(constraint.columns) == 1:
            names.update(column.name for column in constraint.columns)
    for index in table.indexes:
        if index.unique and len(index.columns) == 1:
            names.update(column.name for column in index.columns)
    return names


def _single_column_fk_names(table: Table) -> set[str]:
    names: set[str] = set()
    for constraint in table.constraints:
        if not isinstance(constraint, ForeignKeyConstraint):
            continue
        if len(constraint.columns) == 1:
            names.update(column.name for column in constraint.columns)
    return names


def _index_predicate(index: Any, dialect_name: str) -> str:
    """Return a partial-index predicate (``WHERE …`` body) when one is defined.

    PostgreSQL records partial predicates on the index object's dialect options
    under ``dialect_options['postgresql']['where']``. Other dialects rarely
    expose partial predicates through introspection, so this is best-effort.
    """
    options = getattr(index, "dialect_options", None) or {}
    where: Any = None
    # On indexes, dialect_options is a mapping keyed by bare dialect name whose
    # values are SQLAlchemy _DialectArgDict objects (NOT plain dicts), so use
    # duck-typing via ``.get`` rather than ``isinstance(..., dict)``.
    dialect_block = options.get(dialect_name) if hasattr(options, "get") else None
    if dialect_block is not None and hasattr(dialect_block, "get"):
        where = dialect_block.get("where")
    if where is None and hasattr(options, "get"):
        where = options.get("where")
    if where is None:
        return ""
    text = str(where).strip()
    # The value is sometimes the full ``WHERE …`` clause and sometimes just the
    # predicate body; normalize to the body so the caller can prepend ``WHERE ``.
    return re.sub(r"^\s*WHERE\s+", "", text, flags=re.IGNORECASE)


# ---------------------------------------------------------------------------
# Type compaction
# ---------------------------------------------------------------------------

# Maps verbose dialect-specific type strings to the short tokens used in the
# spec examples. Lowercased input.
_TYPE_ALIASES = {
    "timestamp with time zone": "timestamptz",
    "timestamp without time zone": "timestamp",
    "time without time zone": "time",
    "boolean": "bool",
    "bytea": "bytes",
    "bytea(1)": "bytes",
    "blob": "bytes",
    "varbyte": "bytes",
    "double precision": "float",
    "real": "float",
    "float8": "float",
    "float4": "float",
    "int8": "bigint",
    "int4": "int",
    "int2": "smallint",
    "serial": "serial",
    "bigserial": "bigserial",
    "smallserial": "smallserial",
}

_PARENS_RE = re.compile(r"\(([^)]*)\)")


def compact_type_string(column: Any, dialect: Any) -> str:
    """Return a compact, lowercased type token for a column.

    Uses the dialect-specific compiled form (``VARCHAR(64)`` on MySQL, ``BYTEA``
    on PostgreSQL for binary) so the token reflects what the engine actually
    stores. Length is folded into the name for string types (``varchar64``);
    numeric precision/scale is dropped (``numeric``); a few verbose names are
    aliased (``timestamp with time zone``→``timestamptz``, ``boolean``→``bool``).
    Falls back to the generic type string if compilation fails (e.g. an
    unbounded MySQL VARCHAR cannot compile without an explicit length).
    """
    try:
        compiled = column.type.compile(dialect=dialect)
    except Exception:  # noqa: BLE001 — compile can raise on incomplete types
        compiled = str(column.type)
    text = compiled.strip().lower()
    # Strip MySQL noise that the compiler includes inline.
    text = re.sub(r"\s+character\s+set\s+\w+", "", text)
    text = re.sub(r"\s+collate\s+\w+", "", text)
    text = re.sub(r"\s+unsigned\b", "", text)
    text = re.sub(r"\s+zerofill\b", "", text)
    if text in _TYPE_ALIASES:
        return _TYPE_ALIASES[text]
    # Handle "varchar(64)" → "varchar64", but drop numeric precision/scale.
    base = _PARENS_RE.sub("", text).strip()
    if base in {"varchar", "char", "nvarchar", "nchar", "character varying", "character"}:
        # Keep the length when present.
        match = _PARENS_RE.search(text)
        if match:
            length = match.group(1).strip().split(",")[0].strip()
            if length.isdigit():
                return f"{_normalize_char_base(base)}{length}"
        return _normalize_char_base(base)
    if base in {"numeric", "decimal"}:
        return "numeric"
    if base in {"timestamp", "time"} and "with time zone" in text:
        return "timestamptz" if base == "timestamp" else "time"
    # Handle "tinyint(1)" style mysql booleans and other sized ints: drop the size.
    if base in {"int", "integer", "bigint", "smallint", "tinyint", "mediumint"}:
        return _normalize_int_base(base)
    return base


def _normalize_char_base(base: str) -> str:
    if base in {"character varying", "varchar"}:
        return "varchar"
    if base in {"character", "char"}:
        return "char"
    if base == "nvarchar":
        return "nvarchar"
    if base == "nchar":
        return "nchar"
    return base


def _normalize_int_base(base: str) -> str:
    if base in {"integer", "int", "mediumint"}:
        return "int"
    if base == "tinyint":
        return "int"
    if base == "smallint":
        return "smallint"
    if base == "bigint":
        return "bigint"
    return base
