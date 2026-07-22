# DB Snooper

DB Snooper generates compact, LLM-ready database context for SQL generation, query debugging, and schema exploration.

Specification: see [`spec/main.md`](spec/main.md) for the design notes behind profiling, schema linking, and the text-to-SQL pipeline.

It inspects an existing database and produces two useful artifacts:

- A SQL profile file with DDL, row counts, sampled small tables, and per-column summaries.
- A Markdown schema-link report with declared PK/FK relationships and inferred join candidates.

This is useful when an AI agent, coding assistant, or text-to-SQL pipeline needs reliable database context without dumping the whole database. Instead of guessing table meanings or join paths, the agent can read the generated profile and link report before writing SQL.

## Quick Start

Profile your local MySQL dababase
```bash
 uvx db-snooper profile --db-type mysql --user user --password password --database db
 uvx db-snooper links --db-type mysql --user user --password password --database db
```

This creates:
- `db_profile.sql`
- `db_schema_links.md`

## What The Outputs Contain

The profile `.sql` file contains:

- Metadata with db-snooper version, SQL dialect, database name, and a password-hidden URL.
- `CREATE TABLE` DDL, indexes, and constraints.
- Total row counts.
- Deterministic sampled rows for small tables.
- Latest and random sampled rows for larger tables.
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
```bash
db-snooper profile --db-type postgres --database app_db --user readonly_user --host localhost --ask-password
db-snooper links --db-type postgres --database app_db --user readonly_user --host localhost --ask-password
```

### MySQL
```bash
db-snooper profile --db-type mysql --database app_db --user readonly_user --host localhost --ask-password
db-snooper links --db-type mysql --database app_db --user readonly_user --host localhost --ask-password
```

### MariaDB
```bash
db-snooper profile --db-type mariadb --database app_db --user readonly_user --host localhost --ask-password
db-snooper links --db-type mariadb --database app_db --user readonly_user --host localhost --ask-password
```

### DuckDB
```bash
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

## Help

```bash
db-snooper -h
db-snooper profile -h
db-snooper links -h
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

## License

The DB Snooper source code is licensed under the MIT License. See `LICENCE`.

Third-party Python dependencies remain under their own upstream licenses. See `THIRD_PARTY_NOTICES.md` for a dependency license summary.

The dataset files included under `eval-dataset/` are derived from [birdsql](https://bird-bench.github.io/) by The BIRD Team, and are used and redistributed under the [Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).

These files are not covered by the MIT source-code license. They retain their original CC BY-SA 4.0 terms. Any derivative works that include these files must also be distributed under CC BY-SA 4.0.
