from __future__ import annotations

import json
import re
from collections import Counter
from decimal import Decimal
from typing import Any, Iterable

NUMERIC_TYPES = {
    "bigint",
    "decimal",
    "double",
    "float",
    "int",
    "integer",
    "mediumint",
    "numeric",
    "real",
    "smallint",
    "tinyint",
}

STRING_TYPES = {
    "char",
    "enum",
    "json",
    "longtext",
    "mediumtext",
    "set",
    "text",
    "tinytext",
    "varchar",
}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}")
NUMERIC_RE = re.compile(r"^-?\d+(?:\.\d+)?$")


def base_type(data_type: str) -> str:
    return data_type.split("(", 1)[0].strip().lower()


def is_numeric_type(data_type: str) -> bool:
    return base_type(data_type) in NUMERIC_TYPES


def is_string_type(data_type: str) -> bool:
    return base_type(data_type) in STRING_TYPES


def value_shape(values: Iterable[Any], max_prefixes: int = 5) -> dict[str, Any]:
    strings = [str(value) for value in values if value is not None]
    if not strings:
        return {"non_null_examples": 0}

    lengths = [len(value) for value in strings]
    classes: set[str] = set()
    date_like = 0
    datetime_like = 0
    numeric_like = 0
    json_like = 0
    prefixes: Counter[str] = Counter()

    for value in strings:
        if any(ch.islower() for ch in value):
            classes.add("lower")
        if any(ch.isupper() for ch in value):
            classes.add("upper")
        if any(ch.isdigit() for ch in value):
            classes.add("digit")
        if any(ch.isspace() for ch in value):
            classes.add("space")
        if any(not ch.isalnum() and not ch.isspace() for ch in value):
            classes.add("symbol")
        if DATE_RE.match(value):
            date_like += 1
        if DATETIME_RE.match(value):
            datetime_like += 1
        if NUMERIC_RE.match(value):
            numeric_like += 1
        if looks_json(value):
            json_like += 1
        prefix = common_prefix_token(value)
        if prefix:
            prefixes[prefix] += 1

    total = len(strings)
    return {
        "non_null_examples": total,
        "min_length": min(lengths),
        "max_length": max(lengths),
        "char_classes": sorted(classes),
        "date_like": date_like,
        "datetime_like": datetime_like,
        "numeric_like": numeric_like,
        "json_like": json_like,
        "common_prefixes": prefixes.most_common(max_prefixes),
    }


def looks_json(value: str) -> bool:
    stripped = value.strip()
    if not stripped or stripped[0] not in "[{":
        return False
    try:
        json.loads(stripped)
    except ValueError:
        return False
    return True


def common_prefix_token(value: str) -> str | None:
    match = re.match(r"^[A-Za-z_]{2,}", value)
    if match:
        return match.group(0)[:16]
    return None


def normalize_scalar(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    return value


def compact_value(value: Any, max_length: int = 120) -> str:
    if value is None:
        return "NULL"
    value = normalize_scalar(value)
    text = str(value)
    text = text.replace("\n", "\\n").replace("\r", "\\r")
    if len(text) > max_length:
        text = text[: max_length - 3] + "..."
    return text
