Build a script that generates `.sql` context files for MariaDB, MySQL, DuckDB, and PostgreSQL. These files will be used as LLM context for high-quality text-to-SQL generation.

For each table:
1. Generate `CREATE TABLE` DDL with all indexes and constraints.
2. Generate table and column profiles:
* row count;
* NULL and non-NULL counts per column;
* distinct value count per column;
* if the table has fewer than 50 rows, include all rows;
* if a column has fewer than 20 distinct values, include all values;
* min, max, and median for numeric columns;
* top 10 most frequent values with counts;
* value shape: length, character classes, common prefixes, date/JSON/numeric-like formats.
3. Generate LLM-written metadata from the raw profile:
* short column description for schema linking;
* longer column description for final SQL generation;
* include original database comments when available and fuse them with generated metadata.
4. Detect likely joins:
* declared PK/FK constraints;
* columns with overlapping values using sampled value sketches such as MinHash/LSH;
* join paths seen in query logs, including multi-column joins and computed join keys.
5. If a table or column name is unclear, ask the user interactively for its meaning and purpose.

Context generation must support large schemas:
1. Split unrelated or weakly related tables into domains so the full schema is not always loaded.
2. Build a focused context per user question using:
* semantic search over short column descriptions;
* literal matching against sampled column values;
* generated trial SQL queries, then extract referenced tables, columns, and literals.
3. Prefer recall over precision: include slightly too many relevant fields rather than missing required ones.
4. Use short metadata for schema linking and long metadata only for the final selected context.

If query logs are available, extract additional context:
1. parse SQL with a dialect-aware parser such as SQLGlot;
2. resolve fields through aliases, subqueries, and CTEs;
3. extract common joins, predicates, group-bys, named formulas, table sets, and business logic;
4. optionally generate SQL-to-text examples from real queries for few-shot retrieval.

Output files should be deterministic, compact, and grouped by domain or focused context.
