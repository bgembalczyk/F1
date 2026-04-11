from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from scrapers.parsers.infobox.constants import ACTIVE_YEARS_LABELS
from scrapers.parsers.infobox.constants import INT_CELL_LABELS
from scrapers.parsers.infobox.constants import RACE_EVENT_LABELS
from scrapers.parsers.infobox.constants import TEAM_LABELS
from scrapers.parsers.infobox.drivers.car_numbers import CarNumbersParser
from scrapers.parsers.infobox.drivers.cell import InfoboxCellParser
from scrapers.parsers.infobox.field_parser import CallableInfoboxFieldParser
from scrapers.parsers.infobox.field_parser import InfoboxFieldParser
from scrapers.parsers.infobox.numeric import NumericParser


class InfoboxFieldParsersRegistry:
    def __init__(
        self,
        *,
        default_parser: InfoboxFieldParser[Any, Any],
    ) -> None:
        self._default_parser = default_parser
        self._parsers_by_label: dict[str, InfoboxFieldParser[Any, Any]] = {}

    def register(
        self,
        *,
        labels: Iterable[str],
        parser: InfoboxFieldParser[Any, Any],
    ) -> None:
        for label in labels:
            self._parsers_by_label[label] = parser

    def parser_for_label(self, label: str | None) -> InfoboxFieldParser[Any, Any]:
        if label is None:
            return self._default_parser
        return self._parsers_by_label.get(label, self._default_parser)


def field_parsers_registry(
    cell_parser: InfoboxCellParser,
) -> InfoboxFieldParsersRegistry:
    registry = InfoboxFieldParsersRegistry(default_parser=cell_parser)
    championships_parser = cell_parser.championships_field_parser

    registry.register(
        labels=ACTIVE_YEARS_LABELS,
        parser=cell_parser.active_years_field_parser,
    )
    registry.register(labels={"Car number"}, parser=CarNumbersParser())
    registry.register(labels=TEAM_LABELS, parser=cell_parser.teams_field_parser)
    registry.register(
        labels={"Entries"},
        parser=CallableInfoboxFieldParser(NumericParser.parse_entries),
    )
    registry.register(labels={"Championships"}, parser=championships_parser)
    registry.register(
        labels={"Class wins"},
        parser=CallableInfoboxFieldParser(championships_parser.parse_class_wins),
    )
    registry.register(
        labels=INT_CELL_LABELS,
        parser=CallableInfoboxFieldParser(NumericParser.parse_int_cell),
    )
    registry.register(
        labels={"Career points"},
        parser=CallableInfoboxFieldParser(NumericParser.parse_float_cell),
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
    cell_parser: InfoboxCellParser,
) -> InfoboxFieldParser[Any, Any]:
    return field_parsers_registry(cell_parser).parser_for_label(label)


__all__ = [
    "InfoboxFieldParsersRegistry",
    "field_parsers_registry",
    "parser_for_label",
]
