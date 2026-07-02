from __future__ import annotations

from db_snooper.cli import main


def test_profile_subcommand_dispatches(monkeypatch) -> None:
    called = {}

    def fake_main(argv, prog=None):
        called["profile"] = argv
        called["profile_prog"] = prog
        return 0

    monkeypatch.setattr("db_snooper.cli.profiler.main", fake_main)

    assert main(["profile", "--db-type", "sqlite", "--database", "app.sqlite"]) == 0
    assert called["profile"] == ["--db-type", "sqlite", "--database", "app.sqlite"]
    assert called["profile_prog"] == "db-snooper profile"


def test_links_subcommand_dispatches(monkeypatch) -> None:
    called = {}

    def fake_main(argv, prog=None):
        called["links"] = argv
        called["links_prog"] = prog
        return 0

    monkeypatch.setattr("db_snooper.cli.schema_linker.main", fake_main)

    assert main(["links", "--db-type", "sqlite", "--database", "app.sqlite"]) == 0
    assert called["links"] == ["--db-type", "sqlite", "--database", "app.sqlite"]
    assert called["links_prog"] == "db-snooper links"
