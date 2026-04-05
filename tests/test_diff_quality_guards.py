# ruff: noqa: SLF001
from __future__ import annotations

import ast
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from scripts.ci import enforce_diff_quality_guards as guards

if TYPE_CHECKING:
    from pathlib import Path

EXPECTED_ADDED_LINES_COUNT = 2
LAST_ADDED_LINE_NUMBER = 3

# ---------------------------------------------------------------------------
# Violation format
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_violation_format_returns_colon_separated_string() -> None:
    v = guards.Violation(path="src/foo.py", line=42, message="some error")
    assert v.format() == "src/foo.py:42: some error"


# ---------------------------------------------------------------------------
# parse_args
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_parse_args_parses_base_and_head_sha() -> None:
    args = guards.parse_args(["--base-sha", "abc123", "--head-sha", "def456"])
    assert args.base_sha == "abc123"
    assert args.head_sha == "def456"


# ---------------------------------------------------------------------------
# _iter_added_python_lines
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_iter_added_python_lines_skips_non_python_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(guards, "REPO_ROOT", tmp_path)
    result = guards._iter_added_python_lines({"README.md": {1}})
    assert result == []


@pytest.mark.unit()
def test_iter_added_python_lines_skips_missing_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(guards, "REPO_ROOT", tmp_path)
    result = guards._iter_added_python_lines({"nonexistent.py": {1}})
    assert result == []


@pytest.mark.unit()
def test_iter_added_python_lines_returns_line_tuples(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    py_file = tmp_path / "module.py"
    py_file.write_text("line1\nline2\nline3\n", encoding="utf-8")
    monkeypatch.setattr(guards, "REPO_ROOT", tmp_path)
    result = guards._iter_added_python_lines({"module.py": {1, 3}})
    assert len(result) == EXPECTED_ADDED_LINES_COUNT
    paths = [r[0] for r in result]
    lines = [r[1] for r in result]
    assert all(p == "module.py" for p in paths)
    assert 1 in lines
    assert LAST_ADDED_LINE_NUMBER in lines


@pytest.mark.unit()
def test_iter_added_python_lines_skips_out_of_bounds_lines(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    py_file = tmp_path / "mod.py"
    py_file.write_text("x = 1\n", encoding="utf-8")
    monkeypatch.setattr(guards, "REPO_ROOT", tmp_path)
    result = guards._iter_added_python_lines({"mod.py": {100}})
    assert result == []


# ---------------------------------------------------------------------------
# _check_new_prints
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_check_new_prints_detects_print_call(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    py_file = tmp_path / "mod.py"
    py_file.write_text("print('hello')\n", encoding="utf-8")
    monkeypatch.setattr(guards, "REPO_ROOT", tmp_path)
    violations = guards._check_new_prints({"mod.py": {1}})
    assert len(violations) == 1
    assert "print" in violations[0].message.lower()


@pytest.mark.unit()
def test_check_new_prints_allows_non_print_lines(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    py_file = tmp_path / "mod.py"
    py_file.write_text("x = 1\n", encoding="utf-8")
    monkeypatch.setattr(guards, "REPO_ROOT", tmp_path)
    violations = guards._check_new_prints({"mod.py": {1}})
    assert violations == []


# ---------------------------------------------------------------------------
# _check_critical_defaults_duplication
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_check_critical_defaults_duplication_detects_duplicate_literal(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from scripts.ci.quality_gate_constants import CRITICAL_DEFAULT_LITERALS

    if not CRITICAL_DEFAULT_LITERALS:
        pytest.skip("No critical default literals defined")

    literal = next(iter(CRITICAL_DEFAULT_LITERALS))
    py_file = tmp_path / "mod.py"
    py_file.write_text(f'X = "{literal}"\n', encoding="utf-8")
    monkeypatch.setattr(guards, "REPO_ROOT", tmp_path)
    violations = guards._check_critical_defaults_duplication({"mod.py": {1}})
    assert len(violations) >= 1


@pytest.mark.unit()
def test_check_critical_defaults_skips_central_defaults_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from scripts.ci.quality_gate_constants import CRITICAL_DEFAULT_LITERALS

    if not CRITICAL_DEFAULT_LITERALS:
        pytest.skip("No critical default literals defined")

    literal = next(iter(CRITICAL_DEFAULT_LITERALS))
    # Create a file at the same path as CENTRAL_DEFAULTS_FILE
    central = tmp_path / "central.py"
    central.write_text(f'X = "{literal}"\n', encoding="utf-8")
    monkeypatch.setattr(guards, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(guards, "CENTRAL_DEFAULTS_FILE", central)
    violations = guards._check_critical_defaults_duplication({"central.py": {1}})
    # The central file itself should be skipped
    assert violations == []


# ---------------------------------------------------------------------------
# _iter_python_asts
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_iter_python_asts_skips_non_python(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(guards, "REPO_ROOT", tmp_path)
    result = guards._iter_python_asts({"README.md": {1}})
    assert result == []


@pytest.mark.unit()
def test_iter_python_asts_skips_missing_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(guards, "REPO_ROOT", tmp_path)
    result = guards._iter_python_asts({"missing.py": {1}})
    assert result == []


@pytest.mark.unit()
def test_iter_python_asts_skips_syntax_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    py_file = tmp_path / "bad.py"
    py_file.write_text("def broken(:\n", encoding="utf-8")
    monkeypatch.setattr(guards, "REPO_ROOT", tmp_path)
    result = guards._iter_python_asts({"bad.py": {1}})
    assert result == []


@pytest.mark.unit()
def test_iter_python_asts_returns_ast_tuple(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    py_file = tmp_path / "mod.py"
    py_file.write_text("x = 1\n", encoding="utf-8")
    monkeypatch.setattr(guards, "REPO_ROOT", tmp_path)
    result = guards._iter_python_asts({"mod.py": {1}})
    assert len(result) == 1
    rel_path, source, tree, added_set = result[0]
    assert rel_path == "mod.py"
    assert isinstance(tree, ast.AST)


# ---------------------------------------------------------------------------
# _is_unjustified_broad_exception
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_is_unjustified_broad_exception_returns_false_for_non_handler() -> None:
    node = ast.parse("x = 1").body[0]
    assert not guards._is_unjustified_broad_exception(node, {1}, ["x = 1"])


@pytest.mark.unit()
def test_is_unjustified_broad_exception_returns_false_for_non_added_line() -> None:
    code = "try:\n    pass\nexcept Exception:\n    pass\n"
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            # line 3, but we say only line 1 was added
            assert not guards._is_unjustified_broad_exception(
                node,
                {1},
                code.splitlines(),
            )
            break


@pytest.mark.unit()
def test_is_unjustified_broad_exception_returns_false_for_specific_exception() -> None:
    code = "try:\n    pass\nexcept ValueError:\n    pass\n"
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            assert not guards._is_unjustified_broad_exception(
                node,
                {3},
                code.splitlines(),
            )
            break


# ---------------------------------------------------------------------------
# _extract_target_tuple
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_extract_target_tuple_from_simple_assignment() -> None:
    code = "MY_TUPLE = ('a', 'b', 'c')\n"
    tree = ast.parse(code)
    result = guards._extract_target_tuple(tree.body[0], "MY_TUPLE")
    assert result is not None
    assert isinstance(result, ast.Tuple)


@pytest.mark.unit()
def test_extract_target_tuple_returns_none_for_wrong_symbol() -> None:
    code = "MY_TUPLE = ('a', 'b')\n"
    tree = ast.parse(code)
    result = guards._extract_target_tuple(tree.body[0], "OTHER")
    assert result is None


@pytest.mark.unit()
def test_extract_target_tuple_from_ann_assign() -> None:
    code = "MY_TUPLE: tuple[str, ...] = ('a', 'b')\n"
    tree = ast.parse(code)
    result = guards._extract_target_tuple(tree.body[0], "MY_TUPLE")
    assert result is not None


@pytest.mark.unit()
def test_extract_target_tuple_multiple_targets_returns_none() -> None:
    code = "a = b = ('x',)\n"
    tree = ast.parse(code)
    result = guards._extract_target_tuple(tree.body[0], "a")
    assert result is None


# ---------------------------------------------------------------------------
# _extract_runner_map_keys
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_extract_runner_map_keys_returns_dict_string_keys(tmp_path: Path) -> None:
    code = "def build_map():\n    return {'key1': 1, 'key2': 2}\n"
    py_file = tmp_path / "registry.py"
    py_file.write_text(code, encoding="utf-8")
    result = guards._extract_runner_map_keys(py_file, "build_map")
    assert set(result) == {"key1", "key2"}


@pytest.mark.unit()
def test_extract_runner_map_keys_returns_empty_for_missing_function(
    tmp_path: Path,
) -> None:
    code = "x = 1\n"
    py_file = tmp_path / "registry.py"
    py_file.write_text(code, encoding="utf-8")
    result = guards._extract_runner_map_keys(py_file, "missing_function")
    assert result == ()


@pytest.mark.unit()
def test_extract_runner_map_keys_returns_empty_for_non_dict_return(
    tmp_path: Path,
) -> None:
    code = "def build_map():\n    return []\n"
    py_file = tmp_path / "registry.py"
    py_file.write_text(code, encoding="utf-8")
    result = guards._extract_runner_map_keys(py_file, "build_map")
    assert result == ()


@pytest.mark.unit()
def test_extract_runner_map_keys_handles_non_return_statements(
    tmp_path: Path,
) -> None:
    code = "def build_map():\n    x = 1\n    return {'k': 1}\n"
    py_file = tmp_path / "registry.py"
    py_file.write_text(code, encoding="utf-8")
    result = guards._extract_runner_map_keys(py_file, "build_map")
    assert result == ("k",)


# ---------------------------------------------------------------------------
# _check_registry_implementation_drift
# ---------------------------------------------------------------------------


def test_broad_exception_requires_justification_annotation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    test_file = tmp_path / "sample.py"
    test_file.write_text(
        "try:\n    pass\nexcept Exception:\n    pass\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guards, "REPO_ROOT", tmp_path)

    violations = guards._check_broad_exceptions_with_justification({"sample.py": {3}})

    assert len(violations) == 1
    assert "justified-exception" in violations[0].message


def test_broad_exception_with_marker_is_allowed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    test_file = tmp_path / "sample.py"
    test_file.write_text(
        "try:\n    pass\n"
        "except Exception:  # justified-exception: normalization boundary\n"
        "    pass\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guards, "REPO_ROOT", tmp_path)

    violations = guards._check_broad_exceptions_with_justification({"sample.py": {3}})

    assert violations == []


def test_registry_implementation_drift_check_passes_for_current_repo() -> None:
    assert guards._check_registry_implementation_drift() == []


@pytest.mark.unit()
def test_check_registry_drift_returns_violation_when_registries_empty(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    empty_file = tmp_path / "empty.py"
    empty_file.write_text("x = 1\n", encoding="utf-8")
    monkeypatch.setattr(guards, "SEED_REGISTRY_FILE", empty_file)
    monkeypatch.setattr(guards, "RUNNER_REGISTRY_FILE", empty_file)
    violations = guards._check_registry_implementation_drift()
    assert len(violations) >= 1
    assert any("sparsować" in v.message for v in violations)


# ---------------------------------------------------------------------------
# _extract_string_tuple_assignment
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_extract_string_tuple_assignment_finds_tuple(tmp_path: Path) -> None:
    code = "MY_TUPLE = ('alpha', 'beta')\n"
    py_file = tmp_path / "constants.py"
    py_file.write_text(code, encoding="utf-8")
    result = guards._extract_string_tuple_assignment(py_file, "MY_TUPLE")
    assert set(result) == {"alpha", "beta"}


@pytest.mark.unit()
def test_extract_string_tuple_assignment_returns_empty_for_missing(
    tmp_path: Path,
) -> None:
    py_file = tmp_path / "constants.py"
    py_file.write_text("x = 1\n", encoding="utf-8")
    result = guards._extract_string_tuple_assignment(py_file, "MY_TUPLE")
    assert result == ()


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_main_returns_zero_when_no_violations(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(guards, "REPO_ROOT", tmp_path)

    with (
        patch.object(guards, "_check_registry_implementation_drift", return_value=[]),
        patch("scripts.ci.git_diff.list_changed_files", return_value=[]),
        patch(
            "scripts.ci.git_diff.build_added_lines_map",
            return_value={},
        ),
    ):
        result = guards.main(["--base-sha", "abc", "--head-sha", "def"])
    assert result == 0


@pytest.mark.unit()
def test_main_returns_one_when_violations_exist(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    violation = guards.Violation(path="src/foo.py", line=1, message="bad print")
    monkeypatch.setattr(guards, "REPO_ROOT", tmp_path)

    with (
        patch.object(guards, "_check_registry_implementation_drift", return_value=[]),
        patch.object(guards, "_check_new_prints", return_value=[violation]),
        patch.object(
            guards,
            "_check_critical_defaults_duplication",
            return_value=[],
        ),
        patch.object(
            guards,
            "_check_broad_exceptions_with_justification",
            return_value=[],
        ),
        patch(
            "scripts.ci.git_diff.list_changed_files",
            return_value=[],
        ),
        patch(
            "scripts.ci.git_diff.build_added_lines_map",
            return_value={},
        ),
    ):
        result = guards.main(
            ["--base-sha", "abc", "--head-sha", "def"],
        )
    assert result == 1
    captured = capsys.readouterr()
    assert "FAILED" in captured.out
