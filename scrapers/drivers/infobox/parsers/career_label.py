from collections.abc import Callable
from typing import Any

from scrapers.drivers.infobox.parsers.cell import InfoboxCellParser


def parser_for_label(
    *,
    label: str | None,
    cell_parser: InfoboxCellParser,
) -> Callable[[Any], Any]:
    if label in {"Active years", "Years active", "Years"}:
        return cell_parser.parse_active_years
    if label == "Car number":
        return cell_parser.parse_car_numbers
    if label in {"Teams", "Former teams"}:
        return cell_parser.parse_teams
    if label == "Entries":
        return cell_parser.parse_entries
    if label == "Championships":
        return cell_parser.parse_championships
    if label == "Class wins":
        return cell_parser.parse_class_wins
    if label in {
        "Wins",
        "Podiums",
        "Pole positions",
        "Poles",
        "Fastest laps",
        "Starts",
    }:
        return cell_parser.parse_int_cell
    if label == "Career points":
        return cell_parser.parse_float_cell
    if label == "Best finish":
        return cell_parser.parse_best_finish
    if label in {
        "First race",
        "Last race",
        "First win",
        "Last win",
        "First entry",
        "Last entry",
    }:
        return cell_parser.parse_race_event
    if label == "Finished last season":
        return cell_parser.parse_finished_last_season
    if label == "Racing licence":
        return cell_parser.parse_racing_licence
    if label == "Nationality":
        return cell_parser.parse_nationality
    return cell_parser.parse_cell
