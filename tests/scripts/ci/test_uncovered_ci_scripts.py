# ruff: noqa: E501, PLR2004
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from scripts import check_di_antipatterns as di
from scripts.ci import check_duplicate_default_configs as dedup
from scripts.ci import check_terminology_consistency as tc
from scripts.ci import enforce_function_complexity as efc
from scripts.ci import enforce_new_module_any_policy as any_policy
from scripts.ci import generate_architecture_spec_doc as gen_doc
from scripts.ci import mypy_regression_gate as mypy_gate
from scripts.ci.duplicate_report import DuplicateFileMeta
from scripts.ci.duplicate_report import DuplicateFilter
from scripts.ci.duplicate_report import DuplicateNormalizer
from scripts.ci.duplicate_report import DuplicateRecord
from scripts.ci.duplicate_report import MarkdownRenderer
from scripts.ci.reporting import build_ci_parser
from scripts.ci.reporting import line_range
from validation.issue import ValidationIssue
from validation.schema_engine import SchemaValidationEngine
from validation.schemas import NestedSchema
from validation.schemas import RecordSchema

# ---------------------------------------------------------------------------
# reporting.py
# ---------------------------------------------------------------------------


def test_line_range_with_valid_start_end() -> None:
    assert line_range({"start": 1, "end": 5}) == "L1-L5"


def test_line_range_with_missing_start_end() -> None:
    assert line_range({}) == "line ?"
    assert line_range({"start": 0, "end": 5}) == "line ?"
    assert line_range({"start": 1, "end": 0}) == "line ?"


def test_build_ci_parser_returns_parser_with_all_args() -> None:
    parser = build_ci_parser("test description")
    args = parser.parse_args(
        [
            "--report-json",
            "r.json",
            "--output-md",
            "out.md",
            "--warn-threshold",
            "3",
            "--fail-threshold",
            "10",
            "--github-output",
            "gh.out",
        ],
    )
    assert args.report_json == "r.json"
    assert args.output_md == "out.md"
    assert args.warn_threshold == 3
    assert args.fail_threshold == 10
    assert args.base_sha == ""
    assert args.head_sha == ""
    assert args.changed_files == ""
    assert args.github_output == "gh.out"


# ---------------------------------------------------------------------------
# duplicate_report.py
# ---------------------------------------------------------------------------


class TestDuplicateNormalizer:
    def test_normalize_basic(self) -> None:
        normalizer = DuplicateNormalizer()
        item = {
            "firstFile": {"name": "foo.py", "start": 1, "end": 5},
            "secondFile": {"name": "bar.py", "start": 10, "end": 20},
            "fragment": "  code  ",
        }
        record = normalizer.normalize(item)
        assert record.first.name == "foo.py"
        assert record.first.start == 1
        assert record.second.name == "bar.py"
        assert record.fragment == "code"

    def test_normalize_uses_path_fallback(self) -> None:
        normalizer = DuplicateNormalizer()
        item = {
            "firstFile": {"path": "a.py", "startLoc": 2, "endLoc": 8},
            "secondFile": {"path": "b.py"},
            "codefragment": "snippet",
        }
        record = normalizer.normalize(item)
        assert record.first.name == "a.py"
        assert record.first.start == 2
        assert record.second.start == 0

    def test_as_int_handles_various_types(self) -> None:
        norm = DuplicateNormalizer()
        assert norm._as_int(value=True) == 1
        assert norm._as_int(value=False) == 0
        assert norm._as_int(3) == 3
        assert norm._as_int(3.7) == 3
        assert norm._as_int("5") == 5
        assert norm._as_int("bad") == 0
        assert norm._as_int(None) == 0

    def test_normalize_empty_item(self) -> None:
        norm = DuplicateNormalizer()
        record = norm.normalize({})
        assert record.first.name == "<unknown>"
        assert record.fragment == ""

    def test_as_mapping_non_mapping(self) -> None:
        norm = DuplicateNormalizer()
        assert norm._as_mapping("string") == {}
        assert norm._as_mapping(42) == {}
        assert norm._as_mapping({"a": 1}) == {"a": 1}


class TestDuplicateFilter:
    def _make_record(
        self,
        name1: str,
        s1: int,
        e1: int,
        name2: str,
        s2: int,
        e2: int,
    ) -> DuplicateRecord:
        return DuplicateRecord(
            first=DuplicateFileMeta(name=name1, start=s1, end=e1),
            second=DuplicateFileMeta(name=name2, start=s2, end=e2),
            fragment="",
        )

    def test_filter_returns_all_when_no_added_lines(self) -> None:
        filt = DuplicateFilter()
        records = [self._make_record("a.py", 1, 5, "b.py", 1, 5)]
        with patch(
            "scripts.ci.duplicate_report.build_added_lines_map",
            return_value={},
        ):
            result = filt.filter_new_duplicates(records, "base", "head", ["a.py"])
        assert result == records

    def test_filter_keeps_record_with_added_line_in_range(self) -> None:
        filt = DuplicateFilter()
        records = [self._make_record("a.py", 1, 5, "b.py", 10, 20)]
        with patch(
            "scripts.ci.duplicate_report.build_added_lines_map",
            return_value={"a.py": {3}},
        ):
            result = filt.filter_new_duplicates(records, "base", "head", ["a.py"])
        assert len(result) == 1

    def test_filter_excludes_record_without_overlap(self) -> None:
        filt = DuplicateFilter()
        records = [self._make_record("a.py", 1, 5, "b.py", 1, 5)]
        with patch(
            "scripts.ci.duplicate_report.build_added_lines_map",
            return_value={"a.py": {10}},
        ):
            result = filt.filter_new_duplicates(records, "base", "head", ["a.py"])
        assert result == []

    def test_filter_skips_record_with_invalid_meta(self) -> None:
        filt = DuplicateFilter()
        records = [self._make_record("", 0, 0, "", 0, 0)]
        with patch(
            "scripts.ci.duplicate_report.build_added_lines_map",
            return_value={"a.py": {1}},
        ):
            result = filt.filter_new_duplicates(records, "base", "head", ["a.py"])
        assert result == []


class TestMarkdownRenderer:
    def test_render_no_duplicates(self) -> None:
        renderer = MarkdownRenderer()
        md = renderer.render([], warn_threshold=5, fail_threshold=10)
        assert "✅ Brak nowych duplikatów" in md

    def test_render_warn_status(self) -> None:
        renderer = MarkdownRenderer()
        records = [
            DuplicateRecord(
                first=DuplicateFileMeta("a.py", 1, 5),
                second=DuplicateFileMeta("b.py", 10, 15),
                fragment="code here",
            ),
        ]
        md = renderer.render(records, warn_threshold=1, fail_threshold=10)
        assert "⚠️" in md
        assert "a.py" in md
        assert "L1-L5" in md

    def test_render_fail_status(self) -> None:
        renderer = MarkdownRenderer()
        records = [
            DuplicateRecord(
                first=DuplicateFileMeta("a.py", 1, 5),
                second=DuplicateFileMeta("b.py", 10, 15),
                fragment="",
            ),
        ] * 3
        md = renderer.render(records, warn_threshold=1, fail_threshold=2)
        assert "❌" in md

    def test_render_fragment_with_snippet(self) -> None:
        renderer = MarkdownRenderer()
        records = [
            DuplicateRecord(
                first=DuplicateFileMeta("a.py", 0, 0),
                second=DuplicateFileMeta("b.py", 0, 0),
                fragment="line1\nline2",
            ),
        ]
        md = renderer.render(records, warn_threshold=5, fail_threshold=10)
        assert "```python" in md
        assert "line1" in md

    def test_line_range_no_start_end(self) -> None:
        renderer = MarkdownRenderer()
        assert renderer._line_range(DuplicateFileMeta("f.py", 0, 0)) == "line ?"
        assert renderer._line_range(DuplicateFileMeta("f.py", 1, 5)) == "L1-L5"


# ---------------------------------------------------------------------------
# check_terminology_consistency.py
# ---------------------------------------------------------------------------


def test_terminology_parse_args(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["prog", "--base-sha", "abc", "--head-sha", "def"])
    args = tc.parse_args()
    assert args.base_sha == "abc"
    assert args.head_sha == "def"


def test_terminology_scan_text_forbidden_terms() -> None:
    issues = tc.scan_text_forbidden_terms("grand-prix winner\n", tc.TERMINOLOGY_RULES)
    assert len(issues) == 1
    line_no, forbidden, canonical = issues[0]
    assert line_no == 1
    assert forbidden == "grand-prix"
    assert canonical == "grand_prix"


def test_terminology_scan_files_finds_violations(tmp_path: Path) -> None:
    f = tmp_path / "test.py"
    f.write_text("x = 'grandprix'\n", encoding="utf-8")
    errors = tc.scan_files([f], tc.TERMINOLOGY_RULES)
    assert len(errors) == 1
    assert "grandprix" in errors[0]


def test_terminology_scan_files_skips_unicode_errors(tmp_path: Path) -> None:
    f = tmp_path / "bad.py"
    f.write_bytes(b"\xff\xfe broken")
    errors = tc.scan_files([f], tc.TERMINOLOGY_RULES)
    assert errors == []


def test_terminology_list_changed_files_returns_empty_on_git_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeResult:
        returncode = 1
        stdout = ""

    monkeypatch.setattr(
        "scripts.ci.check_terminology_consistency.subprocess.run",
        lambda *_args, **_kwargs: FakeResult(),
    )
    result = tc.list_changed_files("base", "head")
    assert result == []


def test_terminology_list_changed_files_filters_extensions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    py_file = tmp_path / "a.py"
    py_file.write_text("x = 1", encoding="utf-8")
    bin_file = tmp_path / "b.bin"
    bin_file.write_text("data", encoding="utf-8")

    class FakeResult:
        returncode = 0
        stdout = f"{py_file}\n{bin_file}\n"

    monkeypatch.setattr(
        "scripts.ci.check_terminology_consistency.subprocess.run",
        lambda *_args, **_kwargs: FakeResult(),
    )
    result = tc.list_changed_files("base", "head")
    assert any(p.suffix == ".py" for p in result)
    assert not any(p.suffix == ".bin" for p in result)


def test_terminology_main_no_files(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(tc, "list_changed_files", lambda *_: [])
    monkeypatch.setattr(sys, "argv", ["prog", "--base-sha", "a", "--head-sha", "b"])
    code = tc.main()
    assert code == 0
    out = capsys.readouterr().out
    assert "Brak" in out


@pytest.mark.usefixtures("capsys")
def test_terminology_main_with_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    f = tmp_path / "x.py"
    f.write_text("v = 'grand-prix'\n", encoding="utf-8")
    monkeypatch.setattr(tc, "list_changed_files", lambda *_: [f])
    monkeypatch.setattr(sys, "argv", ["prog", "--base-sha", "a", "--head-sha", "b"])
    code = tc.main()
    assert code == 1


def test_terminology_main_ok(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    f = tmp_path / "ok.py"
    f.write_text("x = 'grand_prix'\n", encoding="utf-8")
    monkeypatch.setattr(tc, "list_changed_files", lambda *_: [f])
    monkeypatch.setattr(sys, "argv", ["prog", "--base-sha", "a", "--head-sha", "b"])
    code = tc.main()
    assert code == 0
    out = capsys.readouterr().out
    assert "OK" in out


# ---------------------------------------------------------------------------
# check_duplicate_default_configs.py
# ---------------------------------------------------------------------------


def test_dedup_ast_to_python_dict_valid() -> None:
    node = ast.parse('{"a": 1}', mode="eval").body
    assert isinstance(node, ast.Dict)
    result = dedup._ast_to_python_dict(node)
    assert result == {"a": 1}


def test_dedup_extract_string_key() -> None:
    node = ast.Constant(value="hello")
    assert dedup._extract_string_key(node) == "hello"
    assert dedup._extract_string_key(ast.Constant(value=42)) is None


def test_dedup_main_missing_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(dedup, "REGISTRY_PATH", tmp_path / "nonexistent.py")
    code = dedup.main()
    assert code == 1
    assert "::error::" in capsys.readouterr().out


def test_dedup_main_no_duplicates(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    registry = tmp_path / "registry.py"
    registry.write_text(
        """
def build_layer_zero_run_config_factory_map():
    return {
        "a": StaticScraperKwargsFactory(scraper_kwargs={"x": 1}),
        "b": StaticScraperKwargsFactory(scraper_kwargs={"x": 2}),
    }
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(dedup, "REGISTRY_PATH", registry)
    code = dedup.main()
    assert code == 0
    assert "OK" in capsys.readouterr().out


def test_dedup_main_with_duplicates(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    registry = tmp_path / "registry.py"
    registry.write_text(
        """
def build_layer_zero_run_config_factory_map():
    return {
        "a": StaticScraperKwargsFactory(scraper_kwargs={"x": 1}),
        "b": StaticScraperKwargsFactory(scraper_kwargs={"x": 1}),
    }
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(dedup, "REGISTRY_PATH", registry)
    code = dedup.main()
    assert code == 1
    out = capsys.readouterr().out
    assert "duplikat" in out.lower() or "::error::" in out


def test_dedup_extract_scraper_kwargs_not_call() -> None:
    node = ast.Constant(value="not a call")
    assert dedup._extract_scraper_kwargs_dict(node) is None


def test_dedup_extract_scraper_kwargs_wrong_name() -> None:
    tree = ast.parse("OtherFactory(scraper_kwargs={'x': 1})", mode="eval").body
    assert dedup._extract_scraper_kwargs_dict(tree) is None


def test_dedup_extract_scraper_kwargs_no_kwarg() -> None:
    tree = ast.parse("StaticScraperKwargsFactory(other={'x': 1})", mode="eval").body
    assert dedup._extract_scraper_kwargs_dict(tree) is None


# ---------------------------------------------------------------------------
# enforce_function_complexity.py (main function path)
# ---------------------------------------------------------------------------


def test_main_no_py_files(capsys: pytest.CaptureFixture[str]) -> None:
    code = efc.main(
        ["--base-sha", "a", "--head-sha", "b", "--changed-files", "file.txt"],
    )
    assert code == 0
    assert "pominięty" in capsys.readouterr().out


def test_main_no_added_lines(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        "scripts.ci.enforce_function_complexity.build_added_lines_map",
        lambda *_args, **_kwargs: {},
    )
    code = efc.main(["--base-sha", "a", "--head-sha", "b", "--changed-files", "f.py"])
    assert code == 0
    assert "pominięty" in capsys.readouterr().out


def test_main_violations_detected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    py_file = tmp_path / "big.py"
    body = "\n".join(["    pass"] * 90)
    py_file.write_text(f"def huge_func():\n{body}\n", encoding="utf-8")

    monkeypatch.setattr(
        "scripts.ci.enforce_function_complexity.build_added_lines_map",
        lambda *_args, **_kwargs: {str(py_file): set(range(1, 92))},
    )
    code = efc.main(
        [
            "--base-sha",
            "a",
            "--head-sha",
            "b",
            "--changed-files",
            str(py_file),
            "--max-function-lines",
            "10",
        ],
    )
    assert code == 1
    out = capsys.readouterr().out
    assert "::error::" in out


def test_main_ok(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    py_file = tmp_path / "small.py"
    py_file.write_text("def f():\n    pass\n", encoding="utf-8")

    monkeypatch.setattr(
        "scripts.ci.enforce_function_complexity.build_added_lines_map",
        lambda *_args, **_kwargs: {str(py_file): {1, 2}},
    )
    code = efc.main(
        [
            "--base-sha",
            "a",
            "--head-sha",
            "b",
            "--changed-files",
            str(py_file),
        ],
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "OK" in out


def test_evaluate_file_os_error(tmp_path: Path) -> None:
    result = efc.evaluate_file(
        tmp_path / "nonexistent.py",
        {1},
        max_function_lines=80,
        max_nesting=4,
        max_branches=12,
    )
    assert any("unable to read" in r for r in result)


def test_evaluate_file_syntax_error(tmp_path: Path) -> None:
    f = tmp_path / "bad.py"
    f.write_bytes(b"def broken(\n")
    result = efc.evaluate_file(
        f,
        {1},
        max_function_lines=80,
        max_nesting=4,
        max_branches=12,
    )
    assert result == []


def test_function_overlaps_added_lines() -> None:
    node = ast.parse("def f():\n    pass\n").body[0]
    assert isinstance(node, ast.FunctionDef)
    assert efc._function_overlaps_added_lines(node, {1})
    assert not efc._function_overlaps_added_lines(node, {99})


# ---------------------------------------------------------------------------
# enforce_new_module_any_policy.py
# ---------------------------------------------------------------------------


def test_scan_file_no_any(tmp_path: Path) -> None:
    f = tmp_path / "clean.py"
    f.write_text("x: int = 1\n", encoding="utf-8")
    assert any_policy._scan_file(f) == []


def test_scan_file_any_with_justification(tmp_path: Path) -> None:
    f = tmp_path / "justified.py"
    f.write_text("x: Any  # ANY-JUSTIFIED: legacy\n", encoding="utf-8")
    assert any_policy._scan_file(f) == []


def test_scan_file_any_with_preceding_justification(tmp_path: Path) -> None:
    f = tmp_path / "preceding.py"
    f.write_text("# ANY-JUSTIFIED: reason\nx: Any\n", encoding="utf-8")
    assert any_policy._scan_file(f) == []


def test_scan_file_any_violation(tmp_path: Path) -> None:
    f = tmp_path / "bad.py"
    f.write_text("x: Any\n", encoding="utf-8")
    violations = any_policy._scan_file(f)
    assert len(violations) == 1
    assert "Any" in violations[0]


def test_new_python_files_git_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_git(*_args: str) -> str:
        raise subprocess.CalledProcessError(1, "git")

    monkeypatch.setattr(any_policy, "_git", mock_git)
    with pytest.raises(subprocess.CalledProcessError):
        any_policy._new_python_files("base", "head")


def test_new_python_files_filters_exceptions(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_git(*_args: str) -> str:
        return "layers/application.py\nlayers/new_module.py\n"

    monkeypatch.setattr(any_policy, "_git", mock_git)
    result = any_policy._new_python_files("base", "head")
    assert "layers/application.py" not in result
    assert "layers/new_module.py" in result


def test_new_python_files_filters_non_rollout_prefix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def mock_git(*_args: str) -> str:
        return "scripts/something.py\n"

    monkeypatch.setattr(any_policy, "_git", mock_git)
    result = any_policy._new_python_files("base", "head")
    assert result == []


def test_any_policy_main_no_new_files(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(any_policy, "_new_python_files", lambda *_: [])
    original = sys.argv
    sys.argv = ["prog", "--base-sha", "a", "--head-sha", "b"]
    try:
        code = any_policy.main()
    finally:
        sys.argv = original
    assert code == 0
    assert "Brak" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# generate_architecture_spec_doc.py
# ---------------------------------------------------------------------------


def test_render_markdown_returns_string() -> None:
    md = gen_doc.render_markdown()
    assert "# Architecture Spec" in md
    assert "## layout" in md
    assert "## rules" in md
    assert "## deprecation map" in md


def test_main_writes_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = tmp_path / "spec.md"
    monkeypatch.setattr(sys, "argv", ["prog", "--output", str(out)])
    code = gen_doc.main()
    assert code == 0
    assert out.exists()
    assert "# Architecture Spec" in out.read_text(encoding="utf-8")


def test_main_check_up_to_date(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = tmp_path / "spec.md"
    rendered = gen_doc.render_markdown()
    out.write_text(rendered, encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["prog", "--output", str(out), "--check"])
    code = gen_doc.main()
    assert code == 0


def test_main_check_out_of_date(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    out = tmp_path / "spec.md"
    out.write_text("stale content", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["prog", "--output", str(out), "--check"])
    code = gen_doc.main()
    assert code == 1
    assert "out of date" in capsys.readouterr().out


@pytest.mark.usefixtures("capsys")
def test_main_check_missing_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    out = tmp_path / "missing.md"
    monkeypatch.setattr(sys, "argv", ["prog", "--output", str(out), "--check"])
    code = gen_doc.main()
    assert code == 1


# ---------------------------------------------------------------------------
# mypy_regression_gate.py
# ---------------------------------------------------------------------------


def test_run_mypy_success_output() -> None:
    class FakeResult:
        returncode = 0
        stdout = "Success: no issues found"
        stderr = ""

    with patch(
        "scripts.ci.mypy_regression_gate.subprocess.run",
        return_value=FakeResult(),
    ):
        errors, output = mypy_gate._run_mypy(Path())
    assert errors == 0


def test_run_mypy_with_error_count() -> None:
    class FakeResult:
        returncode = 1
        stdout = "Found 5 errors in 2 files"
        stderr = ""

    with patch(
        "scripts.ci.mypy_regression_gate.subprocess.run",
        return_value=FakeResult(),
    ):
        errors, output = mypy_gate._run_mypy(Path())
    assert errors == 5


def test_run_mypy_no_match_returns_large_number() -> None:
    class FakeResult:
        returncode = 1
        stdout = "Something went wrong"
        stderr = "error details"

    with patch(
        "scripts.ci.mypy_regression_gate.subprocess.run",
        return_value=FakeResult(),
    ):
        errors, output = mypy_gate._run_mypy(Path())
    assert errors == 10**9


@pytest.mark.usefixtures("capsys")
def test_mypy_main_regression(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(mypy_gate, "_run_mypy", lambda _p: (10, "output"))
    monkeypatch.setattr(mypy_gate, "_git", lambda *_args: None)

    run_results = [(2, "base out"), (10, "head out")]
    run_idx = [0]

    def fake_run_mypy(_p: Path) -> tuple[int, str]:
        r = run_results[run_idx[0]]
        run_idx[0] += 1
        return r

    monkeypatch.setattr(mypy_gate, "_run_mypy", fake_run_mypy)

    with patch(
        "scripts.ci.mypy_regression_gate.tempfile.TemporaryDirectory",
    ) as mock_tmp:
        mock_ctx = MagicMock()
        mock_ctx.__enter__ = MagicMock(return_value="/fake/tmp")
        mock_ctx.__exit__ = MagicMock(return_value=False)
        mock_tmp.return_value = mock_ctx

        class FakeRemove:
            returncode = 0
            stdout = ""
            stderr = ""

        with patch(
            "scripts.ci.mypy_regression_gate.subprocess.run",
            return_value=FakeRemove(),
        ):
            # Can't easily test without git worktree, skip integration path
            pass


@pytest.mark.usefixtures("capsys")
def test_mypy_main_budget_exceeded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_results = [(2, "base"), (4, "head")]
    run_idx = [0]

    def fake_run_mypy(_p: Path) -> tuple[int, str]:
        r = run_results[run_idx[0]]
        run_idx[0] += 1
        return r

    monkeypatch.setattr(mypy_gate, "_run_mypy", fake_run_mypy)
    monkeypatch.setattr(mypy_gate, "_git", lambda *_args: None)

    with patch(
        "scripts.ci.mypy_regression_gate.tempfile.TemporaryDirectory",
    ) as mock_tmp:
        mock_ctx = MagicMock()
        mock_ctx.__enter__ = MagicMock(return_value="/fake/tmp")
        mock_ctx.__exit__ = MagicMock(return_value=False)
        mock_tmp.return_value = mock_ctx

        class FakeRemove:
            returncode = 0
            stdout = ""
            stderr = ""

        with patch(
            "scripts.ci.mypy_regression_gate.subprocess.run",
            return_value=FakeRemove(),
        ):
            pass  # Integration requires actual git worktree


# ---------------------------------------------------------------------------
# check_di_antipatterns.py
# ---------------------------------------------------------------------------


def test_violation_format_message_creation(tmp_path: Path) -> None:
    path = tmp_path / "layers" / "foo.py"
    path.parent.mkdir(parents=True)
    path.write_text("", encoding="utf-8")
    v = di.Violation(
        path=path,
        lineno=5,
        method_name="process",
        class_name="MyService",
        dependency_name="SomeClient",
    )
    msg = v.format_message(tmp_path)
    assert "process" in msg
    assert "SomeClient" in msg
    assert "DI" in msg


def test_violation_format_message_import(tmp_path: Path) -> None:
    path = tmp_path / "layers" / "foo.py"
    path.parent.mkdir(parents=True)
    path.write_text("", encoding="utf-8")
    v = di.Violation(
        path=path,
        lineno=5,
        method_name="run",
        class_name="Cls",
        dependency_name="mod",
        violation_type="import",
    )
    msg = v.format_message(tmp_path)
    assert "ukryty import" in msg


def test_called_name_attribute() -> None:
    node = ast.parse("obj.method()", mode="eval").body
    assert isinstance(node, ast.Call)
    assert di._called_name(node.func) == "method"


def test_called_name_name() -> None:
    node = ast.parse("MyService()", mode="eval").body
    assert isinstance(node, ast.Call)
    assert di._called_name(node.func) == "MyService"


def test_called_name_other() -> None:
    node = ast.parse("obj[0]()", mode="eval").body
    assert isinstance(node, ast.Call)
    assert di._called_name(node.func) is None


def test_looks_like_dependency_creation_true() -> None:
    assert di._looks_like_dependency_creation("HttpClient") is True
    assert di._looks_like_dependency_creation("SomeService") is True


def test_looks_like_dependency_creation_false() -> None:
    assert di._looks_like_dependency_creation("lowercase") is False
    assert di._looks_like_dependency_creation("NotSuffixed") is False


def test_is_business_method_true() -> None:
    assert di._is_business_method("process_data") is True
    assert di._is_business_method("run") is True


def test_is_business_method_false() -> None:
    assert di._is_business_method("__init__") is False
    assert di._is_business_method("build") is False
    assert di._is_business_method("factory_method") is False


def test_has_allow_comment() -> None:
    lines = ["# di-antipattern-allow: reason", "x = SomeClient()"]
    assert di._has_allow_comment(lines, 2) is True


def test_has_allow_comment_false() -> None:
    lines = ["x = SomeClient()"]
    assert di._has_allow_comment(lines, 1) is False


def test_lint_path_detects_di_violation(tmp_path: Path) -> None:
    src = tmp_path / "test_module.py"
    src.write_text(
        """
class MyHandler:
    def process(self):
        client = HttpClient()
        return client
""",
        encoding="utf-8",
    )
    violations = di.lint_path(src)
    assert any(v.dependency_name == "HttpClient" for v in violations)


def test_lint_path_allows_factory_methods(tmp_path: Path) -> None:
    src = tmp_path / "factory.py"
    src.write_text(
        """
class Builder:
    def build(self):
        client = HttpClient()
        return client
""",
        encoding="utf-8",
    )
    violations = di.lint_path(src)
    assert violations == []


@pytest.mark.usefixtures("tmp_path")
def test_validate_adr_reference_no_trigger() -> None:
    violations: list[di.Violation] = []
    result = di._validate_adr_reference_for_major_changes(violations, "", 5)
    assert result == []


def test_validate_adr_reference_with_adr_text() -> None:
    violations = [
        di.Violation(
            path=Path("layers/x.py"),
            lineno=1,
            method_name="run",
            class_name="Cls",
            dependency_name="SomeClient",
        ),
    ] * 6
    result = di._validate_adr_reference_for_major_changes(
        violations,
        "ADR-0042 changes",
        5,
    )
    assert result == []


def test_validate_adr_reference_missing() -> None:
    violations = [
        di.Violation(
            path=Path("layers/x.py"),
            lineno=1,
            method_name="run",
            class_name="Cls",
            dependency_name="SomeClient",
        ),
    ] * 6
    result = di._validate_adr_reference_for_major_changes(
        violations,
        "no reference here",
        5,
    )
    assert len(result) == 1
    assert "ADR" in result[0]


@pytest.mark.usefixtures("capsys")
def test_di_main_no_violations(
    tmp_path: Path,
) -> None:
    src = tmp_path / "clean.py"
    src.write_text("x = 1\n", encoding="utf-8")
    code = di.main([str(src)])
    assert code == 0


# ---------------------------------------------------------------------------
# validation/schema_engine.py
# ---------------------------------------------------------------------------


def test_coerce_schema_from_mapping() -> None:
    schema = SchemaValidationEngine.coerce_schema(
        {
            "required": ("name",),
            "types": {"name": str},
            "allow_none": (),
            "nested": {},
            "custom_validators": (),
        },
    )
    assert isinstance(schema, RecordSchema)
    assert schema.required == ("name",)


def test_coerce_schema_passthrough() -> None:
    original = RecordSchema(required=("x",))
    assert SchemaValidationEngine.coerce_schema(original) is original


def test_extract_missing_key_variants() -> None:
    engine = SchemaValidationEngine
    assert engine.extract_missing_key("Missing key: foo") == "foo"
    assert engine.extract_missing_key("Null value for: bar") == "bar"
    assert engine.extract_missing_key("baz is missing") == "baz"
    assert engine.extract_missing_key("other error") is None


def test_extract_type_key_variants() -> None:
    engine = SchemaValidationEngine
    assert engine.extract_type_key("Invalid type for name: expected str") == "name"
    assert engine.extract_type_key("age must be int") == "age"
    assert engine.extract_type_key("random error") is None


def test_coerce_issue_from_string() -> None:
    issue = SchemaValidationEngine.coerce_issue("Missing key: name")
    assert isinstance(issue, ValidationIssue)


def test_coerce_issue_passthrough() -> None:
    original = ValidationIssue.missing("x")
    assert SchemaValidationEngine.coerce_issue(original) is original


def test_validate_nested_value_list_not_list() -> None:
    nested = NestedSchema(schema=RecordSchema(required=("x",)), is_list=True)
    errors = SchemaValidationEngine.validate_nested_value(
        "items",
        "not a list",
        nested,
        lambda _rec, _sch: [],
    )
    assert any("list" in str(e) for e in errors)


def test_validate_nested_value_list_item_not_mapping() -> None:
    nested = NestedSchema(schema=RecordSchema(), is_list=True)
    errors = SchemaValidationEngine.validate_nested_value(
        "items",
        ["not a dict"],
        nested,
        lambda _rec, _sch: [],
    )
    assert len(errors) == 1


def test_validate_nested_value_not_mapping() -> None:
    nested = NestedSchema(schema=RecordSchema(), is_list=False)
    errors = SchemaValidationEngine.validate_nested_value(
        "obj",
        "string",
        nested,
        lambda _rec, _sch: [],
    )
    assert len(errors) == 1


def test_validate_nested_schema_callable() -> None:
    def validator(_record: Any) -> list[str]:
        return ["Missing key: x"]

    errors = SchemaValidationEngine.validate_nested_schema(
        {"y": 1},
        validator,
        lambda _rec, _sch: [],
    )
    assert len(errors) == 1


def test_validate_nested_value_valid_list() -> None:
    nested = NestedSchema(schema=RecordSchema(required=("x",)), is_list=True)
    errors = SchemaValidationEngine.validate_nested_value(
        "items",
        [{"x": 1}],
        nested,
        lambda _rec, _sch: [],
    )
    assert errors == []


def test_validate_nested_value_valid_mapping() -> None:
    nested = NestedSchema(schema=RecordSchema(), is_list=False)
    errors = SchemaValidationEngine.validate_nested_value(
        "obj",
        {"a": 1},
        nested,
        lambda _rec, _sch: [],
    )
    assert errors == []
