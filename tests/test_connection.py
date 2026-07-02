from __future__ import annotations

import argparse

import pytest

from db_snooper.connection import add_connection_arguments, resolve_database_url


def parse_url(argv: list[str]) -> str:
    parser = argparse.ArgumentParser()
    add_connection_arguments(parser)
    return str(resolve_database_url(parser.parse_args(argv), parser))


def test_sqlite_friendly_flags_build_url() -> None:
    assert parse_url(["--db-type", "sqlite", "--database", "data/app.sqlite"]) == "sqlite:///data/app.sqlite"


def test_duckdb_friendly_flags_build_url() -> None:
    assert parse_url(["--db-type", "duckdb", "--database", "warehouse.duckdb"]) == "duckdb:///warehouse.duckdb"


def test_postgres_friendly_flags_build_url_with_hidden_password() -> None:
    url = parse_url(
        [
            "--db-type",
            "postgres",
            "--host",
            "db.example.com",
            "--port",
            "5432",
            "--database",
            "analytics",
            "--user",
            "reporter",
            "--password",
            "secret",
        ]
    )

    assert url == "postgresql+psycopg://reporter:***@db.example.com:5432/analytics"


def test_environment_variables_build_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DB_SNOOPER_DB_TYPE", "mysql")
    monkeypatch.setenv("DB_SNOOPER_DB_HOST", "db.example.com")
    monkeypatch.setenv("DB_SNOOPER_DB_PORT", "3306")
    monkeypatch.setenv("DB_SNOOPER_DATABASE", "app")
    monkeypatch.setenv("DB_SNOOPER_DB_USER", "app_user")
    monkeypatch.setenv("DB_SNOOPER_DB_PASSWORD", "secret")

    assert parse_url([]) == "mysql+pymysql://app_user:***@db.example.com:3306/app"


def test_ask_password_uses_secure_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("db_snooper.connection.getpass.getpass", lambda prompt: "prompt-secret")

    url = parse_url(["--db-type", "postgres", "--database", "app", "--user", "app_user", "--ask-password"])

    assert url == "postgresql+psycopg://app_user:***@localhost/app"


def test_missing_connection_exits_with_helpful_error(capsys: pytest.CaptureFixture[str]) -> None:
    parser = argparse.ArgumentParser()
    add_connection_arguments(parser)

    with pytest.raises(SystemExit):
        resolve_database_url(parser.parse_args([]), parser)

    assert "--db-type sqlite --database path/to.db" in capsys.readouterr().err
