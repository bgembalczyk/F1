from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts/ci/enforce_canonical_role_imports.py"


def test_canonical_role_imports_passes_on_repo() -> None:
    process = subprocess.run(  # nosec B603
        [sys.executable, str(SCRIPT_PATH)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert process.returncode == 0, process.stdout + process.stderr
    assert "[enforce_canonical_role_imports] OK" in process.stdout


def test_canonical_role_imports_detects_forbidden_path(tmp_path: Path) -> None:
    (tmp_path / "bad.py").write_text(
        "from scrapers.base_domain_roles import Extractor\n",
        encoding="utf-8",
    )

    process = subprocess.run(  # nosec B603
        [sys.executable, str(SCRIPT_PATH)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert process.returncode == 1
    assert "forbidden import from 'scrapers.base_domain_roles'" in process.stdout
