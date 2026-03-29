from pathlib import Path


def test_base_columns_types_stays_domain_neutral() -> None:
    base_types_dir = Path("scrapers/base/table/columns/types")
    forbidden = {
        "constructor.py",
        "constructor_part.py",
        "driver.py",
        "driver_list.py",
        "engine.py",
        "entrant.py",
        "position.py",
        "seasons.py",
        "tyre.py",
    }
    existing = {path.name for path in base_types_dir.glob("*.py")}
    assert forbidden.isdisjoint(existing)
