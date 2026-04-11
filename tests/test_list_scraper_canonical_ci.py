from __future__ import annotations

import ast
from pathlib import Path

CANONICAL_DOMAIN_MODULES = {
    "scrapers/drivers/list_scraper.py",
    "scrapers/constructors/list_scraper.py",
    "scrapers/circuits/list_scraper.py",
    "scrapers/seasons/list_scraper.py",
    "scrapers/grands_prix/list_scraper.py",
}

# Existing non-canonical classes are temporarily allowed for backward compatibility.
ALLOWED_LEGACY_LIST_SCRAPER_CLASSES = {
    ("scrapers/base_constructor_list_scraper.py", "BaseConstructorListScraper"),
    ("scrapers/circuits_list_scraper.py", "CircuitsListScraper"),
    ("scrapers/constructors_list.py", "ConstructorsListScraper"),
    ("scrapers/engine_manufacturers_list.py", "EngineManufacturersListScraper"),
    ("scrapers/fatalities_list_scraper_drivers.py", "F1FatalitiesListScraper"),
    ("scrapers/female_drivers_list.py", "FemaleDriversListScraper"),
    ("scrapers/list/base.py", "ListScraper"),
    ("scrapers/list/indianapolis_only/base.py", "IndianapolisOnlyListScraper"),
    ("scrapers/list_scraper_drivers.py", "F1DriversListScraper"),
    ("scrapers/list_scraper_grands_prix.py", "GrandsPrixListScraper"),
    ("scrapers/list_scraper_seasons.py", "SeasonsListScraper"),
}


def test_new_list_scraper_classes_must_live_in_canonical_domain_modules() -> None:
    violations: list[str] = []

    for py_file in Path("scrapers").rglob("*.py"):
        source = py_file.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=str(py_file))
        except SyntaxError:
            continue

        relative = py_file.as_posix()
        is_compat_or_legacy = "/compat/" in relative or "/legacy/" in relative
        is_canonical_module = relative in CANONICAL_DOMAIN_MODULES

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef) or not node.name.endswith(
                "ListScraper"
            ):
                continue

            marker = (relative, node.name)
            if is_compat_or_legacy or is_canonical_module:
                continue
            if marker in ALLOWED_LEGACY_LIST_SCRAPER_CLASSES:
                continue
            violations.append(f"{relative}:{node.lineno}:{node.name}")

    assert not violations, (
        "New `*ListScraper` classes must be defined in canonical domain modules "
        "(`scrapers/<domain>/list_scraper.py`) or compatibility modules. Violations: "
        + ", ".join(sorted(violations))
    )
