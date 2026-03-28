from pathlib import Path


def test_key_package_file_names_do_not_contain_contants_typo():
    project_root = Path(__file__).resolve().parents[1]
    key_packages = (
        project_root / "scrapers" / "wiki",
        project_root / "scrapers" / "wiki" / "parsers" / "sections",
    )
    typo_file_name = "contants.py"

    typo_paths = []
    for package in key_packages:
        typo_path = package / typo_file_name
        if typo_path.exists():
            typo_paths.append(typo_path)
    assert not typo_paths, f"Found typo filename(s): {typo_paths}"


def test_key_package_constants_modules_exist():
    project_root = Path(__file__).resolve().parents[1]
    expected_paths = (
        project_root / "scrapers" / "wiki" / "constants.py",
        project_root / "scrapers" / "wiki" / "parsers" / "sections" / "constants.py",
    )

    missing_paths = [path for path in expected_paths if not path.exists()]
    assert not missing_paths, f"Missing expected constants module(s): {missing_paths}"


def test_no_typo_import_path_remains():
    project_root = Path(__file__).resolve().parents[1]
    disallowed_import = "scrapers.wiki.contants"
    source_dirs = (
        "layers",
        "scrapers",
        "models",
        "infrastructure",
        "validation",
        "complete_extractor",
    )

    matches = []
    for source_dir in source_dirs:
        root = project_root / source_dir
        if not root.exists():
            continue
        for py_path in root.rglob("*.py"):
            if disallowed_import in py_path.read_text(encoding="utf-8"):
                matches.append(py_path.relative_to(project_root))

    assert not matches, f"Found typo import path(s): {matches}"


def test_no_parallel_typo_and_correct_module_pairs_exist():
    project_root = Path(__file__).resolve().parents[1]
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
