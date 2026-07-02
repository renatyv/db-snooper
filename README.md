## DB Snooper

Snoop through databases and generate compact LLM-ready SQL context.

The `profile` command generates a `.sql` profile containing DDL, row counts, sampled small tables, and per-column data profiles.

Install dependencies with uv:

```bash
uv sync --extra dev
```

SQLite example:

```bash
uv run db-snooper profile --db-type sqlite --database eval-dataset/superhero/superhero.sqlite --output superhero.profile.sql
```

PostgreSQL example:

```bash
uv sync --extra postgres
uv run db-snooper profile --db-type postgres --host localhost --port 5432 --database dbname --user user --ask-password --output db.profile.sql
```

MySQL example:

```bash
uv sync --extra mysql
uv run db-snooper profile --db-type mysql --host localhost --port 3306 --database dbname --user user --ask-password --output db.profile.sql
```

MariaDB example:

```bash
uv sync --extra mariadb
uv run db-snooper profile --db-type mariadb --host localhost --port 3306 --database dbname --user user --ask-password --output db.profile.sql
```

DuckDB example:

```bash
uv sync --extra duckdb
uv run db-snooper profile --db-type duckdb --database warehouse.duckdb --output warehouse.profile.sql
```

Connection values can also come from environment variables:

```bash
DB_SNOOPER_DB_TYPE=sqlite \
DB_SNOOPER_DATABASE=eval-dataset/student_club/student_club.sqlite \
uv run db-snooper profile --output student_club.profile.sql
```

For server databases, use `DB_SNOOPER_DB_PASSWORD` instead of putting the password in shell history:

```bash
DB_SNOOPER_DB_TYPE=postgres \
DB_SNOOPER_DB_HOST=localhost \
DB_SNOOPER_DB_PORT=5432 \
DB_SNOOPER_DATABASE=dbname \
DB_SNOOPER_DB_USER=user \
DB_SNOOPER_DB_PASSWORD=password \
uv run db-snooper profile --output db.profile.sql
```

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
uv run db-snooper links --db-type sqlite --database eval-dataset/superhero/superhero.sqlite --output superhero.schema_links.md
```

Environment variable example:

```bash
DB_SNOOPER_DB_TYPE=sqlite \
DB_SNOOPER_DATABASE=eval-dataset/student_club/student_club.sqlite \
uv run db-snooper links --output student_club.schema_links.md
```

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
