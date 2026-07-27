---
name: db-snooper-context
description: Use when an AI agent needs database profiling or LLM-ready SQL context for text-to-SQL, query generation, query debugging, or schema exploration with db-snooper.
compatibility: opencode, OpenWork, PI, Claude, ChatGPT, custom agent runners
---

# DB Snooper Context

Use this skill to generate compact, LLM-ready database context before writing or reviewing SQL. It runs `db-snooper profile` to produce a `.sql` schema and data profile.

For join-path discovery (declared PK/FK plus inferred candidates), use the separate `schema-linker` tool and its `schema-linker` skill. For schema/data profiling only, use the focused `db-snooper-profile` sibling skill.

## When To Use

- Use when the user asks for database profiling, table summaries, text-to-SQL context, or SQL generation against an existing database.
- Use before asking another agent to generate SQL from natural language.
- Use when debugging a query and the table/column meanings or formats are unclear.
- Do not use this as a full data export tool.
- Do not perform destructive database operations.

## Connection And Options

db-snooper supports SQLite, PostgreSQL, MySQL, MariaDB, and DuckDB (all drivers ship with the base install; no extra is needed).

Run db-snooper with `uvx` (no install needed). PostgreSQL example:

```bash
uvx db-snooper profile --db-type postgres --database app_db --user readonly_user --host localhost --port 5432 --ask-password
```

See every flag and its default — connection details, `--schema`, table filters, thresholds, `--per-table`, `--output`, and the `DB_SNOOPER_*` environment-variable fallbacks — with:

```bash
uvx db-snooper -h
uvx db-snooper profile -h
```

For frequent use, install once with `uv tool install db-snooper` and run `db-snooper ...` directly.

The generated profile (`<database>/<schema>.sql`) contains `CREATE TABLE` DDL with indexes/constraints, total row counts, sampled rows, and per-column null/distinct/range/median/top-value summaries — sensitive columns are redacted and very large tables use internal stats only.

## Enriching Table And Column Descriptions

db-snooper emits the raw schema and data profile. Turn it into concise, accurate short descriptions of each table and column by drawing on any extra context that is available:

- **Source code that queries the data** (ORM models, repositories, query files): infer what each table and column means and how it is used.
- **Table/column descriptions, data dictionaries, or an ontology**: adopt the documented names and definitions.
- **Example or gold queries**: learn the real join paths and the columns that matter for common questions.
- **Chat logs or natural-language questions about the data**: capture how users actually refer to tables and fields.

When a profile for the same database already exists (a previously generated `<database>/<schema>.sql`), read it first and carry over its table/column descriptions and field notes, then refine them with the freshly profiled data instead of starting from scratch.

## Downstream SQL Agent Prompt

Use this prompt pattern when handing the generated context to another agent:

```text
You are generating SQL for this database. First read the attached/generated database profile.

Required context:
- Profile: <database>/<schema>.sql (or `<database>/<schema>/<table>.sql` with `--per-table`)

Rules:
- Use only tables and columns present in the profile.
- Do not guess columns that are absent from the profile.
- Explain which tables and columns the query uses.
- Add a LIMIT for exploratory SELECT queries unless the user asks for a complete result.
```

## Safety And Performance

- Prefer a read-only database user.
- Run against production during low-load windows.
- Use `--include-tables` to narrow large databases.
- Review generated files before sending them to external services.
- Remember that redaction is name-based; do not assume every sensitive value is automatically removed.
