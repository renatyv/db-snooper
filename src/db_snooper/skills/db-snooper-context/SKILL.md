---
name: db-snooper-context
description: Use when an AI agent needs database profiling, schema linking, join discovery, or LLM-ready SQL context for text-to-SQL, query generation, query debugging, or schema exploration with db-snooper.
compatibility: opencode, OpenWork, PI, Claude, ChatGPT, custom agent runners
---

# DB Snooper Context

Use this skill to generate compact, LLM-ready database context before writing or reviewing SQL. It runs `db-snooper profile` to produce a `.sql` schema and data profile, then runs `db-snooper links` to produce a Markdown report of declared and inferred schema links.

For single-purpose tasks, use the focused sibling skills: `db-snooper-profile` (schema/data profiling only) or `db-snooper-schema-links` (join-path discovery only). This umbrella skill runs both in one pass.

## When To Use

- Use when the user asks for database profiling, schema links, table summaries, join candidates, text-to-SQL context, or SQL generation against an existing database.
- Use before asking another agent to generate SQL from natural language.
- Use when debugging a query and the table/column meanings or join paths are unclear.
- Do not use this as a full data export tool.
- Do not perform destructive database operations.

## Connection And Options

db-snooper supports SQLite, PostgreSQL, MySQL, MariaDB, and DuckDB (all drivers ship with the base install; no extra is needed).

Run db-snooper with `uvx` (no install needed). PostgreSQL example:

```bash
uvx db-snooper profile --db-type postgres --database app_db --user readonly_user --host localhost --port 5432 --ask-password
uvx db-snooper links   --db-type postgres --database app_db --user readonly_user --host localhost --port 5432 --ask-password
```

See every flag and its default — connection details, `--schema`, table filters, thresholds, `--per-table`, `--output`, and the `DB_SNOOPER_*` environment-variable fallbacks — with:

```bash
uvx db-snooper -h
uvx db-snooper profile -h
uvx db-snooper links -h
```

Run the profiler first, then the linker. For frequent use, install once with `uv tool install db-snooper` and run `db-snooper ...` directly.

## Enriching Table And Column Descriptions

db-snooper emits the raw schema, data profile, and join report. Turn these into concise, accurate short descriptions of each table and column by drawing on any extra context that is available:

- **Source code that queries the data** (ORM models, repositories, query files): infer what each table and column means and how it is used.
- **Table/column descriptions, data dictionaries, or an ontology**: adopt the documented names and definitions.
- **Example or gold queries**: learn the real join paths and the columns that matter for common questions.
- **Chat logs or natural-language questions about the data**: capture how users actually refer to tables and fields.

When a profile for the same database already exists (a previously generated `<database>/<schema>.sql`), read it first and carry over its table/column descriptions and field notes, then refine them with the freshly profiled data instead of starting from scratch.

Treat inferred links as candidates, not guaranteed joins. Validate them against the user question and the generated profile before writing final SQL.

## Downstream SQL Agent Prompt

Use this prompt pattern when handing the generated context to another agent:

```text
You are generating SQL for this database. First read the attached/generated database profile and schema-link report.

Required context:
- Profile: <database>/<schema>.sql (or `<database>/<schema>/<table>.sql` with `--per-table`)
- Schema links: <database>/<schema>_schema_links.md

Rules:
- Use only tables and columns present in the profile.
- Prefer declared PK/FK links over inferred links.
- Use inferred links only when their evidence fits the user question.
- Do not guess columns that are absent from the profile.
- Explain which tables, columns, and links the query uses.
- Add a LIMIT for exploratory SELECT queries unless the user asks for a complete result.
```

## Safety And Performance

- Prefer a read-only database user.
- Run against production during low-load windows.
- Use `--include-tables` to narrow large databases.
- Increase `--containment-threshold` to reduce noisy inferred links.
- Lower `--max-distinct-values` to cap memory and database load.
- Review generated files before sending them to external services.
- Remember that redaction is name-based; do not assume every sensitive value is automatically removed.
