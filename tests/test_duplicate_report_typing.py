from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_duplicate_report_module_passes_mypy_strict() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    module_path = repo_root / "scripts" / "ci" / "duplicate_report.py"

    result = subprocess.run(  # noqa: S603  # nosec B603 -- test uruchamia zaufane `python -m mypy` lokalnie
        [sys.executable, "-m", "mypy", "--strict", str(module_path)],
        capture_output=True,
        text=True,
        cwd=repo_root,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
