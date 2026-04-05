from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.ci import coverage_wave_report as cwr

TOP_LIMIT = 30
SCRIPT_PATH = Path("scripts/ci/coverage_wave_report.py")
REPO_ROOT = Path()

FIRST_STATEMENT_LINE = 1
SECOND_STATEMENT_LINE = 2
EXPECTED_COVERAGE_PERCENT = 80.0
EXPECTED_STATEMENTS = 10
EXPECTED_EXECUTED = 8
EXPECTED_MISS = 2


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


@pytest.mark.integration()
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


# ---------------------------------------------------------------------------
# _normalize_path
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_normalize_path_strips_root_prefix() -> None:
    path = cwr.ROOT_PREFIX + "scrapers/foo.py"
    assert cwr._normalize_path(path) == "scrapers/foo.py"


@pytest.mark.unit()
def test_normalize_path_leaves_non_root_paths_unchanged() -> None:
    assert cwr._normalize_path("scrapers/foo.py") == "scrapers/foo.py"
    assert cwr._normalize_path("/other/path.py") == "/other/path.py"


# ---------------------------------------------------------------------------
# _load_executed_lines
# ---------------------------------------------------------------------------


def _make_db_with_entries(
    tmp_path: Path,
    entries: list[tuple[str, bytes]],
) -> Path:
    db_path = tmp_path / ".coverage"
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        CREATE TABLE file (id integer primary key, path text);
        CREATE TABLE context (id integer primary key, context text);
        INSERT INTO context VALUES (1, '');
        CREATE TABLE line_bits (
            file_id integer,
            context_id integer,
            numbits blob
        );
        """,
    )
    for path, numbits in entries:
        conn.execute("INSERT INTO file (path) VALUES (?)", (path,))
        fid = conn.execute(
            "SELECT id FROM file WHERE path = ?",
            (path,),
        ).fetchone()[0]
        conn.execute(
            "INSERT INTO line_bits (file_id, context_id, numbits) VALUES (?, 1, ?)",
            (fid, numbits),
        )
    conn.commit()
    conn.close()
    return db_path


@pytest.mark.unit()
def test_load_executed_lines_decodes_numbits(tmp_path: Path) -> None:
    # byte 0b00000001 => line 1 covered
    db = _make_db_with_entries(tmp_path, [("src/foo.py", bytes([0x01]))])
    result = cwr._load_executed_lines(db)
    assert "src/foo.py" in result
    assert 1 in result["src/foo.py"]


@pytest.mark.unit()
def test_load_executed_lines_multiple_bytes(tmp_path: Path) -> None:
    # byte 0xFF (bits 0-7 set) => lines 1-8 covered
    db = _make_db_with_entries(tmp_path, [("src/bar.py", bytes([0xFF]))])
    result = cwr._load_executed_lines(db)
    assert result["src/bar.py"] == set(range(1, 9))


@pytest.mark.unit()
def test_load_executed_lines_normalizes_root_prefix(tmp_path: Path) -> None:
    abs_path = cwr.ROOT_PREFIX + "scrapers/some.py"
    db = _make_db_with_entries(tmp_path, [(abs_path, bytes([0x01]))])
    result = cwr._load_executed_lines(db)
    assert "scrapers/some.py" in result


@pytest.mark.unit()
def test_load_executed_lines_empty_db(tmp_path: Path) -> None:
    db = _make_db_with_entries(tmp_path, [])
    result = cwr._load_executed_lines(db)
    assert result == {}


# ---------------------------------------------------------------------------
# _statement_lines
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_statement_lines_finds_statements(tmp_path: Path) -> None:
    py_file = tmp_path / "sample.py"
    py_file.write_text("x = 1\ny = 2\n", encoding="utf-8")
    lines = cwr._statement_lines(py_file)
    assert 1 in lines
    assert SECOND_STATEMENT_LINE in lines


@pytest.mark.unit()
def test_statement_lines_empty_file(tmp_path: Path) -> None:
    py_file = tmp_path / "empty.py"
    py_file.write_text("", encoding="utf-8")
    lines = cwr._statement_lines(py_file)
    assert lines == set()


# ---------------------------------------------------------------------------
# _collect_misses
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_collect_misses_skips_file_with_no_statements(tmp_path: Path) -> None:
    py_file = tmp_path / "empty.py"
    py_file.write_text("", encoding="utf-8")
    executed = {"empty.py": {1}}
    result = cwr._collect_misses(tmp_path, executed)
    assert result == []


@pytest.mark.unit()
def test_collect_misses_skips_non_python(tmp_path: Path) -> None:
    executed = {"README.md": {1, 2}}
    result = cwr._collect_misses(tmp_path, executed)
    assert result == []


@pytest.mark.unit()
def test_collect_misses_skips_test_files(tmp_path: Path) -> None:
    executed = {"tests/test_foo.py": {1}}
    result = cwr._collect_misses(tmp_path, executed)
    assert result == []


@pytest.mark.unit()
def test_collect_misses_skips_missing_file(tmp_path: Path) -> None:
    executed = {"nonexistent.py": {1}}
    result = cwr._collect_misses(tmp_path, executed)
    assert result == []


@pytest.mark.unit()
def test_collect_misses_counts_correctly(tmp_path: Path) -> None:
    py_file = tmp_path / "mod.py"
    py_file.write_text("a = 1\nb = 2\nc = 3\n", encoding="utf-8")
    # Only line 1 executed
    executed = {"mod.py": {1}}
    result = cwr._collect_misses(tmp_path, executed)
    assert len(result) == 1
    row = result[0]
    assert row.path == "mod.py"
    assert row.executed == 1
    assert row.miss == row.statements - 1


@pytest.mark.unit()
def test_collect_misses_sorted_by_miss_descending(tmp_path: Path) -> None:
    py_a = tmp_path / "a.py"
    py_a.write_text("x = 1\ny = 2\nz = 3\n", encoding="utf-8")  # 3 stmts, 0 executed
    py_b = tmp_path / "b.py"
    py_b.write_text("x = 1\n", encoding="utf-8")  # 1 stmt, 0 executed
    executed = {"a.py": set(), "b.py": set()}
    result = cwr._collect_misses(tmp_path, executed)
    # a.py has more misses, so should come first
    assert result[0].path == "a.py"
    assert result[1].path == "b.py"


# ---------------------------------------------------------------------------
# _wave_for_path
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_wave_for_path_wave1_parser_high_miss() -> None:
    assert cwr._wave_for_path("scrapers/foo/parsers/bar.py", 50) == cwr.WAVE1


@pytest.mark.unit()
def test_wave_for_path_wave1_helper_high_miss() -> None:
    assert cwr._wave_for_path("scrapers/helpers/thing.py", 40) == cwr.WAVE1


@pytest.mark.unit()
def test_wave_for_path_wave1_scripts_ci() -> None:
    assert cwr._wave_for_path("scripts/ci/my_script.py", 50) == cwr.WAVE1


@pytest.mark.unit()
def test_wave_for_path_wave2_domain_service_medium_miss() -> None:
    assert cwr._wave_for_path("scrapers/domain/service.py", 25) == cwr.WAVE2


@pytest.mark.unit()
def test_wave_for_path_wave2_services_directory() -> None:
    assert cwr._wave_for_path("scrapers/seasons/services/foo.py", 30) == cwr.WAVE2


@pytest.mark.unit()
def test_wave_for_path_wave3_any_other_file() -> None:
    assert cwr._wave_for_path("scrapers/foo/bar.py", 5) == cwr.WAVE3


@pytest.mark.unit()
def test_wave_for_path_wave4_zero_misses() -> None:
    assert cwr._wave_for_path("scrapers/foo/bar.py", 0) == cwr.WAVE4


@pytest.mark.unit()
def test_wave_for_path_wave1_requires_min_miss() -> None:
    # miss < WAVE1_MIN_MISS but is a parser -> WAVE3, not WAVE1
    assert cwr._wave_for_path("scrapers/parsers/bar.py", 39) == cwr.WAVE3


@pytest.mark.unit()
def test_wave_for_path_wave2_miss_too_low() -> None:
    # miss < WAVE2_MIN_MISS for domain service -> WAVE3
    assert cwr._wave_for_path("scrapers/domain/service.py", 19) == cwr.WAVE3


@pytest.mark.unit()
def test_wave_for_path_wave2_miss_too_high() -> None:
    # miss > WAVE2_MAX_MISS for domain service (no parser/helper) -> WAVE3
    assert cwr._wave_for_path("scrapers/domain/service.py", 40) == cwr.WAVE3


# ---------------------------------------------------------------------------
# _to_dict
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_to_dict_computes_coverage_percentage() -> None:
    fm = cwr.FileMiss(path="src/foo.py", statements=10, executed=8, miss=2)
    result = cwr._to_dict(fm)
    assert result["coverage"] == EXPECTED_COVERAGE_PERCENT
    assert result["path"] == "src/foo.py"
    assert result["statements"] == EXPECTED_STATEMENTS
    assert result["executed"] == EXPECTED_EXECUTED
    assert result["miss"] == EXPECTED_MISS
    assert "wave" in result


# ---------------------------------------------------------------------------
# _render_top_md
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_render_top_md_empty() -> None:
    result = cwr._render_top_md([])
    assert "# Top remaining misses" in result
    assert "| # |" in result


@pytest.mark.unit()
def test_render_top_md_with_entry() -> None:
    items = [
        {"path": "src/foo.py", "miss": 5, "coverage": 75.0, "wave": cwr.WAVE3},
    ]
    result = cwr._render_top_md(items)
    assert "src/foo.py" in result
    assert "75.0%" in result


# ---------------------------------------------------------------------------
# _render_backlog_md
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_render_backlog_md_empty() -> None:
    result = cwr._render_backlog_md([])
    assert "# Coverage backlog" in result
    assert "Brak plików w top N." in result


@pytest.mark.unit()
def test_render_backlog_md_with_wave1_item() -> None:
    items = [
        {"path": "scripts/ci/foo.py", "miss": 50, "coverage": 40.0, "wave": cwr.WAVE1},
    ]
    result = cwr._render_backlog_md(items)
    assert "scripts/ci/foo.py" in result
    assert cwr.WAVE1 in result


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_main_creates_output_files(tmp_path: Path) -> None:
    py_file = tmp_path / "mod.py"
    py_file.write_text("x = 1\ny = 2\n", encoding="utf-8")

    db = _make_db_with_entries(
        tmp_path,
        [(str(py_file), bytes([0x01]))],  # line 1 covered only
    )
    json_out = tmp_path / "out.json"
    md_out = tmp_path / "out.md"
    backlog_out = tmp_path / "backlog.md"

    args = [
        "--coverage-db",
        str(db),
        "--repo-root",
        str(tmp_path),
        "--top",
        "10",
        "--json-out",
        str(json_out),
        "--md-out",
        str(md_out),
        "--backlog-out",
        str(backlog_out),
    ]
    with patch("sys.argv", ["coverage_wave_report"] + args):
        returncode = cwr.main()
    assert returncode == 0
    assert json_out.exists()
    assert md_out.exists()
    assert backlog_out.exists()
    payload = json.loads(json_out.read_text(encoding="utf-8"))
    assert isinstance(payload, list)
