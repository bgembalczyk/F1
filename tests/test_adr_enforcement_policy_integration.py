from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GIT_BIN = shutil.which("git") or "git"


def _git(cwd: Path, *args: str) -> str:
    # nosec B603 -- test uruchamia zaufane lokalne `git`
    proc = subprocess.run(  # noqa: S603
        [GIT_BIN, *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout.strip()


def _run_enforcement(
    cwd: Path,
    base_sha: str,
    head_sha: str,
    *,
    pr_title: str = "",
    pr_body: str = "",
) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT)
    # nosec B603 -- test uruchamia bieżący interpreter i lokalny moduł
    return subprocess.run(  # noqa: S603
        [
            sys.executable,
            "-m",
            "scripts.ci.enforce_architecture_adr_reference",
            "--base-sha",
            base_sha,
            "--head-sha",
            head_sha,
            "--pr-title",
            pr_title,
            "--pr-body",
            pr_body,
        ],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def _init_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.name", "CI Bot")
    _git(repo, "config", "user.email", "ci@example.com")

    (repo / "layers").mkdir(parents=True)
    (repo / "models").mkdir(parents=True)

    (repo / "layers" / "pipeline.py").write_text(
        "class Pipeline:\n    pass\n",
        encoding="utf-8",
    )
    (repo / "models" / "driver.py").write_text(
        "class Driver:\n    pass\n",
        encoding="utf-8",
    )

    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "base commit")
    base_sha = _git(repo, "rev-parse", "HEAD")
    return repo, base_sha


def test_enforcement_fails_without_adr_for_architectural_non_cosmetic_change(
    tmp_path: Path,
) -> None:
    repo, base_sha = _init_repo(tmp_path)
    (repo / "layers" / "pipeline.py").write_text(
        "class Pipeline:\n    def run(self) -> int:\n        return 1\n",
        encoding="utf-8",
    )

    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "architectural change without adr")
    head_sha = _git(repo, "rev-parse", "HEAD")

    proc = _run_enforcement(repo, base_sha, head_sha)

    assert proc.returncode == 1
    assert "wymagają referencji ADR-XXXX" in proc.stdout


def test_enforcement_passes_when_adr_reference_is_present(tmp_path: Path) -> None:
    repo, base_sha = _init_repo(tmp_path)
    (repo / "layers" / "pipeline.py").write_text(
        "class Pipeline:\n    def run(self) -> int:\n        return 1\n",
        encoding="utf-8",
    )

    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "ADR-0003 architectural change")
    head_sha = _git(repo, "rev-parse", "HEAD")

    proc = _run_enforcement(repo, base_sha, head_sha)

    assert proc.returncode == 0
    assert "Referencja ADR-XXXX znaleziona" in proc.stdout


def test_enforcement_skips_cosmetic_only_architectural_change(tmp_path: Path) -> None:
    repo, base_sha = _init_repo(tmp_path)
    (repo / "layers" / "pipeline.py").write_text(
        "# komentarz kosmetyczny\nclass Pipeline:\n    pass\n",
        encoding="utf-8",
    )

    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "cosmetic architecture change")
    head_sha = _git(repo, "rev-parse", "HEAD")

    proc = _run_enforcement(repo, base_sha, head_sha)

    assert proc.returncode == 0
    assert "wyłącznie zmiany kosmetyczne" in proc.stdout


def test_enforcement_skips_non_architectural_changes(tmp_path: Path) -> None:
    repo, base_sha = _init_repo(tmp_path)
    (repo / "models" / "driver.py").write_text(
        "class Driver:\n    category = 'main'\n",
        encoding="utf-8",
    )

    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "model only change")
    head_sha = _git(repo, "rev-parse", "HEAD")

    proc = _run_enforcement(repo, base_sha, head_sha)

    assert proc.returncode == 0
    assert "Brak zmian w ścieżkach architektonicznych" in proc.stdout
