from scrapers.wiki.parsers.elements.wiki_table_mapped_parser import MappedWikiTableParser


class LapRecordsWikiTableParser(MappedWikiTableParser):
    table_type = "lap_records"
    missing_columns_policy = "require_time_and_driver"
    extra_columns_policy = "ignore"

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
