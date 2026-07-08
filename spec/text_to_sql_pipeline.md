# The Text-to-SQL Pipeline

1. Periodically generate a profile and schema links for your database, for example once each night when load is low.
2. Use the generated profile and schema links to generate `n` candidate SQL queries. A temperature of 1 might help.
3. Execute the candidates to keep only valid queries with no SQL execution errors. Adding `LIMIT` to queries that do not have one can help reduce runtime. Queries can run in parallel threads.
4. Finally, use another LLM to select the candidate with the highest score.
