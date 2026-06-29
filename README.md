# ai-sql-context

Generate compact `.sql` context files that help LLMs write analytic SQL against an existing database.

The first implementation targets MariaDB/MySQL. It extracts native `CREATE TABLE` DDL, row counts, column profiles, enum-like values, top values, numeric ranges, value shapes, declared foreign keys, and simple likely join hints.

## Install

```bash
uv sync
```

## Generate Context

Using environment variables is recommended for credentials:

```bash
export DB_DIALECT=mysql
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=dive_sim
export DB_USER=dive_simmer
export DB_PASSWORD='your-password'

uv run ai-sql-context profile --output context/dive_sim.sql
```

Equivalent explicit flags:

```bash
uv run ai-sql-context profile \
  --dialect mysql \
  --host localhost \
  --port 3306 \
  --database dive_sim \
  --user dive_simmer \
  --password-env DB_PASSWORD \
  --output context/dive_sim.sql
```

Useful options:

```bash
uv run ai-sql-context profile --help
```

## Validation

After generating `context/dive_sim.sql`, use it as the only database context for a fresh agent and ask the prompts in:

- `docs/evals/1.txt`
- `docs/evals/2.txt`

The generated context should expose the relevant tables and relationships, especially `action_history`, `action_status_history`, `robot_state_history`, and `robot`.

## Tests

```bash
uv run pytest
```
