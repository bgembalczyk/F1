from collections.abc import Callable
from typing import Any

from scrapers.drivers.infobox.parsers.car_numbers import CarNumbersParser
from scrapers.drivers.infobox.parsers.cell import InfoboxCellParser
from scrapers.drivers.infobox.parsers.numeric import NumericParser

_ACTIVE_YEARS_LABELS = {"Active years", "Years active", "Years"}
_TEAM_LABELS = {"Teams", "Former teams"}
_INT_CELL_LABELS = {
    "Wins",
    "Podiums",
    "Pole positions",
    "Poles",
    "Fastest laps",
    "Starts",
}
_RACE_EVENT_LABELS = {
    "First race",
    "Last race",
    "First win",
    "Last win",
    "First entry",
    "Last entry",
}


def _parser_mappings(
    cell_parser: InfoboxCellParser,
) -> tuple[tuple[set[str], Callable[[Any], Any]], ...]:
    return (
        (_ACTIVE_YEARS_LABELS, cell_parser.parse_active_years),
        ({"Car number"}, CarNumbersParser.parse_car_numbers),
        (_TEAM_LABELS, cell_parser.parse_teams),
        ({"Entries"}, NumericParser.parse_entries),
        ({"Championships"}, cell_parser.parse_championships),
        ({"Class wins"}, cell_parser.parse_class_wins),
        (_INT_CELL_LABELS, NumericParser.parse_int_cell),
        ({"Career points"}, NumericParser.parse_float_cell),
        ({"Best finish"}, cell_parser.parse_best_finish),
        (_RACE_EVENT_LABELS, cell_parser.parse_race_event),
        ({"Finished last season"}, cell_parser.parse_finished_last_season),
        ({"Racing licence"}, cell_parser.parse_racing_licence),
        ({"Nationality"}, cell_parser.parse_nationality),
    )


def _match_label_parser(
    *,
    label: str | None,
    cell_parser: InfoboxCellParser,
) -> Callable[[Any], Any] | None:
    for labels, parser in _parser_mappings(cell_parser):
        if label in labels:
            return parser
    return None


def parser_for_label(
    *,
    label: str | None,
    cell_parser: InfoboxCellParser,
) -> Callable[[Any], Any]:
    parser = _match_label_parser(label=label, cell_parser=cell_parser)
    if parser is not None:
        return parser
    return cell_parser.parse_cell
