# Problem
To efficiently convert text to analytic SQL queries LLMs need to know a lot about the database and data.

# Idea
Build a python script that generates `.sql` context files for MariaDB, MySQL, DuckDB, and PostgreSQL.

For each table:
1. Generate `CREATE TABLE` DDL with all indexes and constraints.
2. Generate table and column profiles:
* if the table has fewer than 50 rows, include all rows;
If a column has fewer than 20 distinct values => include all values. Otherwise, per-column:
* NULL and non-NULL counts
* distinct value count
* min, max, and median for numeric columns;
* top 10 most frequent values with counts;
* value shape: length, character classes, common prefixes, date/JSON/numeric-like formats.
3. Detect likely joins:
* declared PK/FK constraints;
* columns with overlapping values using sampled value sketches such as MinHash/LSH;
* join paths seen in query logs, including multi-column joins and computed join keys.
4. If a table or column name is unclear, ask the user interactively for its meaning and purpose.

Context generation must support large schemas:
1. Split unrelated or weakly related tables into domains so the full schema is not always loaded.
2. Build a focused context per user question using:
* semantic search over short column descriptions;
* literal matching against sampled column values;
* generated trial SQL queries, then extract referenced tables, columns, and literals.
3. Prefer recall over precision: include slightly too many relevant fields rather than missing required ones.
4. Use short metadata for schema linking and long metadata only for the final selected context.

Output files should be deterministic, compact, and grouped by domain or focused context.

# How test if it works

1. Generate file for local MariaDB database `dive_sim` with login `dive_simmer` and password `Matrix1Tem9Voce`
2. Create a subagent with empty context, load the generate file into his context, ask to generate queries:
3. use evals `docs/evals/1.txt` and `docs/evals/2.txt` to check if generated queries are correct

# Technical
- Use uv to manage dependencies
- add simple readme how to run the cmd
- use cli arguments or env variables to pass database, password, login for DB investigation
