# Problem

To efficiently convert text to analytic SQL queries, LLMs need database schema and data context.

# How the Profiler Should Work

For each database create a separate folder with subfolders for each of the schemas.

Generate a single `db_/schema.md` profile per schema by default. When requested with `--per-table`, generate separate files `db_/schema/table.md`.

For each table:
1. Skip empty tables. A table with zero rows carries no data context, so it is excluded from the profile by default. The skipped names are listed once in a trailing summary bullet, e.g. `- Skipped 2 empty table(s): foo, bar`. Force their inclusion with `--include-empty-tables`; an included empty table emits only its `CREATE TABLE` DDL (and an empty `all rows` marker), with no rows or column profiles (there is nothing to profile).
2. Generate `CREATE TABLE` DDL with all indexes and constraints, normalized to drop engine-specific noise: strip `DEFAULT NULL` (a no-op for nullable columns), `ENGINE=…`, `DEFAULT CHARSET=…` / `CHARACTER SET …`, `COLLATE …` / `COLLATION=…`, and generated index/constraint names that carry no meaning. Preserve primary keys, foreign keys, `UNIQUE` constraints, and the list of columns covered by each index. Omit the DDL when the table is small enough that every row is dumped below (the "all rows" case in step 3): the row data already exposes columns, types, and constraints, so the DDL is redundant. The DDL is still emitted for larger tables, for included empty tables, and for catalog-profiled huge tables.
3. Generate a data profile.
   - Use query timouts to prevent hanging queries. If a query runs for 10s or more -> abort the query and skip this metric
   - Use internal database stats to estimate number of rows. If its hundreds of millions or more -> use the internal stats to generate profile, don't run any queries. Instead, summarize each column from the engine's catalog statistics (PostgreSQL `pg_stats`, MySQL `COLUMN_STATISTICS` histograms, MariaDB `mysql.column_stats`): approximate null fraction, distinct count, numeric min/max, and top values. Mark these estimates with `≈` and a `(from db stats)` tag so they are distinguishable from exact metrics.
   - If a table has fewer than 10 rows, dump every row (the CREATE TABLE is omitted, since the rows expose the schema). Never dump values for sensitive fields. Treat column names containing `password`, `passwd`, `pwd`, `hash`, `salt`, `secret`, or `token` as sensitive, and redact sampled rows and value profiles.
   - If a table has more than 10 rows, include the number of rows, 1 latest row, and 2 random ones. Also generate per-column profiles:
     - If a column is all `NULL`, emit a one-line `all NULL` summary.
     - If a column is a unique identifier, omit top values and value-shape metadata.
     - If a column has fewer than 20 distinct values, emit the full histogram inline as `value=count` pairs directly on the column line, followed by `nulls=N` (and `non_nulls=N` when informative), e.g. `- COMM_REQ_ATTRIBUTE: CIM=94, nulls=9906` or `- status: open=30, closed=20, pending=10, nulls=2`. Omit the separate `N distinct` / null-count line — the histogram already conveys the distribution. When every value is already listed, no value-shape tag is emitted (it would just repeat the obvious).
     - For high-cardinality string columns whose individual values are not all listed, append a single `shape=<shape>` tag to the column summary when one shape (e.g. `email`, `phone`, `date-like`, `UPPER+digits`) dominates the sampled top values; otherwise omit it.
     - If n_rows >= 20, include per-column profile data:
       - `NULL` and non-`NULL` counts. If n_rows > 5M, then compute it only if column is indexed
       - Min, max for numeric columns. If n_rows > 5M, then compute it only if column is indexed
       - average for numeric columns. If n_rows > 1M, then compute it only if column is indexed. If 1M < n_rows <= 10M, compute only if indexed. If n_rows > 10M, skip. Skip entirely when a full histogram is available (a low-cardinality column whose every value and count is already known): the counts are the precise distribution, so the average would only restate it.
       - Median for numeric columns if number of n_rows < 100_000. Use native PERCENTILE_CONT for Postgres & mariadb, while MySQL needs ROW_NUMBER()/NTILE() over a full sort. Skip entirely when a full histogram is available, for the same reason as the average.
       - Distinct value count. n_rows ≤ 100K: exact, COUNT(DISTINCT col); n_rows > 100K and ≤ 1M: exact, only if indexed; n_rows > 1M: don't run
       - Top 10 most frequent values with counts when they are informative. Only if n_rows <= 100K and indexed. n_rows > 100K and indexed - read most_common_vals/most_common_freqs from pg_stats, MySQL `COLUMN_STATISTICS` histogram buckets, or MariaDB `mysql.column_stats` (JSON_HB singletons), if present. rows > 100K and unindexed, or no catalog stats available: skip.
      - Catalog fallback for skipped metrics: when an exact null/non-null count, min/max, or distinct count is skipped because a column is unindexed and the table exceeds the row-count thresholds, fall back to the same catalog statistics and emit a labeled estimate (`nulls≈`, `non_nulls≈`, `min≈`, `max≈`, `distinct≈`). This applies on PostgreSQL, MySQL, and MariaDB where catalog stats are available.
3. LLM summarization (done separately): A short summary, or minimal profile, identifies the meaning and format of each field and table. If source code is available, use it to produce better summaries.

## Reliability

- Don't crash on exceptions, just skip the metric.
- JSON doesn't support `COUNT(distinct)`. Some other columns can't do that either. Think what we can quickly profile from these types. The number of elements for an array, all possible keys for JSON,...
- When profiling JSON/JSONB, you need to provide reasonable gates so that requests don't hang if the JSON data stored is too large or if there are too many of them.
- Migration frameworks for Java, Python, Ruby on Rails, and PHP almost always have standard table names. You should at least use these names and not profile these tables. Also, skip other technical tables used in web frameworks in Java, Python, Ruby, Typescript, PHP,...
- Postgres supports fast sampling with `SELECT avg(col), stddev(col) FROM mytable TABLESAMPLE SYSTEM (1);`. Some other databases too. Use it when there are too many rows for appropriate metrics.

## Result example

````markdown
# batch_box_association

```sql
CREATE TABLE dive_sim.batch_box_association (
    batch_id BIGINT NOT NULL,
    box_id BIGINT NOT NULL,
    PRIMARY KEY (batch_id, box_id),
    FOREIGN KEY(batch_id) REFERENCES dive_sim.batch (id) ON DELETE CASCADE ON UPDATE RESTRICT,
    FOREIGN KEY(box_id) REFERENCES dive_sim.box (id) ON DELETE CASCADE ON UPDATE RESTRICT
);
```

## Indexes

- (box_id)
- (batch_id, box_id) WHERE box_id > 12

## Rows

- total=392

| column | latest | sample | sample |
|---|---|---|---|
| batch_id | 215 | 12 | 1124 |
| box_id | 32000246 | 17000123 | 17000001 |

## Columns

- batch_id: 176 distinct, int 5..214
  - top_values: 204=22, 143=8, 147=8, 198=8, 141=7, 60=6, 67=6, 73=6, 169=6, 170=6
- box_id: 175 distinct, int 17000038..32005989
  - top_values: 17000231=17, 17000217=16, 32000019=14, 17000247=13, 32000480=12, 32000121=9, 32001095=7, 32001155=7, 32000057=6, 32001162=6

# batch_port

## All rows

| column | row 1 | row 2 | row 3 | row 4 | row 5 | row 6 | row 7 |
|---|---|---|---|---|---|---|---|
| id | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
| batch_id | 12 | 12 | 15 | 16 | 17 | 20 | 20 |
| port_short_id | 1 | 2 | 1 | 2 | 2 | 1 | 2 |

```

## Implementation
This can be automated using [python implementation](python_impl.md)
