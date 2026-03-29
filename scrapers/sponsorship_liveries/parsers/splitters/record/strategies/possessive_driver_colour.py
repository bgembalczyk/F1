from typing import Any

from scrapers.sponsorship_liveries.parsers.splitters.record.pipeline_record import (
    PipelineRecord,
)
from scrapers.sponsorship_liveries.helpers.constants import COLOUR_KEYS
from scrapers.sponsorship_liveries.parsers.scope_handlers.colour import (
    ColourScopeHandler,
)
from scrapers.sponsorship_liveries.parsers.splitters.record.protocols import SplitRule
from scrapers.sponsorship_liveries.parsers.splitters.record.rules import (
    HasPossessiveColoursRule,
)


class PossessiveDriverColourSplitStrategy:
    def __init__(self, rule: SplitRule | None = None):
        self._rule = rule or HasPossessiveColoursRule()

    def apply(self, record: PipelineRecord) -> list[PipelineRecord]:
        normalized = self._normalize_colours(record)
        if not self._rule.should_apply(normalized):
            return [normalized]
        return self._split_by_driver_colours(normalized)

    @staticmethod
    def _normalize_colours(record: PipelineRecord) -> PipelineRecord:
        normalized = record.to_dict()
        for key in COLOUR_KEYS:
            if key in normalized:
                normalized[key] = ColourScopeHandler.split_or_colours(normalized[key])
        return PipelineRecord.from_input(normalized)

    @staticmethod
    def _split_by_driver_colours(record: PipelineRecord) -> list[PipelineRecord]:
        driver_colour_map: dict[str, dict[str, list[Any]]] = {}
        common_by_key: dict[str, list[Any]] = {}

        for key in COLOUR_KEYS:
            colours = record.get(key)
            if not isinstance(colours, list):
                continue
            groups = ColourScopeHandler.extract_possessive_colour_groups(colours)
            common_by_key[key] = []
            for driver_name, colour_list in groups:
                if driver_name is None:
                    common_by_key[key].extend(colour_list)
                else:
                    driver_colour_map.setdefault(driver_name, {}).setdefault(
                        key,
                        [],
                    ).extend(colour_list)

        if not driver_colour_map:
            return [record]

        result: list[PipelineRecord] = []
        for driver_name, colour_map in driver_colour_map.items():
            new_record = record.with_updates(driver=[{"text": driver_name}]).to_dict()
            for key in COLOUR_KEYS:
                if key not in record.payload:
                    continue
                specific = colour_map.get(key, [])
                common = common_by_key.get(key, [])
                new_record[key] = specific + common
            result.append(PipelineRecord.from_input(new_record))
        return result
