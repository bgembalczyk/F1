# ruff: noqa: E501, PLR2004
import pytest

from scrapers.grands_prix.mappers.by_year_record import GrandPrixByYearRecordInput
from scrapers.grands_prix.mappers.by_year_record import GrandPrixByYearRecordMapper


@pytest.fixture()
def mapper() -> GrandPrixByYearRecordMapper:
    return GrandPrixByYearRecordMapper()


def link(text: str) -> dict:
    return {"text": text, "url": None}


def not_held_record() -> dict:
    return {
        "driver": [link("Not held")],
        "chassis_constructor": link("Not held"),
        "engine_constructor": link("Not held"),
        "location": {"circuit": link("Not held"), "layout": None},
    }


def test_map_returns_none_for_not_held_by_driver_text(
    mapper: GrandPrixByYearRecordMapper,
) -> None:
    record = not_held_record()
    result = mapper.map(record)
    assert result is None


def test_map_returns_dict_for_normal_record(
    mapper: GrandPrixByYearRecordMapper,
) -> None:
    record = {
        "driver": [link("Lewis Hamilton")],
        "chassis_constructor": link("Mercedes"),
        "engine_constructor": link("Mercedes"),
        "location": {"circuit": link("Silverstone"), "layout": None},
    }
    result = mapper.map(record)
    assert result is not None
    assert isinstance(result, dict)


def test_map_accepts_input_wrapper(mapper: GrandPrixByYearRecordMapper) -> None:
    record = {"key": "value"}
    result = mapper.map(GrandPrixByYearRecordInput(record=record))
    assert result == {"key": "value"}


def test_is_not_held_returns_false_when_texts_differ(
    mapper: GrandPrixByYearRecordMapper,
) -> None:
    record = {
        "driver": [link("Not held")],
        "chassis_constructor": link("Not held"),
        "engine_constructor": link("SomethingElse"),
        "location": {"circuit": link("Not held"), "layout": None},
    }
    result = mapper.map(record)
    assert result is not None


def test_is_not_held_returns_false_when_missing_fields(
    mapper: GrandPrixByYearRecordMapper,
) -> None:
    result = mapper.map({"driver": [link("Not held")]})
    assert result is not None


def test_not_held_detected_via_report_text(mapper: GrandPrixByYearRecordMapper) -> None:
    record = not_held_record()
    record["driver"] = [link("ABC")]
    record["chassis_constructor"] = link("ABC")
    record["engine_constructor"] = link("ABC")
    record["location"]["circuit"] = link("ABC")
    record["report"] = "Not held due to war"
    result = mapper.map(record)
    assert result is None


def test_not_held_detected_via_layout_cancelled(
    mapper: GrandPrixByYearRecordMapper,
) -> None:
    record = not_held_record()
    record["driver"] = [link("XYZ")]
    record["chassis_constructor"] = link("XYZ")
    record["engine_constructor"] = link("XYZ")
    record["location"]["circuit"] = link("XYZ")
    record["location"]["layout"] = "Cancelled due to war"
    result = mapper.map(record)
    assert result is None


def test_list_text_returns_none_for_empty_list(
    mapper: GrandPrixByYearRecordMapper,
) -> None:
    assert mapper._list_text([]) is None


def test_list_text_returns_none_for_mismatched_items(
    mapper: GrandPrixByYearRecordMapper,
) -> None:
    assert mapper._list_text([link("A"), link("B")]) is None


def test_list_text_returns_text_for_all_same(
    mapper: GrandPrixByYearRecordMapper,
) -> None:
    assert mapper._list_text([link("Same"), link("Same")]) == "Same"
