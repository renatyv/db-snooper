from __future__ import annotations

from dataclasses import dataclass

from db_snooper.contracts import ProfileOptions, ProfileProgress


@dataclass(frozen=True)
class ColumnProfile:
    """Inline profile for a single column, rendered as one ``values:`` line.

    ``value_line`` is the full text placed after ``<name>: `` — distinct counts,
    histograms, min/max, avg/median, nulls, and any ``← dropped from samples``
    annotation all live on this single string. Continuation/indented child lines
    are intentionally avoided: the spec requires one line per column.
    """

    name: str
    value_line: str
    is_sensitive: bool
    is_unique_identifier: bool
    dropped_from_samples: bool


__all__ = ["ColumnProfile", "ProfileOptions", "ProfileProgress"]
