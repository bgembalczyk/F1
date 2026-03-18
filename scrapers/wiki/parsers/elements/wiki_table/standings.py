from scrapers.wiki.parsers.elements.wiki_table.mapped import MappedWikiTableParser


class StandingsTableParser(MappedWikiTableParser):
    table_type = "standings"
    missing_columns_policy = "fail_if_missing_subject_or_points"
    extra_columns_policy = "collect_as_round_columns"

    required_header_groups = (
        frozenset({"Pos", "Pos."}),
        frozenset({"Points", "Pts", "Pts."}),
        frozenset({"Driver", "Constructor"}),
    )
    column_mapping = {
        "Pos.": "pos",
        "Pos": "pos",
        "Driver": "driver",
        "Constructor": "constructor",
        "Points": "points",
        "Pts": "points",
        "Pts.": "points",
        "No.": "no",
        "No": "no",
        "Car no.": "no",
    }
