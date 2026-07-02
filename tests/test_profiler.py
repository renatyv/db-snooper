from __future__ import annotations

from sqlalchemy import create_engine, text

from db_snooper.profiler import ProfileOptions, profile_database


def test_small_table_rows_redact_sensitive_values() -> None:
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("create table users (id integer primary key, email text, password_hash text)"))
        conn.execute(text("insert into users values (1, 'a@example.com', 'secret-hash')"))

    output = profile_database(engine, ProfileOptions())

    assert "CREATE TABLE users" in output
    assert "-- total rows=1" in output
    assert '"password_hash": "[REDACTED]"' in output
    assert "secret-hash" not in output


def test_large_table_profiles_columns_without_dumping_sensitive_values() -> None:
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(
            text(
                "create table events ("
                "id integer primary key, status text not null, amount integer, api_token text)"
            )
        )
        for i in range(60):
            conn.execute(
                text("insert into events (id, status, amount, api_token) values (:id, :status, :amount, :token)"),
                {
                    "id": i + 1,
                    "status": "done" if i % 2 else "pending",
                    "amount": i,
                    "token": f"token-{i}",
                },
            )

    output = profile_database(engine, ProfileOptions())

    assert "-- id: unique values=60, range=1..60" in output
    assert "-- status values: done=30, pending=30" in output
    assert "-- amount numeric: min=0, median=29.5, max=59" in output
    assert "-- api_token: nulls=0, non_nulls=60, distinct=60" in output
    assert "-- api_token values:" not in output
    assert "-- api_token top_values:" not in output
    assert "token-" not in output


def test_include_and_exclude_tables() -> None:
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("create table keep_me (id integer)"))
        conn.execute(text("create table skip_me (id integer)"))

    output = profile_database(
        engine,
        ProfileOptions(include_tables=frozenset({"keep_me", "skip_me"}), exclude_tables=frozenset({"skip_me"})),
    )

    assert "CREATE TABLE keep_me" in output
    assert "CREATE TABLE skip_me" not in output
