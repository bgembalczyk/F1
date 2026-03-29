from scrapers.base.infobox.dsl import InfoboxSchemaDSL
from scrapers.base.table.columns.types import SeasonsColumn
from scrapers.base.table.columns.types.parsed_value import ParsedValueColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.dsl.table_schema import TableSchemaDSL


def test_table_schema_dsl_reads_schema_and_maps_columns() -> None:
    data = {
        "columns": [
            {
                "header": "Season",
                "key": "season",
                "column": {
                    "class_path": ("scrapers.seasons.columns.seasons.SeasonsColumn"),
                    "kwargs": {},
                },
            },
            {
                "header": "Races",
                "key": "races",
                "column": {
                    "class_path": "scrapers.base.table.columns.types.int.IntColumn",
                    "kwargs": {},
                },
            },
        ],
    }

    schema = TableSchemaDSL.from_dict(data).build()

    assert schema.column_map == {"Season": "season", "Races": "races"}
    assert isinstance(schema.columns["season"], SeasonsColumn)
    assert isinstance(schema.columns["races"], ParsedValueColumn)


def test_table_schema_dsl_handles_header_specific_columns() -> None:
    data = {
        "columns": [
            {
                "header": "Foo",
                "key": "shared",
                "column": {
                    "class_path": "scrapers.base.table.columns.types.int.IntColumn",
                    "kwargs": {},
                },
            },
            {
                "header": "Bar",
                "key": "shared",
                "column": {
                    "class_path": "scrapers.base.table.columns.types.text.TextColumn",
                    "kwargs": {},
                },
            },
        ],
    }

    schema = TableSchemaDSL.from_dict(data).build()

    assert schema.column_map["Foo"] == "shared"
    assert schema.column_map["Bar"] == "shared"
    assert "shared" not in schema.columns
    assert isinstance(schema.columns["Foo"], ParsedValueColumn)
    assert isinstance(schema.columns["Bar"], TextColumn)


def test_infobox_schema_dsl_reads_schema() -> None:
    data = {
        "name": "driver.general",
        "fields": [
            {
                "key": "born",
                "labels": ["Born"],
                "parser": "date_place",
            },
        ],
    }

    schema = InfoboxSchemaDSL.from_dict(data).build()

    field = schema.field_for_label("Born")
    assert field is not None
    assert field.key == "born"
