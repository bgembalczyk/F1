import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from scripts.diff_runs import _read_text, _canonical_json, _canonicalize, _collect_files, diff_runs, main


def test_read_text(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text("hello", encoding="utf-8")
    assert _read_text(p) == "hello"


def test_canonical_json():
    data = {"b": 2, "a": 1}
    # Should sort keys
    expected = json.dumps(data, sort_keys=True, indent=2) + "\n"
    assert _canonical_json(data) == expected


def test_canonicalize_json(tmp_path):
    p = tmp_path / "test.json"
    p.write_text('{"b": 2, "a": 1}', encoding="utf-8")
    expected = json.dumps({"a": 1, "b": 2}, sort_keys=True, indent=2) + "\n"
    assert _canonicalize(p) == expected


def test_canonicalize_jsonl(tmp_path):
    p = tmp_path / "test.jsonl"
    p.write_text('{"b": 2, "a": 1}\n\n{"d": 4, "c": 3}\n', encoding="utf-8")
    data = [{"a": 1, "b": 2}, {"c": 3, "d": 4}]
    expected = json.dumps(data, sort_keys=True, indent=2) + "\n"
    assert _canonicalize(p) == expected


def test_canonicalize_text(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text("hello", encoding="utf-8")
    assert _canonicalize(p) == "hello"


def test_collect_files_file(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text("hello")
    res = _collect_files(p)
    assert res == {Path("test.txt"): p}


def test_collect_files_dir(tmp_path):
    d = tmp_path / "dir"
    d.mkdir()
    p1 = d / "a.txt"
    p1.write_text("a")
    d2 = d / "sub"
    d2.mkdir()
    p2 = d2 / "b.txt"
    p2.write_text("b")

    res = _collect_files(d)
    assert res == {
        Path("a.txt"): p1,
        Path("sub/b.txt"): p2
    }


def test_diff_runs_identical(tmp_path, capsys):
    d1 = tmp_path / "left"
    d1.mkdir()
    (d1 / "a.txt").write_text("hello")

    d2 = tmp_path / "right"
    d2.mkdir()
    (d2 / "a.txt").write_text("hello")

    assert diff_runs(d1, d2) == 0
    out, err = capsys.readouterr()
    assert out == ""


def test_diff_runs_only_left(tmp_path, capsys):
    d1 = tmp_path / "left"
    d1.mkdir()
    (d1 / "a.txt").write_text("hello")

    d2 = tmp_path / "right"
    d2.mkdir()

    assert diff_runs(d1, d2) == 1
    out, err = capsys.readouterr()
    assert "ONLY_LEFT a.txt" in out


def test_diff_runs_only_right(tmp_path, capsys):
    d1 = tmp_path / "left"
    d1.mkdir()

    d2 = tmp_path / "right"
    d2.mkdir()
    (d2 / "a.txt").write_text("hello")

    assert diff_runs(d1, d2) == 1
    out, err = capsys.readouterr()
    assert "ONLY_RIGHT a.txt" in out


def test_diff_runs_diff(tmp_path, capsys):
    d1 = tmp_path / "left"
    d1.mkdir()
    (d1 / "a.txt").write_text("hello")

    d2 = tmp_path / "right"
    d2.mkdir()
    (d2 / "a.txt").write_text("world")

    assert diff_runs(d1, d2) == 1
    out, err = capsys.readouterr()
    assert "DIFF a.txt" in out
    assert "-hello" in out
    assert "+world" in out


def test_main(monkeypatch):
    monkeypatch.setattr("sys.argv", ["diff_runs.py", "left", "right"])
    with patch("scripts.diff_runs.diff_runs", return_value=0) as mock_diff:
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
        mock_diff.assert_called_once_with(Path("left"), Path("right"))
