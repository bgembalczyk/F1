from __future__ import annotations

from models.services.circuit_service import CircuitService
from models.services.driver_service import DriverService
from models.services.season_service import SeasonService


def test_season_service_parses_years_and_ranges() -> None:
    seasons = SeasonService.parse_seasons("1973, 1975–1976, 1984", current_year=2024)
    years = [season["year"] for season in seasons]

    assert years == [1973, 1975, 1976, 1984]
    assert seasons[0]["url"].endswith("1973_Formula_One_World_Championship")


def test_driver_service_parses_championships() -> None:
    result = DriverService.parse_championships("2\n2005–2006")

    assert result["count"] == 2
    assert [season["year"] for season in result["seasons"]] == [2005, 2006]


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
                        }
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
                    }
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
                        }
                    ],
                }
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
    assert records[0]["time"] == 80.0
