from ai_sql_context.models import ColumnInfo, ColumnProfile, DatabaseContext, LikelyJoin, TableProfile
from ai_sql_context.render import MAX_ALL_ROWS, render_context


def test_render_context_is_deterministic_and_contains_profiles() -> None:
    table = TableProfile(
        name="action_history",
        row_count=2,
        columns=[ColumnInfo("command", "varchar(32)", False)],
        create_table_sql="CREATE TABLE `action_history` (`command` varchar(32) NOT NULL)",
        primary_key=("id",),
        column_profiles=[
            ColumnProfile(
                name="command",
                null_count=0,
                non_null_count=2,
                distinct_count=1,
                low_cardinality_values=[("MOVE", 2)],
                shape={"char_classes": ["upper"], "non_null_examples": 2},
            )
        ],
    )
    context = DatabaseContext(
        dialect="mysql",
        database="dive_sim",
        tables=[table],
        likely_joins=[LikelyJoin("action_history", "robot_id", "robot", "id", "medium", "test")],
    )

    first = render_context(context)
    second = render_context(context)

    assert first == second
    assert "-- database: dive_sim" in first
    assert "-- action_history.robot_id -> robot.id [medium; test]" in first
    assert "-- PROFILE: action_history rows=2" in first
    assert "-- command values: MOVE=2" in first


def test_render_redacts_sensitive_columns() -> None:
    table = TableProfile(
        name="user",
        row_count=3,
        columns=[ColumnInfo("id", "int", False), ColumnInfo("pwd_hash", "varchar(256)", True)],
        create_table_sql="CREATE TABLE `user` (`id` int NOT NULL, `pwd_hash` varchar(256))",
        primary_key=("id",),
        column_profiles=[
            ColumnProfile("id", 0, 3, 3, numeric_min=1, numeric_max=3, numeric_median=2),
            ColumnProfile("pwd_hash", 0, 3, 3, low_cardinality_values=[("secret-hash", 1), ("other", 1), ("third", 1)]),
        ],
        sample_rows=[{"id": 1, "pwd_hash": "secret-hash"}, {"id": 2, "pwd_hash": "other"}],
    )

    rendered = render_context(DatabaseContext("mysql", "app", [table]))

    assert "secret-hash" not in rendered
    assert "other" not in rendered
    assert "third" not in rendered
    assert "values redacted" in rendered
    assert '"pwd_hash": "[REDACTED]"' in rendered


def test_render_omits_empty_table_profiles() -> None:
    table = TableProfile(
        name="audit",
        row_count=0,
        columns=[ColumnInfo("id", "int", False)],
        create_table_sql="CREATE TABLE `audit` (`id` int NOT NULL)",
        column_profiles=[ColumnProfile("id", 0, 0, 0)],
    )

    rendered = render_context(DatabaseContext("mysql", "app", [table]))

    assert "-- PROFILE: audit rows=0 omitted; table is empty" in rendered
    assert "-- id:" not in rendered


def test_render_skips_column_profiles_when_all_rows_are_printed() -> None:
    table = TableProfile(
        name="status",
        row_count=2,
        columns=[ColumnInfo("name", "varchar(32)", False)],
        create_table_sql="CREATE TABLE `status` (`name` varchar(32) NOT NULL)",
        column_profiles=[ColumnProfile("name", 0, 2, 2, low_cardinality_values=[("done", 1), ("new", 1)])],
        sample_rows=[{"name": "done"}, {"name": "new"}],
    )

    rendered = render_context(DatabaseContext("mysql", "app", [table]))

    assert "-- PROFILE: status rows=2" in rendered
    assert "-- ALL_ROWS: status" in rendered
    assert "-- name values:" not in rendered


def test_render_keeps_column_profiles_when_rows_are_partially_printed() -> None:
    table = TableProfile(
        name="status",
        row_count=MAX_ALL_ROWS + 1,
        columns=[ColumnInfo("name", "varchar(32)", False)],
        create_table_sql="CREATE TABLE `status` (`name` varchar(32) NOT NULL)",
        column_profiles=[ColumnProfile("name", 0, MAX_ALL_ROWS + 1, 1, low_cardinality_values=[("done", MAX_ALL_ROWS + 1)])],
        sample_rows=[{"name": "done"} for _ in range(MAX_ALL_ROWS + 1)],
    )

    rendered = render_context(DatabaseContext("mysql", "app", [table]))

    assert "-- name values: done=26" in rendered
    assert "-- rows omitted: 1" in rendered
