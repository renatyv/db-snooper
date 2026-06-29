# Problem
To efficiently convert text to analytic SQL queries LLMs need to know a lot about the database and data.

# Ideas

## 1. [Database profiling](profiler.md)
Build a python script that generates `.sql` profile files for SQLite, MariaDB, MySQL, DuckDB, and PostgreSQL.

## 2. [Schema linking](schema_linking.md)
Use the following techniques to generate a separate .md file with ponentially useful paths for JOINs and how fields from different tables can be combined.

## 3. Multiple candidates voting
When a request to generate SQL is given, generate 3 candidate queries for each question. Introduce variety by changing the LLM's randomization seed and the order of the schema fields in the prompt.

# Evals
Use `eval-dataset/eval.jsonl` to verify if profiler works
1. Load corresponding SQLite database
2. Generate the profile using the script
3. Generate SQL from the query in a subagent with generated profile in the context
4. Compare the SQL to the `gold`: both SQL queries themselves and the resulting data

# Technical
- use python and SQLAlchemy to make profiler as DB-agnostic as possible
- use uv to manage dependencies
- add simple readme how to run the cmd. Examples with sqlite, postgres, mariadb. Use native connectors if possible.
- use cli arguments or env variables to pass database, password, login for DB investigation
- use native database connectors when possible
