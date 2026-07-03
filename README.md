## DB Snooper

Snoop through databases and generate compact LLM-ready SQL context.

The `profile` command generates a `.sql` profile containing DDL, row counts, sampled small tables, and per-column data profiles.

Install dependencies with uv:

```bash
uv sync --extra dev
```

Install as a Python package from this checkout:

```bash
uv pip install -e .
```

Build a distributable package:

```bash
uv build
```

Import from Python:

```python
from db_snooper import generate_profile, generate_schema_links

database_url = "sqlite:///eval-dataset/superhero/superhero.sqlite"

profile_sql = generate_profile(database_url)
schema_links_md = generate_schema_links(database_url)
```

For advanced use, pass a SQLAlchemy engine and options:

```python
from sqlalchemy import create_engine
from db_snooper import ProfileOptions, SchemaLinkOptions, link_schema, profile_database

engine = create_engine("sqlite:///eval-dataset/superhero/superhero.sqlite")

profile_sql = profile_database(engine, ProfileOptions(sample_row_limit=25))
schema_links_md = link_schema(engine, SchemaLinkOptions(containment_threshold=0.9))
```

SQLite example:

```bash
uv run db-snooper profile --db-type sqlite --database eval-dataset/superhero/superhero.sqlite
```

PostgreSQL example:

```bash
uv sync --extra postgres
uv run db-snooper profile --db-type postgres --database dbname --user user
```

MySQL example:

```bash
uv sync --extra mysql
uv run db-snooper profile --db-type mysql --database dbname --user user
```

MariaDB example:

```bash
uv sync --extra mariadb
uv run db-snooper profile --db-type mariadb --database dbname --user user
```

DuckDB example:

```bash
uv sync --extra duckdb
uv run db-snooper profile --db-type duckdb --database warehouse.duckdb
```

Connection values can also come from environment variables:

```bash
DB_SNOOPER_DB_TYPE=sqlite \
DB_SNOOPER_DATABASE=eval-dataset/student_club/student_club.sqlite \
uv run db-snooper profile
```

For server databases, `--host` defaults to `localhost`, `--port` defaults to the database default (`5432` for PostgreSQL and `3306` for MySQL/MariaDB), and the command prompts securely for the password when `DB_SNOOPER_DB_PASSWORD` is not set:

```bash
DB_SNOOPER_DB_TYPE=postgres \
DB_SNOOPER_DATABASE=dbname \
DB_SNOOPER_DB_USER=user \
DB_SNOOPER_DB_PASSWORD=password \
uv run db-snooper profile
```

By default, `profile` writes to `<database>_profile.sql`, such as `superhero_profile.sql` or `dbname_profile.sql`. Pass `--output` to choose a different path.

Useful options:

- `--small-table-threshold 50`: tables with this many rows or fewer are sampled instead of column-profiled.
- `--sample-row-limit 50`: maximum sampled rows for small tables.
- `--include-tables table_a,table_b`: only profile selected tables.
- `--exclude-tables table_c`: skip selected tables.

Sensitive columns whose names contain `password`, `passwd`, `pwd`, `hash`, `salt`, `secret`, or `token` are redacted in sampled rows and do not emit value profiles.

## Schema Links

The `links` command generates a `.md` file containing declared PK/FK links and inferred join candidates.

SQLite example:

```bash
uv run db-snooper links --db-type sqlite --database eval-dataset/superhero/superhero.sqlite
```

Environment variable example:

```bash
DB_SNOOPER_DB_TYPE=sqlite \
DB_SNOOPER_DATABASE=eval-dataset/student_club/student_club.sqlite \
uv run db-snooper links
```

By default, `links` writes to `<database>_schema_links.md`, such as `superhero_schema_links.md` or `dbname_schema_links.md`. Pass `--output` to choose a different path.

Useful options:

- `--include-tables table_a,table_b`: only inspect selected tables.
- `--exclude-tables table_c`: skip selected tables.
- `--containment-threshold 0.8`: minimum exact containment for inferred links.
- `--max-distinct-values 100000`: maximum distinct values loaded per candidate column.

## License

The source code in this repository is licensed under the [MIT License](LICENSE).

The dataset files included under `data/` are derived from
[birdsql](https://bird-bench.github.io/)
by The BIRD Team, and are used and redistributed under the
[Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).

These files retain their original CC BY-SA 4.0 terms. Any derivative works
that include these files must also be distributed under CC BY-SA 4.0.
