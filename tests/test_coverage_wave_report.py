from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

TOP_LIMIT = 30


def test_coverage_wave_report_generates_outputs() -> None:
    script = Path("scripts/ci/coverage_wave_report.py")
    assert script.exists()

    out_json = Path("artifacts/test_coverage_top.json")
    out_md = Path("artifacts/test_coverage_top.md")
    backlog = Path("docs/COVERAGE_WAVE_BACKLOG.test.md")

    for candidate in (out_json, out_md, backlog):
        if candidate.exists():
            candidate.unlink()

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--coverage-db",
            ".coverage",
            "--repo-root",
            ".",
            "--top",
            str(TOP_LIMIT),
            "--json-out",
            str(out_json),
            "--md-out",
            str(out_md),
            "--backlog-out",
            str(backlog),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert out_json.exists()
    assert out_md.exists()
    assert backlog.exists()

    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert isinstance(payload, list)
    assert len(payload) <= TOP_LIMIT
    assert all({"path", "miss", "coverage", "wave"}.issubset(row) for row in payload)

    md_text = out_md.read_text(encoding="utf-8")
    assert "# Top remaining misses" in md_text

    backlog_text = backlog.read_text(encoding="utf-8")
    assert "# Coverage backlog" in backlog_text
    assert "Fala 1" in backlog_text
