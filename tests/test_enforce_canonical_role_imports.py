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


def test_canonical_role_imports_detects_legacy_runner_import(tmp_path: Path) -> None:
    (tmp_path / "bad.py").write_text(
        "from scrapers.runner import ScraperRunner\n",
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
    assert "forbidden import from 'scrapers.runner'" in process.stdout


def test_canonical_role_imports_detects_logic_in_compat_module(tmp_path: Path) -> None:
    scrapers_dir = tmp_path / "scrapers"
    scrapers_dir.mkdir()
    (scrapers_dir / "runner.py").write_text(
        "import warnings\n"
        "from scrapers.runners.scraper_runner import ScraperRunner\n\n"
        "def forbidden_logic() -> int:\n"
        "    return 1\n",
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
    assert "compatibility module must stay thin" in process.stdout
