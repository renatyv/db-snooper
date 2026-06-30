# Schema Linking
Goal: find join-candidate column pairs across tables without scanning every column at full cost.

# Expected result
Separate .md file with potential links:
- PK<->FK connections
- advanced search for additional schema links, see pipeline described below

# Advanced schema linking pipeline
## Stage 0 — Metadata pass
- FK-constrained columns → join already known, skip.
- Mismatched dtypes → exclude pair from consideration.

## Stage 1 — Cheap cardinality estimate
```sql
SELECT COUNT(DISTINCT col), COUNT(*) FROM table;
```
Fallback to `TABLESAMPLE`/modulo sampling if too slow; flag as approximate.

## Stage 2 — Triage by cardinality ratio
| Ratio (distinct/rows) | Action |
|---|---|
| ≈ 1.0, not declared PK | Drop (unstructured/unique text) |
| Very low (enum-like) | Keep, low priority (false-positive prone) |
| Moderate, ID-like | Primary target → Stage 3 |

## Stage 3 — Name/type pre-filter
Trigram/Levenshtein on column names + dtype match.
- Strong match → tentative join, spot-check with small sample.
- No signal → pass to Stage 4.

## Stage 4 — Full DISTINCT extraction
Only on columns surviving Stage 2–3:
```sql
SELECT DISTINCT col FROM table;
```

## Stage 5 — MinHash + LSH Ensemble
Use datasketch python library
- MinHash signature per column (128–256 permutations).
- `datasketch.MinHashLSHEnsemble`, partitioned by set size.
- Query containment (asymmetric, not Jaccard — handles unequal cardinalities).
- Threshold (e.g. > 0.8) → candidate pair.

## Stage 6 — Verification
Exact containment check on the (now small) distinct sets:
```sql
SELECT COUNT(*) FROM (
  SELECT DISTINCT a.col FROM t1 a
  WHERE a.col NOT IN (SELECT col FROM t2)
) x;
```
Confirms or rejects LSH candidates; catches approximation false positives.
