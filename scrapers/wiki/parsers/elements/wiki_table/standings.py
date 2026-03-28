from scrapers.base.table.headers_shared import POINTS_ALIASES
from scrapers.base.table.headers_shared import POINTS_HEADER
from scrapers.base.table.headers_shared import POINTS_HEADER_TO_KEY
from scrapers.wiki.parsers.elements.wiki_table.mapped import MappedWikiTableParser


class StandingsTableParser(MappedWikiTableParser):
    table_type = "standings"
    missing_columns_policy = "fail_if_missing_subject_or_points"
    extra_columns_policy = "collect_as_round_columns"

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
