# How profiler should work

For each table:
1. Generate `CREATE TABLE` DDL with all indexes and constraints.
2. Gererate data profile.
- a. if a table has fewer than 50 rows, include rows up to a small deterministic cap; never dump values for sensitive fields. Treat column names containing password, passwd, pwd, hash, salt, secret, or token as sensitive and redact sampled rows and value profiles;
- b. if a table more than 50 rows, include number of rows. Generate per-column profiles:
    - if a column is all NULL, emit a one-line `all NULL` summary;
    - if a column is a unique identifier, omit top values and value-shape metadata;
    - if a column has fewer than 20 distinct values, include all non-sensitive values. Otherwise, per-column:
    - NULL and non-NULL counts
    - distinct value count
    - min, max, and median for numeric columns;
    - top 10 most frequent values with counts when they are informative;
    - value shape only when it adds meaningful information and does not duplicate type/DDL metadata.
3. LLM-summariazation: A short summary (minimal profile) identifies the meaning and format of a field and a table. If source code is available, us it to produce better summaries


# technicals
- Threads can be used to increase profilers performance. Don't use too many to not overload DB

