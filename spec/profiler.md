# Problem

To efficiently convert text to analytic SQL queries, LLMs need database schema and data context.

# How the Profiler Should Work

For each database create a separate folder with subfolders for each of the schemas.

Generate a single `db_/schema.md` profile per schema by default. When requested with `--per-table`, generate separate files `db_/schema/table.md`.

The profile is written in a **compact one-block-per-table** format (see [Output format](#output-format)). Every table renders its schema and per-column value profiles in one merged `columns:` block, plus row samples, in a single contiguous block of roughly 15–30 lines regardless of column count. The historical `CREATE TABLE` DDL block, the separate `## Indexes` / `## Rows` / `## Columns` sections, and the transposed all-rows table are all superseded by this format.

For each table:
1. Skip empty tables. A table with zero rows carries no data context, so it is excluded from the profile by default. The skipped names are listed once in a trailing summary bullet, e.g. `- Skipped 2 empty table(s): "foo", "bar"`. `ProfileOptions(include_empty_tables=True)` forces their inclusion; an included empty table emits only the bare per-column type tokens in the `columns:` block (and an empty `all rows` marker), with no profile text or `samples:` block (there is nothing to profile).
2. Emit the schema header: the merged `columns:` block plus the `indexes:` line, derived from introspection. Foreign keys are not part of the per-table block; they live only in the top-level `Relationships` section. See [Schema header](#schema-header).
3. Generate a data profile. See [Per-column profiles](#per-column-profiles) and [Row samples](#row-samples).
   - Use query timeouts to prevent hanging queries. If a query runs for 10s or more → abort the query and skip this metric.
   - Use internal database stats to estimate number of rows. If it's hundreds of millions or more → use the internal stats to generate the profile, don't run any queries. Instead, summarize each column from the engine's catalog statistics (PostgreSQL `pg_stats`, MySQL `COLUMN_STATISTICS` histograms, MariaDB `mysql.column_stats`): approximate null fraction, distinct count, numeric min/max, and top values. Mark these estimates with `≈` and a `(from db stats)` tag so they are distinguishable from exact metrics.
4. LLM summarization (done separately): A short summary, or minimal profile, identifies the meaning and format of each field and table. If source code is available, use it to produce better summaries.

## Output format

Each non-empty table renders exactly one block, in this order, separated by blank lines:

```
# "<table>"  (rows=<N>)

columns:
"<col>" <type>[ flags]: <inline profile>
"<col>" <type>[ flags]: <inline profile>
...
indexes: ("<cols>")[, ("<cols>") [WHERE <cond>]] | none

samples:
| column | latest | sample | sample |
| <col> | <v> | <v> | <v> |
...
```

For a table with fewer than 10 rows, `samples:` is replaced by `all rows:` and lists every row (see [Small tables](#small-tables)). The `(rows=N)` count in the header uses the engine's row estimate when available, otherwise an exact `COUNT(*)`.

The block layout is intentionally fixed: a reader (human or LLM) finds everything about one column — its type, flags, and value distribution — on a single `columns:` line, and concrete examples in the `samples:` block, without scanning a long document. Each column name is printed exactly once.

### Schema header

The `columns:` block carries the flattened, normalized table shape — one line per column, in table order, as `"<name>" <type>[ flags]: <inline profile>`. The name is **always rendered as a delimited identifier** (`"Enrollment (K-12)"`): the delimiter marks where the name ends (names may contain spaces, commas, or parentheses) and shows the exact quoting to use when referencing the column in SQL — double quotes on PostgreSQL/Oracle/SQLite (and any other dialect), backticks on MySQL/MariaDB/BigQuery, square brackets on SQL Server. Table names are delimited the same way everywhere they appear — the block header `# "frpm"` and the `Relationships` bullets — so every identifier in the profile reads as the exact reference to use in SQL. The token before the colon replaces the `CREATE TABLE` DDL by default; the text after the colon is the column's data profile (see [Per-column profiles](#per-column-profiles)). When there is no profile text (an included empty table, or a small table whose every row is dumped below), the line is just the bare token `"<name>" <type>[ flags]`.

**Column flags (space-separated, after the type).** Emit only what applies:
- `PK` — column is (part of) the primary key.
- `UNIQ` — column has a single-column `UNIQUE` constraint.
- `NOTNULL` — column is `NOT NULL` and not already `PK` (PK implies NOT NULL, so don't repeat it).
- `FK` — column has a single-column foreign key (the target is listed in the `Relationships` section).

So `"id" bigserial PK`, `"email" varchar255 UNIQ NOTNULL`, `"user_id" bigint FK`.

**Type tokens come from the declared type — unless the data contradicts it (SQLite).** SQLite's declared types are affinity hints, not constraints. Profiling reads the actual per-value storage classes via `typeof(col)` and overrides the token when the declaration is missing or wrong:

- A column declared with no type at all renders its storage class: `"x" int`, or `"x" int|text` when mixed — never a confusing `null` token.
- A declared type that shares no storage class with the stored data renders `declared→stored`: `"qty" numeric→text` — the case where numeric comparisons quietly become lexicographic. Storage classes map to the usual tokens: `integer`→`int`, `real`→`float`, `text`→`text`, `blob`→`bytes`.
- Numeric profiling (min/max, average, median) is skipped for a numeric-declared column whose storage is not purely numeric; the histogram carries the values instead.

**`indexes:`** lists each index as a parenthesized column list, names delimited like in `columns:`. Multi-column indexes keep their column order: `("instance_uuid","volume_id")`. Partial/conditional indexes append the predicate: `("batch_id","box_id") WHERE box_id > 12`. The primary-key index is not repeated here. `none` when there are no non-PK indexes.

**Foreign keys are not rendered per table.** The top-level `Relationships` section (one `- "parent"."col" ← "child"."col"` bullet per referenced column, grouped by parent) is the single place FK structure appears; the per-table `FK` flag on a column token points there.

**When introspection fails or yields nothing usable**, fall back in this order:
1. Parse the raw `CREATE TABLE` DDL emitted by mysqldump or pg_dump with a SQL parser (e.g. `sqlglot`) and derive the `columns:`/`indexes:` lines from the parse tree.
2. If parsing also fails, emit the raw `CREATE TABLE` DDL in a fenced `sql` block in place of the header, and continue with `samples:` as usual (there is no `columns:` block — column profiling is skipped on this path).

The full DDL is **only** ever emitted as this last-resort fallback. In the normal path, introspection produces the one-liner directly.

### Per-column profiles

Each line of the `columns:` block carries the profile text after the `"<name>" <type>[ flags]:` token, in the same left-to-right order as the table's columns. Everything about a column — type, flags, distinct count, nulls, min/max, average, median, histogram — goes on that single line. Never split a column's stats across an indented child line.

Because the type token sits on the same line, numeric ranges omit the historical `int`/`float`/`numeric` qualifier — `1..12592`, not `int 1..12592`. Apply these rules in order; the first that matches determines the profile text:

1. **All NULL.** Emit `all NULL`.
2. **Unique identifier** (every present value distinct, high cardinality, e.g. a PK or UUID). Emit `unique identifier` plus the numeric range if the column is numeric (`unique identifier, 1..12592`). Omit top values. Any nulls are appended: `, nulls=8`.
3. **Low-cardinality column** (fewer than 20 distinct values, present values): emit the full histogram inline as `value=count` pairs, followed by `nulls=N` when non-zero. Quoted string literals; bare numbers/bools. Omit the separate `N distinct` — the histogram is the distribution. Examples:
   - `"status" varchar20: open=30, closed=20, pending=10, nulls=2`
   - `"delete_on_termination" bool: 0=11986, 1=4812`
4. **High-cardinality numeric column.** Emit `N distinct` (or `all distinct` when every present value is unique but the column is not an identifier), then the numeric range `min..max`, then `avg=…` and `median=…` when computed, then `nulls=N` when non-zero, all comma-separated on the same line. Example:
   - `"tick" bigint: 4079 distinct, 1..12592, avg=1944.8, median=1160`
5. **High-cardinality non-numeric column** (strings, timestamps, etc.). Emit `N distinct` (or `all distinct`) plus top-10 values when the distribution is **skewed** — the top value's count is at least 2× the uniform baseline (non-null rows / distinct). A near-uniform column shows only `N distinct`: a value list where every count is ~equal is noise, not a distribution. Plus `nulls=N`. For free-text / blob / JSON columns that are per-row diagnostics, add a trailing `← dropped from samples` annotation so a reader knows why the column is absent from `samples:`. Examples:
   - `"command_id" varchar30: "RECOVER"=6125, "MOVE"=1462, "IDLE"=446, ...`
   - `"message" varchar512: 2751 distinct  ← dropped from samples (per-row diagnostic)`
   - `"json_data" text: 9437 distinct  ← dropped from samples (blob, per-row)`

**Content shape for string columns.** A declared `text`/`varchar` token says nothing about what the strings contain — and CSV-imported databases (SQLite especially) park numbers, dates, and booleans in text columns. For a string column whose line does not already show its values (high-cardinality, no histogram), classify a bounded sample (≤1000 values) of its non-null values and prepend the first matching label:

- `bool-like` — every value is `t`/`f`/`true`/`false`/`y`/`n`/`yes`/`no`/`0`/`1`.
- `uuid` — standard 8-4-4-4-12 hex form.
- `iso-date` — ISO 8601 date or datetime (`2019-09-10`, `2020-01-31T08:30:00`).
- `digits` — ASCII digit strings only. Compare them as strings: leading zeros survive and `ORDER BY`/`>` run lexicographically.
- `numeric` — otherwise int/float-parseable (`-1.5`, `2e5`).

Every non-null value must match; mixed columns and columns with an inlined histogram (whose quoted values already show the content) get no label. Examples:

- `"County Code" text: digits, 58 distinct`
- `"CDSCode" text PK FK: digits, unique identifier`
- `"event_date" text: iso-date, 41 distinct`

**Metric computation rules** (same thresholds as before, retained verbatim — only the rendering changed):

- `NULL` / non-`NULL` counts. If n_rows > 5M, compute only if the column is indexed.
- Min, max for numeric columns. If n_rows > 5M, compute only if indexed.
- Average for numeric columns. If 1M < n_rows ≤ 10M, compute only if indexed. If n_rows > 10M, skip. **Skip entirely when a full histogram is available** (the low-cardinality case above): the counts already state the precise distribution, so an average would only restate it. Also skip on key-like columns (`id`, `*_id`, `*_CODE`, `*_KEY`, `uuid`): a mean over arbitrary codes says nothing.
- Median for numeric columns if n_rows < 100,000. Use native `PERCENTILE_CONT` for PostgreSQL & MariaDB; MySQL needs `ROW_NUMBER()`/`NTILE()` over a full sort. **Skip entirely when a full histogram is available**, for the same reason as the average.
- Distinct count. n_rows ≤ 100K: exact `COUNT(DISTINCT col)`. 100K < n_rows ≤ 1M: exact, only if indexed. n_rows > 1M: don't run.
- Top-10 most frequent values with counts. n_rows ≤ 100K and indexed → exact. 100K < n_rows and indexed → read `most_common_vals`/`most_common_freqs` from `pg_stats`, MySQL `COLUMN_STATISTICS` histogram buckets, or MariaDB `mysql.column_stats` (`JSON_HB` singletons), if present. n_rows > 100K and unindexed, or no catalog stats available → skip.
- **Catalog fallback.** When an exact null/non-null count, min/max, or distinct count is skipped because a column is unindexed and the table exceeds the row-count thresholds, fall back to the same catalog statistics and emit a labeled estimate: `nulls≈`, `non_nulls≈`, `min≈`, `max≈`, `distinct≈`. Available on PostgreSQL, MySQL, and MariaDB.
- **SQLite storage-class audit.** Per column, `SELECT typeof(col), count(*) … GROUP BY 1` when n_rows ≤ 5M (same gate as the null/non-null counts), feeding the type-token overrides above.

**Sensitive fields.** Never dump values for sensitive fields. Treat column names containing `password`, `passwd`, `pwd`, `hash`, `salt`, `secret`, or `token` as sensitive: redact sampled rows and value profiles (emit the column's `columns:` line with `redacted` as the profile text).

### Row samples

The `samples:` block is a transposed markdown table: one row per column, columns are `latest | sample | sample`. It shows 1 latest row and 2 random rows.

Only columns whose concrete values add information beyond the `values:` block appear in `samples:`. Exclude sensitive columns. (redacted elsewhere).

Keep numeric ranges, identifiers, timestamps, foreign-key columns, and any column whose `columns:` line is merely `N distinct` without a histogram — those benefit from seeing actual values. The header lists every kept column in the same order as the `columns:` block.

Values are rendered as the underlying SQL would print them: timestamps in ISO 8601 with offset, numbers bare, strings bare (no quotes in the samples table), `null` for NULL. Oversized values (long JSON containers, large strings) are capped at ~200 characters with a trailing `…` — in the samples table and in inline histogram values alike.

### Small tables

A table with fewer than 10 rows uses `all rows:` instead of `samples:`, and the `columns:` block carries only the bare `"name" <type>[ flags]` tokens — the profile text is omitted, since the dumped rows already expose every value (histograms, ranges, and null counts would restate them):

```
# "<table>"  (rows=<N>)

columns:
"<col>" <type>[ flags]
...
indexes: ...

all rows:
| column | row 1 | row 2 | ... | row N |
| <col> | <v> | <v> | ... | <v> |
```

## Reliability

- Don't crash on exceptions, just skip the metric.
- JSON doesn't support `COUNT(distinct)`. Some other columns can't do that either. Think what we can quickly profile from these types. The number of elements for an array, all possible keys for JSON, ...
- When profiling JSON/JSONB, provide reasonable gates so that requests don't hang if the JSON data stored is too large or if there are too many of them.
- Migration frameworks for Java, Python, Ruby on Rails, and PHP almost always have standard table names. Use these names and don't profile these tables. Also skip other technical tables used in web frameworks in Java, Python, Ruby, TypeScript, PHP, ...
- PostgreSQL supports fast sampling with `SELECT avg(col), stddev(col) FROM mytable TABLESAMPLE SYSTEM (1);`. Some other databases too. Use it when there are too many rows for appropriate metrics.
- MySQL and MariaDB have no `TABLESAMPLE`; `ORDER BY RAND()` materializes and sorts the whole table, so reserve it for small tables. The random sample rows come from a random primary-key seek — read `MIN(pk)`/`MAX(pk)` (index dives; an SQL-side `FLOOR(MIN(pk) + (MAX(pk)-MIN(pk)) * RAND())` cannot use them, it scans an index), pick a random threshold in between, and range-scan `WHERE pk >= threshold LIMIT n` — or, on tables without a numeric single-column key, from a streaming `WHERE RAND() < p LIMIT n` filter sized from the row count.

## Result example

````markdown
---
generator: db-snooper
version: 0.0.28
generated_at_utc: 2026-08-12T09:51:16Z
dialect: postgresql
database: dw
schema: public
skipped_technical_tables:
  - "migrations"
---

## Relationships

- "batch"."id" ← "batch_box_association"."batch_id", "batch_port"."batch_id"
- "box"."id" ← "batch_box_association"."box_id"
- "port"."short_id" ← "batch_port"."port_short_id"

# "batch_box_association"  (rows=392)

columns:
"batch_id" bigint PK FK: 176 distinct, 5..214
"box_id" bigint PK FK: 175 distinct, 17000038..32005989

indexes: ("box_id")

samples:
| column | latest | sample | sample |
| batch_id | 215 | 12 | 1124 |
| box_id | 32000246 | 17000123 | 17000001 |

# "batch_port"  (rows=7)

columns:
"id" int PK
"batch_id" bigint FK
"port_short_id" int FK

indexes: none

all rows:
| column | row 1 | row 2 | row 3 | row 4 | row 5 | row 6 | row 7 |
| id | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
| batch_id | 12 | 12 | 15 | 16 | 17 | 20 | 20 |
| port_short_id | 1 | 2 | 1 | 2 | 2 | 1 | 2 |

# "safety_events"  (rows=9713)

columns:
"id" bigserial PK: unique identifier, 1..12592
"check_name" varchar64: "InterrobotCollisionsChecker"=4677, "CMDConstraintsCheck"=3343, "StartStateCheck"=1222, "MoveWithLoweredLiftCheck"=399, "LiftSafetyChecker"=60, "LiftDownToInactivePort"=7, "MoveOutboundCheck"=5
"message" varchar512: 2751 distinct  ← dropped from samples (per-row diagnostic)
"tick" bigint: 4079 distinct, 1..12592, avg=1944.8, median=1160
"time" timestamptz: 9713 distinct
"robot_id" bigint: 6=3679, 7=3452, 5=1884, 1=387, 8=268, 3=27, 4=16
"task_id" bigint: 984 distinct, nulls=256, 155269..197255
"box_id" bigint: 248 distinct, nulls=5489, 17000047..32002154
"command_id" varchar30: "RECOVER"=6125, "MOVE"=1462, "IDLE"=446, "LIFT"=400, "ROTATE_WHEELS"=338, "STOP"=300, "TAKE_BOX"=277, "PUT_BOX"=148, "EXTEND_GRIPPER"=87, "ACK_ERROR"=75, "UNCLENCH"=35, "CHECK_ROBOT_READY"=20
"param1" bigint: 117 distinct, -68..4688, avg=756.5, median=1005
"start_tick" bigint: 4314 distinct, 1..12592, avg=1952.8, median=1160
"finished_tick" bigint: 4326 distinct, 2..12594, avg=1985.9, median=1163
"json_data" text: 9437 distinct  ← dropped from samples (blob, per-row)

indexes: ("time")

samples:
| column | latest | sample | sample |
| check_name | StartStateCheck | CMDConstraintsCheck | InterrobotCollisionsChecker |
| time | 2026-07-16T10:26:51+01:00 | 2026-03-18T10:07:01+00:00 | 2026-05-19T08:46:02+01:00 |
| robot_id | 7 | 6 | 5 |
| command_id | PUT_BOX | RECOVER | MOVE |
| task_id | 197255 | 189944 | null |

- Skipped 1 empty table(s): "archived_events"
````

## Implementation

This can be automated using [python implementation](python_impl.md).
