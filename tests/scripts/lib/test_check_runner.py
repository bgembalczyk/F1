from __future__ import annotations

from pathlib import Path

from scripts.lib.check_runner import iter_python_paths
from scripts.lib.check_runner import print_report
from scripts.lib.check_runner import run_cli


def test_iter_python_paths_collects_files_from_file_and_directory(tmp_path: Path) -> None:
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    direct_py = tmp_path / "direct.py"
    nested_py = pkg / "nested.py"
    txt = pkg / "note.txt"
    direct_py.write_text("print('x')\n", encoding="utf-8")
    nested_py.write_text("print('y')\n", encoding="utf-8")
    txt.write_text("not python\n", encoding="utf-8")

    result = iter_python_paths([direct_py, pkg, txt])

    assert direct_py in result
    assert nested_py in result
    assert all(path.suffix == ".py" for path in result)


def test_print_report_outputs_ok_and_error(capsys) -> None:
    assert print_report("demo", []) == 0
    ok_output = capsys.readouterr().out
    assert "[demo] OK" in ok_output

    assert print_report("demo", ["first", "second"]) == 1
    err_output = capsys.readouterr().out
    assert "[demo] ERROR" in err_output
    assert "- first" in err_output
    assert "- second" in err_output


def test_run_cli_propagates_runner_result(capsys) -> None:
    exit_code = run_cli("term-check", lambda: ["broken entry"])

    assert exit_code == 1
    assert "[term-check] ERROR" in capsys.readouterr().out
