# Problem
To efficiently convert text to analytic SQL queries LLMs need to know a lot about the database and data.

# Ideas

## 1. [Database profiling](profiler.md)
Build a python script that generates `.sql` profile files for MariaDB, MySQL, DuckDB, and PostgreSQL.

## 2. [Schema linking](schema_linking.md)
Use the following techniques to generate a separate .md file with ponentially useful paths for JOINs and how fields from different tables can be combined.

## 3. Multiple candidates voting
When a request to generate SQL is given, generate 3 candidate queries for each question. Introduce variety by changing the LLM's randomization seed and the order of the schema fields in the prompt.

# How test if it works
check the [example](profile_example.sql)

1. Generate file for a local MariaDB database using credentials supplied from environment variables.
2. Create a subagent with empty context, load the generate file into his context, ask to generate queries:
3. use evals `docs/evals/1.txt` and `docs/evals/2.txt` to check if generated queries are correct

# Technical
- Use uv to manage dependencies
- add simple readme how to run the cmd
- use cli arguments or env variables to pass database, password, login for DB investigation
- use native database connectors when possible
