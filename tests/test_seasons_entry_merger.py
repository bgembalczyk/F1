# ruff: noqa: SLF001
from scrapers.seasons.parsers.entry_merger import EntryMerger

EXPECTED_TWO_ITEMS = 2
LEWIS_NUMBER = 44
BOTTAS_NUMBER = 77
THIRD_ITEM_INDEX = 2


def test_merge_entries_full_match_combines_drivers_into_single_domain_entry() -> None:
    merger = EntryMerger()
    records = [
        {
            "constructor": {"text": "Team A"},
            "chassis": "A01",
            "engine": "E1",
            "driver": {"text": "Driver 1"},
            "rounds": "1-2",
        },
        {
            "constructor": {"text": "Team A"},
            "chassis": "A01",
            "engine": "E1",
            "driver": {"text": "Driver 2"},
            "rounds": "3",
        },
    ]

    merged = merger.merge_entries(records)

    assert len(merged) == 1
    assert merged[0]["constructor"]["text"] == "Team A"
    assert merged[0]["race_drivers"] == [
        {"driver": {"text": "Driver 1"}, "rounds": [1, 2]},
        {"driver": {"text": "Driver 2"}, "rounds": [3]},
    ]


def test_merge_entries_partial_match_keeps_separate_subgroups_for_conflicting_values():
    merger = EntryMerger()
    records = [
        {
            "constructor": {"text": "Team A"},
            "chassis": "A01",
            "engine": "E1",
            "driver": "Driver 1",
        },
        {
            "constructor": {"text": "Team A"},
            "chassis": "A01",
            "engine": "E2",
            "driver": "Driver 2",
        },
    ]

    merged = merger.merge_entries(records)

    assert len(merged) == 1
    assert merged[0]["engine"] == [
        {"engine": "E1", "race_drivers": [{"driver": "Driver 1"}]},
        {"engine": "E2", "race_drivers": [{"driver": "Driver 2"}]},
    ]


def test_merge_entries_collisions_are_deduplicated_to_single_group() -> None:
    merger = EntryMerger()
    records = [
        {
            "constructor": {"text": "Team A"},
            "driver": "Driver 1",
        },
        {
            "constructor": {"text": "Team A"},
            "driver": "Driver 2",
        },
    ]

    merged = merger.merge_entries(records)

    assert merged == [
        {
            "constructor": {"text": "Team A"},
            "race_drivers": [{"driver": "Driver 1"}, {"driver": "Driver 2"}],
        },
    ]


def test_merge_entries_returns_empty_input_unchanged() -> None:
    merger = EntryMerger()

    assert merger.merge_entries([]) == []


# ---------------------------------------------------------------------------
# merge_entries - no group keys case
# ---------------------------------------------------------------------------


def test_merge_entries_with_only_driver_fields_returns_single_merged_record() -> None:
    merger = EntryMerger()
    records = [
        {"driver": {"text": "Driver 1"}, "rounds": "1"},
        {"driver": {"text": "Driver 2"}, "rounds": "2"},
    ]
    merged = merger.merge_entries(records)
    assert len(merged) == 1
    assert "race_drivers" in merged[0]
    assert len(merged[0]["race_drivers"]) == EXPECTED_TWO_ITEMS


def test_merge_entries_with_only_driver_fields_empty_drivers_returns_empty_merged() -> (
    None
):
    merger = EntryMerger()
    # Records with only driver fields but driver value is None
    records = [{"rounds": "1"}]
    merged = merger.merge_entries(records)
    assert len(merged) == 1
    # merged should be empty dict or have no race_drivers
    assert merged[0] == {}


# ---------------------------------------------------------------------------
# _merge_entry_groups - constructor special case
# ---------------------------------------------------------------------------


def test_merge_entries_constructor_dict_values_are_inlined() -> None:
    merger = EntryMerger()
    # When there are multiple constructors within same team group,
    # constructor dict values should be inlined
    records = [
        {
            "team": "T1",
            "constructor": {"text": "Team A", "url": "http://a.com"},
            "driver": "D1",
        },
        {
            "team": "T1",
            "constructor": {"text": "Team B", "url": "http://b.com"},
            "driver": "D2",
        },
    ]
    merged = merger.merge_entries(records)
    assert len(merged) == 1
    # Constructor items in the subgroup should have inlined dict keys
    constructors = merged[0]["constructor"]
    assert isinstance(constructors, list)
    assert len(constructors) == EXPECTED_TWO_ITEMS
    # Each item should have "text" inlined from the dict
    assert all("text" in c for c in constructors)


# ---------------------------------------------------------------------------
# _entry_merge_key
# ---------------------------------------------------------------------------


def test_entry_merge_key_excludes_driver_fields() -> None:
    record = {"constructor": "A", "driver": "D", "chassis": "C01"}
    key = EntryMerger._entry_merge_key(record)
    # Should include constructor and chassis but not driver
    key_dict = dict(key)
    assert "constructor" in key_dict
    assert "chassis" in key_dict
    assert "driver" not in key_dict


# ---------------------------------------------------------------------------
# _strip_entry_driver_fields
# ---------------------------------------------------------------------------


def test_strip_entry_driver_fields_removes_driver_fields() -> None:
    record = {
        "constructor": "A",
        "race_drivers": [{"driver": "D"}],
        "driver": "D",
        "drivers": ["D"],
        "rounds": [1],
        "races": [1],
        "no": LEWIS_NUMBER,
    }
    cleaned = EntryMerger._strip_entry_driver_fields(record)
    assert "constructor" in cleaned
    assert "driver" not in cleaned
    assert "race_drivers" not in cleaned
    assert "rounds" not in cleaned


# ---------------------------------------------------------------------------
# _extract_race_driver_records
# ---------------------------------------------------------------------------


def test_extract_race_driver_records_handles_indexed_rounds() -> None:
    merger = EntryMerger()
    record = {
        "race_drivers": [{"driver": "D1"}, {"driver": "D2"}],
        "rounds": [[1, 2], [3, 4]],
    }
    result = merger._extract_race_driver_records(record)
    assert len(result) == EXPECTED_TWO_ITEMS
    assert result[0].get("rounds") == [1, 2]
    assert result[1].get("rounds") == [3, 4]


def test_extract_race_driver_records_returns_empty_for_non_list() -> None:
    merger = EntryMerger()
    result = merger._extract_race_driver_records({"race_drivers": "not a list"})
    assert result == []


def test_extract_race_driver_records_adds_number_per_driver() -> None:
    merger = EntryMerger()
    record = {
        "race_drivers": [{"driver": "D1"}, {"driver": "D2"}],
        "no": [LEWIS_NUMBER, BOTTAS_NUMBER],
    }
    result = merger._extract_race_driver_records(record)
    assert result[0].get("no") == LEWIS_NUMBER
    assert result[1].get("no") == BOTTAS_NUMBER


def test_extract_race_driver_records_adds_single_number_for_single_driver() -> None:
    merger = EntryMerger()
    record = {
        "race_drivers": [{"driver": "D1"}],
        "no": LEWIS_NUMBER,
    }
    result = merger._extract_race_driver_records(record)
    assert result[0].get("no") == LEWIS_NUMBER


# ---------------------------------------------------------------------------
# _extract_fallback_driver_records
# ---------------------------------------------------------------------------


def test_extract_fallback_driver_records_uses_drivers_key() -> None:
    merger = EntryMerger()
    record = {
        "drivers": [{"text": "D1"}, {"text": "D2"}],
        "rounds": "1-3",
    }
    result = merger._extract_fallback_driver_records(record)
    assert len(result) == EXPECTED_TWO_ITEMS


def test_extract_fallback_driver_records_returns_empty_when_no_driver() -> None:
    merger = EntryMerger()
    result = merger._extract_fallback_driver_records({"constructor": "A"})
    assert result == []


def test_extract_fallback_driver_records_with_indexed_rounds() -> None:
    merger = EntryMerger()
    record = {
        "driver": [{"text": "D1"}, {"text": "D2"}],
        "rounds": [[1, 2], [3, 4]],
    }
    result = merger._extract_fallback_driver_records(record)
    assert len(result) == EXPECTED_TWO_ITEMS
    assert result[0].get("rounds") == [1, 2]


def test_extract_fallback_driver_records_with_indexed_numbers() -> None:
    merger = EntryMerger()
    record = {
        "driver": [{"text": "D1"}, {"text": "D2"}],
        "no": [LEWIS_NUMBER, BOTTAS_NUMBER],
    }
    result = merger._extract_fallback_driver_records(record)
    assert result[0].get("no") == LEWIS_NUMBER
    assert result[1].get("no") == BOTTAS_NUMBER


# ---------------------------------------------------------------------------
# _rounds_by_index
# ---------------------------------------------------------------------------


def test_rounds_by_index_returns_value_when_size_matches() -> None:
    result = EntryMerger._rounds_by_index([[1, 2], [3, 4]], 2)
    assert result == [[1, 2], [3, 4]]


def test_rounds_by_index_returns_none_when_size_mismatch() -> None:
    result = EntryMerger._rounds_by_index([[1], [2], [3]], EXPECTED_TWO_ITEMS)
    assert result is None


def test_rounds_by_index_returns_none_for_non_list() -> None:
    result = EntryMerger._rounds_by_index("1-5", THIRD_ITEM_INDEX)
    assert result is None


# ---------------------------------------------------------------------------
# _add_number
# ---------------------------------------------------------------------------


def test_add_number_sets_from_index_when_numbers_by_index() -> None:
    merger = EntryMerger()
    entry: dict = {}
    merger._add_number(
        entry,
        [LEWIS_NUMBER, BOTTAS_NUMBER],
        [LEWIS_NUMBER, BOTTAS_NUMBER],
        1,
        EXPECTED_TWO_ITEMS,
    )
    assert entry["no"] == BOTTAS_NUMBER


def test_add_number_sets_single_number_for_single_driver() -> None:
    merger = EntryMerger()
    drivers = merger._build_drivers_with_shared_rounds(
        [{"text": "D1"}],
        [1],
        [LEWIS_NUMBER],
        [],
    )
    assert drivers[0]["no"] == LEWIS_NUMBER


def test_add_number_does_nothing_for_multiple_drivers_no_index() -> None:
    merger = EntryMerger()
    entry: dict = {}
    merger._add_number(entry, [LEWIS_NUMBER, BOTTAS_NUMBER], [], 0, EXPECTED_TWO_ITEMS)
    assert "no" not in entry


# ---------------------------------------------------------------------------
# _add_rounds
# ---------------------------------------------------------------------------


def test_add_rounds_uses_indexed_rounds_when_available() -> None:
    merger = EntryMerger()
    entry: dict = {}
    merger._add_rounds(entry, [[1, 2], [3, 4]], [], 1)
    assert entry.get("rounds") == [3, 4]


def test_add_rounds_uses_all_rounds_when_no_index() -> None:
    merger = EntryMerger()
    entry: dict = {}
    merger._add_rounds(entry, None, [1, 2, 3], 0)
    assert entry["rounds"] == [1, 2, 3]


def test_add_rounds_skips_empty_indexed_rounds() -> None:
    merger = EntryMerger()
    entry: dict = {}
    merger._add_rounds(entry, [[], []], [], 0)
    assert "rounds" not in entry


# ---------------------------------------------------------------------------
# _build_drivers_with_indexed_rounds
# ---------------------------------------------------------------------------


def test_build_drivers_with_indexed_rounds_assigns_rounds_per_driver() -> None:
    merger = EntryMerger()
    drivers = merger._build_drivers_with_indexed_rounds(
        [{"text": "D1"}, {"text": "D2"}],
        [[1, 2], [3, 4]],
        [LEWIS_NUMBER, BOTTAS_NUMBER],
    )
    assert len(drivers) == EXPECTED_TWO_ITEMS
    assert drivers[0]["rounds"] == [1, 2]
    assert drivers[0]["no"] == LEWIS_NUMBER
    assert drivers[1]["rounds"] == [3, 4]


def test_build_drivers_with_indexed_rounds_skips_empty_rounds() -> None:
    merger = EntryMerger()
    drivers = merger._build_drivers_with_indexed_rounds(
        [{"text": "D1"}],
        [[]],
        [],
    )
    assert len(drivers) == 1
    assert "rounds" not in drivers[0]


# ---------------------------------------------------------------------------
# _build_drivers_with_shared_rounds
# ---------------------------------------------------------------------------


def test_build_drivers_with_shared_rounds_adds_number_by_index() -> None:
    merger = EntryMerger()
    drivers = merger._build_drivers_with_shared_rounds(
        [{"text": "D1"}, {"text": "D2"}],
        [1, 2],
        [LEWIS_NUMBER, BOTTAS_NUMBER],
        [LEWIS_NUMBER, BOTTAS_NUMBER],
    )
    assert drivers[0]["no"] == LEWIS_NUMBER
    assert drivers[1]["no"] == BOTTAS_NUMBER


def test_build_drivers_with_shared_rounds_adds_single_number_for_single_driver() -> (
    None
):
    merger = EntryMerger()
    drivers = merger._build_drivers_with_shared_rounds(
        [{"text": "D1"}],
        [1],
        [LEWIS_NUMBER],
        [],
    )
    assert drivers[0]["no"] == LEWIS_NUMBER


# ---------------------------------------------------------------------------
# _normalize_entry_numbers
# ---------------------------------------------------------------------------


def test_normalize_entry_numbers_handles_list_of_ints() -> None:
    result = EntryMerger._normalize_entry_numbers([LEWIS_NUMBER, BOTTAS_NUMBER])
    assert result == [LEWIS_NUMBER, BOTTAS_NUMBER]


def test_normalize_entry_numbers_handles_list_with_string_ints() -> None:
    result = EntryMerger._normalize_entry_numbers(
        [str(LEWIS_NUMBER), str(BOTTAS_NUMBER)],
    )
    assert result == [LEWIS_NUMBER, BOTTAS_NUMBER]


def test_normalize_entry_numbers_handles_list_with_unparseable_strings() -> None:
    result = EntryMerger._normalize_entry_numbers(["N/A", LEWIS_NUMBER])
    assert result == [LEWIS_NUMBER]


def test_normalize_entry_numbers_handles_none() -> None:
    assert EntryMerger._normalize_entry_numbers(None) == []


def test_normalize_entry_numbers_handles_single_int() -> None:
    assert EntryMerger._normalize_entry_numbers(LEWIS_NUMBER) == [LEWIS_NUMBER]


def test_normalize_entry_numbers_handles_single_string() -> None:
    assert EntryMerger._normalize_entry_numbers(str(LEWIS_NUMBER)) == [LEWIS_NUMBER]


def test_normalize_entry_numbers_handles_unparseable_string() -> None:
    assert EntryMerger._normalize_entry_numbers("N/A") == []


def test_normalize_entry_numbers_handles_unknown_type() -> None:
    assert EntryMerger._normalize_entry_numbers(object()) == []


# ---------------------------------------------------------------------------
# _normalize_rounds
# ---------------------------------------------------------------------------


def test_normalize_rounds_handles_list_of_ints() -> None:
    result = EntryMerger._normalize_rounds([1, 2, 3])
    assert result == [1, 2, 3]


def test_normalize_rounds_handles_single_int() -> None:
    result = EntryMerger._normalize_rounds(5)
    assert result == [5]


def test_normalize_rounds_handles_string() -> None:
    result = EntryMerger._normalize_rounds("1-3")
    assert result == [1, 2, 3]


def test_normalize_rounds_handles_none() -> None:
    assert EntryMerger._normalize_rounds(None) == []


def test_normalize_rounds_handles_unknown_type() -> None:
    assert EntryMerger._normalize_rounds(object()) == []


def test_merge_entry_groups_returns_empty_merged_when_no_drivers_and_no_keys() -> None:
    merger = EntryMerger()
    # Records with no driver fields -> empty merged
    records = [{"no_driver_field": "x"}]
    result = merger._merge_entry_groups(records, [])
    assert result == {}


def test_normalize_entry_numbers_list_with_unparseable_str_is_skipped() -> None:
    result = EntryMerger._normalize_entry_numbers(["not_a_number", LEWIS_NUMBER])
    assert result == [LEWIS_NUMBER]


def test_normalize_entry_numbers_list_with_non_str_non_int_items_ignored() -> None:
    # Items that are neither int nor str should be skipped
    result = EntryMerger._normalize_entry_numbers([None, LEWIS_NUMBER, {"no": 5}])
    assert result == [LEWIS_NUMBER]
