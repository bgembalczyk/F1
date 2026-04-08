from collections.abc import Callable
from typing import Any

from scrapers.drivers.infobox.parsers.car_numbers import CarNumbersParser
from scrapers.drivers.infobox.parsers.cell import InfoboxCellParser
from scrapers.drivers.infobox.parsers.constants import ACTIVE_YEARS_LABELS
from scrapers.drivers.infobox.parsers.constants import INT_CELL_LABELS
from scrapers.drivers.infobox.parsers.constants import RACE_EVENT_LABELS
from scrapers.drivers.infobox.parsers.constants import TEAM_LABELS
from scrapers.drivers.infobox.parsers.numeric import NumericParser


def parser_mappings(
    cell_parser: InfoboxCellParser,
) -> tuple[tuple[set[str], Callable[[Any], Any]], ...]:
    return (
        (ACTIVE_YEARS_LABELS, cell_parser.parse_active_years),
        ({"Car number"}, CarNumbersParser.parse_car_numbers),
        (TEAM_LABELS, cell_parser.parse_teams),
        ({"Entries"}, NumericParser.parse_entries),
        ({"Championships"}, cell_parser.parse_championships),
        ({"Class wins"}, cell_parser.parse_class_wins),
        (INT_CELL_LABELS, NumericParser.parse_int_cell),
        ({"Career points"}, NumericParser.parse_float_cell),
        ({"Best finish"}, cell_parser.parse_best_finish),
        (RACE_EVENT_LABELS, cell_parser.parse_race_event),
        ({"Finished last season"}, cell_parser.parse_finished_last_season),
        ({"Racing licence"}, cell_parser.parse_racing_licence),
        ({"Nationality"}, cell_parser.parse_nationality),
    )


def match_label_parser(
    *,
    label: str | None,
    cell_parser: InfoboxCellParser,
) -> Callable[[Any], Any] | None:
    for labels, parser in parser_mappings(cell_parser):
        if label in labels:
            return parser
    return None


def parser_for_label(
    *,
    label: str | None,
    cell_parser: InfoboxCellParser,
) -> Callable[[Any], Any]:
    parser = match_label_parser(label=label, cell_parser=cell_parser)
    if parser is not None:
        return parser
    return cell_parser.parse_cell


__all__ = [
    "parser_mappings",
    "parser_for_label",
    "match_label_parser",
]
