from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any
from typing import ClassVar

import pytest

from models.value_objects.base import ValueObject
from models.value_objects.drivers_championships import DriversChampionships
from models.value_objects.link import Link
from models.value_objects.normalized_date import NormalizedDate
from models.value_objects.season_ref import SeasonRef
from models.value_objects.time_types import DateValue


@pytest.mark.parametrize(
    ("vo_cls", "payload", "expected"),
    [
        (
            DateValue,
            {"iso": "2024-01-01", "year": 2024},
            DateValue(iso="2024-01-01", year=2024),
        ),
        (
            Link,
            {"text": "Docs", "url": "https://example.com"},
            Link(text="Docs", url="https://example.com"),
        ),
        (
            NormalizedDate,
            {"text": " Test ", "iso": " 2024-01-01 "},
            NormalizedDate(text="Test", iso="2024-01-01"),
        ),
        (
            SeasonRef,
            {"year": 2024, "url": "https://example.com"},
            SeasonRef(year=2024, url="https://example.com"),
        ),
        (
            DriversChampionships,
            {"count": 1, "seasons": [{"year": 2021}]},
            DriversChampionships(count=1, seasons=[SeasonRef(year=2021)]),
        ),
    ],
)
def test_from_dict_matches_from_mapping_contract(
    vo_cls: type[ValueObject],
    payload: Mapping[str, Any],
    expected: ValueObject,
) -> None:
    assert vo_cls.from_mapping(payload) == expected
    assert vo_cls.from_dict(payload) == expected


def test_from_dict_delegates_to_from_mapping() -> None:
    @dataclass
    class ProbeValueObject(ValueObject):
        value: int

        called: ClassVar[bool] = False

        @classmethod
        def from_mapping(cls, data: Mapping[str, Any]) -> ProbeValueObject:
            cls.called = True
            return cls(value=int(data["value"]))

    value = ProbeValueObject.from_dict({"value": 7})

    assert value == ProbeValueObject(value=7)
    assert ProbeValueObject.called is True


@pytest.mark.parametrize(
    "vo_cls",
    [DateValue, Link, NormalizedDate, SeasonRef, DriversChampionships],
)
def test_from_dict_rejects_non_mapping_inputs(vo_cls: type[ValueObject]) -> None:
    with pytest.raises(TypeError, match="Nieobsługiwany typ danych"):
        vo_cls.from_dict("not-a-mapping")


@pytest.mark.parametrize(
    ("vo_cls", "payload"),
    [
        (SeasonRef, {"year": "x"}),
        (Link, {"text": "Docs", "url": "notaurl"}),
        (DriversChampionships, {"count": "bad"}),
    ],
)
def test_from_dict_normalizes_construction_errors(
    vo_cls: type[ValueObject],
    payload: Mapping[str, Any],
) -> None:
    with pytest.raises(ValueError, match=rf"Nie można utworzyć {vo_cls.__name__}"):
        vo_cls.from_dict(payload)
