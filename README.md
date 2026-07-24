# DB Snooper

[![PyPI](https://img.shields.io/pypi/v/db-snooper.svg)](https://pypi.org/project/db-snooper/)
[![Python](https://img.shields.io/pypi/pyversions/db-snooper.svg)](https://pypi.org/project/db-snooper/)

DB Snooper generates compact, LLM-ready database context for SQL generation, query debugging, and schema exploration. Profiling alone drives state-of-the-art text-to-SQL accuracy ([Automatic Metadata Extraction for Text-to-SQL](https://arxiv.org/abs/2505.19988)). Supports SQLite, PostgreSQL, MySQL, MariaDB, and DuckDB. Requires Python ≥ 3.10.

Specification: see [`spec/main.md`](spec/main.md) for the design notes behind profiling, schema linking, and the text-to-SQL pipeline.

It inspects an existing database and produces two artifacts:

- A SQL profile (`<database>/<schema>.sql`): DDL, row counts, sampled rows, and per-column summaries. Use `--per-table` for one `.sql` per table.
- A schema-link report (`<database>/<schema>_schema_links.md`): declared PK/FK relationships and inferred join candidates.

AI agents and text-to-SQL pipelines can read this context instead of guessing table meanings or join paths.

## Quick Start

Install with pip:
```bash
pip install db-snooper
```

Or run instantly with `uvx` (no install needed):
```bash
uvx db-snooper profile --db-type mysql --user user --password password --database db --schema sch --port 3306
```

This creates a profile at `db/sch.sql`. To (re)generate just the schema-link report for the same database:

```bash
db-snooper links --db-type mysql --user user --password password --database db --schema sch --port 3306
```

The schema-link report lists declared PK/FK joins and inferred join candidates with evidence labels. See [What The Outputs Contain](#what-the-outputs-contain) for details.

## What The Outputs Contain

The profile `.sql` file contains:

- Metadata with db-snooper version, UTC generation timestamp, SQL dialect, database name, and schema.
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
Profile
```bash
db-snooper profile --db-type postgres --database app_db --schema sch --user readonly_user --host localhost --port 5432 --ask-password
```

Schema links
```bash
db-snooper links --db-type postgres --database app_db --schema sch  --user readonly_user --host localhost --port 5432 --ask-password
```

### MySQL
```bash
db-snooper profile --db-type mysql --database app_db --user readonly_user --host localhost --port 3306 --ask-password
db-snooper links --db-type mysql --database app_db --user readonly_user --host localhost --port 3306 --ask-password
```

### MariaDB
```bash
db-snooper profile --db-type mariadb --database app_db --user readonly_user --host localhost --port 3306 --ask-password
db-snooper links --db-type mariadb --database app_db --user readonly_user --host localhost --port 3306 --ask-password
```

### DuckDB
```bash
db-snooper profile --db-type duckdb --database warehouse.duckdb --schema sch
db-snooper links --db-type duckdb --database warehouse.duckdb --schema sch
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
- `DB_SNOOPER_SCHEMA`

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

Schema filter:

```bash
db-snooper profile --db-type postgres --database app_db --schema reporting --user readonly_user --port 5432 --ask-password
DB_SNOOPER_SCHEMA=reporting db-snooper links --db-type postgres --database app_db --user readonly_user --port 5432 --ask-password
```

Profile options:

- `--small-table-threshold 50`: tables with this many rows or fewer are sampled instead of column-profiled.
- `--large-table-threshold 100000000`: tables whose catalog row estimate is at/above this count are profiled from internal database stats only. `COUNT(*)`, sampled rows, and per-column queries are skipped because they would be too slow on hundreds of millions of rows; the output shows an approximate row count instead.
- `--sample-row-limit 50`: maximum sampled rows for small tables.
- `--include-tables table_a,table_b`: only profile selected tables.
- `--exclude-tables table_c`: skip selected tables.
- `--per-table`: generate one `.sql` profile for each table instead of a single schema profile.

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
