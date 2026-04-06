from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.seasons.parsers.entries import SeasonEntriesParser


class _FakePolicy:
    def resolve_engine_config(self, _season_year: int | None):
        return None

    def should_normalize_entry_numbers(self, season_year: int | None) -> bool:
        return season_year is not None and season_year < 2007  # noqa: PLR2004


class _FakeTableParser:
    def __init__(self, records: list[dict]):
        self.records = records

    def parse_table(self, *_args, **_kwargs):
        return list(self.records)


class _FakeMerger:
    def merge_entries(self, records: list[dict]):
        return records


def test_entries_parser_normalizes_single_number_for_multiple_drivers_pre_2007(
) -> None:
    parser = SeasonEntriesParser(
        table_parser=_FakeTableParser(
            [
                {
                    "constructor": {"text": "Team"},
                    "no": ["44", ""],
                    "race_drivers": [{"text": "A"}, {"text": "B"}],
                },
            ],
        ),
        entry_merger=_FakeMerger(),
        policy=_FakePolicy(),
    )

    parsed = parser.parse(BeautifulSoup("<html></html>", "html.parser"), 2006)

    assert parsed[0]["no"] == ["44", "44"]


def test_entries_parser_does_not_normalize_when_multiple_numbers_present() -> None:
    parser = SeasonEntriesParser(
        table_parser=_FakeTableParser(
            [
                {
                    "no": ["44", "77"],
                    "drivers": [{"text": "A"}, {"text": "B"}],
                },
            ],
        ),
        entry_merger=_FakeMerger(),
        policy=_FakePolicy(),
    )

    parsed = parser.parse(BeautifulSoup("<html></html>", "html.parser"), 2006)

    assert parsed[0]["no"] == ["44", "77"]
