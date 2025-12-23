from dataclasses import dataclass

from scrapers.base.normalization import RecordNormalizer


def test_record_normalizer_normalizes_keys_and_drops_empty_fields() -> None:
    normalizer = RecordNormalizer(normalize_keys=True)
    data = [
        {"Driver Name": "Max", "Wins": 54, "Notes": ""},
        {"driver name": "Lewis", "wins": 103, "Notes": None},
    ]

    normalized = normalizer.normalize(data)

    assert normalized == [
        {"driver_name": "Max", "wins": 54},
        {"driver_name": "Lewis", "wins": 103},
    ]


def test_record_normalizer_applies_custom_rules_after_default() -> None:
    def rename_wins(record: dict) -> dict:
        if "wins" not in record:
            return record
        value = record.pop("wins")
        record["total_wins"] = value
        return record

    normalizer = RecordNormalizer(
        normalize_keys=True, normalization_rules=[rename_wins]
    )
    data = [{"Wins": 41, "Notes": ""}]

    normalized = normalizer.normalize(data)

    assert normalized == [{"total_wins": 41}]


def test_record_normalizer_passes_through_non_dict_items() -> None:
    @dataclass(frozen=True)
    class Driver:
        name: str

    driver = Driver(name="Max")
    normalizer = RecordNormalizer(normalize_keys=True)
    data = [{"Driver Name": "Max"}, driver]

    normalized = normalizer.normalize(data)

    assert normalized[0] == {"driver_name": "Max"}
    assert normalized[1] is driver
