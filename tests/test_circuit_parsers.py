import pytest
from bs4 import BeautifulSoup

from scrapers.base.infobox.scraper import WikipediaInfoboxScraper
from scrapers.circuits.infobox.services.additional_info import (
    CircuitAdditionalInfoParser,
)
from scrapers.circuits.infobox.services.entities import CircuitEntitiesParser
from scrapers.circuits.infobox.services.entity_parsing import CircuitEntityParser
from scrapers.circuits.infobox.services.geo import CircuitGeoParser
from scrapers.circuits.infobox.services.history import CircuitHistoryParser
from scrapers.circuits.infobox.services.lap_record import CircuitLapRecordParser
from scrapers.circuits.infobox.services.lap_record import extract_time
from scrapers.circuits.infobox.services.lap_record import select_details_paren
from scrapers.circuits.infobox.services.layouts import CircuitLayoutsParser
from scrapers.circuits.infobox.services.specs import CircuitSpecsParser
from scrapers.circuits.infobox.services.text_utils import InfoboxTextUtils

LAYOUT_YEARS = "2020-"
EXPECTED_LENGTH_KM = 5.0
EXPECTED_TURNS = 10



def test_circuit_geo_parser_location_and_coordinates() -> None:
    parser = CircuitGeoParser()
    row = {
        "text": "Paris, France",
        "links": [
            {"text": "Paris", "url": "https://en.wikipedia.org/wiki/Paris"},
            {"text": "France", "url": "https://en.wikipedia.org/wiki/France"},
        ],
    }
    location = parser._parse_location(row)  # noqa: SLF001
    assert location == {
        "localisation1": {
            "text": "Paris",
            "link": {
                "text": "Paris",
                "url": "https://en.wikipedia.org/wiki/Paris",
            },
        },
        "localisation2": {
            "text": "France",
            "link": {
                "text": "France",
                "url": "https://en.wikipedia.org/wiki/France",
            },
        },
    }

    coords = parser._parse_coordinates({"text": "48.8566; 2.3522"})  # noqa: SLF001
    assert coords == {"lat": 48.8566, "lon": 2.3522}


def test_circuit_history_parser_former_names() -> None:
    parser = CircuitHistoryParser()
    row = {"text": "Old Name (1959-1979)"}
    names = parser._parse_former_names(row)  # noqa: SLF001
    assert names == [{"name": "Old Name", "periods": [{"from": "1959", "to": "1979"}]}]


def test_circuit_specs_parser_surface_and_banking() -> None:
    parser = CircuitSpecsParser()
    surface = parser._parse_surface({"text": "Asphalt (since 2020)"})  # noqa: SLF001
    assert surface == {
        "values": ["Asphalt"],
        "text": "Asphalt (since 2020)",
        "note": "since 2020",
    }

    banking = parser._parse_banking({"text": "18° (Turn 1)"})  # noqa: SLF001
    assert banking == {"value": 18.0, "unit": "deg", "note": "Turn 1"}


def test_circuit_lap_record_parser_basic() -> None:
    parser = CircuitLapRecordParser()
    row = {
        "text": "1:20.123 (John Doe, Fast Car, 2023, Formula One)",
        "links": [
            {"text": "John Doe", "url": "https://en.wikipedia.org/wiki/John_Doe"},
            {"text": "Fast Car", "url": "https://en.wikipedia.org/wiki/Fast_Car"},
            {"text": "Formula One", "url": "https://en.wikipedia.org/wiki/Formula_One"},
        ],
    }
    record = parser.parse_lap_record(row)
    assert record is not None
    assert record["time"] == pytest.approx(80.123)
    assert record["driver"] == {
        "text": "John Doe",
        "url": "https://en.wikipedia.org/wiki/John_Doe",
    }
    assert record["vehicle"] == {
        "text": "Fast Car",
        "url": "https://en.wikipedia.org/wiki/Fast_Car",
    }
    assert record["year"] == "2023"


def test_extract_time_parser() -> None:
    assert extract_time("1:20.123 (John Doe, Fast Car, 2023)") == pytest.approx(80.123)
    assert extract_time("Record (John Doe, 2023) 1:02.500") == pytest.approx(62.5)
    assert extract_time("No time here") is None


def test_select_details_paren() -> None:
    text = "1:20.123 (John Doe, Fast Car, 2023, Formula One) (234 km/h)"
    assert select_details_paren(text) == [
        "John Doe",
        "Fast Car",
        "2023",
        "Formula One",
    ]

    text = "1:20.123 (234 km/h) (John Doe, Fast Car)"
    assert select_details_paren(text) == ["John Doe", "Fast Car"]

    text = "1:20.123 (John Doe)"
    assert select_details_paren(text) == []


def test_circuit_layouts_parser_basic() -> None:
    infobox_scraper = WikipediaInfoboxScraper()
    text_utils = InfoboxTextUtils()
    lap_record_parser = CircuitLapRecordParser()
    specs_parser = CircuitSpecsParser()
    parser = CircuitLayoutsParser(
        infobox_scraper=infobox_scraper,
        text_utils=text_utils,
        lap_record_parser=lap_record_parser,
        specs_parser=specs_parser,
    )

    soup = BeautifulSoup(
        """
        <table class="infobox">
            <tr><th class="infobox-header" colspan="2">
                Grand Prix layout (2020-)
            </th></tr>
            <tr><th>Length</th><td>5.0 km (3.1 mi)</td></tr>
            <tr><th>Turns</th><td>15</td></tr>
        </table>
        """,
        "html.parser",
    )
    layouts = parser.parse_layout_sections(soup)
    assert layouts == [
        {
            "layout": "Grand Prix layout",
            "years": LAYOUT_YEARS,
            "length_km": EXPECTED_LENGTH_KM,
            "length_mi": 3.1,
            "turns": 15,
            "race_lap_record": None,
            "surface": None,
            "banking": None,
        },
    ]


def test_circuit_entities_parser_default_layout() -> None:
    text_utils = InfoboxTextUtils()
    geo_parser = CircuitGeoParser()
    history_parser = CircuitHistoryParser()
    specs_parser = CircuitSpecsParser()
    lap_record_parser = CircuitLapRecordParser()
    entity_parser = CircuitEntityParser()
    additional_info_parser = CircuitAdditionalInfoParser()

    parser = CircuitEntitiesParser(
        text_utils=text_utils,
        geo_parser=geo_parser,
        history_parser=history_parser,
        specs_parser=specs_parser,
        lap_record_parser=lap_record_parser,
        entity_parser=entity_parser,
        additional_info_parser=additional_info_parser,
    )

    raw = {
        "title": "Test Circuit",
        "rows": {
            "location": {
                "text": "Test City, Testland",
                "links": [
                    {
                        "text": "Test City",
                        "url": "https://en.wikipedia.org/wiki/Test_City",
                    },
                    {
                        "text": "Testland",
                        "url": "https://en.wikipedia.org/wiki/Testland",
                    },
                ],
            },
            "coordinates": {"text": "12.34; 56.78"},
            "length": {"text": "5.0 km (3.1 mi)"},
            "turns": {"text": "10"},
            "race_lap_record": {
                "text": "1:10.000 (Jane Roe, Speedster, 2022)",
                "links": [
                    {
                        "text": "Jane Roe",
                        "url": "https://en.wikipedia.org/wiki/Jane_Roe",
                    },
                    {
                        "text": "Speedster",
                        "url": "https://en.wikipedia.org/wiki/Speedster",
                    },
                ],
            },
            "surface": {"text": "Asphalt"},
            "banking": {"text": "18°"},
            "opened": {"text": "1950"},
            "architect": {
                "text": "Jane Designer",
                "links": [
                    {
                        "text": "Jane Designer",
                        "url": "https://en.wikipedia.org/wiki/Jane_Designer",
                    },
                ],
            },
            "nickname": {"text": "The Test"},
        },
    }

    result = parser.with_normalized(raw, layout_records=None)
    assert result["normalized"]["name"] == "Test Circuit"
    assert result["normalized"]["specs"]["length_km"] == EXPECTED_LENGTH_KM
    assert result["normalized"]["specs"]["turns"] == EXPECTED_TURNS
    assert result["normalized"]["architect"] == {
        "text": "Jane Designer",
        "url": "https://en.wikipedia.org/wiki/Jane_Designer",
    }
    assert result["layouts"][0]["surface"]["values"] == ["Asphalt"]
    assert result["normalized"]["additional_info"]["nickname"]["text"] == "The Test"


def test_entity_parser_multiple_links_language_marker() -> None:
    parser = CircuitEntityParser()
    row = {
        "text": "Example [it]",
        "links": [
            {"text": "it", "url": "https://it.wikipedia.org/wiki/Example"},
            {"text": "Example", "url": "https://en.wikipedia.org/wiki/Example"},
        ],
    }
    result = parser.parse_linked_entity(row)
    assert result == [
        {"text": "Example", "url": "https://en.wikipedia.org/wiki/Example"},
    ]


def test_entity_parser_single_link_with_multiple_parts() -> None:
    parser = CircuitEntityParser()
    row = {
        "text": "A, B and C",
        "links": [{"text": "B", "url": "https://en.wikipedia.org/wiki/B"}],
    }
    result = parser.parse_linked_entity(row)
    assert result == [
        {"text": "A", "url": None},
        {"text": "B", "url": "https://en.wikipedia.org/wiki/B"},
        {"text": "C", "url": None},
    ]


def test_entity_parser_redlink_url_none() -> None:
    parser = CircuitEntityParser()
    row = {
        "text": "Red Page",
        "links": [
            {
                "text": "Red Page",
                "url": (
                    "https://en.wikipedia.org/w/index.php?title=Red_Page"
                    "&action=edit&redlink=1"
                ),
            },
        ],
    }
    result = parser.parse_linked_entity(row)
    assert result == {"text": "Red Page", "url": None}
