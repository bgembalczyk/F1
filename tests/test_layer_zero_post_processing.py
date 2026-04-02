import logging

from layers.zero.merge import _post_process_domain_records


def test_post_process_logs_step_input_output_and_changes(caplog) -> None:
    records = [
        {"driver": {"text": "Lewis Hamilton", "url": "https://example.com/lewis"}},
        {"driver": {"text": "Max Verstappen", "url": "https://example.com/max"}},
    ]

    with caplog.at_level(logging.DEBUG):
        processed = _post_process_domain_records("drivers", records)

    assert processed[0]["driver"]["text"] == "Lewis Hamilton"
    assert "Post-process step 'merge_duplicates' domain=drivers input_records=2" in caplog.text
    assert "Post-process step 'sort_records' domain=drivers output_records=2" in caplog.text
    assert "changes=" in caplog.text


def test_post_process_can_run_single_diagnostic_step() -> None:
    records = [
        {"driver": {"text": "Max Verstappen", "url": "https://example.com/max"}},
        {"driver": {"text": "Lewis Hamilton", "url": "https://example.com/lewis"}},
        {"driver": {"text": "Lewis Hamilton", "url": "https://example.com/lewis"}},
    ]

    processed = _post_process_domain_records(
        "drivers",
        records,
        diagnostic_step="sort_records",
    )

    assert [record["driver"]["text"] for record in processed] == [
        "Lewis Hamilton",
        "Lewis Hamilton",
        "Max Verstappen",
    ]
