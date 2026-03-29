from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("script_rel_path", "arguments", "ok_message"),
    [
        (
            Path("scripts/check_single_wiki_hook_names.py"),
            ("scrapers/base/helpers/path.py",),
            "[single-wiki-hook-names] OK",
        ),
        (
            Path("scripts/check_di_antipatterns.py"),
            ("scripts/lib/bootstrap.py",),
            "[di-antipatterns] OK",
        ),
        (
            Path("scripts/check_known_module_typos.py"),
            tuple(),
            "[known-module-typos] OK",
        ),
    ],
)
def test_check_script_runs_from_foreign_cwd(
    tmp_path: Path,
    script_rel_path: Path,
    arguments: tuple[str, ...],
    ok_message: str,
) -> None:
    script_path = REPO_ROOT / script_rel_path

    process = subprocess.run(
        [sys.executable, str(script_path), *arguments],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert process.returncode == 0, process.stdout + process.stderr
    assert ok_message in process.stdout
