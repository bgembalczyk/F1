from scrapers.base.options import ScraperOptions
from scrapers.engines.engine_manufacturers_list import EngineManufacturersListScraper

EXPECTED_SUBSECTION_COUNT = 3


def test_indianapolis_record_normalization_embeds_url_into_manufacturer_link() -> None:
    scraper = EngineManufacturersListScraper(options=ScraperOptions(include_urls=True))

    normalized = scraper.normalize_indianapolis_record(
        {
            "manufacturer": "Cadillac",
            "manufacturer_url": "/wiki/Cadillac_in_Formula_One",
            "engines_built_in": [],
            "manufacturer_status": None,
            "seasons": [],
        },
    )

    assert normalized["manufacturer"] == {
        "text": "Cadillac",
        "url": "https://en.wikipedia.org/wiki/Cadillac_in_Formula_One",
    }
    assert "manufacturer_url" not in normalized


def test_indianapolis_record_normalization_omits_url_when_include_urls_disabled() -> (
    None
):
    scraper = EngineManufacturersListScraper(options=ScraperOptions(include_urls=False))

    normalized = scraper.normalize_indianapolis_record(
        {
            "manufacturer": "Cadillac",
            "manufacturer_url": "/wiki/Cadillac_in_Formula_One",
            "engines_built_in": [],
            "manufacturer_status": None,
            "seasons": [],
        },
    )

    assert normalized["manufacturer"] == {"text": "Cadillac", "url": None}
    assert "manufacturer_url" not in normalized


# ---------------------------------------------------------------------------
# EngineManufacturersTableParser
# ---------------------------------------------------------------------------


def test_engine_manufacturers_table_parser_matches_valid_headers() -> None:
    from scrapers.engines.engine_manufacturers_list import (
        EngineManufacturersTableParser,
    )

    parser = EngineManufacturersTableParser()
    headers = ["Manufacturer", "Engines built in", "Seasons", "Wins", "Points"]
    assert parser.matches(headers, {})


def test_engine_manufacturers_table_parser_rejects_missing_required_headers() -> None:
    from scrapers.engines.engine_manufacturers_list import (
        EngineManufacturersTableParser,
    )

    parser = EngineManufacturersTableParser()
    assert not parser.matches(["Name", "Year"], {})


def test_engine_manufacturers_table_parser_maps_known_columns() -> None:
    from scrapers.engines.engine_manufacturers_list import (
        EngineManufacturersTableParser,
    )

    parser = EngineManufacturersTableParser()
    result = parser.map_columns(["Manufacturer", "Wins", "Points"])
    assert result["Manufacturer"] == "manufacturer"
    assert result["Wins"] == "wins"
    assert "Unknown" not in result


# ---------------------------------------------------------------------------
# IndianapolisOnlyListParser
# ---------------------------------------------------------------------------


def test_indianapolis_only_list_parser_parses_simple_list() -> None:
    from bs4 import BeautifulSoup

    from scrapers.engines.engine_manufacturers_list import IndianapolisOnlyListParser

    html = '<ul><li><a href="/wiki/Ferrari">Ferrari</a></li></ul>'
    soup = BeautifulSoup(html, "html.parser")
    ul = soup.find("ul")

    parser = IndianapolisOnlyListParser()
    result = parser.parse(ul)

    assert "items" in result
    items = result["items"]
    assert len(items) == 1
    assert items[0]["manufacturer"] == "Ferrari"
    assert items[0]["manufacturer_url"] == "/wiki/Ferrari"


def test_indianapolis_only_list_parser_skips_empty_items() -> None:
    from bs4 import BeautifulSoup

    from scrapers.engines.engine_manufacturers_list import IndianapolisOnlyListParser

    html = "<ul><li></li><li><a href='/wiki/Mercedes'>Mercedes</a></li></ul>"
    soup = BeautifulSoup(html, "html.parser")
    ul = soup.find("ul")

    parser = IndianapolisOnlyListParser()
    result = parser.parse(ul)

    items = result["items"]
    assert len(items) == 1
    assert items[0]["manufacturer"] == "Mercedes"


def test_indianapolis_only_list_parser_handles_no_anchor() -> None:
    from bs4 import BeautifulSoup

    from scrapers.engines.engine_manufacturers_list import IndianapolisOnlyListParser

    html = "<ul><li>No Link</li></ul>"
    soup = BeautifulSoup(html, "html.parser")
    ul = soup.find("ul")

    parser = IndianapolisOnlyListParser()
    result = parser.parse(ul)

    items = result["items"]
    assert len(items) == 1
    assert items[0]["manufacturer"] == "No Link"
    assert "manufacturer_url" not in items[0]


# ---------------------------------------------------------------------------
# EngineManufacturersListScraper - init with invalid scope
# ---------------------------------------------------------------------------


def test_engine_manufacturers_list_scraper_rejects_invalid_scope() -> None:
    import pytest

    from scrapers.base.options import ScraperOptions
    from scrapers.engines.engine_manufacturers_list import (
        EngineManufacturersListScraper,
    )

    with pytest.raises(ValueError, match="Unsupported export_scope"):
        EngineManufacturersListScraper(
            options=ScraperOptions(include_urls=True),
            export_scope="invalid_scope",
        )


# ---------------------------------------------------------------------------
# _iter_sub_sections
# ---------------------------------------------------------------------------


def test_iter_sub_sections_returns_sub_and_sub_sub() -> None:
    from scrapers.base.options import ScraperOptions
    from scrapers.engines.engine_manufacturers_list import (
        EngineManufacturersListScraper,
    )

    scraper = EngineManufacturersListScraper(options=ScraperOptions(include_urls=True))
    node = {
        "sub_sections": [{"name": "A"}],
        "sub_sub_sections": [{"name": "B"}],
        "sub_sub_sub_sections": [{"name": "C"}],
    }
    result = scraper._iter_sub_sections(node)
    assert len(result) == EXPECTED_SUBSECTION_COUNT


def test_iter_sub_sections_skips_non_dict_values() -> None:
    from scrapers.base.options import ScraperOptions
    from scrapers.engines.engine_manufacturers_list import (
        EngineManufacturersListScraper,
    )

    scraper = EngineManufacturersListScraper(options=ScraperOptions(include_urls=True))
    node = {"sub_sections": [{"name": "A"}, "not a dict"]}
    result = scraper._iter_sub_sections(node)
    assert len(result) == 1


# ---------------------------------------------------------------------------
# _extract_element_records
# ---------------------------------------------------------------------------


def test_extract_element_records_returns_empty_for_non_list_kind() -> None:
    from scrapers.base.options import ScraperOptions
    from scrapers.engines.engine_manufacturers_list import (
        EngineManufacturersListScraper,
    )

    scraper = EngineManufacturersListScraper(options=ScraperOptions(include_urls=True))
    assert scraper._extract_element_records({"kind": "table"}) == []


def test_extract_element_records_returns_empty_for_missing_data() -> None:
    from scrapers.base.options import ScraperOptions
    from scrapers.engines.engine_manufacturers_list import (
        EngineManufacturersListScraper,
    )

    scraper = EngineManufacturersListScraper(options=ScraperOptions(include_urls=True))
    assert scraper._extract_element_records({"kind": "list"}) == []


def test_extract_element_records_returns_empty_for_non_dict_data() -> None:
    from scrapers.base.options import ScraperOptions
    from scrapers.engines.engine_manufacturers_list import (
        EngineManufacturersListScraper,
    )

    scraper = EngineManufacturersListScraper(options=ScraperOptions(include_urls=True))
    assert (
        scraper._extract_element_records({"kind": "list", "data": "not a dict"}) == []
    )


def test_extract_element_records_returns_empty_for_non_list_items() -> None:
    from scrapers.base.options import ScraperOptions
    from scrapers.engines.engine_manufacturers_list import (
        EngineManufacturersListScraper,
    )

    scraper = EngineManufacturersListScraper(options=ScraperOptions(include_urls=True))
    element = {"kind": "list", "data": {"items": "not a list"}}
    assert scraper._extract_element_records(element) == []


def test_extract_element_records_normalizes_items() -> None:
    from scrapers.base.options import ScraperOptions
    from scrapers.engines.engine_manufacturers_list import (
        EngineManufacturersListScraper,
    )

    scraper = EngineManufacturersListScraper(options=ScraperOptions(include_urls=True))
    element = {
        "kind": "list",
        "data": {
            "items": [
                {"manufacturer": "Ferrari", "manufacturer_url": "/wiki/Ferrari"},
            ],
        },
    }
    result = scraper._extract_element_records(element)
    assert len(result) == 1


# ---------------------------------------------------------------------------
# _visit_indianapolis_sections
# ---------------------------------------------------------------------------


def test_visit_indianapolis_sections_collects_records_from_elements() -> None:
    from scrapers.base.options import ScraperOptions
    from scrapers.engines.engine_manufacturers_list import (
        EngineManufacturersListScraper,
    )

    scraper = EngineManufacturersListScraper(options=ScraperOptions(include_urls=True))
    node = {
        "elements": [
            {
                "kind": "list",
                "data": {
                    "items": [
                        {
                            "manufacturer": "Ferrari",
                            "manufacturer_url": "/wiki/Ferrari",
                        },
                    ],
                },
            },
        ],
    }
    records: list = []
    scraper._visit_indianapolis_sections(node, records)
    assert len(records) == 1


# ---------------------------------------------------------------------------
# IndianapolisOnlySubSectionParser
# ---------------------------------------------------------------------------


def test_indianapolis_only_sub_section_parser_handles_non_list_elements() -> None:
    from scrapers.engines.engine_manufacturers_list import (
        IndianapolisOnlySubSectionParser,
    )

    parser = IndianapolisOnlySubSectionParser()
    payload = {
        "elements": [
            {"kind": "table", "raw_html_fragment": "<table></table>"},
        ],
    }
    # Should not raise or modify table elements
    parser._apply_indianapolis_only_list_parser(payload)
    assert payload["elements"][0]["kind"] == "table"


def test_indianapolis_only_sub_section_parser_processes_list_elements() -> None:
    from scrapers.engines.engine_manufacturers_list import (
        IndianapolisOnlySubSectionParser,
    )

    parser = IndianapolisOnlySubSectionParser()
    payload = {
        "elements": [
            {
                "kind": "list",
                "raw_html_fragment": (
                    "<ul><li><a href='/wiki/Ferrari'>Ferrari</a></li></ul>"
                ),
            },
        ],
    }
    parser._apply_indianapolis_only_list_parser(payload)
    elem = payload["elements"][0]
    assert "data" in elem
    assert "items" in elem["data"]


def test_indianapolis_only_sub_section_parser_processes_nested_dicts() -> None:
    from scrapers.engines.engine_manufacturers_list import (
        IndianapolisOnlySubSectionParser,
    )

    parser = IndianapolisOnlySubSectionParser()
    payload = {
        "child": {
            "elements": [
                {
                    "kind": "list",
                    "raw_html_fragment": "<ul><li>Test</li></ul>",
                },
            ],
        },
    }
    parser._apply_indianapolis_only_list_parser(payload)
    # Should process nested dict
    assert "elements" in payload["child"]


def test_indianapolis_only_sub_section_parser_processes_nested_lists() -> None:
    from scrapers.engines.engine_manufacturers_list import (
        IndianapolisOnlySubSectionParser,
    )

    parser = IndianapolisOnlySubSectionParser()
    payload = {
        "items": [
            {
                "elements": [
                    {
                        "kind": "list",
                        "raw_html_fragment": "<ul><li>Item</li></ul>",
                    },
                ],
            },
        ],
    }
    parser._apply_indianapolis_only_list_parser(payload)
    # Should process lists of dicts recursively
    assert len(payload["items"]) == 1


# ---------------------------------------------------------------------------
# EngineManufacturersSectionParser
# ---------------------------------------------------------------------------


def test_engine_manufacturers_section_parser_processes_table_elements() -> None:
    from scrapers.engines.engine_manufacturers_list import (
        EngineManufacturersSectionParser,
    )

    parser = EngineManufacturersSectionParser()
    # Create a fake parsed payload with a table element (dict with kind=table)
    payload = {
        "elements": [
            {"kind": "table", "data": {"headers": ["Name"], "rows": []}},
            {"kind": "table", "data": None},
        ],
    }
    parser._apply_engine_table_parser(payload)
    # Should not raise


def test_engine_manufacturers_section_parser_handles_nested_payload() -> None:
    from scrapers.engines.engine_manufacturers_list import (
        EngineManufacturersSectionParser,
    )

    parser = EngineManufacturersSectionParser()
    payload = {
        "section": {"elements": [{"kind": "table", "data": None}]},
        "items": [{"elements": [{"kind": "table", "data": None}]}],
    }
    parser._apply_engine_table_parser(payload)
    # Should not raise
