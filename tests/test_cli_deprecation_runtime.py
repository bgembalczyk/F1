from __future__ import annotations

from datetime import date
from pathlib import Path

from scrapers.deprecation_catalog import get_deprecated_elements_report
from scrapers.deprecation_catalog import get_deprecated_module_migrations


def test_deprecated_module_migrations_include_domain_entrypoints() -> None:
    migrations = dict(get_deprecated_module_migrations())

    assert migrations["scrapers.drivers.list_scraper"] == "scrapers.drivers.entrypoint"
    assert (
        migrations["scrapers.circuits.list_scraper"] == "scrapers.circuits.entrypoint"
    )
    assert (
        migrations["scrapers.constructors.current_constructors_list"]
        == "scrapers.constructors.entrypoint"
    )


def test_deprecated_elements_report_contains_required_metadata() -> None:
    report = get_deprecated_elements_report()
    assert report

    today = date(2026, 4, 2)
    for module_path, deprecated_since, replacement, remove_after in report:
        assert module_path.startswith("scrapers.")
        assert deprecated_since
        assert replacement
        assert remove_after
        assert date.fromisoformat(remove_after) >= today
