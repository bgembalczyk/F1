from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING

from scripts.ci import enforce_architecture_adr_reference
from scripts.ci import enforce_new_module_any_policy
from scripts.ci import enforce_no_dead_code
from scripts.ci import mypy_regression_gate
from scripts.ci import validate_pr_description

if TYPE_CHECKING:
    from pathlib import Path


DEAD_CODE_TOOL_ERROR_EXIT = 2


def test_enforce_architecture_main_uses_sys_argv_and_fails_without_adr(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(
        enforce_architecture_adr_reference.sys,
        "argv",
        [
            "enforce_architecture_adr_reference.py",
            "--base-sha",
            "base",
            "--head-sha",
            "head",
        ],
    )
    monkeypatch.setattr(
        enforce_architecture_adr_reference,
        "list_changed_files",
        lambda *_args: ["layers/pipeline.py"],
    )
    monkeypatch.setattr(
        enforce_architecture_adr_reference,
        "has_non_cosmetic_changes",
        lambda *_args: True,
    )
    monkeypatch.setattr(
        enforce_architecture_adr_reference,
        "collect_commit_messages",
        lambda *_args: "commit without adr",
    )
    fake_policy = SimpleNamespace(
        is_architecture_path=lambda path: path.startswith("layers/"),
        is_cosmetic_line=lambda _line: False,
        should_require_adr_for_architecture_diff=lambda **_kwargs: True,
        has_adr_reference=lambda *_args: False,
    )
    monkeypatch.setattr(
        enforce_architecture_adr_reference,
        "DEFAULT_ADR_ENFORCEMENT_POLICY",
        fake_policy,
    )

    exit_code = enforce_architecture_adr_reference.main()

    out = capsys.readouterr().out
    assert exit_code == 1
    assert "wymagają referencji ADR-XXXX" in out


def test_enforce_architecture_main_uses_sys_argv_and_skips_without_arch_changes(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(
        enforce_architecture_adr_reference.sys,
        "argv",
        [
            "enforce_architecture_adr_reference.py",
            "--base-sha",
            "base",
            "--head-sha",
            "head",
        ],
    )
    monkeypatch.setattr(
        enforce_architecture_adr_reference,
        "list_changed_files",
        lambda *_args: [],
    )

    exit_code = enforce_architecture_adr_reference.main()

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "Brak zmian w ścieżkach architektonicznych" in out


def test_enforce_new_module_any_policy_main_uses_sys_argv_pass_and_fail(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(
        enforce_new_module_any_policy.sys,
        "argv",
        [
            "enforce_new_module_any_policy.py",
            "--base-sha",
            "base",
            "--head-sha",
            "head",
        ],
    )

    monkeypatch.setattr(
        enforce_new_module_any_policy,
        "_new_python_files",
        lambda *_args: ["layers/new_module.py"],
    )
    monkeypatch.setattr(
        enforce_new_module_any_policy,
        "_scan_file",
        lambda _path: ["layers/new_module.py:3: użyto 'Any' bez uzasadnienia"],
    )
    fail_code = enforce_new_module_any_policy.main()
    fail_out = capsys.readouterr().out
    assert fail_code == 1
    assert "Znaleziono naruszenia polityki Any" in fail_out

    monkeypatch.setattr(enforce_new_module_any_policy, "_scan_file", lambda _path: [])
    pass_code = enforce_new_module_any_policy.main()
    pass_out = capsys.readouterr().out
    assert pass_code == 0
    assert "Polityka Any dla nowych modułów: OK" in pass_out


def test_enforce_no_dead_code_main_uses_sys_argv_and_reports_error(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(
        enforce_no_dead_code.sys,
        "argv",
        ["enforce_no_dead_code.py", "layers"],
    )
    monkeypatch.setattr(
        enforce_no_dead_code.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=DEAD_CODE_TOOL_ERROR_EXIT),
    )

    exit_code = enforce_no_dead_code.main()

    out = capsys.readouterr().out
    assert exit_code == DEAD_CODE_TOOL_ERROR_EXIT
    assert "Potential dead code detected" in out


def test_validate_pr_description_main_uses_sys_argv_with_file_input(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    body = """
## SRP impact
ok

## DRY impact
ok

## Contracts changed
none

## Backward compatibility
no impact

## DoD
done

## Code review evidence
```\npytest -q\n```

- [x] Testy kontraktowe
- [x] Brak nowych Any
- [x] Brak nowych magic strings
- [x] Brak nowych print
- [x] Złożoność i długość modułów
- [x] Spójność rejestru konfiguracji i implementacji
- [x] Wyjątki tylko jawnie uzasadnione
- [x] Zaktualizowany ADR/docs
""".strip()
    body_file = tmp_path / "pr_body.md"
    body_file.write_text(body, encoding="utf-8")

    monkeypatch.setattr(
        validate_pr_description.sys,
        "argv",
        ["validate_pr_description.py", "--pr-body-file", str(body_file)],
    )
    ok_code = validate_pr_description.main()
    ok_out = capsys.readouterr().out
    assert ok_code == 0
    assert "validation passed" in ok_out

    body_file.write_text("## SRP impact\nonly one section", encoding="utf-8")
    fail_code = validate_pr_description.main()
    fail_out = capsys.readouterr().out
    assert fail_code == 1
    assert "Missing required section heading" in fail_out
    assert "Checklist item must be checked" in fail_out


def test_mypy_regression_gate_main_uses_sys_argv_and_reports_regression(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        mypy_regression_gate.sys,
        "argv",
        [
            "mypy_regression_gate.py",
            "--base-sha",
            "abc1234",
            "--head-sha",
            "def5678",
            "--error-budget",
            "5",
        ],
    )

    monkeypatch.setattr(mypy_regression_gate, "_git", lambda *_args: None)
    monkeypatch.setattr(
        mypy_regression_gate.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=0),
    )

    calls: list[Path] = []

    def _fake_run_mypy(repo_dir: Path) -> tuple[int, str]:
        calls.append(repo_dir)
        if len(calls) == 1:
            return 1, "base output"
        return 3, "head output"

    monkeypatch.setattr(mypy_regression_gate, "_run_mypy", _fake_run_mypy)

    exit_code = mypy_regression_gate.main()

    out = capsys.readouterr().out
    assert exit_code == 1
    assert "Regresja typowania" in out
    assert "=== BASE OUTPUT ===" in out
    assert "=== HEAD OUTPUT ===" in out


def test_mypy_regression_gate_fails_on_error_budget_without_regression(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        mypy_regression_gate.sys,
        "argv",
        [
            "mypy_regression_gate.py",
            "--base-sha",
            "abc1234",
            "--head-sha",
            "def5678",
            "--error-budget",
            "1",
        ],
    )
    monkeypatch.setattr(mypy_regression_gate, "_git", lambda *_args: None)
    monkeypatch.setattr(
        mypy_regression_gate.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=0),
    )

    calls: list[Path] = []

    def _fake_run_mypy(repo_dir: Path) -> tuple[int, str]:
        calls.append(repo_dir)
        if len(calls) == 1:
            return 5, "base output"
        return 2, "head output"

    monkeypatch.setattr(mypy_regression_gate, "_run_mypy", _fake_run_mypy)

    exit_code = mypy_regression_gate.main()

    out = capsys.readouterr().out
    assert exit_code == 1
    assert "Przekroczony budżet błędów mypy" in out
