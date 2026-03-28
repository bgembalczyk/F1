# ruff: noqa: E501, PLR2004, RUF001, RUF002, RUF003, SLF001, ARG001, ARG002, N802, B017, PT011, PT017, E402, PT001, PLC0415, RUF100
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
from tests.support.compat_stubs import ensure_bs4_stub
from tests.support.compat_stubs import ensure_certifi_stub

ensure_bs4_stub()
ensure_certifi_stub()


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


def test_validated_model_exposes_shared_record_contract():
    errors = Circuit.validate_record(
        {"circuit": {"text": "Monza", "url": "https://example.com"}},
    )

    messages = [error.message for error in errors]
    assert "Missing key: circuit_status" in messages
    assert "Missing key: country" in messages
    assert "Missing key: seasons" in messages


def test_validated_model_model_validate_uses_schema_before_instantiation():
    with pytest.raises(ValueError, match="Circuit validation failed"):
        Circuit.model_validate(
            {"circuit": {"text": "Monza", "url": "https://example.com"}},
        )


def test_scraper_config_validates_on_init():
    with pytest.raises(
        ValueError,
        match=r"ScraperConfig\.url must be a non-empty string\.",
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
