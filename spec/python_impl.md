# Python implementation

- Use Python and SQLAlchemy to make the profiler as database-agnostic as possible. Use pytest for tests.
- Use `uv` to manage dependencies.
- Put sources in `src/` and tests in `test` or `tests`.
- Add a simple README that explains how to run the command. Include examples for SQLite, PostgreSQL, and MariaDB. Use non-native (pure python) connectors if possible to simplify use.

- CLI interface: both profile and schema links.
  - Infer host, login, and password from environment variables and/or CLI arguments.
  - Use sensible defaults: `localhost`, inferred port from database type, prompt for a password if it is not given in the environment, and derive the output profile filename from the database name.
  - Use a progress bar to show how profiling and schema linking are progressing. Consider showing which tables are currently being profiled.
