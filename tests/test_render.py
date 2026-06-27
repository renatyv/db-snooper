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
