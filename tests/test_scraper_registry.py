import pkgutil
import sys

import scrapers

from scrapers.base.registry import load_default_scrapers


def _scraper_modules() -> list[str]:
    module_names: list[str] = []
    for module_info in pkgutil.walk_packages(
        scrapers.__path__,
        prefix="scrapers.",
    ):
        if module_info.ispkg:
            continue
        if module_info.name.startswith("scrapers.base."):
            continue
        if module_info.name == "scrapers.config":
            continue
        module_names.append(module_info.name)
    return module_names


def test_all_scraper_modules_are_loaded() -> None:
    module_names = _scraper_modules()

    load_default_scrapers()

    missing_modules = [
        module_name
        for module_name in module_names
        if module_name not in sys.modules
    ]

    assert not missing_modules, (
        "Nie załadowano automatycznie modułów: "
        f"{', '.join(sorted(missing_modules))}"
    )
