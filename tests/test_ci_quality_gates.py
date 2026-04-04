# ruff: noqa: SLF001
from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from scripts.ci import check_duplicate_default_configs
from scripts.ci import enforce_function_complexity
from scripts.ci import enforce_no_new_prints
from scripts.ci import enforce_source_name_magic_strings
from scripts.ci import enforce_structural_quality

if TYPE_CHECKING:
    from pathlib import Path


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
