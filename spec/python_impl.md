# Python implementation

- Use Python and SQLAlchemy to make the profiler as database-agnostic as possible. Use pytest for tests.
- Use `uv` to manage dependencies.
- Put sources in `src/` and tests in `test` or `tests`.
- Add a simple README that explains how to run the command. Include examples for SQLite, PostgreSQL, and MariaDB. Use non-native (pure python) connectors if possible to simplify use.
- If SQLAlchemy's inspection fails, use output of `pg_dump`, `mysqldump`, or `mariadb-dump` to create CREATE_TABLE sequences. Parse their outputs to emit profile in the required format.
- Reuse each engine's built-in column statistics to avoid scanning large tables: a single `ColumnStat` read per table pulls PostgreSQL `pg_stats` (null_frac, n_distinct, histogram_bounds for min/max, most_common_vals/freqs), MySQL `COLUMN_STATISTICS` JSON histograms (singleton + equi-height), and MariaDB `mysql.column_stats` (min_value, max_value, nulls_ratio, avg_frequency, JSON_HB histogram). Detect MariaDB at runtime via `dialect.is_mariadb` (it connects through `mysql+pymysql`, so `dialect.name` is `"mysql"`). These feed the stats-only path for huge tables and labeled (`≈`) fallback estimates for metrics skipped on medium-large tables. Any catalog-read failure collapses to no stats, never a crash; the permission check probes the dialect-appropriate stats table and warns when it is unreadable.

- CLI interface: profile generation.
  - Infer host, login, and password from environment variables and/or CLI arguments.
  - Use sensible defaults: `localhost`, inferred port from database type, prompt for a password if it is not given in the environment, and derive the output profile filename from the database name.
  - Use a progress bar to show how profiling is progressing. Consider showing which tables are currently being profiled.
