from models.value_objects.enums import ExtraColumnsPolicy
from models.value_objects.enums import MissingColumnsPolicy
from models.value_objects.enums import TableType
from scrapers.wiki.parsers.elements.wiki_table.mapped import MappedWikiTableParser


class RaceResultsTableParser(MappedWikiTableParser):
    table_type = TableType.RACE_RESULTS
    missing_columns_policy = MissingColumnsPolicy.REQUIRE_ROUND_AND_WINNER
    extra_columns_policy = ExtraColumnsPolicy.IGNORE

    required_header_groups = (
        frozenset({"Round"}),
        frozenset({"Winning driver"}),
    )
    column_mapping = {
        "Round": "round",
        "Grand Prix": "grand_prix",
        "Race": "grand_prix",
        "Pole position": "pole_position",
        "Pole Position": "pole_position",
        "Fastest lap": "fastest_lap",
        "Winning driver": "winning_driver",
        "Winning constructor": "winning_constructor",
        "Constructor": "winning_constructor",
        "Report": "report",
        "Tyre": "tyre",
    }
