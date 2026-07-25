# Reliability
- Don't crash on exceptions, just skip the metric.
- JSON doesn't support distinct. What other columns can't do that? What can we quickly profile from these types? The number of elements for an array, all possible keys for JSON?
- Migration frameworks for Java, Python, Ruby on Rails, and PHP almost always have standard table names. You should at least use these names and not profile these tables. What other technical tables could there be that don't make sense to profile?
- When profiling JSON/JSONB, you need to provide reasonable gates so that requests don't hang if the JSON data stored is too large or if there are too many of them.
