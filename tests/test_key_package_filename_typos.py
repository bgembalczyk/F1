from pathlib import Path

import pytest

from scripts.check_known_module_typos import DISALLOWED_FILENAME_PATTERNS

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = (
    "layers",
    "scrapers",
    "models",
    "infrastructure",
    "validation",
    "complete_extractor",
    "tests",
)


@pytest.mark.parametrize(
    ("package", "expected_module"),
    [
        (PROJECT_ROOT / "scrapers" / "wiki", "constants.py"),
        (
            PROJECT_ROOT / "scrapers" / "wiki" / "parsers" / "sections",
            "constants.py",
        ),
        (
            PROJECT_ROOT / "scrapers" / "base" / "orchestration" / "components",
            "section_source_adapter.py",
        ),
    ],
)
def test_expected_modules_exist(package: Path, expected_module: str) -> None:
    assert (package / expected_module).exists(), (
        "Missing expected module: "
        f"{package / expected_module}"
    )


@pytest.mark.parametrize(
    "package",
    [
        PROJECT_ROOT / "scrapers" / "wiki",
        PROJECT_ROOT / "scrapers" / "wiki" / "parsers" / "sections",
        PROJECT_ROOT / "scrapers" / "base" / "orchestration" / "components",
    ],
)
def test_target_packages_do_not_contain_disallowed_filename_patterns(
    package: Path,
) -> None:
    matches = [
        py_path
        for py_path in package.glob("*.py")
        if any(pattern in py_path.name for pattern in DISALLOWED_FILENAME_PATTERNS)
    ]
    assert not matches, f"Found typo filename(s): {matches}"


def test_no_disallowed_filename_pattern_in_import_paths() -> None:
    matches = []
    for source_dir in SOURCE_DIRS:
        root = PROJECT_ROOT / source_dir
        if not root.exists():
            continue
        matches.extend(
            py_path.relative_to(PROJECT_ROOT)
            for py_path in root.rglob("*.py")
            if py_path.name != "test_key_package_filename_typos.py"
            if any(
                pattern in py_path.read_text(encoding="utf-8")
                for pattern in DISALLOWED_FILENAME_PATTERNS
            )
        )

    assert not matches, f"Found typo import path(s): {matches}"


def test_regression_detects_section_soruce_adapter_typo_pattern() -> None:
    assert "soruce" in DISALLOWED_FILENAME_PATTERNS
