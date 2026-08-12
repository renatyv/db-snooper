# DB Snooper

[![PyPI](https://img.shields.io/pypi/v/db-snooper.svg)](https://pypi.org/project/db-snooper/)
[![Python](https://img.shields.io/pypi/pyversions/db-snooper.svg)](https://pypi.org/project/db-snooper/)

**Agent skill: [`src/db_snooper/skills/SKILL.md`](src/db_snooper/skills/SKILL.md)**

**Spec: [`spec/profiler.md`](spec/profiler.md)**

DB Snooper generates compact, LLM-ready database context for SQL generation, query debugging, and schema exploration. Profiling alone drives state-of-the-art text-to-SQL accuracy ([Automatic Metadata Extraction for Text-to-SQL](https://arxiv.org/abs/2505.19988)). Supports SQLite, PostgreSQL, MySQL, MariaDB, DuckDB, Google BigQuery, and Amazon RDS for PostgreSQL/MySQL/MariaDB. Requires Python ≥ 3.10.

It inspects an existing database and produces a Markdown profile (`<database>/<schema>.md`): DDL, row counts, sampled rows, and per-column summaries. Use `--per-table` for one `.md` per table.

AI agents and text-to-SQL pipelines can read this context instead of guessing table meanings.

## Quick Start

Install with pip:
```bash
pip install db-snooper
```

Or run instantly with `uvx` (no install needed):
```bash
uvx db-snooper profile --db-type mysql --user user --password password --database db --schema sch --port 3306
```

This creates a profile at `db/sch.md`.

## What The Outputs Contain

The profile `.md` file contains:

- Metadata (YAML frontmatter) with db-snooper version, UTC generation timestamp, SQL dialect, database name, and schema.
- A top-level `Relationships` section listing every foreign key as `- parent.col ← child.col` bullets (composite keys as `table.(c1, c2)`), grouped so a parent referenced by many tables appears once as `- parent.col ← child1.col, child2.col`. Lines are sorted by parent.
- One compact block per non-empty table, in this fixed layout:
  - A `# <table>  (rows=<N>)` header (the count uses the engine's row estimate — `≈N` — when available, otherwise an exact `COUNT(*)`).
  - A flattened schema header — three one-liners derived from introspection:
    - `columns:` — one token per column as `name(type[,flags])`. Flags (emitted only when they apply): `PK`, `UNIQ` (single-column unique), `NOTNULL`, `FK`. Example: `id(bigserial,PK), email(varchar255,UNIQ,NOTNULL), user_id(bigint,FK)`.
    - `indexes:` — parenthesized column lists, multi-column indexes keep their order, partial indexes append `WHERE <predicate>`. The primary-key index is not repeated. `none` when there are no non-PK indexes.
    - `fk:` — `col→ref_table.ref_col` (composite FKs as `(c1,c2)→ref_table.(r1,r2)`). `none` when there are none.
  - A `values:` block with one inline line per column — distinct counts, full histograms for low-cardinality columns, null fractions, numeric ranges (`int`/`float`/`numeric min..max`), average/median, and top values all sit on that single line. High-cardinality free-text/JSON/blob columns are annotated `← dropped from samples`.
  - A `samples:` block — a transposed markdown table (one row per column, columns `latest | sample | sample`) showing 1 latest row and 2 random rows for the columns whose concrete values add information.
- Tables with fewer than 10 rows emit `all rows:` (listing every row) in place of `samples:`, and still include a `values:` block when any column has a useful profile.
- Views and materialized views emit their `CREATE VIEW` DDL (their SELECT definition) in place of the flattened header lines.
- Catalog-derived estimates for very large tables (hundreds of millions of rows or more) from each engine's internal statistics — PostgreSQL `pg_stats`, MySQL `COLUMN_STATISTICS` histograms, and MariaDB `mysql.column_stats` — emitted with `≈` markers and a trailing `(from db stats)` tag so they are distinguishable from exact values.
- Top-level key frequencies for JSON/JSONB columns and min/avg/max element counts for ARRAY columns (when row counts allow), rendered as trailing annotations on the column's `values:` line.
- Redacted values for sensitive column names containing `password`, `passwd`, `pwd`, `hash`, `salt`, `secret`, or `token` — the column appears in `values:` with `redacted` and is excluded from samples.
- A `skipped_technical_tables` entry in the frontmatter naming migration/framework tables excluded from the profile.
- Empty tables are skipped by default. A `- Skipped N empty table(s):` bullet names them; the Python API's `ProfileOptions(include_empty_tables=True)` includes them (emitting only the flattened `columns:` line, with no `values:`/`samples:`).

## Database Examples

### SQLite
```bash
db-snooper profile --db-type sqlite --database path/to/app.sqlite
```

### PostgreSQL
Profile
```bash
db-snooper profile --db-type postgres --database app_db --schema sch --user readonly_user --host localhost --port 5432 --ask-password
```

### MySQL
```bash
db-snooper profile --db-type mysql --database app_db --user readonly_user --host localhost --port 3306 --ask-password
```

### MariaDB
```bash
db-snooper profile --db-type mariadb --database app_db --user readonly_user --host localhost --port 3306 --ask-password
```

### Amazon RDS

RDS uses the matching PostgreSQL, MySQL, or MariaDB type. Download the [Amazon RDS CA bundle](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.SSL.html), then connect with a database password:

```bash
db-snooper profile --db-type postgres --database app_db --user readonly_user \
  --host mydb.123456789012.eu-west-1.rds.amazonaws.com --ssl-ca global-bundle.pem --ask-password
```

Or use IAM database authentication with a configured AWS CLI:

```bash
db-snooper profile --db-type postgres --database app_db --user readonly_user \
  --host mydb.123456789012.eu-west-1.rds.amazonaws.com --ssl-ca global-bundle.pem \
  --rds-iam --aws-region eu-west-1
```

### DuckDB
```bash
db-snooper profile --db-type duckdb --database warehouse.duckdb --schema sch
```

### Google BigQuery

Authenticate with [Application Default Credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc), then use the Google Cloud project as the database and the dataset as the schema. BigQuery query charges apply to profiling queries.

```bash
gcloud auth application-default login
db-snooper profile --db-type bigquery --database project-id --schema dataset
```

### Files (Parquet, JSON, CSV, ...) via DuckDB

DuckDB reads many file formats directly (parquet, JSON/JSONL, CSV/TSV, Arrow, Iceberg, ...), so profile a file by loading it into a DuckDB database as a table, then profiling that database.

```bash
duckdb warehouse.duckdb -c "CREATE TABLE sales AS SELECT * FROM read_parquet('sales.parquet')"
db-snooper profile --db-type duckdb --database warehouse.duckdb
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
- `DB_SNOOPER_SSL_CA`
- `DB_SNOOPER_SCHEMA`

For server databases, `--host` defaults to `localhost`, `--port` defaults to the database default, and DB Snooper securely prompts for a password when `DB_SNOOPER_DB_PASSWORD` is not set.

## Help

```bash
db-snooper -h
db-snooper profile -h
```

Table filters:

```bash
db-snooper profile --db-type sqlite --database app.sqlite --include-tables users,orders,line_items
```

Schema filter:

```bash
db-snooper profile --db-type postgres --database app_db --schema reporting --user readonly_user --port 5432 --ask-password
DB_SNOOPER_SCHEMA=reporting db-snooper profile --db-type postgres --database app_db --user readonly_user --port 5432 --ask-password
```

Profile options:

- `--output path`: write profiles to a custom directory.
- `--metadata-only`: emit schema, relationships, row estimates, and available catalog statistics without scanning table rows.
- `--per-table`: generate one `.md` profile for each table instead of a single schema profile.
- `--include-tables table_a,table_b`: only profile selected tables.
- `--exclude-tables table_c`: skip selected tables.
- `--query-timeout 10`: skip individual PostgreSQL/MySQL/MariaDB profiling queries that exceed this many seconds; `0` disables the timeout.
- `--max-bytes-billed 1073741824`: cumulative BigQuery scan budget. Each profiling query is dry-run first and skipped if it would exceed the remaining budget; `0` disables the cap.

Sampling thresholds and edge-case inclusion behavior are available through `ProfileOptions` in the Python API.

## Python API

Use the simple helpers when you have a SQLAlchemy URL:

```python
from db_snooper import generate_profile

database_url = "sqlite:///eval-dataset/superhero/superhero.sqlite"

profile_md = generate_profile(database_url)
```

Use the lower-level API when you already have a SQLAlchemy engine or need options:

```python
from sqlalchemy import create_engine
from db_snooper import ProfileOptions, profile_database

engine = create_engine("sqlite:///eval-dataset/superhero/superhero.sqlite")

profile_md = profile_database(
    engine,
    ProfileOptions(
        small_table_threshold=25,
        include_tables=frozenset({"superhero", "publisher"}),
        include_empty_tables=True,
    ),
)
```

## Agent Skill

DB Snooper bundles [`db-snooper-profile`](src/db_snooper/skills/SKILL.md), an [agent skill](https://opencode.ai/docs/skills/) for generating schema and data context before writing or debugging SQL. It runs `db-snooper profile` and produces `<database>/<schema>.md`.

Install it as a Claude Code plugin:

```text
/plugin marketplace add renatyv/db-snooper
/plugin install db-snooper@db-snooper
```

The skill ships inside the wheel, so you can inspect or install it without cloning this repository:

```bash
uvx db-snooper skills list
uvx db-snooper skills install
uvx db-snooper skills install --target all
uvx db-snooper skills install --dir ./.opencode/skills --force
```

By default, installation targets `~/.config/opencode/skills`. Use `--target` for Claude or agents-compatible directories, or `--dir` for a custom location.

## License

The DB Snooper source code is licensed under the MIT License. See `LICENCE`.

Third-party Python dependencies remain under their own upstream licenses. See `THIRD_PARTY_NOTICES.md` for a dependency license summary.

The dataset files included under `eval-dataset/` are derived from [birdsql](https://bird-bench.github.io/) by The BIRD Team, and are used and redistributed under the [Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).

These files are not covered by the MIT source-code license. They retain their original CC BY-SA 4.0 terms. Any derivative works that include these files must also be distributed under CC BY-SA 4.0.
