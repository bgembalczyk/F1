from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from scrapers.infobox.field.parsers_registry import InfoboxFieldRegistry
from scrapers.parsers.infobox.constants import ACTIVE_YEARS_LABELS
from scrapers.parsers.infobox.constants import INT_CELL_LABELS
from scrapers.parsers.infobox.constants import RACE_EVENT_LABELS
from scrapers.parsers.infobox.constants import TEAM_LABELS
from scrapers.parsers.infobox.driver_cell import InfoboxCellValueExtractor
from scrapers.parsers.infobox.field.callable import CallableInfoboxFieldParser
from scrapers.parsers.infobox.field.car_numbers import CarNumbersParser
from scrapers.parsers.infobox.field.protocol import InfoboxFieldParser
from scrapers.parsers.numeric_extractor import NumericExtractor


def field_parsers_registry(
    cell_parser: InfoboxCellValueExtractor,
) -> InfoboxFieldRegistry:
    registry = InfoboxFieldRegistry(default_parser=cell_parser)
    championships_parser = cell_parser.championships_field_parser

    registry.register(
        labels=ACTIVE_YEARS_LABELS,
        parser=cell_parser.active_years_field_parser,
    )
    registry.register(labels={"Car number"}, parser=CarNumbersParser())
    registry.register(labels=TEAM_LABELS, parser=cell_parser.teams_field_parser)
    registry.register(
        labels={"Entries"},
        parser=CallableInfoboxFieldParser(NumericExtractor.parse_entries),
    )
    registry.register(labels={"Championships"}, parser=championships_parser)
    registry.register(
        labels={"Class wins"},
        parser=CallableInfoboxFieldParser(championships_parser.parse_class_wins),
    )
    registry.register(
        labels=INT_CELL_LABELS,
        parser=CallableInfoboxFieldParser(NumericExtractor.parse_int_cell),
    )
    registry.register(
        labels={"Career points"},
        parser=CallableInfoboxFieldParser(NumericExtractor.parse_float_cell),
    )
    registry.register(
        labels={"Best finish"},
        parser=cell_parser.best_finish_field_parser,
    )
    registry.register(
        labels=RACE_EVENT_LABELS,
        parser=cell_parser.race_event_field_parser,
    )
    registry.register(
        labels={"Finished last season"},
        parser=cell_parser.finished_last_season_field_parser,
    )
    registry.register(
        labels={"Racing licence"},
        parser=cell_parser.racing_licence_field_parser,
    )
    registry.register(
        labels={"Nationality"},
        parser=cell_parser.nationality_field_parser,
    )
    return registry


def parser_for_label(
    *,
    label: str | None,
    cell_parser: InfoboxCellValueExtractor,
) -> InfoboxFieldParser[Any]:
    return field_parsers_registry(cell_parser).parser_for_label(label)


__all__ = [
    "field_parsers_registry",
    "parser_for_label",
]
