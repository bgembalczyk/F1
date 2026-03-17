from scrapers.wiki.parsers.elements.wiki_table_mapped_parser import MappedWikiTableParser


class RaceResultsTableParser(MappedWikiTableParser):
    table_type = "race_results"
    missing_columns_policy = "require_round_and_winner"
    extra_columns_policy = "ignore"

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
