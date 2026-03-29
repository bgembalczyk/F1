from __future__ import annotations

from pathlib import Path
import subprocess
import sys


def test_single_wiki_hook_names_runs_from_foreign_cwd(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "check_single_wiki_hook_names.py"
    target_path = tmp_path / "target.py"
    target_path.write_text("class PlainModule:\n    pass\n", encoding="utf-8")

    process = subprocess.run(
        [sys.executable, str(script_path), str(target_path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert process.returncode == 0, process.stdout + process.stderr
    assert "[single-wiki-hook-names] OK" in process.stdout
