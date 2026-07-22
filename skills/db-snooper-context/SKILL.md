---
name: db-snooper-context
description: Use when an AI agent needs database profiling, schema linking, join discovery, or LLM-ready SQL context for text-to-SQL, query generation, query debugging, or schema exploration with db-snooper.
compatibility: opencode, OpenWork, PI, Claude, ChatGPT, custom agent runners
---

# DB Snooper Context

Use this skill to generate compact, LLM-ready database context before writing or reviewing SQL. It runs `db-snooper profile` to produce a `.sql` schema and data profile, then runs `db-snooper links` to produce a Markdown report of declared and inferred schema links.

## When To Use

- Use when the user asks for database profiling, schema links, table summaries, join candidates, text-to-SQL context, or SQL generation against an existing database.
- Use before asking another agent to generate SQL from natural language.
- Use when debugging a query and the table/column meanings or join paths are unclear.
- Do not use this as a full data export tool.
- Do not perform destructive database operations.

## Inputs To Gather

- Database type: `sqlite`, `postgres`, `mysql`, `mariadb`, or `duckdb`.
- Database name or file path.
- Optional server connection details: host, port, user, and password.
- Optional table filters: `--include-tables` and `--exclude-tables`.
- Optional schema filter: `--schema` or `DB_SNOOPER_SCHEMA`.
- Optional output directory for the generated profile and schema links.

Prefer environment variables or secure prompts for passwords. Do not print passwords in logs, prompts, generated files, or summaries.

Supported environment variables:

- `DB_SNOOPER_DB_TYPE`
- `DB_SNOOPER_DATABASE`
- `DB_SNOOPER_DB_HOST`
- `DB_SNOOPER_DB_PORT`
- `DB_SNOOPER_DB_USER`
- `DB_SNOOPER_DB_PASSWORD`
- `DB_SNOOPER_SCHEMA`

## Workflow

1. Use `db-snooper` directly if it is installed as a CLI app, or use `uv run db-snooper` from the repository checkout.
2. For server databases, install the relevant driver extra: `postgres`, `mysql`, `mariadb`, or `duckdb`.
3. Run the profiler first.
4. Run schema linking second.
5. Inspect the outputs before using or sharing them.
6. If available, use the source code to make short descriptions of tables and fields.
7. Feed both generated files to the SQL-generation agent as required context.

If profile was already generated recently, re-use it instead of re-generating on every skill use.

## CLI Recipes

SQLite examples:

```bash
db-snooper profile --db-type sqlite --database eval-dataset/superhero/superhero.sqlite
db-snooper links --db-type sqlite --database eval-dataset/superhero/superhero.sqlite
db-snooper profile --db-type sqlite --database eval-dataset/superhero/superhero.sqlite --output superhero_context
db-snooper links --db-type sqlite --database eval-dataset/superhero/superhero.sqlite --output superhero_context
```
