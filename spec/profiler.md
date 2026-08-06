# Problem
To efficiently convert text to analytic SQL queries, LLMs need database schema and data context.

# How the Profiler Should Work

For each database create a separate folder with subfolders for each of the schemas.

Generate a single `db_/schema.sql` profile per schema by default. When requested with `--per-table`, generate separate files `db_/schema/table.sql`.

For each table:
1. Skip empty tables. A table with zero rows carries no data context, so it is excluded from the profile by default. The skipped names are listed once in a trailing summary line, e.g. `-- Skipped 2 empty table(s): foo, bar`. Force their inclusion with `--include-empty-tables`; an included empty table emits only its `CREATE TABLE` DDL and a `-- total rows=0` line, with no rows or column profiles (there is nothing to profile).
2. Generate `CREATE TABLE` DDL with all indexes and constraints. Omit the DDL when the table is small enough that every row is dumped below (the "all rows" case in step 3): the row data already exposes columns, types, and constraints, so the DDL is redundant. The DDL is still emitted for larger tables, for included empty tables, and for catalog-profiled huge tables.
3. Generate a data profile.
   - Use query timouts to prevent hanging queries. If a query runs for 10s or more -> abort the query and skip this metric
   - Use internal database stats to estimate number of rows. If its hundreds of millions or more -> use the internal stats to generate profile, don't run any queries. Instead, summarize each column from the engine's catalog statistics (PostgreSQL `pg_stats`, MySQL `COLUMN_STATISTICS` histograms, MariaDB `mysql.column_stats`): approximate null fraction, distinct count, numeric min/max, and top values. Mark these estimates with `≈` and a `(from db stats)` tag so they are distinguishable from exact metrics.
   - If a table has fewer than 50 rows, include rows up to a small deterministic cap. Never dump values for sensitive fields. Treat column names containing `password`, `passwd`, `pwd`, `hash`, `salt`, `secret`, or `token` as sensitive, and redact sampled rows and value profiles.
   - If a table has more than 50 rows, include the number of rows, three latest rows, and five random rows. Also generate per-column profiles:
     - If a column is all `NULL`, emit a one-line `all NULL` summary.
     - If a column is a unique identifier, omit top values and value-shape metadata.
     - If a column has fewer than 20 distinct values, include all non-sensitive values; when every value is already listed, no value-shape tag is emitted (it would just repeat the obvious).
     - For high-cardinality string columns whose individual values are not all listed, append a single `shape=<shape>` tag to the column summary when one shape (e.g. `email`, `phone`, `date-like`, `UPPER+digits`) dominates the sampled top values; otherwise omit it.
     - If n_rows >= 20, include per-column profile data:
       - `NULL` and non-`NULL` counts. If n_rows > 5M, then compute it only if column is indexed
       - Min, max for numeric columns. If n_rows > 5M, then compute it only if column is indexed
       - average for numeric columns. If n_rows > 1M, then compute it only if column is indexed. If 1M < n_rows <= 10M, compute only if indexed. If n_rows > 10M, skip.
       - Median for numeric columns if number of n_rows < 100_000. Use native PERCENTILE_CONT for Postgres & mariadb, while MySQL needs ROW_NUMBER()/NTILE() over a full sort
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

Single profile for a schema `main` in database `dive_sim`

`dive_sim/main.sql`

Each table emits its `CREATE TABLE` DDL followed by its profile. Small tables that dump every row omit the DDL (the rows already expose the schema); empty tables are skipped entirely and listed in a trailing summary.

```SQL
-- db-snooper
-- version: 0.0.1
-- generated_at_utc: 2026-07-22T12:34:56.789012Z
-- dialect: mysql
-- database: dive_sim
-- schema: main

CREATE TABLE `action_status_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_history_id` int(11) NOT NULL,
  `tick` int(11) NOT NULL,
  `time` timestamp(3) NOT NULL,
  `action_status` varchar(255) NOT NULL,
  `state_history_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `action_history_id` (`action_history_id`),
  KEY `state_history_id` (`state_history_id`),
  KEY `action_status_history_time_IDX` (`time`) USING BTREE,
  CONSTRAINT `action_status_history_ibfk_1` FOREIGN KEY (`action_history_id`) REFERENCES `action_history` (`id`),
  CONSTRAINT `action_status_history_ibfk_2` FOREIGN KEY (`state_history_id`) REFERENCES `robot_state_history` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=943812 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=551830
-- action_history_id: nulls=0, non_nulls=551830, distinct=179744
--   numeric: min=362732, median=459736, max=542475
--   top_values: 423373=4, 423378=4, 423383=4, 423384=4, 423386=4, 423387=4, 423388=4, 423391=4, 423392=4, 423395=4
-- action_status: nulls=0, non_nulls=551830, distinct=5
--   values: SCHEDULED=298848, DONE=165650, EXEC=73332, FAILED=12558, FAILED_TIMEOUT=1442
-- id: unique values=551830, range=391982..943811
-- state_history_id: nulls=98520, non_nulls=453310, distinct=453310
--   numeric: min=734084, median=960738, max=1187393
-- tick: nulls=0, non_nulls=551830, distinct=12029
--   numeric: min=1, median=854, max=15446
--   top_values: 1=4069, 2=1772, 3=1463, 10=1133, 4=861, 21=855, 20=852, 15=839, 5=837, 22=834
-- time: nulls=0, non_nulls=551830, distinct=551830


-- blocked_area
-- all rows
-- row: {"id": "40307", "level": "0", "reason": "NOT_IN_USE", "robot_id": "5", "timestamp": "2026-06-25 14:32:42", "x_begin_mm": "1000", "x_end_mm": "1500", "y_begin_mm": "3797", "y_end_mm": "4497"}
-- row: {"id": "40308", "level": "0", "reason": "NOT_IN_USE", "robot_id": "5", "timestamp": "2026-06-25 14:32:42", "x_begin_mm": "1500", "x_end_mm": "1980", "y_begin_mm": "3797", "y_end_mm": "4497"}
```


## Implementation
This can be automated using [python implementation](python_impl.md)
