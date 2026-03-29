from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.ci.git_diff import build_added_lines_map
from scripts.ci.git_diff import parse_added_lines_from_unified_diff
from scripts.ci.io_utils import append_output_vars
from scripts.ci.io_utils import read_json_file
from scripts.ci.io_utils import write_text_file
from scripts.ci.reporting import CiStatus
from scripts.ci.reporting import exit_code_for_status
from scripts.ci.reporting import line_range
from scripts.ci.reporting import resolve_status
from scripts.ci.reporting import split_csv


def test_parse_added_lines_from_unified_diff_parses_hunks() -> None:
    diff_text = (
        "+++ b/src/app.py\n"
        "@@ -1,0 +5,2 @@\n"
        "@@ -10,1 +20 @@\n"
        "+++ b/src/other.py\n"
        "@@ -4 +7,0 @@"
    )

    added = parse_added_lines_from_unified_diff(diff_text)

    assert added["src/app.py"] == {5, 6, 20}
    assert added["src/other.py"] == set()


def test_build_added_lines_map_returns_empty_on_git_error(monkeypatch: Any) -> None:
    class Completed:
        returncode = 1
        stdout = ""

    def fake_run(*_args: Any, **_kwargs: Any) -> Completed:
        return Completed()

    monkeypatch.setattr("scripts.ci.git_diff.subprocess.run", fake_run)

    assert build_added_lines_map("base", "head", ["src/app.py"]) == {}


def test_io_utils_read_write_and_append(tmp_path: Path) -> None:
    text_path = tmp_path / "out" / "report.md"
    write_text_file(text_path, "hello")
    assert text_path.read_text(encoding="utf-8") == "hello"

    output_path = tmp_path / "out" / "github_output.txt"
    append_output_vars(output_path, {"duplicate_count": 3, "duplicate_status": "warn"})
    assert output_path.read_text(encoding="utf-8") == (
        "duplicate_count=3\n"
        "duplicate_status=warn\n"
    )


def test_read_json_file_missing_returns_empty_dict(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.json"
    assert read_json_file(missing_path) == {}


def test_reporting_helpers() -> None:
    assert split_csv("a,b,,c") == ["a", "b", "c"]
    assert line_range({"start": 1, "end": 3}) == "L1-L3"
    assert resolve_status(0, warn_threshold=1, fail_threshold=2) == CiStatus.ok
    assert resolve_status(1, warn_threshold=1, fail_threshold=2) == CiStatus.warn
    assert resolve_status(2, warn_threshold=1, fail_threshold=2) == CiStatus.fail
    assert exit_code_for_status(CiStatus.ok) == 0
    assert exit_code_for_status(CiStatus.warn) == 0
    assert exit_code_for_status(CiStatus.fail) == 1
