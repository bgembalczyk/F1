from pathlib import Path

from scripts.lib.known_typos import (
    SOURCE_DIRS,
    build_default_rules,
    run_known_typos_check,
    scan_typo_imports,
    validate_target_packages,
)


def test_known_typo_rule_target_packages_are_valid():
    project_root = Path(__file__).resolve().parents[1]
    rules = build_default_rules(project_root)

    errors = validate_target_packages(rules)

    assert not errors, f"Known typo package validation failed: {errors}"


def test_no_known_typo_imports_remain_in_source_dirs():
    project_root = Path(__file__).resolve().parents[1]
    rules = build_default_rules(project_root)

    errors = scan_typo_imports(project_root, rules, SOURCE_DIRS)

    assert not errors, f"Known typo import validation failed: {errors}"


def test_known_module_typo_check_passes_as_a_whole():
    project_root = Path(__file__).resolve().parents[1]

    errors = run_known_typos_check(project_root)

    assert not errors, f"Known module typo check failed: {errors}"
