import re
import sys
import types
from dataclasses import dataclass

import pytest

from models.validation.base import ValidatedModel
from models.validation.circuit import Circuit
from models.validation.constants import CIRCUIT_STATUS_CURRENT
from models.validation.constants import MANUFACTURER_STATUS_FORMER
from models.validation.engine_manufacturer import EngineManufacturer
from models.value_objects.link_utils import normalize_link
from scrapers.base.options import ScraperOptions
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper

if "bs4" not in sys.modules:
    bs4_stub = types.ModuleType("bs4")

    class _StubTag:
        def __init__(self, attrs=None, text: str = ""):
            self.attrs = attrs or {}
            self.text = text

        def get(self, key, default=None):
            return self.attrs.get(key, default)

        def get_text(self, *_, **__):
            return self.text

        def find_all(self, *_, **__):
            return []

        def find_all_next(self, *_, **__):
            return []

        @property
        def contents(self):
            return [self.text]

    class _StubBeautifulSoup:
        def __init__(self, html: str, *_):
            self.html = html

        def find(self, name: str | None = None, *_, **__):
            if name == "a":
                return self._parse_a(self.html)
            return _StubTag()

        def find_all(self, *_, **__):
            return []

        def _parse_a(self, html: str) -> _StubTag:
            href_match = re.search(r'href="([^"]*)"', html)
            class_match = re.search(r'class="([^"]*)"', html)
            text_match = re.search(r">([^<]*)<", html)

            attrs = {}
            if href_match:
                attrs["href"] = href_match.group(1)
            if class_match:
                attrs["class"] = class_match.group(1).split()

            return _StubTag(attrs, text_match.group(1) if text_match else "")

    bs4_stub.Tag = _StubTag
    bs4_stub.BeautifulSoup = _StubBeautifulSoup
    sys.modules["bs4"] = bs4_stub

if "certifi" not in sys.modules:
    certifi_stub = types.ModuleType("certifi")
    certifi_stub.where = lambda: ""
    sys.modules["certifi"] = certifi_stub


def test_circuit_rejects_invalid_url():
    with pytest.raises(ValueError):
        Circuit(
            circuit={"text": "Test", "url": "notaurl"},
            circuit_status=CIRCUIT_STATUS_CURRENT,
        )


def test_engine_manufacturer_rejects_negative_values():
    with pytest.raises(ValueError):
        EngineManufacturer(
            manufacturer={"text": "Test", "url": "https://example.com"},
            manufacturer_status=MANUFACTURER_STATUS_FORMER,
            races_entered=-1,
        )


def test_circuit_rejects_invalid_status():
    with pytest.raises(ValueError, match="Pole circuit_status"):
        Circuit(
            circuit={"text": "Test", "url": "https://example.com"},
            circuit_status="invalid",
        )


def test_circuit_rejects_invalid_season_url():
    with pytest.raises(ValueError, match="Pole seasons zawiera nieprawidłowy URL"):
        Circuit(
            circuit={"text": "Test", "url": "https://example.com"},
            circuit_status="current",
            seasons=[{"year": 2024, "url": "invalid"}],
        )


def test_validated_model_calls_validate():
    calls = []

    @dataclass
    class DummyModel(ValidatedModel):
        value: int

        def validate(self) -> None:
            calls.append(self.value)

    DummyModel(1)

    assert calls == [1]


def test_scraper_config_validates_on_init():
    with pytest.raises(
        ValueError,
        match="ScraperConfig.url must be a non-empty string.",
    ):
        ScraperConfig(url="")


def test_table_scraper_instantiates_model_and_filters_unknown_fields():
    @dataclass
    class RowModel:
        name: str

    class DummyScraper(F1TableScraper):
        url = "https://example.com"
        expected_headers = ["Name"]
        model_class = RowModel

    class FakeCell:
        def __init__(self, text: str):
            self.text = text

        def get_text(self, *_args, **_kwargs):
            return self.text

        def find_all(self, *_args, **_kwargs):
            return []

        @property
        def contents(self):
            return [self.text]

    scraper = DummyScraper(options=ScraperOptions(include_urls=False))
    result = scraper.parse_row(
        row={
            "Name": FakeCell("Example"),
            "Extra": FakeCell("Ignored"),
        },
    )

    assert result == {"name": "Example"}


def test_normalize_link_strips_text_and_empty_url():
    assert normalize_link({"text": " Example ", "url": ""}) == {
        "text": "Example",
        "url": None,
    }
