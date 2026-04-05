from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

TOP_LIMIT = 30
SCRIPT_PATH = Path("scripts/ci/coverage_wave_report.py")
REPO_ROOT = Path()


def _create_test_coverage_db(tmp_path: Path) -> Path:
    """Create a minimal .coverage SQLite database for testing."""
    db_path = tmp_path / ".coverage"
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(
            """
            CREATE TABLE coverage_schema (version integer);
            INSERT INTO coverage_schema VALUES (7);
            CREATE TABLE meta (key text, value text);
            INSERT INTO meta VALUES ('has_arcs', '1');
            CREATE TABLE file (id integer primary key, path text);
            CREATE TABLE context (id integer primary key, context text);
            INSERT INTO context VALUES (1, '');
            CREATE TABLE line_bits (
                file_id integer,
                context_id integer,
                numbits blob
            );
            CREATE TABLE arc (
                file_id integer,
                context_id integer,
                fromno integer,
                tono integer
            );
            CREATE TABLE tracer (file_id integer, tracer text);
            """,
        )
        script_path = str(SCRIPT_PATH.resolve())
        conn.execute("INSERT INTO file (path) VALUES (?)", (script_path,))
        file_id = conn.execute(
            "SELECT id FROM file WHERE path = ?",
            (script_path,),
        ).fetchone()[0]
        conn.execute(
            "INSERT INTO line_bits (file_id, context_id, numbits) VALUES (?, 1, ?)",
            (file_id, bytes([0xFF, 0xFF])),
        )
        conn.commit()
    finally:
        conn.close()
    return db_path


@pytest.mark.integration
def test_coverage_wave_report_generates_outputs(tmp_path: Path) -> None:
    assert SCRIPT_PATH.exists()
    assert SCRIPT_PATH.is_file()
    python_executable = Path(sys.executable).resolve()
    assert python_executable.exists()

    coverage_db = _create_test_coverage_db(tmp_path)

    out_json = tmp_path / "coverage_top.json"
    out_md = tmp_path / "coverage_top.md"
    backlog = tmp_path / "COVERAGE_WAVE_BACKLOG.md"

    result = subprocess.run(  # - trusted local command and fixed args
        [
            str(python_executable),
            str(SCRIPT_PATH),
            "--coverage-db",
            str(coverage_db),
            "--repo-root",
            str(REPO_ROOT.resolve()),
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

    md_text = out_md.read_text(encoding="utf-8")
    assert "# Top remaining misses" in md_text

    backlog_text = backlog.read_text(encoding="utf-8")
    assert "# Coverage backlog" in backlog_text
    assert "Fala 1" in backlog_text
