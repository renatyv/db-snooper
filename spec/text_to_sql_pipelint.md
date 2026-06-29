# The text-to-SQL pipeline

1. Periodically generate a profile and schema linking for your database, e.g. once every night when load is low
2. Use generated profile and schema linking to generate `n` candidate SQL queries. A temperature of 1 might help.
3. Execute the candidates to keep only the valid ones (no SQL execution error). Adding LIMIT to queries which don't have one might help reduce time. Queries can be done in parallel threads.
4. Finally, use another LLM for selecting the candidate with the highest score.


