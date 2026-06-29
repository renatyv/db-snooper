import pytest

from ai_sql_context.cli import build_parser


def test_parser_accepts_profile_command() -> None:
    args = build_parser().parse_args(["profile", "--database", "app", "--user", "user"])

    assert args.command == "profile"


def test_parser_rejects_generate_command() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args(["generate"])
