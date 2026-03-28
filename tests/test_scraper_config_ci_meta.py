from __future__ import annotations

import ast
from pathlib import Path

SCRAPERS_ROOT = Path("scrapers")


def _iter_scraper_python_files() -> list[Path]:
    return sorted(
        path
        for path in SCRAPERS_ROOT.rglob("*.py")
        if "__pycache__" not in path.parts
    )


def _class_config_uses_direct_scraper_config(source: str) -> list[str]:
    tree = ast.parse(source)
    offenders: list[str] = []

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        for statement in node.body:
            if not isinstance(statement, ast.Assign):
                continue

            has_config_target = any(
                isinstance(target, ast.Name) and target.id == "CONFIG"
                for target in statement.targets
            )
            if not has_config_target:
                continue

            value = statement.value
            if not isinstance(value, ast.Call):
                continue

            if isinstance(value.func, ast.Name) and value.func.id == "ScraperConfig":
                offenders.append(node.name)

    return offenders


def test_ci_meta_requires_build_scraper_config_for_class_config() -> None:
    offenders: list[str] = []

    for path in _iter_scraper_python_files():
        source = path.read_text(encoding="utf-8")
        classes = _class_config_uses_direct_scraper_config(source)
        offenders.extend(f"{path}:{class_name}" for class_name in classes)

    assert not offenders, (
        "New scraper configs must use build_scraper_config(...) + schema DSL; "
        f"replace manual ScraperConfig(...) in: {offenders}"
    )


def test_ci_meta_forbids_deprecated_build_scraper_config_alias() -> None:
    offenders: list[str] = []

    for path in _iter_scraper_python_files():
        source = path.read_text(encoding="utf-8")
        if "from scrapers.base.table.builders import build_scraper_config" in source:
            offenders.append(str(path))

    assert not offenders, (
        "Use scrapers.base.table.config.build_scraper_config (not builders alias): "
        f"{offenders}"
    )
