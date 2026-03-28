from scrapers.base.mappers import InfoboxRecordMapper
from scrapers.base.mappers import LayoutTableRecordMapper
from scrapers.base.mappers import SectionRecordMapper


def test_section_record_mapper_validates_and_trims_labels() -> None:
    mapper = SectionRecordMapper()
    payload = {
        "section_id": " Career_results ",
        "section_label": " Career results ",
        "records": [{"year": 2020}],
        "metadata": {"source": "table"},
    }

    mapped = mapper.map(payload)

    assert mapped["section_id"] == "Career_results"
    assert mapped["section_label"] == "Career results"
    assert mapped["records"] == [{"year": 2020}]
    assert mapped["metadata"] == {"source": "table"}


def test_infobox_record_mapper_normalizes_keys_recursively() -> None:
    mapper = InfoboxRecordMapper()

    mapped = mapper.map(
        {
            " Name ": "Driver",
            " stats ": {" Titles ": 2},
            "teams": [{" Name ": "Ferrari"}],
        },
    )

    assert mapped == {
        "Name": "Driver",
        "stats": {"Titles": 2},
        "teams": [{"Name": "Ferrari"}],
    }


def test_layout_table_record_mapper_groups_by_layout() -> None:
    mapper = LayoutTableRecordMapper()
    rows = [
        {"layout": "A", "driver": "X"},
        {"layout": "A", "driver": "Y"},
        {"layout": "B", "driver": "Z"},
        {"driver": "ignored"},
    ]

    mapped = mapper.map(rows)

    assert mapped == [
        {"layout": "A", "lap_records": [{"driver": "X"}, {"driver": "Y"}]},
        {"layout": "B", "lap_records": [{"driver": "Z"}]},
    ]
