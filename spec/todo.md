1. **Cap values at ~150–200 chars with `…`** — the spec already mandates it (`profiler.md:126`), the code just doesn't do it. Worst offenders in nova are 8.5KB histogram lines, not samples. One helper, three call sites.
2. **Drop the per-table MySQL "random rows skipped" note** — 89 identical lines in dw; the samples header already carries the semantics.
3. **Float formatting** — replace `2.91772e+06` with `2.9e+06`.
4. **Skip avg/median on key-like columns** — current `id`/`*_id` heuristic misses dw's `TERM_CODE`/`X_KEY` naming; extend it, mayb 'UUID'.
5. top-k suppression should use skew (top count vs rows/distinct), not a distinct>20 cutoff; `indexes: none` is a deliberate spec choice — change spec + code together if at all.
