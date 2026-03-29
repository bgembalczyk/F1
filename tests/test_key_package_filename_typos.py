from pathlib import Path

from scripts.lib.paths import PROJECT_ROOT, SOURCE_DIR_NAMES, SOURCE_DIRS, iter_python_files


def test_paths_module_exposes_single_source_scan_dirs():
    expected_dir_names = (
        "layers",
        "scrapers",
        "models",
        "infrastructure",
        "validation",
        "complete_extractor",
    )
    assert SOURCE_DIR_NAMES == expected_dir_names
    assert SOURCE_DIRS == tuple(PROJECT_ROOT / name for name in expected_dir_names)


def test_key_package_file_names_do_not_contain_contants_typo():
    project_root = PROJECT_ROOT
    key_packages = (
        project_root / "scrapers" / "wiki",
        project_root / "scrapers" / "wiki" / "parsers" / "sections",
    )
    typo_file_name = "contants.py"

    typo_paths = [
        typo_path
        for package in key_packages
        if (typo_path := package / typo_file_name).exists()
    ]
    assert not typo_paths, f"Found typo filename(s): {typo_paths}"


def test_key_package_constants_modules_exist():
    project_root = PROJECT_ROOT
    expected_paths = (
        project_root / "scrapers" / "wiki" / "constants.py",
        project_root / "scrapers" / "wiki" / "parsers" / "sections" / "constants.py",
    )

    missing_paths = [path for path in expected_paths if not path.exists()]
    assert not missing_paths, f"Missing expected constants module(s): {missing_paths}"


def test_no_typo_import_path_remains():
    project_root = PROJECT_ROOT
    disallowed_import = "scrapers.wiki.contants"

    matches = [
        py_path.relative_to(project_root)
        for py_path in iter_python_files(SOURCE_DIRS)
        if disallowed_import in py_path.read_text(encoding="utf-8")
    ]

    assert not matches, f"Found typo import path(s): {matches}"


def test_no_parallel_typo_and_correct_module_pairs_exist():
    project_root = PROJECT_ROOT
    target_packages = (
        project_root / "scrapers" / "wiki",
        project_root / "scrapers" / "wiki" / "parsers" / "sections",
    )

    duplicates = []
    for package in target_packages:
        has_correct = (package / "constants.py").exists()
        has_typo = (package / "contants.py").exists()
        if has_correct and has_typo:
            duplicates.append(package)

    assert not duplicates, f"Found parallel typo/correct module pairs: {duplicates}"
