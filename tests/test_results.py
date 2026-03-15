# ruff: noqa: E501, PLR2004, RUF001, RUF002, RUF003, SLF001, ARG001, ARG002, N802, B017, PT011, PT017, E402, PT001, PLC0415, RUF100
from dataclasses import dataclass

from scrapers.base.results import ScrapeResult


def test_scrape_result_normalizes_mixed_data() -> None:
    @dataclass(frozen=True)
    class Driver:
        name: str

    driver = Driver(name="Max")
    result = ScrapeResult(
        data=[{"Driver Name": "Max"}, driver],
        source_url=None,
    )

    normalized = result._with_normalized_data(
        normalize_keys=True,
        normalization_rules=None,
    )

    assert normalized.data[0] == {"driver_name": "Max"}
    assert normalized.data[1] is driver
