# ruff: noqa: E501, PLR2004
from unittest.mock import MagicMock, patch

import pytest

from scrapers.constructors.helpers.export import constructor_name_initial


@pytest.mark.parametrize(
    ("record", "expected"),
    [
        # dict constructor with text
        ({"constructor": {"text": "Ferrari"}}, "F"),
        # dict constructor without text, uses names list
        ({"constructor": {"text": "", "names": ["McLaren F1 Team"]}}, "M"),
        # dict constructor without text, names list first item not str
        ({"constructor": {"text": "", "names": [123]}}, "other"),
        # dict constructor without text, empty names list
        ({"constructor": {"text": "", "names": []}}, "other"),
        # dict constructor without text, no names key
        ({"constructor": {"text": ""}}, "other"),
        # string constructor
        ({"constructor": "Williams"}, "W"),
        # team key fallback
        ({"team": "Red Bull"}, "R"),
        # empty team
        ({"team": ""}, "other"),
        # no constructor or team
        ({}, "other"),
        # name with no letters (e.g., digits only)
        ({"constructor": "123"}, "other"),
        # lowercase first letter should be uppercased
        ({"constructor": "alpine"}, "A"),
    ],
)
def test_constructor_name_initial(record: dict, expected: str) -> None:
    assert constructor_name_initial(record) == expected


def test_export_complete_constructors_calls_fetch_and_export() -> None:
    from pathlib import Path

    with (
        patch("scrapers.constructors.helpers.export.init_scraper_options") as mock_opts,
        patch("scrapers.constructors.helpers.export.CompleteConstructorsDataExtractor") as mock_cls,
        patch("scrapers.constructors.helpers.export.export_grouped_json") as mock_export,
    ):
        mock_scraper = MagicMock()
        mock_scraper.fetch.return_value = [{"constructor": {"text": "Ferrari"}}]
        mock_cls.return_value = mock_scraper

        from scrapers.constructors.helpers.export import export_complete_constructors

        output_dir = Path("/fake/output")
        export_complete_constructors(output_dir=output_dir, include_urls=False)

        mock_opts.assert_called_once_with(None, include_urls=False)
        mock_scraper.fetch.assert_called_once()
        mock_export.assert_called_once()
