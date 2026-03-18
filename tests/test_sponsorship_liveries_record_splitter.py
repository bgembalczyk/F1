"""Record splitter focused tests for sponsorship liveries."""
from scrapers.base.helpers.text_normalization import split_delimited_text
from scrapers.sponsorship_liveries.parsers.splitters.record.facade import SponsorshipRecordSplitter


def test_livery_principal_sponsors_year_filter() -> None:
    """livery_principal_sponsors is correctly filtered per expanded season year."""
    sponsors = [
        {"text": "OKX", "url": "https://en.wikipedia.org/wiki/OKX"},
        {
            "text": "Google Chrome",
            "url": "https://en.wikipedia.org/wiki/Google_Chrome",
            "params": ["2024-2025"],
        },
        {
            "text": "Google Gemini",
            "url": "https://en.wikipedia.org/wiki/Gemini_(chatbot)",
            "params": ["2025-2026"],
        },
        {"text": "Mastercard", "url": "https://en.wikipedia.org/wiki/Mastercard"},
    ]
    record = {
        "season": [
            {
                "year": 2024,
                "url": "https://en.wikipedia.org/wiki/2024_Formula_One_World_Championship",
            },
            {
                "year": 2025,
                "url": "https://en.wikipedia.org/wiki/2025_Formula_One_World_Championship",
            },
            {
                "year": 2026,
                "url": "https://en.wikipedia.org/wiki/2026_Formula_One_World_Championship",
            },
        ],
        "main_colours": ["Orange", "Black"],
        "livery_principal_sponsors": sponsors,
    }
    splitter = SponsorshipRecordSplitter()
    result = splitter.split_record_by_season(record)

    assert len(result) == 3

    by_year = {r["season"][0]["year"]: r for r in result}

    texts_2024 = [s.get("text") for s in by_year[2024]["livery_principal_sponsors"]]
    assert texts_2024 == ["OKX", "Google Chrome", "Mastercard"]

    texts_2025 = [s.get("text") for s in by_year[2025]["livery_principal_sponsors"]]
    assert texts_2025 == ["OKX", "Google Chrome", "Google Gemini", "Mastercard"]

    texts_2026 = [s.get("text") for s in by_year[2026]["livery_principal_sponsors"]]
    assert texts_2026 == ["OKX", "Google Gemini", "Mastercard"]


def test_split_record_by_season_matra_case() -> None:
    """Full Matra integration: possessive groups produce two driver records."""

    text = "Green and White (Pescarolo's car), White and Red (Beltoise's car)"
    colour_list = split_delimited_text(text)

    record = {
        "season": [
            {
                "year": 1970,
                "url": "https://en.wikipedia.org/wiki/1970_Formula_One_World_Championship",
            },
            {
                "year": 1971,
                "url": "https://en.wikipedia.org/wiki/1971_Formula_One_World_Championship",
            },
            {
                "year": 1972,
                "url": "https://en.wikipedia.org/wiki/1972_Formula_One_World_Championship",
            },
        ],
        "main_colours": ["Blue"],
        "additional_colours": colour_list,
        "livery_sponsors": ["Matra-Simca"],
    }

    splitter = SponsorshipRecordSplitter()
    result = splitter.split_record_by_season(record)

    assert len(result) == 2

    by_driver = {r["driver"][0]["text"]: r for r in result}

    pescarolo = by_driver["Pescarolo"]
    assert pescarolo["main_colours"] == ["Blue"]
    assert pescarolo["additional_colours"] == ["Green", "White"]
    assert len(pescarolo["season"]) == 3

    beltoise = by_driver["Beltoise"]
    assert beltoise["main_colours"] == ["Blue"]
    assert beltoise["additional_colours"] == ["White", "Red"]
    assert len(beltoise["season"]) == 3


def test_split_record_by_season_possessive_with_common_colours() -> None:
    """Common (non-possessive) colours are shared across all driver records."""

    record = {
        "season": [{"year": 1970}],
        "main_colours": ["Blue"],
        "additional_colours": [
            "Yellow",
            "Green and White (Pescarolo's car)",
            "White and Red (Beltoise's car)",
        ],
    }

    splitter = SponsorshipRecordSplitter()
    result = splitter.split_record_by_season(record)

    assert len(result) == 2
    by_driver = {r["driver"][0]["text"]: r for r in result}
    assert by_driver["Pescarolo"]["additional_colours"] == ["Green", "White", "Yellow"]
    assert by_driver["Beltoise"]["additional_colours"] == ["White", "Red", "Yellow"]


def test_split_pipeline_mixed_season_gp_and_possessive_order() -> None:
    """Pipeline applies possessive -> season -> GP split in deterministic order."""

    record = {
        "season": [{"year": 2024}, {"year": 2025}],
        "main_colours": [
            "Blue (Monaco Grand Prix)",
            "Green and White (Driver A's car)",
            "White and Red (Driver B's car)",
        ],
        "main_sponsors": [
            {"text": "Base"},
            {"text": "Season 2024", "params": ["2024"]},
            {"text": "Season 2025", "params": ["2025"]},
        ],
        "livery_sponsors": [
            {"text": "Monaco only", "params": ["Monaco Grand Prix"]},
        ],
    }

    result = SponsorshipRecordSplitter().split_record_by_season(record)

    assert len(result) == 8
    signature = [
        (
            r["driver"][0]["text"],
            tuple(s["year"] for s in r["season"]),
            r.get("grand_prix_scope", {}).get("type"),
        )
        for r in result
    ]
    assert signature == [
        ("Driver A", (2024,), "only"),
        ("Driver A", (2024,), "other"),
        ("Driver A", (2025,), "only"),
        ("Driver A", (2025,), "other"),
        ("Driver B", (2024,), "only"),
        ("Driver B", (2024,), "other"),
        ("Driver B", (2025,), "only"),
        ("Driver B", (2025,), "other"),
    ]


def test_split_pipeline_is_deterministic_for_mixed_case() -> None:
    """Same mixed input produces identical output ordering across repeated runs."""

    record = {
        "season": [{"year": 2024}, {"year": 2025}],
        "main_colours": [
            "Blue (Monaco Grand Prix)",
            "Green and White (Driver A's car)",
            "White and Red (Driver B's car)",
        ],
        "main_sponsors": [{"text": "Base"}],
    }

    splitter = SponsorshipRecordSplitter()
    result_1 = splitter.split_record_by_season(record)
    result_2 = splitter.split_record_by_season(record)

    assert result_1 == result_2
