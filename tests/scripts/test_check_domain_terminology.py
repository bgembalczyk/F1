from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts import check_domain_terminology


@pytest.fixture()
def terminology_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "docs").mkdir()
    (repo / "models" / "safe").mkdir(parents=True)
    (repo / "layers").mkdir()

    (repo / "docs" / "DOMAIN_GLOSSARY.md").write_text(
        """
# Glossary

```
constructor standings -> team standings
```
""",
        encoding="utf-8",
    )
    return repo


def test_run_check_reports_forbidden_terms_and_skips_allowlist(
    terminology_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = terminology_repo
    violating = repo / "layers" / "violating.py"
    violating.write_text("text = 'constructor standings'\n", encoding="utf-8")

    allowed = repo / "models" / "records" / "factories"
    allowed.mkdir(parents=True)
    (allowed / "build.py").write_text(
        "text = 'constructor standings'\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(check_domain_terminology, "REPO_ROOT", repo)

    errors = check_domain_terminology.run_check()

    assert len(errors) == 1
    assert "forbidden term 'constructor standings'" in errors[0]
    assert "layers/violating.py" in errors[0]


def test_cli_success_and_failure_exit_codes_and_stdout(
    terminology_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = terminology_repo
    monkeypatch.setattr(check_domain_terminology, "REPO_ROOT", repo)

    assert check_domain_terminology.main([]) == 0
    assert "[domain-terminology] OK" in capsys.readouterr().out

    (repo / "layers" / "bad.py").write_text(
        "value = 'constructor standings'\n",
        encoding="utf-8",
    )
    assert check_domain_terminology.main([]) == 1
    assert "[domain-terminology] ERROR" in capsys.readouterr().out


def test_cli_ignores_unknown_arguments_for_backward_compatibility() -> None:
    script_path = (
        Path(__file__).resolve().parents[2] / "scripts" / "check_domain_terminology.py"
    )

    proc = subprocess.run(
        [sys.executable, str(script_path), "--unknown-option"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0
    assert "[domain-terminology]" in proc.stdout
    assert proc.stderr == ""
