from datetime import datetime
from datetime import timezone

from scrapers.wiki.seed_l0 import SEED_RECORD_SCHEMA_VERSION
from scrapers.wiki.seed_l0 import compute_seed_quality
from scrapers.wiki.seed_l0 import normalize_seed_records


def test_normalize_seed_records_contract() -> None:
    records = [
        {"driver": "Lewis Hamilton", "url": "https://example.com/hamilton"},
        {"name": "Max Verstappen", "link": "https://example.com/max"},
    ]

    normalized = normalize_seed_records(
        records,
        source_url="https://en.wikipedia.org/wiki/List_of_Formula_One_drivers",
        scraped_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )

    assert normalized[0]["schema_version"] == SEED_RECORD_SCHEMA_VERSION
    assert normalized[0]["name"] == "Lewis Hamilton"
    assert normalized[0]["link"] == "https://example.com/hamilton"
    assert normalized[0]["source_url"].startswith("https://")
    assert normalized[0]["scraped_at"].startswith("2026-01-01")


def test_compute_seed_quality() -> None:
    report = compute_seed_quality(
        [
            {"name": "Ayrton Senna", "link": "https://example.com/senna"},
            {"name": "", "link": "https://example.com/prost"},
            {"name": "Ayrton Senna", "link": None},
        ],
        seed_name="drivers",
        category="drivers",
    )

    assert report.records_count == len([1, 2, 3])
    assert report.empty_name_count == 1
    assert report.empty_link_count == 1
    assert report.duplicate_name_count == 1
