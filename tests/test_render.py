from ai_sql_context.models import ColumnInfo, ColumnProfile, DatabaseContext, LikelyJoin, TableProfile
from ai_sql_context.render import render_context


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
    assert "-- column command values: MOVE=2" in first


def test_render_redacts_sensitive_columns() -> None:
    table = TableProfile(
        name="user",
        row_count=2,
        columns=[ColumnInfo("id", "int", False), ColumnInfo("pwd_hash", "varchar(256)", True)],
        create_table_sql="CREATE TABLE `user` (`id` int NOT NULL, `pwd_hash` varchar(256))",
        primary_key=("id",),
        column_profiles=[
            ColumnProfile("id", 0, 2, 2, numeric_min=1, numeric_max=2, numeric_median=1),
            ColumnProfile("pwd_hash", 0, 2, 2, low_cardinality_values=[("secret-hash", 1), ("other", 1)]),
        ],
        sample_rows=[{"id": 1, "pwd_hash": "secret-hash"}, {"id": 2, "pwd_hash": "other"}],
    )

    rendered = render_context(DatabaseContext("mysql", "app", [table]))

    assert "secret-hash" not in rendered
    assert "other" not in rendered
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

    assert "-- PROFILE: audit omitted; table is empty" in rendered
    assert "-- column id:" not in rendered
