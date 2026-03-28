from models.value_objects.enums import ExtraColumnsPolicy
from models.value_objects.enums import MissingColumnsPolicy
from models.value_objects.enums import TableType
from scrapers.base.table.headers_shared import POINTS_ALIASES
from scrapers.base.table.headers_shared import POINTS_HEADER
from scrapers.base.table.headers_shared import POINTS_HEADER_TO_KEY
from scrapers.wiki.parsers.elements.wiki_table.mapped import MappedWikiTableParser


class StandingsTableParser(MappedWikiTableParser):
    table_type = TableType.STANDINGS
    missing_columns_policy = MissingColumnsPolicy.FAIL_IF_MISSING_SUBJECT_OR_POINTS
    extra_columns_policy = ExtraColumnsPolicy.COLLECT_AS_ROUND_COLUMNS

    required_header_groups = (
        frozenset({"Pos", "Pos."}),
        frozenset({POINTS_HEADER, *POINTS_ALIASES}),
        frozenset({"Driver", "Constructor"}),
    )
    column_mapping = {
        "Pos.": "pos",
        "Pos": "pos",
        "Driver": "driver",
        "Constructor": "constructor",
        **POINTS_HEADER_TO_KEY,
        "No.": "no",
        "No": "no",
        "Car no.": "no",
    }
