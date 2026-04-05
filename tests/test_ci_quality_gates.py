# ruff: noqa: SLF001
from __future__ import annotations

import ast
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from scripts.ci import check_duplicate_default_configs
from scripts.ci import enforce_function_complexity
from scripts.ci import enforce_no_new_prints
from scripts.ci import enforce_source_name_magic_strings
from scripts.ci import enforce_structural_quality

if TYPE_CHECKING:
    pass


def test_function_complexity_detects_length_nesting_and_branching(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "module.py"
    file_path.write_text(
        """

def target():
    if True:
        for _ in range(2):
            while False:
                pass
    if True:
        pass
""".strip()
        + "\n",
        encoding="utf-8",
    )

    violations = enforce_function_complexity.evaluate_file(
        file_path,
        {1, 2, 3, 4, 5, 6, 7, 8},
        max_function_lines=4,
        max_nesting=2,
        max_branches=3,
    )

    assert any("length=" in item for item in violations)
    assert any("nesting=" in item for item in violations)
    assert any("branching=" in item for item in violations)


def test_source_name_magic_string_gate_flags_new_json_literal(
    tmp_path: Path,
    monkeypatch,
) -> None:
    file_path = tmp_path / "module.py"
    file_path.write_text('source_name = "f1_new_source.json"\n', encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        enforce_source_name_magic_strings,
        "build_added_lines_map",
        lambda *_args, **_kwargs: {"module.py": {1}},
    )

    exit_code = enforce_source_name_magic_strings.main(
        ["--base-sha", "base", "--head-sha", "head", "--changed-files", "module.py"],
    )

    assert exit_code == 1


def test_no_new_prints_gate_allows_scripts_and_blocks_other_paths(
    tmp_path: Path,
    monkeypatch,
) -> None:
    (tmp_path / "app").mkdir()
    file_path = tmp_path / "app" / "module.py"
    file_path.write_text("print('debug')\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        enforce_no_new_prints,
        "build_added_lines_map",
        lambda *_args, **_kwargs: {"app/module.py": {1}},
    )

    exit_code = enforce_no_new_prints.main(
        [
            "--base-sha",
            "base",
            "--head-sha",
            "head",
            "--changed-files",
            "app/module.py",
        ],
    )

    assert exit_code == 1
    assert enforce_no_new_prints._is_allowed("scripts/example.py")


def test_duplicate_default_config_detection_finds_same_kwargs_for_two_seeds() -> None:
    source = """

def build_layer_zero_run_config_factory_map():
    return {
        "a": StaticScraperKwargsFactory(scraper_kwargs={"export_scope": "same"}),
        "b": StaticScraperKwargsFactory(scraper_kwargs={"export_scope": "same"}),
    }
"""
    tree = ast.parse(source)
    duplicates = check_duplicate_default_configs._extract_static_kwargs_duplicates(tree)

    assert len(duplicates) == 1
    seeds = next(iter(duplicates.values()))
    assert seeds == ["a", "b"]


def test_structural_quality_detects_file_function_and_class_length(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "module.py"
    class_body = "\n".join("    pass" for _ in range(4))
    function_body = "\n".join("    x = 1" for _ in range(4))
    file_path.write_text(
        f"class Oversized:\n{class_body}\n\ndef oversized_fn():\n{function_body}\n",
        encoding="utf-8",
    )

    violations = enforce_structural_quality.evaluate_file(
        file_path,
        max_function_lines=3,
        max_class_lines=3,
        max_file_lines=8,
    )

    assert any("file length=" in item for item in violations)
    assert any("function 'oversized_fn'" in item for item in violations)
    assert any("class 'Oversized'" in item for item in violations)


def test_structural_quality_flags_redundant_public_alias_and_allows_private_wrapper(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "module.py"
    file_path.write_text(
        """

def redundant(value):
    return normalize(value)


def _private_wrapper(value):
    return normalize(value)


def wrapper_for_private_attr(self, payload):
    return self._service.handle(payload)
""".strip()
        + "\n",
        encoding="utf-8",
    )

    violations = enforce_structural_quality.evaluate_file(
        file_path,
        max_function_lines=100,
        max_class_lines=500,
        max_file_lines=1000,
    )

    assert any(
        "function 'redundant' is a redundant alias" in item for item in violations
    )
    assert not any("_private_wrapper" in item for item in violations)
    assert not any("wrapper_for_private_attr" in item for item in violations)


def test_structural_quality_allows_lambda_in_call_args(tmp_path: Path) -> None:
    file_path = tmp_path / "module.py"
    file_path.write_text(
        """
def find_header(soup):
    return soup.find(
        "h1",
        class_=lambda x: x and "cls" in (x if isinstance(x, list) else x.split()),
    )
""".strip()
        + "\n",
        encoding="utf-8",
    )

    violations = enforce_structural_quality.evaluate_file(
        file_path,
        max_function_lines=100,
        max_class_lines=500,
        max_file_lines=1000,
    )

    assert not any("redundant alias" in item for item in violations)


def test_structural_quality_allows_generator_expr_in_call_args(tmp_path: Path) -> None:
    file_path = tmp_path / "module.py"
    file_path.write_text(
        """
def should_apply(record):
    return any(
        handler.has_group(record.get(key))
        for key in COLOUR_KEYS
    )
""".strip()
        + "\n",
        encoding="utf-8",
    )

    violations = enforce_structural_quality.evaluate_file(
        file_path,
        max_function_lines=100,
        max_class_lines=500,
        max_file_lines=1000,
    )

    assert not any("redundant alias" in item for item in violations)


def test_structural_quality_allows_method_override_in_derived_class(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "module.py"
    file_path.write_text(
        """
class RestartStatusColumn(BackgroundMixin, BaseColumn):
    def parse(self, ctx):
        return restart_status(ctx)
""".strip()
        + "\n",
        encoding="utf-8",
    )

    violations = enforce_structural_quality.evaluate_file(
        file_path,
        max_function_lines=100,
        max_class_lines=500,
        max_file_lines=1000,
    )

    assert not any("redundant alias" in item for item in violations)


def test_structural_quality_still_flags_standalone_redundant_alias(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "module.py"
    file_path.write_text(
        """
def redundant(value):
    return normalize(value)
""".strip()
        + "\n",
        encoding="utf-8",
    )

    violations = enforce_structural_quality.evaluate_file(
        file_path,
        max_function_lines=100,
        max_class_lines=500,
        max_file_lines=1000,
    )

    assert any(
        "function 'redundant' is a redundant alias" in item for item in violations
    )


def test_structural_quality_allows_multiline_alias_even_with_single_usage(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "record_definition.py"
    file_path.write_text(
        """
class RecordDefinition:
    def to_schema(self):
        return RecordSchema(
            required=self.required,
            types=self.types,
        )
""".strip()
        + "\n",
        encoding="utf-8",
    )

    violations = enforce_structural_quality.evaluate_file(
        file_path,
        max_function_lines=100,
        max_class_lines=500,
        max_file_lines=1000,
    )

    assert not any(
        "function 'to_schema' is a redundant alias" in item for item in violations
    )


# ---------------------------------------------------------------------------
# _collect_overload_names
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_collect_overload_names_detects_overload_decorator() -> None:
    import ast

    code = """
from typing import overload

@overload
def process(x: int) -> int: ...

@overload
def process(x: str) -> str: ...

def process(x):
    return x
"""
    tree = ast.parse(code)
    names = enforce_structural_quality._collect_overload_names(tree)
    assert "process" in names


@pytest.mark.unit()
def test_collect_overload_names_handles_attribute_decorator() -> None:
    import ast

    code = """
import typing

@typing.overload
def do_thing(x: int) -> int: ...
"""
    tree = ast.parse(code)
    names = enforce_structural_quality._collect_overload_names(tree)
    assert "do_thing" in names


# ---------------------------------------------------------------------------
# _collect_call_counts
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_collect_call_counts_handles_attribute_calls() -> None:
    import ast

    code = "obj.method()\nobj.other()\nobj.method()\n"
    tree = ast.parse(code)
    counts = enforce_structural_quality._collect_call_counts(tree)
    assert counts.get("method", 0) == 2
    assert counts.get("other", 0) == 1


# ---------------------------------------------------------------------------
# _decorator_names
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_decorator_names_handles_attribute_decorator() -> None:
    import ast

    code = """
@module.decorator
def my_func():
    pass
"""
    tree = ast.parse(code)
    func = tree.body[0]
    assert isinstance(func, ast.FunctionDef)
    names = enforce_structural_quality.StructuralVisitor._decorator_names(func)
    assert "decorator" in names


# ---------------------------------------------------------------------------
# _is_redundant_alias_body edge cases
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_is_redundant_alias_body_returns_false_for_empty_body() -> None:
    import ast
    from pathlib import Path

    visitor = enforce_structural_quality.StructuralVisitor(file_path="test.py")
    visitor.max_function_lines = 100
    visitor.max_class_lines = 500

    code = "def empty(): ..."
    tree = ast.parse(code)
    func = tree.body[0]
    assert isinstance(func, ast.FunctionDef)
    func.body = []
    assert not visitor._is_redundant_alias_body(func)


@pytest.mark.unit()
def test_is_redundant_alias_body_filters_docstrings() -> None:
    import ast

    visitor = enforce_structural_quality.StructuralVisitor(file_path="test.py")
    visitor.max_function_lines = 100
    visitor.max_class_lines = 500

    code = '''
def alias():
    """Docstring."""
    return other_func()
'''
    tree = ast.parse(code.strip())
    func = tree.body[0]
    assert isinstance(func, ast.FunctionDef)
    result = visitor._is_redundant_alias_body(func)
    assert result


@pytest.mark.unit()
def test_is_redundant_alias_body_handles_expr_call() -> None:
    import ast

    visitor = enforce_structural_quality.StructuralVisitor(file_path="test.py")
    visitor.max_function_lines = 100
    visitor.max_class_lines = 500

    code = "def alias():\n    other_func()\n"
    tree = ast.parse(code)
    func = tree.body[0]
    assert isinstance(func, ast.FunctionDef)
    result = visitor._is_redundant_alias_body(func)
    assert result


@pytest.mark.unit()
def test_is_redundant_alias_body_returns_false_for_non_call_stmt() -> None:
    import ast

    visitor = enforce_structural_quality.StructuralVisitor(file_path="test.py")
    visitor.max_function_lines = 100
    visitor.max_class_lines = 500

    code = "def not_alias():\n    x = 1\n"
    tree = ast.parse(code)
    func = tree.body[0]
    result = visitor._is_redundant_alias_body(func)
    assert not result


@pytest.mark.unit()
def test_is_redundant_alias_body_private_called_name_returns_false() -> None:
    import ast

    visitor = enforce_structural_quality.StructuralVisitor(file_path="test.py")
    visitor.max_function_lines = 100
    visitor.max_class_lines = 500

    code = "def alias():\n    return _private_func()\n"
    tree = ast.parse(code)
    func = tree.body[0]
    result = visitor._is_redundant_alias_body(func)
    assert not result


@pytest.mark.unit()
def test_is_redundant_alias_body_private_attribute_caller_returns_false() -> None:
    import ast

    visitor = enforce_structural_quality.StructuralVisitor(file_path="test.py")
    visitor.max_function_lines = 100
    visitor.max_class_lines = 500

    # attribute with private attr name
    code = "def alias():\n    return self._private.method()\n"
    tree = ast.parse(code)
    func = tree.body[0]
    result = visitor._is_redundant_alias_body(func)
    assert not result


# ---------------------------------------------------------------------------
# _body_spans_multiple_lines
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_body_spans_multiple_lines_returns_false_for_empty_body() -> None:
    import ast

    code = "def empty_func(): ..."
    tree = ast.parse(code)
    func = tree.body[0]
    assert isinstance(func, ast.FunctionDef)
    func.body = []
    result = enforce_structural_quality.StructuralVisitor._body_spans_multiple_lines(
        func
    )
    assert not result


# ---------------------------------------------------------------------------
# visit_AsyncFunctionDef
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_evaluate_file_detects_long_async_functions(tmp_path: Path) -> None:
    long_async_body = "\n    ".join(f"x{i} = {i}" for i in range(200))
    code = f"async def long_async_fn():\n    {long_async_body}\n"
    py_file = tmp_path / "async_fn.py"
    py_file.write_text(code, encoding="utf-8")
    violations = enforce_structural_quality.evaluate_file(
        py_file, max_function_lines=50, max_class_lines=500, max_file_lines=10000
    )
    assert any("long_async_fn" in v for v in violations)


# ---------------------------------------------------------------------------
# _should_skip
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_should_skip_returns_true_for_venv() -> None:
    from pathlib import Path

    assert enforce_structural_quality._should_skip(Path(".venv/lib/site.py"))


@pytest.mark.unit()
def test_should_skip_returns_false_for_regular_path() -> None:
    from pathlib import Path

    assert not enforce_structural_quality._should_skip(Path("scrapers/foo/bar.py"))


# ---------------------------------------------------------------------------
# _iter_python_files
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_iter_python_files_filters_by_extension() -> None:
    result = enforce_structural_quality._iter_python_files(
        ["src/foo.py", "src/bar.txt", "README.md"]
    )
    assert len(result) == 1
    assert str(result[0]) == "src/foo.py"


@pytest.mark.unit()
def test_iter_python_files_empty_list_returns_disk_files(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "mod.py").write_text("x = 1\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = enforce_structural_quality._iter_python_files([])
    # Should find the py file (excluding venv etc.)
    assert len(result) >= 1


# ---------------------------------------------------------------------------
# evaluate_file edge cases
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_evaluate_file_handles_os_error(tmp_path: Path) -> None:
    missing = tmp_path / "nonexistent.py"
    violations = enforce_structural_quality.evaluate_file(
        missing, max_function_lines=100, max_class_lines=500, max_file_lines=1000
    )
    assert len(violations) == 1
    assert "unable to read" in violations[0]


@pytest.mark.unit()
def test_evaluate_file_handles_syntax_error(tmp_path: Path) -> None:
    bad_file = tmp_path / "bad.py"
    bad_file.write_text("def broken(:\n", encoding="utf-8")
    violations = enforce_structural_quality.evaluate_file(
        bad_file, max_function_lines=100, max_class_lines=500, max_file_lines=1000
    )
    # No violations from syntax error (just skip parsing)
    assert isinstance(violations, list)


# ---------------------------------------------------------------------------
# parse_args
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_parse_args_uses_defaults() -> None:
    args = enforce_structural_quality.parse_args([])
    assert args.max_function_lines == 100
    assert args.max_class_lines == 500
    assert args.max_file_lines == 1000


@pytest.mark.unit()
def test_parse_args_accepts_custom_limits() -> None:
    args = enforce_structural_quality.parse_args(
        ["--max-function-lines", "50", "--max-class-lines", "200"]
    )
    assert args.max_function_lines == 50
    assert args.max_class_lines == 200


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_main_no_files_returns_zero(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = enforce_structural_quality.main([])
    assert result == 0


@pytest.mark.unit()
def test_main_with_clean_file_returns_zero(tmp_path: Path) -> None:
    py_file = tmp_path / "clean.py"
    py_file.write_text("x = 1\n", encoding="utf-8")
    result = enforce_structural_quality.main([str(py_file)])
    assert result == 0


@pytest.mark.unit()
def test_main_with_violations_returns_one(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    long_body = "\n    ".join(f"x{i} = {i}" for i in range(200))
    code = f"def super_long():\n    {long_body}\n"
    py_file = tmp_path / "bad.py"
    py_file.write_text(code, encoding="utf-8")
    result = enforce_structural_quality.main([str(py_file), "--max-function-lines", "5"])
    assert result == 1
    assert "violations" in capsys.readouterr().out.lower()


@pytest.mark.unit()
def test_decorator_names_handles_name_decorator() -> None:
    code = """
@mydecorator
def my_func():
    pass
"""
    tree = ast.parse(code.strip())
    func = tree.body[0]
    assert isinstance(func, ast.FunctionDef)
    names = enforce_structural_quality.StructuralVisitor._decorator_names(func)
    assert "mydecorator" in names


@pytest.mark.unit()
def test_is_redundant_alias_body_returns_false_for_private_attribute_call() -> None:
    visitor = enforce_structural_quality.StructuralVisitor(file_path="test.py")
    visitor.max_function_lines = 100
    visitor.max_class_lines = 500

    # Called via attribute where the attribute name is private
    code = "def alias():\n    return module._private_method()\n"
    tree = ast.parse(code)
    func = tree.body[0]
    result = visitor._is_redundant_alias_body(func)
    assert not result
