# DB Snooper

DB Snooper generates compact, LLM-ready database context for SQL generation, query debugging, and schema exploration.

It inspects an existing database and produces two useful artifacts:

- A SQL profile file with DDL, row counts, sampled small tables, and per-column summaries.
- A Markdown schema-link report with declared PK/FK relationships and inferred join candidates.

This is useful when an AI agent, coding assistant, or text-to-SQL pipeline needs reliable database context without dumping the whole database. Instead of guessing table meanings or join paths, the agent can read the generated profile and link report before writing SQL.

## Install

Choose the install path that matches how you want to use DB Snooper.

### As An Agent Skill

Use the bundled skill when you want an AI agent to know when and how to run DB Snooper before generating SQL.

From this repository, register the included `skills/` directory with your agent runtime. For opencode, add this to `opencode.json` or `opencode.jsonc`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "skills": {
    "paths": ["skills"]
  }
}
```

If you installed the CLI, copy the bundled skill into any skills directory you register with your agent:

```bash
db-snooper skill install ./skills
```

Then register that directory with your agent runtime. You can also print the bundled skill path:

```bash
db-snooper skill path
```

The skill file is `skills/db-snooper-context/SKILL.md`. It covers safe credential handling, when to run `profile` and `links`, how to interpret outputs, and how to pass the generated context to a downstream SQL agent.

### As A CLI App

Install the command-line app from this checkout:

```bash
uv tool install .
db-snooper --help
```

Install the database driver extra you need:

```bash
uv tool install '.[postgres]' --reinstall
uv tool install '.[mysql]' --reinstall
uv tool install '.[mariadb]' --reinstall
uv tool install '.[duckdb]' --reinstall
```

If you need multiple drivers in the same CLI install, combine the extras in one command:

```bash
uv tool install '.[postgres,mysql,duckdb]' --reinstall
```

During development, you can run the CLI directly from the repository without installing it globally:

```bash
uv run db-snooper --help
```

### As A Python Library

Install the library from this checkout:

```bash
uv pip install .
```

For editable local development:

```bash
uv pip install -e .
```

Then import the simple API:

```python
from db_snooper import generate_profile, generate_schema_links

database_url = "sqlite:///eval-dataset/superhero/superhero.sqlite"

profile_sql = generate_profile(database_url)
schema_links_md = generate_schema_links(database_url)
```

## Quick Start

Run DB Snooper against the included SQLite sample database:

```bash
uv run db-snooper profile --db-type sqlite --database eval-dataset/superhero/superhero.sqlite
uv run db-snooper links --db-type sqlite --database eval-dataset/superhero/superhero.sqlite
```

This creates:

- `superhero_profile.sql`
- `superhero_schema_links.md`

If you installed DB Snooper as a CLI app, use `db-snooper` instead of `uv run db-snooper`.

## What The Outputs Contain

The profile `.sql` file contains:

- Metadata with db-snooper version, SQL dialect, database name, and a password-hidden URL.
- `CREATE TABLE` DDL, indexes, and constraints.
- Total row counts.
- Deterministic sampled rows for small tables.
- Per-column null, non-null, distinct, numeric range, median, top-value, and shape summaries for larger tables.
- Redacted values for sensitive column names containing `password`, `passwd`, `pwd`, `hash`, `salt`, `secret`, or `token`.

The schema links `.md` file contains:

- Declared primary-key and foreign-key links from database constraints.
- Inferred links from name, type, cardinality, and containment evidence.
- Evidence labels for each inferred join candidate.

Treat inferred links as candidates, not guaranteed joins. Validate them against the user question and the generated profile before writing final SQL.

## Database Examples

### SQLite

```bash
db-snooper profile --db-type sqlite --database path/to/app.sqlite
db-snooper links --db-type sqlite --database path/to/app.sqlite
```

### PostgreSQL

Install the PostgreSQL extra first:

```bash
uv tool install '.[postgres]' --reinstall
```

Then connect with flags or environment variables:

```bash
db-snooper profile --db-type postgres --database app_db --user readonly_user --host localhost --ask-password
db-snooper links --db-type postgres --database app_db --user readonly_user --host localhost --ask-password
```

### MySQL

```bash
uv tool install '.[mysql]' --reinstall
db-snooper profile --db-type mysql --database app_db --user readonly_user --host localhost --ask-password
db-snooper links --db-type mysql --database app_db --user readonly_user --host localhost --ask-password
```

### MariaDB

```bash
uv tool install '.[mariadb]' --reinstall
db-snooper profile --db-type mariadb --database app_db --user readonly_user --host localhost --ask-password
db-snooper links --db-type mariadb --database app_db --user readonly_user --host localhost --ask-password
```

### DuckDB

```bash
uv tool install '.[duckdb]' --reinstall
db-snooper profile --db-type duckdb --database warehouse.duckdb
db-snooper links --db-type duckdb --database warehouse.duckdb
```

## Environment Variables

Connection values can come from environment variables instead of flags:

```bash
DB_SNOOPER_DB_TYPE=sqlite \
DB_SNOOPER_DATABASE=eval-dataset/student_club/student_club.sqlite \
db-snooper profile
```

Supported variables:

- `DB_SNOOPER_DB_TYPE`
- `DB_SNOOPER_DATABASE`
- `DB_SNOOPER_DB_HOST`
- `DB_SNOOPER_DB_PORT`
- `DB_SNOOPER_DB_USER`
- `DB_SNOOPER_DB_PASSWORD`

For server databases, `--host` defaults to `localhost`, `--port` defaults to the database default, and DB Snooper securely prompts for a password when `DB_SNOOPER_DB_PASSWORD` is not set.

## Useful Options

Output paths:

```bash
db-snooper profile --db-type sqlite --database app.sqlite --output app_profile.sql
db-snooper links --db-type sqlite --database app.sqlite --output app_schema_links.md
```

Table filters:

```bash
db-snooper profile --db-type sqlite --database app.sqlite --include-tables users,orders,line_items
db-snooper links --db-type sqlite --database app.sqlite --exclude-tables audit_log,temp_imports
```

Profile options:

- `--small-table-threshold 50`: tables with this many rows or fewer are sampled instead of column-profiled.
- `--sample-row-limit 50`: maximum sampled rows for small tables.
- `--include-tables table_a,table_b`: only profile selected tables.
- `--exclude-tables table_c`: skip selected tables.

Schema-link options:

- `--include-tables table_a,table_b`: only inspect selected tables.
- `--exclude-tables table_c`: skip selected tables.
- `--containment-threshold 0.8`: minimum exact containment for inferred links.
- `--max-distinct-values 10000`: maximum distinct values loaded per candidate column.

## Python API

Use the simple helpers when you have a SQLAlchemy URL:

```python
from db_snooper import generate_profile, generate_schema_links

database_url = "sqlite:///eval-dataset/superhero/superhero.sqlite"

profile_sql = generate_profile(database_url)
schema_links_md = generate_schema_links(database_url)
```

Use the lower-level API when you already have a SQLAlchemy engine or need options:

```python
from sqlalchemy import create_engine
from db_snooper import ProfileOptions, SchemaLinkOptions, link_schema, profile_database

engine = create_engine("sqlite:///eval-dataset/superhero/superhero.sqlite")

profile_sql = profile_database(
    engine,
    ProfileOptions(sample_row_limit=25, include_tables=frozenset({"superhero", "publisher"})),
)
schema_links_md = link_schema(
    engine,
    SchemaLinkOptions(containment_threshold=0.9),
)
```

## Safety Notes

- Prefer a read-only database user.
- Run against production databases during low-load windows.
- Use `--include-tables` to narrow large databases.
- Prefer environment variables or secure prompts for passwords.
- Do not paste passwords into prompts, logs, generated files, or issue reports.
- Review generated files before sending them to an external service.
- Redaction is name-based, so do not assume every sensitive value is automatically removed.

## License

The source code in this repository is licensed under the MIT License.

The dataset files included under `eval-dataset/` are derived from [birdsql](https://bird-bench.github.io/) by The BIRD Team, and are used and redistributed under the [Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).

These files retain their original CC BY-SA 4.0 terms. Any derivative works that include these files must also be distributed under CC BY-SA 4.0.
