---
name: db-snooper-profile
description: "Use when an AI agent needs to generate a database schema and data profile (.md: DDL, row counts, sampled rows, per-column summaries) for text-to-SQL, query planning, schema understanding, data exploration, or data-engineering work (database onboarding, data quality checks, join discovery, profiling raw files) with db-snooper."
compatibility: opencode, OpenWork, PI, Claude, ChatGPT, custom agent runners
---

# DB Snooper Profiling

Use this skill to generate a compact, LLM-ready schema and data profile of an existing database before writing or reviewing SQL. It runs `db-snooper profile` to produce a `.md` artifact containing DDL, indexes/constraints, row counts, sampled rows, and per-column summaries.

## When To Use
- Use for data-engineering work: onboarding to an unfamiliar database, assessing data quality, finding join paths, reviewing a migration's schema changes, or checking what raw files contain before ingesting them.
- Use when the user asks to profile a database, generate schema context, understand table structures, column meanings, data types, or value distributions.
- Use before generating SQL from natural language, so the SQL agent knows the real schema and data shapes.
- Use when debugging a query and the table/column meanings or formats are unclear.
- Use when the data lives in files (parquet, JSON/JSONL, CSV/TSV, Arrow, ...) rather than a database: load them into DuckDB first (see [Profiling Files](#profiling-files-parquet-json-csv-arrow-)), then profile.
- Do not use this as a full data export tool.
- Do not perform destructive database operations.

## Data Engineering Tasks

The profile replaces the dozens of catalog and sampling queries these tasks normally take:

- **Onboarding to an unfamiliar database**: one artifact shows every table's DDL, indexes, constraints, and row counts, plus a `Relationships` section listing every foreign key — the join graph you need before writing ELT jobs or transformation models.
- **Data quality checks**: per-column null fractions, distinct counts, ranges, medians, and top values expose dirty columns, sentinel values, and type confusion. Mixed stored types render as `numeric→text`, and numeric- or date-looking text is labeled `digits` or `iso-date` so it is never mistaken for real numbers/dates.
- **Understanding raw files before ingesting them**: load parquet/CSV/JSON/Arrow into DuckDB and profile to see the schema, row counts, and value distributions before writing any transformation (see [Profiling Files](#profiling-files-parquet-json-csv-arrow-)).
- **Schema drift and migration reviews**: regenerate the profile and diff it against the previous one to see exactly what a migration or deploy changed.
- **Data documentation**: enrich the profile with table/column descriptions (see below) and it doubles as a living data dictionary.

## Connection And Options

db-snooper supports SQLite, PostgreSQL, MySQL, MariaDB, DuckDB, Google BigQuery, and Amazon RDS for PostgreSQL/MySQL/MariaDB (all database drivers ship with the base install; RDS IAM authentication uses the AWS CLI).

Run the profiler with `uvx` (no install needed). PostgreSQL example:

```bash
uvx db-snooper profile --db-type postgres --database app_db --user readonly_user --host localhost --port 5432 --ask-password
```

See every flag and its default — connection details, `--schema`, `--include-tables`/`--exclude-tables`, safety limits, `--per-table`, `--output`, and the `DB_SNOOPER_*` environment-variable fallbacks — with:

```bash
uvx db-snooper -h
uvx db-snooper profile -h
```

For frequent use, install once with `uv tool install db-snooper` and run `db-snooper ...` directly.

The generated profile (`<database>/<schema>.md`) contains `CREATE TABLE` DDL with indexes/constraints, total row counts, sampled rows, and per-column null/distinct/range/median/top-value summaries — sensitive columns are redacted and very large tables use internal stats only. A `<schema>.toc.md` sidecar is written alongside it, indexing every section (relationships, tables, summary) with exact line ranges and the profile's sha256, so specific tables can be read by line range without loading the whole profile. For metered or production databases, use `--metadata-only`; BigQuery scans are capped at 1 GiB by default and can be changed with `--max-bytes-billed`.

## Using The Profile For Text-to-SQL

How the profile reaches the SQL-generating prompt matters as much as generating it:

- When the profile is small, feed the **whole profile** into the prompt verbatim — do not summarize or excerpt it. With the full schema, relationships, and value distributions in context up front, the agent writes correct SQL on the first attempt instead of exploring the schema interactively (listing tables, describing columns, sampling values one round trip at a time). In practice this improves text-to-SQL time-to-answer by roughly **2x**.
- Check the profile's size before deciding. Single-schema applications and marts typically profile to a few KB or tens of KB — feed those whole.
- When the profile is too large to fit the prompt comfortably (large warehouses can produce hundreds of KB), use the `<schema>.toc.md` sidecar to load only the `Relationships` section and the specific table blocks (by line range) that the question touches.

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
