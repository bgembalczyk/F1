from models.value_objects.enums import ExtraColumnsPolicy
from models.value_objects.enums import MissingColumnsPolicy
from models.value_objects.enums import TableType
from scrapers.wiki.parsers.elements.wiki_table.mapped import MappedWikiTableParser


class LapRecordsWikiTableParser(MappedWikiTableParser):
    table_type = TableType.LAP_RECORDS
    missing_columns_policy = MissingColumnsPolicy.REQUIRE_TIME_AND_DRIVER
    extra_columns_policy = ExtraColumnsPolicy.IGNORE

    required_header_groups = (
        frozenset({"Time"}),
        frozenset({"Driver", "Driver/Rider"}),
    )
    column_mapping = {
        "Time": "time",
        "Driver": "driver",
        "Driver/Rider": "driver",
        "Vehicle": "vehicle",
        "Car": "vehicle",
        "Year": "year",
        "Series": "series",
    }
