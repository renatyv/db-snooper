from __future__ import annotations

import argparse
import os
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from datasketch import MinHash, MinHashLSHEnsemble
from sqlalchemy import MetaData, Table, create_engine, func, inspect, select
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql.sqltypes import BigInteger, Date, DateTime, Float, Integer, Numeric, SmallInteger, String, Text, Time

from db_snooper import __version__
from db_snooper.connection import add_connection_arguments, resolve_database_url
from db_snooper.profiler import default_output_path as default_profile_output_path
from db_snooper.profiler import is_sensitive, parse_table_set
from db_snooper.progress import ProgressBar


@dataclass(frozen=True)
class SchemaLinkOptions:
    include_tables: frozenset[str] | None = None
    exclude_tables: frozenset[str] = frozenset()
    low_cardinality_ratio: float = 0.05
    unique_drop_ratio: float = 0.98
    containment_threshold: float = 0.8
    max_distinct_values: int = 10_000
    minhash_permutations: int = 128


@dataclass(frozen=True)
class ColumnRef:
    table: str
    column: str
    type_group: str
    is_primary_or_unique: bool
    is_id_like: bool
    total_rows: int
    non_nulls: int
    distinct_count: int

    @property
    def key(self) -> tuple[str, str]:
        return (self.table, self.column)

    @property
    def label(self) -> str:
        return f"{self.table}.{self.column}"

    @property
    def cardinality_ratio(self) -> float:
        if self.non_nulls == 0:
            return 0.0
        return self.distinct_count / self.non_nulls


@dataclass(frozen=True)
class DeclaredLink:
    from_table: str
    from_columns: tuple[str, ...]
    to_table: str
    to_columns: tuple[str, ...]


@dataclass(frozen=True)
class CandidatePair:
    left: ColumnRef
    right: ColumnRef
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class InferredLink:
    source: ColumnRef
    target: ColumnRef
    containment: float
    evidence: tuple[str, ...]
    notes: tuple[str, ...]


SchemaLinkProgress = Callable[[int, int, str], None]


def link_schema(engine: Engine, options: SchemaLinkOptions, progress: SchemaLinkProgress | None = None) -> str:
    inspector = inspect(engine)
    table_names = sorted(inspector.get_table_names())
    if options.include_tables is not None:
        table_names = [table for table in table_names if table in options.include_tables]
    table_names = [table for table in table_names if table not in options.exclude_tables]

    url = engine.url.render_as_string(hide_password=True)
    database = engine.url.database or ""

    with engine.connect() as conn:
        metadata = MetaData()
        tables = []
        for index, table_name in enumerate(table_names, start=1):
            if progress is not None:
                progress(index - 1, len(table_names), f"reflecting {table_name}")
            tables.append(Table(table_name, metadata, autoload_with=conn))
            if progress is not None:
                progress(index, len(table_names), f"reflected {table_name}")
        declared_links = collect_declared_links(tables, set(table_names))
        column_refs = collect_column_refs(conn, tables, options, progress)
        inferred_links = infer_links(conn, tables, column_refs, declared_links, options, progress)

    return render_markdown(engine.dialect.name, database, url, declared_links, inferred_links)


def collect_declared_links(tables: list[Table], selected_tables: set[str]) -> list[DeclaredLink]:
    links: list[DeclaredLink] = []
    for table in tables:
        for constraint in sorted(table.foreign_key_constraints, key=lambda item: constraint_sort_key(item.elements)):
            if constraint.referred_table.name not in selected_tables:
                continue
            from_columns = tuple(element.parent.name for element in constraint.elements)
            to_columns = tuple(element.column.name for element in constraint.elements)
            links.append(DeclaredLink(table.name, from_columns, constraint.referred_table.name, to_columns))
    return sorted(links, key=lambda link: (link.from_table, link.from_columns, link.to_table, link.to_columns))


def constraint_sort_key(elements: Any) -> tuple[str, ...]:
    return tuple(element.parent.name for element in elements)


def collect_column_refs(
    conn: Connection,
    tables: list[Table],
    options: SchemaLinkOptions,
    progress: SchemaLinkProgress | None = None,
) -> dict[tuple[str, str], ColumnRef]:
    refs: dict[tuple[str, str], ColumnRef] = {}
    row_counts = {table.name: int(conn.execute(select(func.count()).select_from(table)).scalar_one()) for table in tables}
    for index, table in enumerate(tables, start=1):
        if progress is not None:
            progress(index - 1, len(tables), f"inspecting {table.name}")
        unique_columns = get_unique_column_names(table)
        for column in table.columns:
            if is_sensitive(column.name):
                continue
            type_group = get_type_group(column)
            if type_group == "other":
                continue
            non_nulls = int(conn.execute(select(func.count(column)).select_from(table)).scalar_one())
            if non_nulls == 0:
                continue
            distinct_count = int(conn.execute(select(func.count(func.distinct(column))).select_from(table)).scalar_one())
            ref = ColumnRef(
                table=table.name,
                column=column.name,
                type_group=type_group,
                is_primary_or_unique=column.name in unique_columns,
                is_id_like=is_id_like(column.name),
                total_rows=row_counts[table.name],
                non_nulls=non_nulls,
                distinct_count=distinct_count,
            )
            refs[ref.key] = ref
        if progress is not None:
            progress(index, len(tables), f"inspected {table.name}")
    return refs


def infer_links(
    conn: Connection,
    tables: list[Table],
    column_refs: dict[tuple[str, str], ColumnRef],
    declared_links: list[DeclaredLink],
    options: SchemaLinkOptions,
    progress: SchemaLinkProgress | None = None,
) -> list[InferredLink]:
    table_by_name = {table.name: table for table in tables}
    declared_pairs = get_declared_column_pairs(declared_links)

    triaged_refs = get_triaged_refs(column_refs, options)
    name_candidates = get_name_candidates(conn, table_by_name, triaged_refs, declared_pairs, options)
    candidate_columns = get_distinct_candidate_columns(triaged_refs, name_candidates, options)

    distinct_sets = load_distinct_sets(
        conn,
        table_by_name,
        column_refs,
        candidate_columns,
        options.max_distinct_values,
        progress,
    )
    lsh_candidates = get_lsh_candidates(triaged_refs, distinct_sets, declared_pairs, options)
    candidates = merge_candidates(name_candidates + lsh_candidates)

    links: dict[frozenset[tuple[str, str]], InferredLink] = {}
    for candidate in candidates:
        left_values = distinct_sets.get(candidate.left.key)
        right_values = distinct_sets.get(candidate.right.key)
        if not left_values or not right_values:
            continue
        for source, target, source_values, target_values in (
            (candidate.left, candidate.right, left_values, right_values),
            (candidate.right, candidate.left, right_values, left_values),
        ):
            containment = len(source_values & target_values) / len(source_values)
            if containment < options.containment_threshold:
                continue
            if not plausible_direction(source, target, candidate.evidence):
                continue
            evidence = tuple(sorted(set(candidate.evidence) | set(get_cardinality_evidence(source, target, options))))
            if len(evidence) < 3:
                continue
            key = frozenset({source.key, target.key})
            notes = tuple(sorted(get_notes(source, target, options)))
            link = InferredLink(source, target, containment, evidence, notes)
            existing = links.get(key)
            if existing is None or link_rank_key(link) < link_rank_key(existing):
                links[key] = link

    return sorted(
        links.values(),
        key=link_rank_key,
    )


def get_declared_column_pairs(declared_links: list[DeclaredLink]) -> set[frozenset[tuple[str, str]]]:
    pairs: set[frozenset[tuple[str, str]]] = set()
    for link in declared_links:
        for from_column, to_column in zip(link.from_columns, link.to_columns, strict=False):
            pairs.add(frozenset({(link.from_table, from_column), (link.to_table, to_column)}))
    return pairs


def get_distinct_candidate_columns(
    column_refs: dict[tuple[str, str], ColumnRef],
    name_candidates: list[CandidatePair],
    options: SchemaLinkOptions,
) -> set[tuple[str, str]]:
    candidate_columns = {candidate.left.key for candidate in name_candidates} | {candidate.right.key for candidate in name_candidates}
    for ref in column_refs.values():
        if is_primary_lsh_target(ref, options):
            candidate_columns.add(ref.key)
    return candidate_columns


def get_triaged_refs(
    column_refs: dict[tuple[str, str], ColumnRef],
    options: SchemaLinkOptions,
) -> dict[tuple[str, str], ColumnRef]:
    refs: dict[tuple[str, str], ColumnRef] = {}
    for key, ref in column_refs.items():
        if ref.cardinality_ratio >= options.unique_drop_ratio and not ref.is_primary_or_unique:
            continue
        refs[key] = ref
    return refs


def get_name_candidates(
    conn: Connection,
    table_by_name: dict[str, Table],
    column_refs: dict[tuple[str, str], ColumnRef],
    declared_pairs: set[frozenset[tuple[str, str]]],
    options: SchemaLinkOptions,
) -> list[CandidatePair]:
    refs = sorted(column_refs.values(), key=lambda ref: ref.key)
    candidates: list[CandidatePair] = []
    for index, left in enumerate(refs):
        for right in refs[index + 1 :]:
            if left.table == right.table or left.type_group != right.type_group:
                continue
            if frozenset({left.key, right.key}) in declared_pairs:
                continue
            name_evidence = get_name_evidence(left, right)
            if not name_evidence:
                continue
            evidence = tuple(dict.fromkeys(name_evidence + get_cardinality_evidence(left, right, options) + ("type match",)))
            if is_strong_name_candidate(evidence) and not spot_check_overlap(conn, table_by_name, left, right):
                continue
            candidates.append(CandidatePair(left, right, evidence))
    return candidates


def load_distinct_sets(
    conn: Connection,
    table_by_name: dict[str, Table],
    column_refs: dict[tuple[str, str], ColumnRef],
    candidate_columns: set[tuple[str, str]],
    max_distinct_values: int,
    progress: SchemaLinkProgress | None = None,
) -> dict[tuple[str, str], set[Any]]:
    distinct_sets: dict[tuple[str, str], set[Any]] = {}
    sorted_candidate_columns = sorted(candidate_columns)
    for index, key in enumerate(sorted_candidate_columns, start=1):
        ref = column_refs[key]
        if progress is not None:
            progress(index - 1, len(sorted_candidate_columns), f"loading {ref.label}")
        if ref.distinct_count > max_distinct_values:
            if progress is not None:
                progress(index, len(sorted_candidate_columns), f"skipped {ref.label}")
            continue
        table = table_by_name[ref.table]
        column = table.c[ref.column]
        values = {
            normalize_value(row[0])
            for row in conn.execute(select(column).where(column.is_not(None)).distinct())
            if normalize_value(row[0]) is not None
        }
        if values:
            distinct_sets[key] = values
        if progress is not None:
            progress(index, len(sorted_candidate_columns), f"loaded {ref.label}")
    return distinct_sets


def get_lsh_candidates(
    column_refs: dict[tuple[str, str], ColumnRef],
    distinct_sets: dict[tuple[str, str], set[Any]],
    declared_pairs: set[frozenset[tuple[str, str]]],
    options: SchemaLinkOptions,
) -> list[CandidatePair]:
    if len(distinct_sets) < 2:
        return []

    minhashes: dict[tuple[str, str], MinHash] = {}
    for key, values in distinct_sets.items():
        minhash = MinHash(num_perm=options.minhash_permutations)
        for value in sorted(values, key=stable_sort_value):
            minhash.update(stable_hash_value(value))
        minhashes[key] = minhash

    ensemble = MinHashLSHEnsemble(threshold=options.containment_threshold, num_perm=options.minhash_permutations)
    ensemble.index((key, minhashes[key], len(distinct_sets[key])) for key in sorted(minhashes))

    candidates: list[CandidatePair] = []
    for left_key, minhash in sorted(minhashes.items()):
        for right_key in ensemble.query(minhash, len(distinct_sets[left_key])):
            if left_key == right_key:
                continue
            first_key, second_key = sorted([left_key, right_key])
            left = column_refs[first_key]
            right = column_refs[second_key]
            if left.table == right.table or left.type_group != right.type_group:
                continue
            if frozenset({left.key, right.key}) in declared_pairs:
                continue
            candidates.append(CandidatePair(left, right, ("minhash containment candidate",)))
    return candidates


def merge_candidates(candidates: list[CandidatePair]) -> list[CandidatePair]:
    merged: dict[frozenset[tuple[str, str]], CandidatePair] = {}
    for candidate in candidates:
        key = frozenset({candidate.left.key, candidate.right.key})
        existing = merged.get(key)
        if existing is None:
            merged[key] = candidate
            continue
        evidence = tuple(sorted(set(existing.evidence) | set(candidate.evidence)))
        merged[key] = CandidatePair(existing.left, existing.right, evidence)
    return sorted(merged.values(), key=lambda candidate: (candidate.left.key, candidate.right.key))


def link_rank_key(link: InferredLink) -> tuple[int, float, str, str, str, str]:
    return (-len(link.evidence), -link.containment, link.source.table, link.source.column, link.target.table, link.target.column)


def plausible_direction(source: ColumnRef, target: ColumnRef, evidence: tuple[str, ...]) -> bool:
    if source.is_primary_or_unique and target.is_primary_or_unique:
        return False
    if not has_name_signal(evidence) and source.type_group == "numeric" and (source.is_id_like or target.is_id_like):
        return False
    if target.is_primary_or_unique and not source.is_primary_or_unique:
        return True
    if source.is_id_like and not target.is_id_like:
        return True
    if "name match" in evidence or "table-name id match" in evidence:
        return target.is_primary_or_unique or target.column.lower() == "id" or source.is_id_like
    return not source.is_primary_or_unique or target.is_primary_or_unique


def has_name_signal(evidence: tuple[str, ...]) -> bool:
    return any(item in evidence for item in ("name match", "table-name id match", "shared name tokens", "similar names"))


def get_notes(source: ColumnRef, target: ColumnRef, options: SchemaLinkOptions) -> list[str]:
    notes: list[str] = []
    if is_low_cardinality(source, options) or is_low_cardinality(target, options):
        notes.append("low cardinality")
    else:
        notes.append("moderate cardinality")
    if target.is_primary_or_unique:
        notes.append("target primary/unique")
    return notes


def get_cardinality_evidence(left: ColumnRef, right: ColumnRef, options: SchemaLinkOptions) -> tuple[str, ...]:
    evidence: list[str] = []
    if left.distinct_count == right.distinct_count:
        evidence.append("same distinct count")
    elif min(left.distinct_count, right.distinct_count) / max(left.distinct_count, right.distinct_count) >= 0.8:
        evidence.append("similar distinct counts")
    if is_low_cardinality(left, options) or is_low_cardinality(right, options):
        evidence.append("low cardinality")
    elif left.is_id_like or right.is_id_like:
        evidence.append("moderate ID-like cardinality")
    else:
        evidence.append("moderate cardinality")
    return tuple(evidence)


def get_name_evidence(left: ColumnRef, right: ColumnRef) -> tuple[str, ...]:
    left_name = normalize_name(left.column)
    right_name = normalize_name(right.column)
    left_tokens = name_tokens(left.column)
    right_tokens = name_tokens(right.column)
    left_table = singularize(normalize_name(left.table))
    right_table = singularize(normalize_name(right.table))

    evidence: list[str] = []
    if left_name == right_name and left_name != "id":
        evidence.append("name match")
    if (left_table in right_tokens and left.column.lower() == "id") or (right_table in left_tokens and right.column.lower() == "id"):
        evidence.append("table-name id match")
    if left_tokens & right_tokens and left_tokens & right_tokens != {"id"}:
        evidence.append("shared name tokens")
    if SequenceMatcher(None, left_name, right_name).ratio() >= 0.82 and left_name != "id" and right_name != "id":
        evidence.append("similar names")
    return tuple(dict.fromkeys(evidence))


def is_primary_lsh_target(ref: ColumnRef, options: SchemaLinkOptions) -> bool:
    return ref.is_id_like and not is_low_cardinality(ref, options)


def is_strong_name_candidate(evidence: tuple[str, ...]) -> bool:
    return len(set(evidence) & {"name match", "table-name id match", "shared name tokens", "similar names"}) >= 2


def spot_check_overlap(
    conn: Connection,
    table_by_name: dict[str, Table],
    left: ColumnRef,
    right: ColumnRef,
    limit: int = 50,
) -> bool:
    left_values = load_limited_distinct_values(conn, table_by_name[left.table], left.column, limit)
    right_values = load_limited_distinct_values(conn, table_by_name[right.table], right.column, limit)
    if not left_values or not right_values:
        return False
    return bool(left_values & right_values)


def load_limited_distinct_values(conn: Connection, table: Table, column_name: str, limit: int) -> set[Any]:
    column = table.c[column_name]
    values = set()
    for row in conn.execute(select(column).where(column.is_not(None)).distinct().limit(limit)):
        value = normalize_value(row[0])
        if value is not None:
            values.add(value)
    return values


def is_low_cardinality(ref: ColumnRef, options: SchemaLinkOptions) -> bool:
    return ref.cardinality_ratio <= options.low_cardinality_ratio or ref.distinct_count <= 3


def get_unique_column_names(table: Table) -> set[str]:
    unique_columns = {column.name for column in table.primary_key.columns}
    for constraint in table.constraints:
        if isinstance(constraint, UniqueConstraint) and len(constraint.columns) == 1:
            unique_columns.update(column.name for column in constraint.columns)
    for index in table.indexes:
        if index.unique and len(index.columns) == 1:
            unique_columns.update(column.name for column in index.columns)
    return unique_columns


def get_type_group(column: Any) -> str:
    column_type = column.type
    if isinstance(column_type, (Integer, BigInteger, SmallInteger, Numeric, Float)):
        return "numeric"
    if isinstance(column_type, (String, Text)):
        return "string"
    if isinstance(column_type, (Date, DateTime, Time)):
        return "datetime"
    return "other"


def is_id_like(column_name: str) -> bool:
    lower_name = column_name.lower()
    return lower_name == "id" or lower_name.endswith("_id") or lower_name.endswith("id")


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def name_tokens(value: str) -> set[str]:
    tokens = {token for token in re.split(r"[^a-z0-9]+", value.lower()) if token}
    normalized = normalize_name(value)
    if normalized.endswith("id") and normalized != "id":
        tokens.add(normalized[:-2])
        tokens.add("id")
    return {singularize(token) for token in tokens if token}


def singularize(value: str) -> str:
    if value.endswith("ies") and len(value) > 3:
        return value[:-3] + "y"
    if value.endswith("s") and len(value) > 1:
        return value[:-1]
    return value


def normalize_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return str(value.normalize())
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else None
    return value


def stable_sort_value(value: Any) -> tuple[str, str]:
    return (type(value).__name__, str(value))


def stable_hash_value(value: Any) -> bytes:
    value_type, rendered = stable_sort_value(value)
    return f"{value_type}:{rendered}".encode("utf-8")


def render_markdown(
    dialect: str,
    database: str,
    url: str,
    declared_links: list[DeclaredLink],
    inferred_links: list[InferredLink],
) -> str:
    lines = [
        "# Schema Links",
        "",
        f"- version: {__version__}",
        f"- dialect: {dialect}",
        f"- database: {database}",
        "",
        "## Declared PK/FK Links",
        "",
    ]
    if declared_links:
        lines.extend([
            "| From | To |",
            "|---|---|",
        ])
        for link in declared_links:
            from_label = ", ".join(f"{link.from_table}.{column}" for column in link.from_columns)
            to_label = ", ".join(f"{link.to_table}.{column}" for column in link.to_columns)
            lines.append(f"| {markdown_cell(from_label)} | {markdown_cell(to_label)} |")
    else:
        lines.append("No declared PK/FK links found.")

    lines.extend(["", "## Inferred Links", ""])
    if inferred_links:
        lines.extend([
            "| From | To | Evidence |",
            "|---|---|---|",
        ])
        for link in inferred_links:
            evidence = ", ".join(link.evidence)
            lines.append(f"| {markdown_cell(link.source.label)} | {markdown_cell(link.target.label)} | {markdown_cell(evidence)} |")
    else:
        lines.append("No inferred links found.")

    return "\n".join(lines).rstrip() + "\n"


def markdown_cell(value: str) -> str:
    return value.replace("|", "\\|")


def build_arg_parser(prog: str | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate Markdown schema join links for a database.", prog=prog)
    add_connection_arguments(parser)
    parser.add_argument("--output", help="Output .md file. Defaults to <database>_schema_links.md.")
    parser.add_argument("--include-tables", help="Comma-separated table allowlist.")
    parser.add_argument("--exclude-tables", help="Comma-separated table denylist.")
    parser.add_argument("--containment-threshold", type=float, default=0.8, help="Minimum exact containment for inferred links.")
    parser.add_argument("--max-distinct-values", type=int, default=10_000, help="Maximum distinct values to load per candidate column.")
    return parser


def default_output_path(database: str) -> Path:
    profile_path = default_profile_output_path(database)
    return profile_path.with_name(f"{profile_path.stem.removesuffix('_profile')}_schema_links.md")


def main(argv: list[str] | None = None, prog: str | None = None) -> int:
    parser = build_arg_parser(prog=prog)
    args = parser.parse_args(argv)
    url = resolve_database_url(args, parser)

    options = SchemaLinkOptions(
        include_tables=parse_table_set(args.include_tables),
        exclude_tables=parse_table_set(args.exclude_tables) or frozenset(),
        containment_threshold=args.containment_threshold,
        max_distinct_values=args.max_distinct_values,
    )
    engine = create_engine(url)
    progress_bar = ProgressBar("Linking", 0)

    def show_progress(current: int, total: int, item: str) -> None:
        nonlocal progress_bar
        if progress_bar.total != total:
            progress_bar.finish()
            progress_bar = ProgressBar("Linking", total)
            progress_bar.start(item)
            return
        progress_bar.update(current, item)

    try:
        output = link_schema(engine, options, progress=show_progress)
    except Exception:
        progress_bar.finish()
        raise
    else:
        progress_bar.finish("Schema linking complete")
    output_path = Path(args.output) if args.output else default_output_path(args.database or os.environ["DB_SNOOPER_DATABASE"])
    output_path.write_text(output, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
