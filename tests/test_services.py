# ruff: noqa: F821, PLC0415, RUF001
import json
from pathlib import Path

from models.domain_utils.years import parse_year_range
from models.services.driver_service import parse_championships
from models.services.helpers import parse_int_values
from models.services.helpers import split_delimited_text
from models.services.rounds_service import parse_rounds
from models.services.season_service import parse_seasons
from scrapers.base.export.exporters import DataExporter
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.options import ScraperOptions
from scrapers.base.runner import RunConfig
from scrapers.circuits.models.services.circuit_service import CircuitService

CHAMPIONSHIP_SEASON_COUNT = 2
EXPECTED_LAP_TIME = 80.0


def test_season_service_parses_years_and_ranges() -> None:
    seasons = parse_seasons("1973, 1975-1976, 1984", current_year=2024)
    years = [season.year for season in seasons]

    assert years == [1973, 1975, 1976, 1984]
    assert seasons[0].url is not None
    assert seasons[0].url.endswith("1973_Formula_One_World_Championship")


def test_season_service_parses_onwards_range() -> None:
    seasons = parse_seasons("2025 onwards", current_year=2027)

    assert [season.year for season in seasons] == [2025, 2026, 2027]


def test_driver_service_parses_championships() -> None:
    result = parse_championships("2\n2005-2006")

    assert result.count == CHAMPIONSHIP_SEASON_COUNT
    assert [season.year for season in result.seasons] == [2005, 2006]


def test_driver_service_parses_championships_variants() -> None:
    cases = [
        ("0", 0, []),
        ("2\n2005-2006", CHAMPIONSHIP_SEASON_COUNT, [2005, 2006]),
        ("7\n1994-1995, 2000-2004", 7, [1994, 1995, 2000, 2001, 2002, 2003, 2004]),
    ]

    for raw, expected_count, expected_years in cases:
        result = parse_championships(raw)

        assert result.count == expected_count
        assert [season.year for season in result.seasons] == expected_years


def test_circuit_service_normalizes_record_and_merges_laps() -> None:
    raw = {
        "circuit": {"text": "Test Circuit", "url": "https://example.com"},
        "circuit_status": "current",
        "country": "Testland",
        "location": {"text": "Oldtown", "url": "https://oldtown.example.com"},
        "details": {
            "infobox": {
                "title": "Test Circuit",
                "normalized": {
                    "name": "Test Circuit",
                    "location": {
                        "city": {
                            "text": "Newcity",
                            "link": {"url": "https://newcity.example.com"},
                        },
                    },
                    "coordinates": {"lat": 1.0, "lon": 2.0},
                    "specs": {"fia_grade": "1"},
                    "history": {
                        "events": [{"year": 2000}],
                        "former_names": [{"text": "Old Circuit"}],
                    },
                },
                "layouts": [
                    {
                        "layout": "GP",
                        "length_km": 5.0,
                        "years": "2000-2001",
                        "race_lap_record": {
                            "driver": "Driver A",
                            "vehicle": "Car A",
                            "time": "1:20.000",
                            "year": 2000,
                        },
                    },
                ],
            },
            "tables": [
                {
                    "layout": "GP (2000)",
                    "lap_records": [
                        {
                            "driver": "Driver A",
                            "vehicle": "Car A",
                            "time": 80.0,
                            "year": 2000,
                        },
                    ],
                },
            ],
        },
        "grands_prix": [{"text": "Test GP", "url": "https://gp.example.com"}],
        "seasons": [{"year": 2000, "url": "https://season.example.com"}],
        "grands_prix_held": 1,
    }

    normalized = CircuitService.normalize_record(raw)

    assert normalized["url"] == "https://example.com"
    assert normalized["fia_grade"] == "1"
    assert normalized["history"] == [{"year": 2000}]

    places = {place["text"] for place in normalized["location"]["places"]}
    assert {"Oldtown", "Newcity", "Testland"} <= places

    layouts = normalized["layouts"]
    assert len(layouts) == 1
    records = layouts[0]["race_lap_records"]
    assert len(records) == 1
    assert records[0]["time"] == EXPECTED_LAP_TIME


def test_run_and_export_uses_run_config(tmp_path: Path) -> None:
    class DummyScraper:
        def __init__(self, *, options: ScraperOptions, marker: str) -> None:
            self.options = options
            self.marker = marker
            self.exporter = DataExporter()

        def fetch(self):
            return [
                {
                    "name": "test",
                    "marker": self.marker,
                    "url": "https://example.com" if self.options.include_urls else None,
                },
            ]

    run_config = RunConfig(
        include_urls=False,
        output_dir=tmp_path,
        scraper_kwargs={"marker": "custom"},
        options=ScraperOptions(include_urls=True),
    )

    run_and_export(
        DummyScraper,
        "dummy.json",
        "dummy.csv",
        run_config=run_config,
    )

    json_path = tmp_path / "dummy.json"
    csv_path = tmp_path / "dummy.csv"

    assert json_path.exists()
    assert csv_path.exists()

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload == [
        {"name": "test", "marker": "custom", "url": None},
    ]
    assert "marker" in csv_path.read_text(encoding="utf-8")


def test_split_delimited_text_handles_multiple_separators() -> None:
    assert split_delimited_text("A, B;C / D") == ["A", "B", "C", "D"]
    assert split_delimited_text("") == []


def test_parse_int_values_handles_missing_and_multiple_numbers() -> None:
    assert parse_int_values("12 entries, 10 starts") == [12, 10]
    assert parse_int_values(None) == []


def test_parse_year_range_handles_present_and_short_end_year() -> None:
    assert parse_year_range("2001-03") == {"start": 2001, "end": 2003}
    assert parse_year_range("2005-present") == {"start": 2005, "end": None}
    assert parse_year_range("1999") == {"start": 1999, "end": 1999}
    assert parse_year_range("unknown") == {"start": None, "end": None}


def test_season_service_handles_dash_variants_reversed_ranges_and_duplicates() -> None:
    seasons = parse_seasons(
        "2005—2003, 2001–03, 2003, 2004",
        current_year=2026,
    )

    assert [season.year for season in seasons] == [2003, 2004, 2005, 2001, 2002]


def test_parse_year_range_handles_edge_cases() -> None:
    assert parse_year_range("2001–03") == {"start": 2001, "end": 2003}
    assert parse_year_range("2007—2005") == {"start": 2005, "end": 2007}
    assert parse_year_range("2005 onwards") == {"start": 2005, "end": None}
    assert parse_year_range("2019-present") == {"start": 2019, "end": None}


def test_year_parser_uses_domain_range_rules() -> None:
    from scrapers.drivers.infobox.parsers.year import YearParser

    assert YearParser.parse_year_range("2019 onwards") == {"start": 2019, "end": None}
    assert YearParser.parse_year_range("2007—2005") == {"start": 2005, "end": 2007}


def test_rounds_service_handles_dash_variants_and_reversed_ranges() -> None:
    rounds = parse_rounds("5—3; 2–4; round 4")
    assert rounds == [2, 3, 4, 5]
