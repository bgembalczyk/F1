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
