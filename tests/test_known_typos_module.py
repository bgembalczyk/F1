from pathlib import Path

from scripts.lib.known_typos import TypoRule
from scripts.lib.known_typos import run_known_typos_check
from scripts.lib.known_typos import scan_typo_imports
from scripts.lib.known_typos import validate_target_packages


def test_validate_target_packages_reports_missing_expected_module(tmp_path: Path):
    package = tmp_path / "pkg"
    package.mkdir()
    rules = (
        TypoRule(
            target_packages=(package,),
            expected_module_name="constants.py",
            disallowed_typo_name="contants.py",
            disallowed_import="pkg.contants",
        ),
    )

    errors = validate_target_packages(rules)

    assert errors == [f"missing expected module: {package / 'constants.py'}"]


def test_validate_target_packages_reports_existing_typo_module(tmp_path: Path):
    package = tmp_path / "pkg"
    package.mkdir()
    (package / "constants.py").write_text("", encoding="utf-8")
    (package / "contants.py").write_text("", encoding="utf-8")
    rules = (
        TypoRule(
            target_packages=(package,),
            expected_module_name="constants.py",
            disallowed_typo_name="contants.py",
            disallowed_import="pkg.contants",
        ),
    )

    errors = validate_target_packages(rules)

    assert errors == [f"found typo module: {package / 'contants.py'}"]


def test_scan_typo_imports_returns_matching_relative_paths(tmp_path: Path):
    src = tmp_path / "src"
    src.mkdir()
    matching_file = src / "bad.py"
    matching_file.write_text("from pkg.contants import X", encoding="utf-8")
    (src / "ok.py").write_text("from pkg.constants import X", encoding="utf-8")
    rules = (
        TypoRule(
            target_packages=(),
            expected_module_name="constants.py",
            disallowed_typo_name="contants.py",
            disallowed_import="pkg.contants",
        ),
    )

    errors = scan_typo_imports(tmp_path, rules, ("src",))

    assert errors == ["found typo import in src/bad.py"]


def test_run_known_typos_check_combines_package_and_import_errors(tmp_path: Path):
    package = tmp_path / "pkg"
    package.mkdir()
    (package / "contants.py").write_text("", encoding="utf-8")

    source_root = tmp_path / "source"
    source_root.mkdir()
    (source_root / "bad.py").write_text("import pkg.contants", encoding="utf-8")

    rules = (
        TypoRule(
            target_packages=(package,),
            expected_module_name="constants.py",
            disallowed_typo_name="contants.py",
            disallowed_import="pkg.contants",
        ),
    )

    errors = run_known_typos_check(tmp_path, rules, ("source",))

    assert errors == [
        f"missing expected module: {package / 'constants.py'}",
        f"found typo module: {package / 'contants.py'}",
        "found typo import in source/bad.py",
    ]
