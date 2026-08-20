from __future__ import annotations

from dataclasses import dataclass

from db_snooper.contracts import ProfileOptions, ProfileProgress


@dataclass(frozen=True)
class ColumnProfile:
    """Inline profile for a single column, rendered on its ``columns:`` line.

    ``value_line`` is the profile text placed after the ``"name" type[ flags]:``
    token — distinct counts, histograms, min/max, avg/median, nulls, and any
    ``← dropped from samples`` annotation all live on this single string.
    Continuation/indented child lines are intentionally avoided: the spec
    requires one line per column.

    ``type_override`` replaces the declared type inside the ``"name" type``
    token when the declared type is missing or provably wrong: SQLite columns
    declared without a type (NullType) resolve to their actual storage class,
    and declared↔stored mismatches render as ``declared→stored`` (e.g.
    ``numeric→text``). ``None`` keeps the declared type token.
    """

    name: str
    value_line: str
    is_sensitive: bool
    is_unique_identifier: bool
    dropped_from_samples: bool
    type_override: str | None = None


__all__ = ["ColumnProfile", "ProfileOptions", "ProfileProgress"]
