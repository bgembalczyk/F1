"""Unit tests for scripts/diff_runs.py."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

import scripts.diff_runs as dr

EXPECTED_JSON_KEYS_COUNT = 2
EXPECTED_JSONL_ITEM_COUNT = 2

# ---------------------------------------------------------------------------
# _read_text
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_read_text_returns_file_contents(tmp_path: Path) -> None:
    f = tmp_path / "sample.txt"
    f.write_text("hello world", encoding="utf-8")
    assert dr._read_text(f) == "hello world"


# ---------------------------------------------------------------------------
# _canonical_json
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_canonical_json_sorts_keys() -> None:
    result = dr._canonical_json({"b": 2, "a": 1})
    parsed = json.loads(result)
    assert list(parsed.keys()) == sorted(parsed.keys())


@pytest.mark.unit()
def test_canonical_json_ends_with_newline() -> None:
    result = dr._canonical_json({})
    assert result.endswith("\n")


# ---------------------------------------------------------------------------
# _canonicalize
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_canonicalize_json_file(tmp_path: Path) -> None:
    f = tmp_path / "data.json"
    f.write_text('{"b": 2, "a": 1}', encoding="utf-8")
    result = dr._canonicalize(f)
    parsed = json.loads(result)
    assert parsed["a"] == 1
    assert parsed["b"] == EXPECTED_JSON_KEYS_COUNT


@pytest.mark.unit()
def test_canonicalize_jsonl_file(tmp_path: Path) -> None:
    f = tmp_path / "data.jsonl"
    f.write_text('{"b": 2}\n{"a": 1}\n', encoding="utf-8")
    result = dr._canonicalize(f)
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) == EXPECTED_JSONL_ITEM_COUNT


@pytest.mark.unit()
def test_canonicalize_text_file(tmp_path: Path) -> None:
    f = tmp_path / "data.txt"
    f.write_text("raw content", encoding="utf-8")
    assert dr._canonicalize(f) == "raw content"


# ---------------------------------------------------------------------------
# _collect_files
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_collect_files_from_single_file(tmp_path: Path) -> None:
    f = tmp_path / "file.txt"
    f.write_text("x", encoding="utf-8")
    result = dr._collect_files(f)
    assert Path("file.txt") in result
    assert result[Path("file.txt")] == f


@pytest.mark.unit()
def test_collect_files_from_directory(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    result = dr._collect_files(tmp_path)
    assert Path("a.txt") in result
    assert Path("b.txt") in result


# ---------------------------------------------------------------------------
# diff_runs
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_diff_runs_no_difference_returns_zero(tmp_path: Path) -> None:
    left = tmp_path / "left"
    right = tmp_path / "right"
    left.mkdir()
    right.mkdir()
    (left / "file.txt").write_text("same", encoding="utf-8")
    (right / "file.txt").write_text("same", encoding="utf-8")
    assert dr.diff_runs(left, right) == 0


@pytest.mark.unit()
def test_diff_runs_different_content_returns_one(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    left = tmp_path / "left"
    right = tmp_path / "right"
    left.mkdir()
    right.mkdir()
    (left / "file.txt").write_text("old", encoding="utf-8")
    (right / "file.txt").write_text("new", encoding="utf-8")
    result = dr.diff_runs(left, right)
    assert result == 1
    captured = capsys.readouterr()
    assert "DIFF" in captured.out


@pytest.mark.unit()
def test_diff_runs_only_in_right(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    left = tmp_path / "left"
    right = tmp_path / "right"
    left.mkdir()
    right.mkdir()
    (right / "new.txt").write_text("x", encoding="utf-8")
    result = dr.diff_runs(left, right)
    assert result == 1
    assert "ONLY_RIGHT" in capsys.readouterr().out


@pytest.mark.unit()
def test_diff_runs_only_in_left(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    left = tmp_path / "left"
    right = tmp_path / "right"
    left.mkdir()
    right.mkdir()
    (left / "old.txt").write_text("x", encoding="utf-8")
    result = dr.diff_runs(left, right)
    assert result == 1
    assert "ONLY_LEFT" in capsys.readouterr().out


@pytest.mark.unit()
def test_diff_runs_json_canonical_comparison(tmp_path: Path) -> None:
    left = tmp_path / "left"
    right = tmp_path / "right"
    left.mkdir()
    right.mkdir()
    # Same JSON content but different key ordering - should match canonically
    (left / "data.json").write_text('{"a": 1, "b": 2}', encoding="utf-8")
    (right / "data.json").write_text('{"b": 2, "a": 1}', encoding="utf-8")
    assert dr.diff_runs(left, right) == 0


@pytest.mark.unit()
def test_diff_runs_single_file_comparison(tmp_path: Path) -> None:
    left = tmp_path / "left.txt"
    right = tmp_path / "right.txt"
    # When comparing two files with different names, they'll appear as
    # ONLY_LEFT and ONLY_RIGHT since keys are based on basename
    left.write_text("content", encoding="utf-8")
    right.write_text("content", encoding="utf-8")
    result = dr.diff_runs(left, right)
    assert result == 1


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_main_exits_with_zero_on_identical_dirs(tmp_path: Path) -> None:
    left = tmp_path / "left"
    right = tmp_path / "right"
    left.mkdir()
    right.mkdir()
    (left / "file.txt").write_text("same", encoding="utf-8")
    (right / "file.txt").write_text("same", encoding="utf-8")

    with patch("sys.argv", ["diff_runs", str(left), str(right)]):
        with pytest.raises(SystemExit) as exc_info:
            dr.main()
    assert exc_info.value.code == 0


@pytest.mark.unit()
def test_main_exits_with_one_on_different_dirs(tmp_path: Path) -> None:
    left = tmp_path / "left"
    right = tmp_path / "right"
    left.mkdir()
    right.mkdir()
    (left / "file.txt").write_text("old", encoding="utf-8")
    (right / "file.txt").write_text("new", encoding="utf-8")

    with patch("sys.argv", ["diff_runs", str(left), str(right)]):
        with pytest.raises(SystemExit) as exc_info:
            dr.main()
    assert exc_info.value.code == 1
