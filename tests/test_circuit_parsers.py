import pytest
from bs4 import BeautifulSoup

from scrapers.base.infobox.circuits.services.additional_info import (
    CircuitAdditionalInfoParser,
)
from scrapers.base.infobox.circuits.services.entities import CircuitEntitiesParser
from scrapers.base.infobox.circuits.services.entity_parsing import CircuitEntityParser
from scrapers.base.infobox.circuits.services.geo import CircuitGeoParser
from scrapers.base.infobox.circuits.services.history import CircuitHistoryParser
from scrapers.base.infobox.circuits.services.lap_record import CircuitLapRecordParser
from scrapers.base.infobox.circuits.services.layouts import CircuitLayoutsParser
from scrapers.base.infobox.circuits.services.sections import WikipediaSectionExtractor
from scrapers.base.infobox.circuits.services.specs import CircuitSpecsParser
from scrapers.base.infobox.circuits.services.text_utils import InfoboxTextUtils
from scrapers.base.infobox.scraper import WikipediaInfoboxScraper


def test_circuit_geo_parser_location_and_coordinates() -> None:
    parser = CircuitGeoParser()
    row = {
        "text": "Paris, France",
        "links": [
            {"text": "Paris", "url": "https://en.wikipedia.org/wiki/Paris"},
            {"text": "France", "url": "https://en.wikipedia.org/wiki/France"},
        ],
    }
    location = parser._parse_location(row)
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

    coords = parser._parse_coordinates({"text": "48.8566; 2.3522"})
    assert coords == {"lat": 48.8566, "lon": 2.3522}


def test_circuit_history_parser_former_names() -> None:
    parser = CircuitHistoryParser()
    row = {"text": "Old Name (1959–1979)"}
    names = parser._parse_former_names(row)
    assert names == [{"name": "Old Name", "periods": [{"from": "1959", "to": "1979"}]}]


def test_circuit_specs_parser_surface_and_banking() -> None:
    parser = CircuitSpecsParser()
    surface = parser._parse_surface({"text": "Asphalt (since 2020)"})
    assert surface == {
        "values": ["Asphalt"],
        "text": "Asphalt (since 2020)",
        "note": "since 2020",
    }

    banking = parser._parse_banking({"text": "18° (Turn 1)"})
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
    record = parser._parse_lap_record(row)
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
            <tr><th class="infobox-header" colspan="2">Grand Prix layout (2020–)</th></tr>
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
            "years": "2020–",
            "length_km": 5.0,
            "length_mi": 3.1,
            "turns": 15,
            "race_lap_record": None,
            "surface": None,
            "banking": None,
        }
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
            "Location": {
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
            "Coordinates": {"text": "12.34; 56.78"},
            "Length": {"text": "5.0 km (3.1 mi)"},
            "Turns": {"text": "10"},
            "Race lap record": {
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
            "Surface": {"text": "Asphalt"},
            "Banking": {"text": "18°"},
            "Opened": {"text": "1950"},
            "Architect": {
                "text": "Jane Designer",
                "links": [
                    {
                        "text": "Jane Designer",
                        "url": "https://en.wikipedia.org/wiki/Jane_Designer",
                    }
                ],
            },
            "Nickname": {"text": "The Test"},
        },
    }

    result = parser.with_normalized(raw, layout_records=None)
    assert result["normalized"]["name"] == "Test Circuit"
    assert result["normalized"]["specs"]["length_km"] == 5.0
    assert result["normalized"]["specs"]["turns"] == 10
    assert result["normalized"]["architect"] == {
        "text": "Jane Designer",
        "url": "https://en.wikipedia.org/wiki/Jane_Designer",
    }
    assert result["layouts"][0]["surface"]["values"] == ["Asphalt"]
    assert result["normalized"]["additional_info"]["Nickname"]["text"] == "The Test"


def test_wikipedia_section_extractor() -> None:
    extractor = WikipediaSectionExtractor()
    soup = BeautifulSoup(
        """
        <h2 id="History">History</h2>
        <p>Some history text.</p>
        <h2 id="Legacy">Legacy</h2>
        <p>Legacy text.</p>
        """,
        "html.parser",
    )
    section = extractor.extract_section_by_id(soup, "History")
    assert section is not None
    assert "Some history text." in section.get_text(" ")
    assert "Legacy text." not in section.get_text(" ")
