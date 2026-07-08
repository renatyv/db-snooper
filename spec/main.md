# Problem
To efficiently convert text to analytic SQL queries, LLMs need database schema and data context.

# Ideas

## 1. [Database profiling](profiler.md)
Build a Python script that generates `.sql` profile files for SQLite, MariaDB, MySQL, DuckDB, and PostgreSQL.

## 2. [Schema linking](schema_linking.md)
Use the following techniques to generate a separate `.md` file with potentially useful JOIN paths and notes on how fields from different tables can be combined.

## 3. [Multiple-candidate voting](text_to_sql_pipeline.md)
When a request to generate SQL is given, generate three candidate queries for each question. Introduce variety by changing the LLM's randomization seed and the order of the schema fields in the prompt.

# Evals
Use `eval-dataset/eval.jsonl` to verify that the profiler works:
1. Load the corresponding SQLite database.
2. Generate the profile with the script.
3. Generate SQL from the query in a subagent with the generated profile in the context.
4. Compare the SQL to the `gold` query: both the SQL text and the resulting data.


## Implementation
This can be automated using [python implementation](python_impl.md)
