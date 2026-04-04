from scrapers.seasons.parsers.entry_merger import EntryMerger


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


def test_merge_entries_partial_match_keeps_separate_subgroups_for_conflicting_values() -> (
    None
):
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
