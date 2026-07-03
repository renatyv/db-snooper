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
- Optional output paths for the generated profile and schema links.

Prefer environment variables or secure prompts for passwords. Do not print passwords in logs, prompts, generated files, or summaries.

Supported environment variables:

- `DB_SNOOPER_DB_TYPE`
- `DB_SNOOPER_DATABASE`
- `DB_SNOOPER_DB_HOST`
- `DB_SNOOPER_DB_PORT`
- `DB_SNOOPER_DB_USER`
- `DB_SNOOPER_DB_PASSWORD`

## Workflow

1. Install dependencies if needed with `uv sync --extra dev`.
2. For server databases, install the relevant driver extra: `postgres`, `mysql`, `mariadb`, or `duckdb`.
3. Run the profiler first.
4. Run schema linking second.
5. Inspect the outputs before using or sharing them.
6. Feed both generated files to the SQL-generation agent as required context.

## CLI Recipes

SQLite:

```bash
uv run db-snooper profile --db-type sqlite --database eval-dataset/superhero/superhero.sqlite
uv run db-snooper links --db-type sqlite --database eval-dataset/superhero/superhero.sqlite
```

SQLite with explicit output paths:

```bash
uv run db-snooper profile --db-type sqlite --database eval-dataset/superhero/superhero.sqlite --output superhero_profile.sql
uv run db-snooper links --db-type sqlite --database eval-dataset/superhero/superhero.sqlite --output superhero_schema_links.md
```

Table filters:

```bash
uv run db-snooper profile --db-type sqlite --database app.sqlite --include-tables users,orders,line_items
uv run db-snooper links --db-type sqlite --database app.sqlite --include-tables users,orders,line_items
```

DuckDB:

```bash
uv sync --extra duckdb
uv run db-snooper profile --db-type duckdb --database warehouse.duckdb
uv run db-snooper links --db-type duckdb --database warehouse.duckdb
```

PostgreSQL:

```bash
uv sync --extra postgres
DB_SNOOPER_DB_TYPE=postgres \
DB_SNOOPER_DATABASE=app_db \
DB_SNOOPER_DB_HOST=localhost \
DB_SNOOPER_DB_USER=readonly_user \
uv run db-snooper profile --ask-password
DB_SNOOPER_DB_TYPE=postgres \
DB_SNOOPER_DATABASE=app_db \
DB_SNOOPER_DB_HOST=localhost \
DB_SNOOPER_DB_USER=readonly_user \
uv run db-snooper links --ask-password
```

MySQL:

```bash
uv sync --extra mysql
DB_SNOOPER_DB_TYPE=mysql \
DB_SNOOPER_DATABASE=app_db \
DB_SNOOPER_DB_HOST=localhost \
DB_SNOOPER_DB_USER=readonly_user \
uv run db-snooper profile --ask-password
DB_SNOOPER_DB_TYPE=mysql \
DB_SNOOPER_DATABASE=app_db \
DB_SNOOPER_DB_HOST=localhost \
DB_SNOOPER_DB_USER=readonly_user \
uv run db-snooper links --ask-password
```

MariaDB:

```bash
uv sync --extra mariadb
DB_SNOOPER_DB_TYPE=mariadb \
DB_SNOOPER_DATABASE=app_db \
DB_SNOOPER_DB_HOST=localhost \
DB_SNOOPER_DB_USER=readonly_user \
uv run db-snooper profile --ask-password
DB_SNOOPER_DB_TYPE=mariadb \
DB_SNOOPER_DATABASE=app_db \
DB_SNOOPER_DB_HOST=localhost \
DB_SNOOPER_DB_USER=readonly_user \
uv run db-snooper links --ask-password
```

## Python API Recipes

Simple use:

```python
from db_snooper import generate_profile, generate_schema_links

database_url = "sqlite:///eval-dataset/superhero/superhero.sqlite"

profile_sql = generate_profile(database_url)
schema_links_md = generate_schema_links(database_url)
```

Advanced options:

```python
from sqlalchemy import create_engine
from db_snooper import ProfileOptions, SchemaLinkOptions, link_schema, profile_database

engine = create_engine("sqlite:///eval-dataset/superhero/superhero.sqlite")

profile_sql = profile_database(
    engine,
    ProfileOptions(
        small_table_threshold=50,
        sample_row_limit=25,
        include_tables=frozenset({"superhero", "publisher", "alignment"}),
    ),
)
schema_links_md = link_schema(
    engine,
    SchemaLinkOptions(
        containment_threshold=0.8,
        max_distinct_values=10_000,
    ),
)
```

## How To Read The Outputs

The profile `.sql` file contains:

- Metadata header with db-snooper version, SQL dialect, database, and URL with hidden password.
- `CREATE TABLE` DDL and indexes/constraints.
- Total row counts.
- Deterministic sampled rows for small tables.
- Per-column null, non-null, distinct, numeric range, median, top-value, and shape summaries for larger tables.
- Redacted values for sensitive column names containing `password`, `passwd`, `pwd`, `hash`, `salt`, `secret`, or `token`.

The schema links `.md` file contains:

- Declared PK/FK links from database constraints.
- Inferred links from name/type/cardinality/containment evidence.
- Evidence labels for each inferred join candidate.

Treat inferred links as candidates, not guaranteed joins. Validate them against the user question and the generated profile before writing final SQL.

## Downstream SQL Agent Prompt

Use this prompt pattern when handing the generated context to another agent:

```text
You are generating SQL for this database. First read the attached/generated database profile and schema-link report.

Required context:
- Profile: <path-to-database>_profile.sql
- Schema links: <path-to-database>_schema_links.md

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

## Verification Checklist

Use included databases for smoke verification. Do not add or run unit tests unless the user explicitly asks.

```bash
uv run db-snooper profile --db-type sqlite --database eval-dataset/superhero/superhero.sqlite --output /tmp/superhero_profile.sql
uv run db-snooper links --db-type sqlite --database eval-dataset/superhero/superhero.sqlite --output /tmp/superhero_schema_links.md
```

Confirm:

- The profile file exists and starts with `-- db-snooper`.
- The profile contains `CREATE TABLE` statements and `-- total rows=` summaries.
- The schema-link file exists and starts with `# Schema Links`.
- The schema-link file contains `## Declared PK/FK Links` and `## Inferred Links`.
- The generated files do not contain unexpected secrets before sharing them.
