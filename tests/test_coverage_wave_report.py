import pytest
import sqlite3
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import scripts.ci.coverage_wave_report as cwr
from scripts.ci.coverage_wave_report import (
    FileMiss,
    _parse_args,
    _normalize_path,
    _load_executed_lines,
    _statement_lines,
    _collect_misses,
    _wave_for_path,
    _to_dict,
    _render_top_md,
    _render_backlog_md,
    main,
    ROOT_PREFIX,
    WAVE1, WAVE2, WAVE3, WAVE4
)


def test_file_miss():
    fm = FileMiss(path="a.py", statements=10, executed=5, miss=5)
    assert fm.path == "a.py"
    assert fm.miss == 5


def test_normalize_path():
    assert _normalize_path(f"{ROOT_PREFIX}tests/a.py") == "tests/a.py"
    assert _normalize_path("tests/b.py") == "tests/b.py"


def test_load_executed_lines(tmp_path):
    db_path = tmp_path / ".coverage"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE file (id INTEGER PRIMARY KEY, path TEXT)")
    conn.execute("CREATE TABLE line_bits (file_id INTEGER, numbits BLOB)")
    conn.execute("INSERT INTO file (id, path) VALUES (1, 'a.py')")

    # 0x01 = bit 0 (line 1), 0x04 = bit 2 (line 3)
    conn.execute("INSERT INTO line_bits (file_id, numbits) VALUES (1, ?)", (bytes([0x05]),))
    conn.commit()
    conn.close()

    res = _load_executed_lines(db_path)
    assert res == {"a.py": {1, 3}}


def test_statement_lines(tmp_path):
    p = tmp_path / "a.py"
    p.write_text("a = 1\nb = 2\n\nif a:\n    pass\n")
    res = _statement_lines(p)
    assert res == {1, 2, 4, 5}


def test_collect_misses(tmp_path):
    p = tmp_path / "a.py"
    p.write_text("a = 1\nb = 2\n")

    # Ignore missing files, non-python files, and test files
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/test_a.py").write_text("a=1")
    (tmp_path / "b.txt").write_text("b=1")

    executed = {
        "a.py": {1},
        "missing.py": {1},
        "tests/test_a.py": {1},
        "b.txt": {1}
    }

    res = _collect_misses(tmp_path, executed)
    assert len(res) == 1
    assert res[0].path == "a.py"
    assert res[0].statements == 2
    assert res[0].executed == 1
    assert res[0].miss == 1


def test_wave_for_path():
    assert _wave_for_path("scripts/ci/report.py", 50) == WAVE1
    assert _wave_for_path("domain/test.py", 25) == WAVE2
    assert _wave_for_path("other.py", 5) == WAVE3
    assert _wave_for_path("perfect.py", 0) == WAVE4


def test_to_dict():
    fm = FileMiss(path="a.py", statements=10, executed=8, miss=2)
    res = _to_dict(fm)
    assert res["path"] == "a.py"
    assert res["miss"] == 2
    assert res["coverage"] == 80.0
    assert res["wave"] == WAVE3


def test_render_top_md():
    top = [{"path": "a.py", "miss": 5, "coverage": 50.0, "wave": WAVE3}]
    res = _render_top_md(top)
    assert "| 1 | `a.py` | 5 | 50.0% | Fala 3 |" in res


def test_render_backlog_md():
    top = [
        {"path": "a.py", "miss": 50, "coverage": 50.0, "wave": WAVE1},
        {"path": "b.py", "miss": 5, "coverage": 90.0, "wave": WAVE3}
    ]
    res = _render_backlog_md(top)
    assert "- [ ] `a.py` - miss: 50, coverage: 50.0%" in res
    assert "- [ ] `b.py` - miss: 5, coverage: 90.0%" in res
    assert "- Brak plików w top N." in res # For Wave 2 and 4


def test_main(monkeypatch, tmp_path):
    db_path = tmp_path / ".coverage"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE file (id INTEGER PRIMARY KEY, path TEXT)")
    conn.execute("CREATE TABLE line_bits (file_id INTEGER, numbits BLOB)")
    conn.execute("INSERT INTO file (id, path) VALUES (1, 'a.py')")
    conn.execute("INSERT INTO line_bits (file_id, numbits) VALUES (1, ?)", (bytes([0x01]),)) # line 1 executed
    conn.commit()
    conn.close()

    p = tmp_path / "a.py"
    p.write_text("a = 1\nb = 2\nc = 3\n")

    json_out = tmp_path / "out.json"
    md_out = tmp_path / "out.md"
    backlog_out = tmp_path / "backlog.md"

    monkeypatch.setattr("sys.argv", [
        "script",
        "--coverage-db", str(db_path),
        "--repo-root", str(tmp_path),
        "--top", "10",
        "--json-out", str(json_out),
        "--md-out", str(md_out),
        "--backlog-out", str(backlog_out)
    ])

    assert main() == 0

    assert json_out.exists()
    assert md_out.exists()
    assert backlog_out.exists()

    data = json.loads(json_out.read_text())
    assert len(data) == 1
    assert data[0]["path"] == "a.py"
    assert data[0]["miss"] == 2
