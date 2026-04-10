from __future__ import annotations

import sys

import pytest

from scripts.ci import enforce_no_scraper_config_alias_imports as gate


def test_collect_alias_import_violations_detects_new_scraper_config_import(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_file = tmp_path / "example.py"
    source_file.write_text(
        "from scrapers.config import ScraperConfig\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(gate, "REPO_ROOT", tmp_path)

    violations = gate.collect_alias_import_violations(
        added_lines_map={"example.py": {1}},
    )

    assert len(violations) == 1
    assert "Zakaz nowego importu aliasu `ScraperConfig`" in violations[0].message


def test_collect_alias_import_violations_ignores_public_api_import(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_file = tmp_path / "ok.py"
    source_file.write_text(
        "from scrapers.configs.public import TableConfig\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(gate, "REPO_ROOT", tmp_path)

    violations = gate.collect_alias_import_violations(
        added_lines_map={"ok.py": {1}},
    )

    assert violations == []


def test_main_reports_errors_when_alias_import_found(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prog",
            "--base-sha",
            "a",
            "--head-sha",
            "b",
        ],
    )
    monkeypatch.setattr(gate, "list_changed_files", lambda *_a, **_k: ["a.py"])
    monkeypatch.setattr(gate, "build_added_lines_map", lambda *_a, **_k: {"a.py": {1}})
    monkeypatch.setattr(
        gate,
        "collect_alias_import_violations",
        lambda **_k: [
            gate.Violation(path="a.py", line=1, message="boom"),
        ],
    )

    assert gate.main() == 1
    assert "::error::a.py:1: boom" in capsys.readouterr().out
