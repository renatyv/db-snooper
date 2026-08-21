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
- A top-level `Relationships` section listing every foreign key as `- "parent"."col" ← "child"."col"` bullets (composite keys as `"table".("c1", "c2")`), grouped so a parent referenced by many tables appears once as `- "parent"."col" ← "child1"."col", "child2"."col"`. Lines are sorted by parent.
- One compact block per non-empty table, in this fixed layout:
  - A `# "<table>"  (rows=<N>)` header (the count uses the engine's row estimate — `≈N` — when available, otherwise an exact `COUNT(*)`). Table names are delimited identifiers everywhere they appear — headers, `Relationships` bullets, and the skipped-table summaries — for the same reason as column names.
  - A merged `columns:` block — one line per column as `"name" type[ flags]: profile`, so each column's type, flags, and value distribution sit together and the name is printed once. The name is always a delimited identifier (`"Enrollment (K-12)"` — double quotes on PostgreSQL/Oracle/SQLite and any other dialect, backticks on MySQL/MariaDB/BigQuery, square brackets on SQL Server): the delimiter marks where the name ends even when it contains spaces or parentheses, and shows the exact quoting to use when referencing the column in SQL. Flags (emitted only when they apply): `PK`, `UNIQ` (single-column unique), `NOTNULL`, `FK`. Example: `"id" bigserial PK: unique identifier, 1..12592`, `"tick" bigint: 4079 distinct, 1..12592, avg=1944.8`. Numeric ranges omit the `int`/`float`/`numeric` qualifier — the type token already carries it.
  - SQLite declared types are affinity hints, so the profile checks them against the actual storage (`typeof()`): untyped columns resolve to their storage class (`"x" int`, or `"x" int|text` when mixed), and declared↔stored contradictions render as `"qty" numeric→text`. String columns also get a content-shape label — `digits` (compare as strings: leading zeros, lexicographic ordering), `iso-date`, `bool-like`, `uuid`, `numeric` — so numeric- or date-looking text is never mistaken for real numbers/dates: `"County Code" text: digits, 58 distinct`.
  - `indexes:` — parenthesized column lists with delimited names, multi-column indexes keep their order, partial indexes append `WHERE <predicate>`. The primary-key index is not repeated. `none` when there are no non-PK indexes. Foreign keys are not repeated per table — the `Relationships` section is their single home, and the per-column `FK` flag points there.
  - Profiles carry distinct counts, full histograms for low-cardinality columns, null fractions, numeric ranges, average/median, and top values on the column's single line. High-cardinality free-text/JSON/blob columns are annotated `← dropped from samples`.
  - A `samples:` block — a transposed markdown table (one row per column, columns `latest | sample | sample`) showing 1 latest row and 2 random rows for the columns whose concrete values add information.
- Tables with fewer than 10 rows emit `all rows:` (listing every row) in place of `samples:`, with bare `"name" type[ flags]` tokens in their `columns:` block — the dumped rows already expose every value, so profile text would restate them.
- Views and materialized views emit their `CREATE VIEW` DDL (their SELECT definition) in place of the `indexes:` line, followed by the merged `columns:` block.
- Catalog-derived estimates for very large tables (hundreds of millions of rows or more) from each engine's internal statistics — PostgreSQL `pg_stats`, MySQL `COLUMN_STATISTICS` histograms, and MariaDB `mysql.column_stats` — emitted with `≈` markers and a trailing `(from db stats)` tag so they are distinguishable from exact values.
- Top-level key frequencies for JSON/JSONB columns and min/avg/max element counts for ARRAY columns (when row counts allow), rendered as trailing annotations on the column's `columns:` line.
- Redacted values for sensitive column names containing `password`, `passwd`, `pwd`, `hash`, `salt`, `secret`, or `token` — the column's `columns:` line reads `redacted` and it is excluded from samples.
- A `skipped_technical_tables` entry in the frontmatter naming migration/framework tables excluded from the profile.
- Empty tables are skipped by default. A `- Skipped N empty table(s):` bullet names them; the Python API's `ProfileOptions(include_empty_tables=True)` includes them (emitting only the bare per-column type tokens in the `columns:` block, with no profile text or `samples:`).
- A `<schema>.toc.md` sidecar written next to the profile in the same run, indexing every top-level section — `Relationships`, each table block (`"Match" (rows=25979): lines 50-289`), and the trailing summary bullets — with its exact line range. Its frontmatter pins the profile by `profile_sha256` (plus `generator`, `version`, `generated_at_utc`, and `profile_lines`) so consumers can fail fast on a stale TOC instead of reading shifted line ranges. Emitted by default; `--no-toc` disables it, and `--per-table` profiles get none.

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
- `--no-toc`: skip the `<schema>.toc.md` sidecar (emitted by default).
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

To also get the `<profile>.toc.md` sidecar content (write it next to the profile file yourself), use the with-TOC variants:

```python
from db_snooper import generate_profile_with_toc

profile_md, toc_md = generate_profile_with_toc(database_url)
```

`toc_md` is `None` when `ProfileOptions(emit_toc=False)` is set or the profile has no sections to index. `profile_database_with_toc` offers the same pair for an existing engine.

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
