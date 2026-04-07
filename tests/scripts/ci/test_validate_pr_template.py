from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest

from scripts.ci import validate_pr_template


def _complete_pr_body(*, field_value: str = "tak") -> str:
    checks = "\n".join(
        f"- [x] **{label}**: ok" for label in validate_pr_template.REQUIRED_CHECKBOXES
    )
    fields = "\n".join(
        f"- {field}: {field_value}"
        for field in validate_pr_template.ARCHITECTURE_IMPACT_FIELDS
    )
    headings = "\n".join(validate_pr_template.REQUIRED_HEADINGS)
    return f"{headings}\n\n{checks}\n\n{fields}\n"


def test_collect_template_errors_reports_missing_heading_checkbox_and_field() -> None:
    body = "## Opis zmiany\n"
    fields = validate_pr_template.extract_architecture_fields(body)

    errors = validate_pr_template._collect_template_errors(body, fields)

    assert any("Brak sekcji" in err for err in errors)
    assert any("Checklista niepotwierdzona" in err for err in errors)
    assert any("Brak wartości pola" in err for err in errors)


def test_validate_detailed_architecture_impact_accepts_and_rejects_values() -> None:
    detailed = dict.fromkeys(
        validate_pr_template.ARCHITECTURE_IMPACT_FIELDS,
        "wykonano",
    )
    assert (
        validate_pr_template._validate_detailed_architecture_impact(
            detailed,
        )
        == []
    )

    with_not_applicable = {
        field: ("nie dotyczy" if field == "Dotknięte domeny" else "ok")
        for field in validate_pr_template.ARCHITECTURE_IMPACT_FIELDS
    }

    errors = validate_pr_template._validate_detailed_architecture_impact(
        with_not_applicable,
    )
    assert len(errors) == 1
    assert "nie może mieć wartości 'nie dotyczy'" in errors[0]


def test_main_success_and_error_paths(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_pr_template.py",
            "--base-sha",
            "a",
            "--head-sha",
            "b",
            "--pr-body",
            _complete_pr_body(),
        ],
    )
    monkeypatch.setattr(
        validate_pr_template,
        "list_changed_files",
        lambda *_a, **_k: [],
    )

    assert validate_pr_template.main() == 0
    assert "zakończona sukcesem" in capsys.readouterr().out

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_pr_template.py",
            "--base-sha",
            "a",
            "--head-sha",
            "b",
            "--pr-body",
            _complete_pr_body(field_value="nie dotyczy"),
        ],
    )
    monkeypatch.setattr(
        validate_pr_template,
        "list_changed_files",
        lambda *_a, **_k: ["scrapers/base/helpers.py"],
    )

    assert validate_pr_template.main() == 1
    assert "::error::" in capsys.readouterr().out


def test_list_changed_files_handles_git_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Proc:
        returncode = 1
        stdout = ""

    monkeypatch.setattr(
        validate_pr_template.subprocess,
        "run",
        lambda *_a, **_k: Proc(),
    )

    assert validate_pr_template.list_changed_files("a", "b") == []


def test_cli_argument_validation_stderr(capsys: pytest.CaptureFixture[str]) -> None:
    old_argv = sys.argv
    try:
        sys.argv = ["validate_pr_template.py"]
        try:
            validate_pr_template.main()
            raise AssertionError("expected SystemExit")
        except SystemExit as exc:
            assert exc.code == 2  # noqa: PLR2004
    finally:
        sys.argv = old_argv

    err = capsys.readouterr().err
    assert "usage:" in err
    assert "required" in err
