from __future__ import annotations

from pathlib import Path

import pytest

from scripts import check_known_module_typos


@pytest.mark.parametrize(
    "typo_module_name",
    [
        "contants.py",
        "section_soruce_adapter.py",
    ],
)
def test_check_known_module_typos_detects_module_name_typos(
    monkeypatch,
    capsys,
    typo_module_name: str,
) -> None:
    monkeypatch.setattr(check_known_module_typos, "REPO_ROOT", Path("/tmp/repo"))
    monkeypatch.setattr(
        check_known_module_typos,
        "run_known_typos_check",
        lambda _root: [f"found typo module: /tmp/repo/{typo_module_name}"],
    )

    exit_code = check_known_module_typos.main([])

    out = capsys.readouterr().out
    assert exit_code == 1
    assert "[known-module-typos] ERROR" in out
    assert f"- found typo module: /tmp/repo/{typo_module_name}" in out


def test_check_known_module_typos_returns_success_without_typos(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(check_known_module_typos, "REPO_ROOT", Path("/tmp/repo"))
    monkeypatch.setattr(
        check_known_module_typos,
        "run_known_typos_check",
        lambda _root: [],
    )

    exit_code = check_known_module_typos.main([])

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "[known-module-typos] OK" in out


@pytest.mark.parametrize(
    "errors,expected_lines",
    [
        (
            ["found typo module: /tmp/repo/contants.py"],
            [
                "[known-module-typos] ERROR",
                "- found typo module: /tmp/repo/contants.py",
            ],
        ),
        (
            [
                "missing expected module: /tmp/repo/scrapers/wiki/constants.py",
                "found typo import in layers/bad_import.py",
            ],
            [
                "[known-module-typos] ERROR",
                "- missing expected module: /tmp/repo/scrapers/wiki/constants.py",
                "- found typo import in layers/bad_import.py",
            ],
        ),
    ],
)
def test_check_known_module_typos_error_output_format_and_exit_code(
    monkeypatch,
    capsys,
    errors: list[str],
    expected_lines: list[str],
) -> None:
    monkeypatch.setattr(check_known_module_typos, "REPO_ROOT", Path("/tmp/repo"))
    monkeypatch.setattr(
        check_known_module_typos,
        "run_known_typos_check",
        lambda _root: errors,
    )

    exit_code = check_known_module_typos.main([])

    out_lines = capsys.readouterr().out.strip().splitlines()
    assert exit_code == 1
    assert out_lines == expected_lines
