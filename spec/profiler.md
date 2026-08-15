# Problem

To efficiently convert text to analytic SQL queries, LLMs need database schema and data context.

# How the Profiler Should Work

For each database create a separate folder with subfolders for each of the schemas.

Generate a single `db_/schema.md` profile per schema by default. When requested with `--per-table`, generate separate files `db_/schema/table.md`.

The profile is written in a **compact one-block-per-table** format (see [Output format](#output-format)). Every table renders its schema and per-column value profiles in one merged `columns:` block, plus row samples, in a single contiguous block of roughly 15–30 lines regardless of column count. The historical `CREATE TABLE` DDL block, the separate `## Indexes` / `## Rows` / `## Columns` sections, and the transposed all-rows table are all superseded by this format.

For each table:
1. Skip empty tables. A table with zero rows carries no data context, so it is excluded from the profile by default. The skipped names are listed once in a trailing summary bullet, e.g. `- Skipped 2 empty table(s): foo, bar`. `ProfileOptions(include_empty_tables=True)` forces their inclusion; an included empty table emits only the bare per-column type tokens in the `columns:` block (and an empty `all rows` marker), with no profile text or `samples:` block (there is nothing to profile).
2. Emit the schema header: the merged `columns:` block plus the `indexes:` and `fk:` lines, derived from introspection. See [Schema header](#schema-header).
3. Generate a data profile. See [Per-column profiles](#per-column-profiles) and [Row samples](#row-samples).
   - Use query timeouts to prevent hanging queries. If a query runs for 10s or more → abort the query and skip this metric.
   - Use internal database stats to estimate number of rows. If it's hundreds of millions or more → use the internal stats to generate the profile, don't run any queries. Instead, summarize each column from the engine's catalog statistics (PostgreSQL `pg_stats`, MySQL `COLUMN_STATISTICS` histograms, MariaDB `mysql.column_stats`): approximate null fraction, distinct count, numeric min/max, and top values. Mark these estimates with `≈` and a `(from db stats)` tag so they are distinguishable from exact metrics.
4. LLM summarization (done separately): A short summary, or minimal profile, identifies the meaning and format of each field and table. If source code is available, use it to produce better summaries.

## Output format

Each non-empty table renders exactly one block, in this order, separated by blank lines:

```
# <table>  (rows=<N>)

columns:
<col>(<type>[,flags]): <inline profile>
<col>(<type>[,flags]): <inline profile>
...
indexes: (<cols>)[, (<cols>) [WHERE <cond>]] | none
fk: <col>→<ref_table>.<ref_col>[, ...] | none

samples:
| column | latest | sample | sample |
| <col> | <v> | <v> | <v> |
...
```

For a table with fewer than 10 rows, `samples:` is replaced by `all rows:` and lists every row (see [Small tables](#small-tables)). The `(rows=N)` count in the header uses the engine's row estimate when available, otherwise an exact `COUNT(*)`.

The block layout is intentionally fixed: a reader (human or LLM) finds everything about one column — its type, flags, and value distribution — on a single `columns:` line, and concrete examples in the `samples:` block, without scanning a long document. Each column name is printed exactly once.

### Schema header

The `columns:` block carries the flattened, normalized table shape — one line per column, in table order, as `name(type[,flags]): <inline profile>`. The token before the colon replaces the `CREATE TABLE` DDL by default; the text after the colon is the column's data profile (see [Per-column profiles](#per-column-profiles)). When there is no profile text (e.g. an included empty table), the line is just the bare token `name(type[,flags])`.

**Column flags (comma-separated, after the type).** Emit only what applies:
- `PK` — column is (part of) the primary key.
- `UNIQ` — column has a single-column `UNIQUE` constraint.
- `NOTNULL` — column is `NOT NULL` and not already `PK` (PK implies NOT NULL, so don't repeat it).
- `FK` — column has a single-column foreign key (the target is listed in the `fk:` line).

So `id(bigserial,PK)`, `email(varchar255,UNIQ,NOTNULL)`, `user_id(bigint,FK)`.

**`indexes:`** lists each index as a parenthesized column list. Multi-column indexes keep their column order: `(instance_uuid,volume_id)`. Partial/conditional indexes append the predicate: `(batch_id,box_id) WHERE box_id > 12`. The primary-key index is not repeated here. `none` when there are no non-PK indexes.

**`fk:`** lists each foreign key as `col→ref_table.ref_col`. Multi-column FKs use `(col1,col2)→ref_table.(ref1,ref2)`. `none` when there are none.

**When introspection fails or yields nothing usable**, fall back in this order:
1. Parse the raw `CREATE TABLE` DDL emitted by mysqldump or pg_dump with a SQL parser (e.g. `sqlglot`) and derive the `columns:`/`indexes:`/`fk:` lines from the parse tree.
2. If parsing also fails, emit the raw `CREATE TABLE` DDL in a fenced `sql` block in place of the header, and continue with `samples:` as usual (there is no `columns:` block — column profiling is skipped on this path).

The full DDL is **only** ever emitted as this last-resort fallback. In the normal path, introspection produces the one-liner directly.

### Per-column profiles

Each line of the `columns:` block carries the profile text after the `name(type[,flags]):` token, in the same left-to-right order as the table's columns. Everything about a column — type, flags, distinct count, nulls, min/max, average, median, histogram — goes on that single line. Never split a column's stats across an indented child line.

Because the type token sits on the same line, numeric ranges omit the historical `int`/`float`/`numeric` qualifier — `1..12592`, not `int 1..12592`. Apply these rules in order; the first that matches determines the profile text:

1. **All NULL.** Emit `all NULL`.
2. **Unique identifier** (every present value distinct, high cardinality, e.g. a PK or UUID). Emit `unique identifier` plus the numeric range if the column is numeric (`unique identifier, 1..12592`). Omit top values. Any nulls are appended: `, nulls=8`.
3. **Low-cardinality column** (fewer than 20 distinct values, present values): emit the full histogram inline as `value=count` pairs, followed by `nulls=N` when non-zero. Quoted string literals; bare numbers/bools. Omit the separate `N distinct` — the histogram is the distribution. Examples:
   - `status(varchar20): open=30, closed=20, pending=10, nulls=2`
   - `delete_on_termination(bool): 0=11986, 1=4812`
4. **High-cardinality numeric column.** Emit `N distinct` (or `all distinct` when every present value is unique but the column is not an identifier), then the numeric range `min..max`, then `avg=…` and `median=…` when computed, then `nulls=N` when non-zero, all comma-separated on the same line. Example:
   - `tick(bigint): 4079 distinct, 1..12592, avg=1944.8, median=1160`
5. **High-cardinality non-numeric column** (strings, timestamps, etc.). Emit `N distinct` (or `all distinct`) plus optional top-10 values when informative, plus `nulls=N`. For free-text / blob / JSON columns that are per-row diagnostics, add a trailing `← dropped from samples` annotation so a reader knows why the column is absent from `samples:`. Examples:
   - `command_id(varchar30): "RECOVER"=6125, "MOVE"=1462, "IDLE"=446, ...`
   - `message(varchar512): 2751 distinct  ← dropped from samples (per-row diagnostic)`
   - `json_data(text): 9437 distinct  ← dropped from samples (blob, per-row)`

**Metric computation rules** (same thresholds as before, retained verbatim — only the rendering changed):

- `NULL` / non-`NULL` counts. If n_rows > 5M, compute only if the column is indexed.
- Min, max for numeric columns. If n_rows > 5M, compute only if indexed.
- Average for numeric columns. If 1M < n_rows ≤ 10M, compute only if indexed. If n_rows > 10M, skip. **Skip entirely when a full histogram is available** (the low-cardinality case above): the counts already state the precise distribution, so an average would only restate it.
- Median for numeric columns if n_rows < 100,000. Use native `PERCENTILE_CONT` for PostgreSQL & MariaDB; MySQL needs `ROW_NUMBER()`/`NTILE()` over a full sort. **Skip entirely when a full histogram is available**, for the same reason as the average.
- Distinct count. n_rows ≤ 100K: exact `COUNT(DISTINCT col)`. 100K < n_rows ≤ 1M: exact, only if indexed. n_rows > 1M: don't run.
- Top-10 most frequent values with counts. n_rows ≤ 100K and indexed → exact. 100K < n_rows and indexed → read `most_common_vals`/`most_common_freqs` from `pg_stats`, MySQL `COLUMN_STATISTICS` histogram buckets, or MariaDB `mysql.column_stats` (`JSON_HB` singletons), if present. n_rows > 100K and unindexed, or no catalog stats available → skip.
- **Catalog fallback.** When an exact null/non-null count, min/max, or distinct count is skipped because a column is unindexed and the table exceeds the row-count thresholds, fall back to the same catalog statistics and emit a labeled estimate: `nulls≈`, `non_nulls≈`, `min≈`, `max≈`, `distinct≈`. Available on PostgreSQL, MySQL, and MariaDB.

**Sensitive fields.** Never dump values for sensitive fields. Treat column names containing `password`, `passwd`, `pwd`, `hash`, `salt`, `secret`, or `token` as sensitive: redact sampled rows and value profiles (emit the column's `columns:` line with `redacted` as the profile text).

### Row samples

The `samples:` block is a transposed markdown table: one row per column, columns are `latest | sample | sample`. It shows 1 latest row and 2 random rows.

Only columns whose concrete values add information beyond the `values:` block appear in `samples:`. Exclude sensitive columns. (redacted elsewhere).

Keep numeric ranges, identifiers, timestamps, foreign-key columns, and any column whose `columns:` line is merely `N distinct` without a histogram — those benefit from seeing actual values. The header lists every kept column in the same order as the `columns:` block.

Values are rendered as the underlying SQL would print them: timestamps in ISO 8601 with offset, numbers bare, strings bare (no quotes in the samples table), `null` for NULL. Oversized container values (long JSON, large strings) are truncated with a trailing `…`.

### Small tables

A table with fewer than 10 rows uses `all rows:` instead of `samples:`. The block is otherwise identical:

```
# <table>  (rows=<N>)

columns:
<col>(<type>[,flags]): <inline profile>
...
indexes: ...
fk: ...

all rows:
| column | row 1 | row 2 | ... | row N |
| <col> | <v> | <v> | ... | <v> |
```

The profile text in the `columns:` block is still emitted for small tables when any column has a useful profile (null fractions, a small histogram, etc.). When the table is so small that `all rows:` already exposes every value, a column's profile may simply read `<v>=N, <v>=M` (which is the histogram) — this is fine and not considered redundant, since the two blocks serve different readers.

## Reliability

- Don't crash on exceptions, just skip the metric.
- JSON doesn't support `COUNT(distinct)`. Some other columns can't do that either. Think what we can quickly profile from these types. The number of elements for an array, all possible keys for JSON, ...
- When profiling JSON/JSONB, provide reasonable gates so that requests don't hang if the JSON data stored is too large or if there are too many of them.
- Migration frameworks for Java, Python, Ruby on Rails, and PHP almost always have standard table names. Use these names and don't profile these tables. Also skip other technical tables used in web frameworks in Java, Python, Ruby, TypeScript, PHP, ...
- PostgreSQL supports fast sampling with `SELECT avg(col), stddev(col) FROM mytable TABLESAMPLE SYSTEM (1);`. Some other databases too. Use it when there are too many rows for appropriate metrics.

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
  - migrations
---

## Relationships

- batch.id ← batch_box_association.batch_id, batch_port.batch_id
- box.id ← batch_box_association.box_id
- port.short_id ← batch_port.port_short_id

# batch_box_association  (rows=392)

columns:
batch_id(bigint,PK,FK): 176 distinct, 5..214
box_id(bigint,PK,FK): 175 distinct, 17000038..32005989

indexes: (box_id)
fk: batch_id→batch.id, box_id→box.id

samples:
| column | latest | sample | sample |
| batch_id | 215 | 12 | 1124 |
| box_id | 32000246 | 17000123 | 17000001 |

# batch_port  (rows=7)

columns:
id(int,PK): 5, 6, 7, 8, 9, 10, 11
batch_id(bigint,FK): 12=2, 15, 16, 17, 20=2
port_short_id(int,FK): 1=3, 2=4

indexes: none
fk: batch_id→batch.id, port_short_id→port.short_id

all rows:
| column | row 1 | row 2 | row 3 | row 4 | row 5 | row 6 | row 7 |
| id | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
| batch_id | 12 | 12 | 15 | 16 | 17 | 20 | 20 |
| port_short_id | 1 | 2 | 1 | 2 | 2 | 1 | 2 |

# safety_events  (rows=9713)

columns:
id(bigserial,PK): unique identifier, 1..12592
check_name(varchar64): "InterrobotCollisionsChecker"=4677, "CMDConstraintsCheck"=3343, "StartStateCheck"=1222, "MoveWithLoweredLiftCheck"=399, "LiftSafetyChecker"=60, "LiftDownToInactivePort"=7, "MoveOutboundCheck"=5
message(varchar512): 2751 distinct  ← dropped from samples (per-row diagnostic)
tick(bigint): 4079 distinct, 1..12592, avg=1944.8, median=1160
time(timestamptz): 9713 distinct
robot_id(bigint): 6=3679, 7=3452, 5=1884, 1=387, 8=268, 3=27, 4=16
task_id(bigint): 984 distinct, nulls=256, 155269..197255
box_id(bigint): 248 distinct, nulls=5489, 17000047..32002154
command_id(varchar30): "RECOVER"=6125, "MOVE"=1462, "IDLE"=446, "LIFT"=400, "ROTATE_WHEELS"=338, "STOP"=300, "TAKE_BOX"=277, "PUT_BOX"=148, "EXTEND_GRIPPER"=87, "ACK_ERROR"=75, "UNCLENCH"=35, "CHECK_ROBOT_READY"=20
param1(bigint): 117 distinct, -68..4688, avg=756.5, median=1005
start_tick(bigint): 4314 distinct, 1..12592, avg=1952.8, median=1160
finished_tick(bigint): 4326 distinct, 2..12594, avg=1985.9, median=1163
json_data(text): 9437 distinct  ← dropped from samples (blob, per-row)

indexes: (time)
fk: none

samples:
| column | latest | sample | sample |
| check_name | StartStateCheck | CMDConstraintsCheck | InterrobotCollisionsChecker |
| time | 2026-07-16T10:26:51+01:00 | 2026-03-18T10:07:01+00:00 | 2026-05-19T08:46:02+01:00 |
| robot_id | 7 | 6 | 5 |
| command_id | PUT_BOX | RECOVER | MOVE |
| task_id | 197255 | 189944 | null |

- Skipped 1 empty table(s): archived_events
````

## Implementation

This can be automated using [python implementation](python_impl.md).
