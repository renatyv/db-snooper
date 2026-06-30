## DB Profiler

Generate a `.sql` profile containing DDL, row counts, sampled small tables, and per-column data profiles.

Install dependencies with uv:

```bash
uv sync --extra dev
```

SQLite example:

```bash
uv run ai-sql-profile --url sqlite:///eval-dataset/superhero/superhero.sqlite --output superhero.profile.sql
```

PostgreSQL example:

```bash
uv sync --extra postgres
uv run ai-sql-profile --url 'postgresql+psycopg://user:password@localhost:5432/dbname' --output db.profile.sql
```

MySQL example:

```bash
uv sync --extra mysql
uv run ai-sql-profile --url 'mysql+pymysql://user:password@localhost:3306/dbname' --output db.profile.sql
```

MariaDB example:

```bash
uv sync --extra mariadb
uv run ai-sql-profile --url 'mariadb+mariadbconnector://user:password@localhost:3306/dbname' --output db.profile.sql
```

DuckDB example:

```bash
uv sync --extra duckdb
uv run ai-sql-profile --url 'duckdb:///warehouse.duckdb' --output warehouse.profile.sql
```

You can also pass the URL through `AI_SQL_CONTEXT_DB_URL`:

```bash
AI_SQL_CONTEXT_DB_URL=sqlite:///eval-dataset/student_club/student_club.sqlite uv run ai-sql-profile --output student_club.profile.sql
```

Useful options:

- `--small-table-threshold 50`: tables with this many rows or fewer are sampled instead of column-profiled.
- `--sample-row-limit 50`: maximum sampled rows for small tables.
- `--include-tables table_a,table_b`: only profile selected tables.
- `--exclude-tables table_c`: skip selected tables.

Sensitive columns whose names contain `password`, `passwd`, `pwd`, `hash`, `salt`, `secret`, or `token` are redacted in sampled rows and do not emit value profiles.

## License

The source code in this repository is licensed under the [MIT License](LICENSE).

The dataset files included under `data/` are derived from
[birdsql](https://bird-bench.github.io/)
by The BIRD Team, and are used and redistributed under the
[Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).

These files retain their original CC BY-SA 4.0 terms. Any derivative works
that include these files must also be distributed under CC BY-SA 4.0.
