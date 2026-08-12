---
name: db-snooper-profile
description: "Use when an AI agent needs to generate a database schema and data profile (.md: DDL, row counts, sampled rows, per-column summaries) for text-to-SQL, query planning, schema understanding, or data exploration with db-snooper."
compatibility: opencode, OpenWork, PI, Claude, ChatGPT, custom agent runners
---

# DB Snooper Profiling

Use this skill to generate a compact, LLM-ready schema and data profile of an existing database before writing or reviewing SQL. It runs `db-snooper profile` to produce a `.md` artifact containing DDL, indexes/constraints, row counts, sampled rows, and per-column summaries.

## When To Use

- Use when the user asks to profile a database, generate schema context, understand table structures, column meanings, data types, or value distributions.
- Use before generating SQL from natural language, so the SQL agent knows the real schema and data shapes.
- Use when debugging a query and the table/column meanings or formats are unclear.
- Use when the data lives in files (parquet, JSON/JSONL, CSV/TSV, Arrow, ...) rather than a database: load them into DuckDB first (see [Profiling Files](#profiling-files-parquet-json-csv-arrow-)), then profile.
- Do not use this as a full data export tool.
- Do not perform destructive database operations.

## Connection And Options

db-snooper supports SQLite, PostgreSQL, MySQL, MariaDB, DuckDB, and Google BigQuery (all drivers ship with the base install; no extra is needed).

Run the profiler with `uvx` (no install needed). PostgreSQL example:

```bash
uvx db-snooper profile --db-type postgres --database app_db --user readonly_user --host localhost --port 5432 --ask-password
```

See every flag and its default — connection details, `--schema`, `--include-tables`/`--exclude-tables`, thresholds, `--per-table`, `--output`, and the `DB_SNOOPER_*` environment-variable fallbacks — with:

```bash
uvx db-snooper -h
uvx db-snooper profile -h
```

For frequent use, install once with `uv tool install db-snooper` and run `db-snooper ...` directly.

The generated profile (`<database>/<schema>.md`) contains `CREATE TABLE` DDL with indexes/constraints, total row counts, sampled rows, and per-column null/distinct/range/median/top-value summaries — sensitive columns are redacted and very large tables use internal stats only.

## Profiling Files (Parquet, JSON, CSV, Arrow, ...)

DuckDB reads many file formats directly — parquet, JSON/JSONL, CSV/TSV, Arrow/Feather, Iceberg, and more. Because db-snooper already supports DuckDB, you profile any of these files by loading them into a DuckDB database as tables, then profiling that database. No separate tooling or per-format handling is needed.

1. Load the files into a DuckDB database
2. Profile the DuckDB database

## Enriching Table And Column Descriptions

db-snooper emits the raw schema and data profile. Turn it into concise, accurate short descriptions of each table and column by drawing on any extra context that is available:

- **Source code that queries the data** (ORM models, repositories, query files): infer what each table and column means and how it is used.
- **Table/column descriptions, data dictionaries, or an ontology**: adopt the documented names and definitions.
- **Example or gold queries**: learn the real join paths and the columns that matter for common questions.
- **Chat logs or natural-language questions about the data**: capture how users actually refer to tables and fields.

When a profile for the same database already exists (a previously generated `<database>/<schema>.md`), read it first and carry over its table/column descriptions and field notes, then refine them with the freshly profiled data instead of starting from scratch.

## Safety And Performance

- Prefer a read-only database user.
- Run against production during low-load windows.
- Use `--include-tables` to narrow large databases.
- Review generated files before sending them to external services.
- Remember that redaction is name-based; do not assume every sensitive value is automatically removed.
