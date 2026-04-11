from __future__ import annotations

from pathlib import Path

MAX_DEPRECATED_BASE_IMPORTS_BY_FILE: dict[str, int] = {
    "scrapers/base_engine_table_scraper.py": 2,
    "scrapers/builders_table.py": 11,
    "scrapers/config_factory_points.py": 8,
    "scrapers/config_table.py": 6,
    "scrapers/constants_table.py": 4,
    "scrapers/constructors_config_factory.py": 3,
    "scrapers/driver_results_schema_factory.py": 3,
    "scrapers/extractors/table_extractor.py": 2,
    "scrapers/helpers_seasons.py": 2,
    "scrapers/lap_records_table.py": 7,
    "scrapers/mixins/table_row_parsing.py": 1,
    "scrapers/parser_table.py": 3,
    "scrapers/pipeline_table.py": 7,
    "scrapers/schema_table.py": 1,
    "scrapers/scraper_table.py": 4,
    "scrapers/seed_list_scraper_table.py": 7,
    "scrapers/single_scraper_engines.py": 4,
    "scrapers/single_scraper_grands_prix.py": 6,
    "scrapers/table_parsing_helper.py": 2,
    "scrapers/table_schema_dsl.py": 5,
    "scrapers/wiring/factory.py": 6,
}

GROUP_KEYWORDS: tuple[str, ...] = (
    "table",
    "single",
    "factory",
    "helper",
    "validator",
)


def _is_tracked_group_file(path: Path) -> bool:
    return any(keyword in path.name for keyword in GROUP_KEYWORDS)


def test_no_new_scrapers_base_imports_in_tracked_groups() -> None:
    tracked_files = [
        path for path in Path("scrapers").rglob("*.py") if _is_tracked_group_file(path)
    ]

    violations: list[str] = []
    for path in tracked_files:
        rel = path.as_posix()
        count = path.read_text(encoding="utf-8").count("scrapers.base.")

        allowed_max = MAX_DEPRECATED_BASE_IMPORTS_BY_FILE.get(rel, 0)
        if count > allowed_max:
            violations.append(
                f"{rel}: found {count} deprecated imports, "
                f"allowed max is {allowed_max}",
            )

    assert not violations, "\n".join(violations)
