# How the Profiler Should Work

For each database create a separate folder with subfolders for each of the schemas.

Generate a single `db_/schema.sql` profile per schema by default. When requested with `--per-table`, generate separate files `db_/schema/table.sql`.

For each table:
1. Generate `CREATE TABLE` DDL with all indexes and constraints.
2. Generate a data profile.
   - If a table has fewer than 50 rows, include rows up to a small deterministic cap. Never dump values for sensitive fields. Treat column names containing `password`, `passwd`, `pwd`, `hash`, `salt`, `secret`, or `token` as sensitive, and redact sampled rows and value profiles.
   - If a table has more than 50 rows, include the number of rows, three latest rows, and five random rows. Also generate per-column profiles:
     - If a column is all `NULL`, emit a one-line `all NULL` summary.
     - If a column is a unique identifier, omit top values and value-shape metadata.
     - If a column has fewer than 20 distinct values, include all non-sensitive values. Otherwise, include per-column profile data:
       - `NULL` and non-`NULL` counts.
       - Distinct value count.
       - Min, max, and median for numeric columns.
       - Top 10 most frequent values with counts when they are informative.
       - Value shape only when it adds meaningful information and does not duplicate type or DDL metadata.
3. LLM summarization (done separately): A short summary, or minimal profile, identifies the meaning and format of each field and table. If source code is available, use it to produce better summaries.


## Result example

Single profile for a schema `main` in database `dive_sim`

`dive_sim/main.sql`

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
-- action_history_id numeric: min=362732, median=459736, max=542475
-- action_history_id top_values: 423373=4, 423378=4, 423383=4, 423384=4, 423386=4, 423387=4, 423388=4, 423391=4, 423392=4, 423395=4
-- action_status: nulls=0, non_nulls=551830, distinct=5
-- action_status values: SCHEDULED=298848, DONE=165650, EXEC=73332, FAILED=12558, FAILED_TIMEOUT=1442
-- id: unique values=551830, range=391982..943811
-- state_history_id: nulls=98520, non_nulls=453310, distinct=453310
-- state_history_id numeric: min=734084, median=960738, max=1187393
-- tick: nulls=0, non_nulls=551830, distinct=12029
-- tick numeric: min=1, median=854, max=15446
-- tick top_values: 1=4069, 2=1772, 3=1463, 10=1133, 4=861, 21=855, 20=852, 15=839, 5=837, 22=834
-- time: nulls=0, non_nulls=551830, distinct=551830


CREATE TABLE `blocked_area` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` timestamp NOT NULL,
  `level` int(11) NOT NULL,
  `robot_id` int(11) NOT NULL,
  `reason` varchar(255) NOT NULL,
  `x_begin_mm` int(11) NOT NULL,
  `x_end_mm` int(11) NOT NULL,
  `y_begin_mm` int(11) NOT NULL,
  `y_end_mm` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=40341 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=2
-- ALL_ROWS: blocked_area
-- row: {"id": "40307", "level": "0", "reason": "NOT_IN_USE", "robot_id": "5", "timestamp": "2026-06-25 14:32:42", "x_begin_mm": "1000", "x_end_mm": "1500", "y_begin_mm": "3797", "y_end_mm": "4497"}
-- row: {"id": "40308", "level": "0", "reason": "NOT_IN_USE", "robot_id": "5", "timestamp": "2026-06-25 14:32:42", "x_begin_mm": "1500", "x_end_mm": "1980", "y_begin_mm": "3797", "y_end_mm": "4497"}
```
