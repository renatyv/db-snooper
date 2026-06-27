from ai_sql_context.profiling import compact_value, value_shape


def test_value_shape_detects_common_formats() -> None:
    shape = value_shape(["2026-06-08", "123", '{"ok": true}', "ABC-123"])

    assert shape["date_like"] == 1
    assert shape["numeric_like"] == 1
    assert shape["json_like"] == 1
    assert shape["char_classes"] == ["digit", "lower", "space", "symbol", "upper"]


def test_compact_value_handles_null_and_long_text() -> None:
    assert compact_value(None) == "NULL"
    assert compact_value("a\n" * 100, max_length=10) == "a\\na\\na..."
