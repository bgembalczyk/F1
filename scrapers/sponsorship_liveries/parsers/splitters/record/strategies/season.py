from typing import Any

from scrapers.sponsorship_liveries.helpers.constants import COLOUR_KEYS
from scrapers.sponsorship_liveries.helpers.constants import SPONSOR_KEYS
from scrapers.sponsorship_liveries.parsers.record_text import SponsorshipRecordText
from scrapers.sponsorship_liveries.parsers.scope_handlers.colour import (
    ColourScopeHandler,
)
from scrapers.sponsorship_liveries.parsers.scope_handlers.sponsor import (
    SponsorScopeHandler,
)
from scrapers.sponsorship_liveries.parsers.splitters.record.pipeline_record import (
    PipelineRecord,
)
from scrapers.sponsorship_liveries.parsers.splitters.record.protocols import SplitRule
from scrapers.sponsorship_liveries.parsers.splitters.record.rules import (
    HasMultipleSeasonsRule,
)
from scrapers.sponsorship_liveries.parsers.splitters.record.rules import (
    HasYearSpecificColoursRule,
)
from scrapers.sponsorship_liveries.parsers.splitters.record.rules import (
    HasYearSpecificSponsorsRule,
)


class SeasonSplitStrategy:
    def __init__(
        self,
        *,
        multiple_seasons_rule: SplitRule | None = None,
        year_sponsors_rule: SplitRule | None = None,
        year_colours_rule: SplitRule | None = None,
    ):
        self._multiple_seasons_rule = multiple_seasons_rule or HasMultipleSeasonsRule()
        self._year_sponsors_rule = year_sponsors_rule or HasYearSpecificSponsorsRule()
        self._year_colours_rule = year_colours_rule or HasYearSpecificColoursRule()

    def apply(self, record: PipelineRecord) -> list[PipelineRecord]:
        raw_record = record.payload
        if not self._multiple_seasons_rule.should_apply(record):
            return [record]

        seasons = raw_record.get("season")
        season_entries = self._season_entries(seasons)
        if len(season_entries) <= 1:
            return [record]

        if not self._year_sponsors_rule.should_apply(record):
            if self._year_colours_rule.should_apply(record):
                return self._split_record_by_colour_scopes(record, season_entries)
            return [record]

        split_records: list[PipelineRecord] = []
        for season_entry in season_entries:
            year = season_entry["year"]
            new_record = record.with_updates(season=[season_entry]).to_dict()
            for key in SPONSOR_KEYS:
                if key in raw_record:
                    new_record[key] = SponsorScopeHandler.filter_sponsors_for_year(
                        raw_record[key],
                        year,
                    )
            for key in COLOUR_KEYS:
                if key in raw_record:
                    new_record[key] = ColourScopeHandler.filter_colours_for_year(
                        raw_record[key],
                        year,
                    )
            split_records.append(PipelineRecord.from_input(new_record))

        return split_records

    @staticmethod
    def _season_entries(seasons: Any) -> list[dict[str, Any]]:
        if not isinstance(seasons, list):
            return []
        return [
            season
            for season in seasons
            if isinstance(season, dict) and isinstance(season.get("year"), int)
        ]

    @staticmethod
    def _split_record_by_colour_scopes(
        record: PipelineRecord,
        season_entries: list[dict[str, Any]],
    ) -> list[PipelineRecord]:
        colour_year_sets = SeasonSplitStrategy._extract_colour_year_sets(record)
        if not colour_year_sets:
            return [record]

        split_records = SeasonSplitStrategy._build_base_colour_scoped_records(
            record,
            season_entries,
            colour_year_sets,
        )
        split_records.extend(
            SeasonSplitStrategy._build_year_scoped_colour_records(
                record,
                season_entries,
                colour_year_sets,
            ),
        )
        return split_records

    @staticmethod
    def _extract_colour_year_sets(record: PipelineRecord) -> list[set[int]]:
        colour_year_sets: list[set[int]] = []
        for key in COLOUR_KEYS:
            colours = record.get(key)
            if not isinstance(colours, list):
                continue
            for item in colours:
                if not isinstance(item, str):
                    continue
                years = SponsorshipRecordText.extract_years_from_text(item)
                if years:
                    colour_year_sets.append(years)
        return colour_year_sets

    @staticmethod
    def _build_base_colour_scoped_records(
        record: PipelineRecord,
        season_entries: list[dict[str, Any]],
        colour_year_sets: list[set[int]],
    ) -> list[PipelineRecord]:
        raw_record = record.payload
        all_years = set().union(*colour_year_sets)
        base_seasons = [
            season for season in season_entries if season["year"] not in all_years
        ]
        if not base_seasons:
            return []

        base_record = record.with_updates(season=base_seasons).to_dict()
        for key in COLOUR_KEYS:
            if key in raw_record:
                base_record[key] = ColourScopeHandler.remove_year_specific_colours(
                    raw_record[key],
                )
        return [PipelineRecord.from_input(base_record)]

    @staticmethod
    def _build_year_scoped_colour_records(
        record: PipelineRecord,
        season_entries: list[dict[str, Any]],
        colour_year_sets: list[set[int]],
    ) -> list[PipelineRecord]:
        raw_record = record.payload
        scoped_records: list[PipelineRecord] = []
        for years in SeasonSplitStrategy._unique_year_sets(colour_year_sets):
            scoped_seasons = [
                season for season in season_entries if season["year"] in years
            ]
            if not scoped_seasons:
                continue
            scoped_record = record.with_updates(season=scoped_seasons).to_dict()
            for key in COLOUR_KEYS:
                if key in raw_record:
                    scoped_record[key] = ColourScopeHandler.filter_colours_for_years(
                        raw_record[key],
                        years,
                    )
            scoped_records.append(PipelineRecord.from_input(scoped_record))
        return scoped_records

    @staticmethod
    def _unique_year_sets(year_sets: list[set[int]]) -> list[set[int]]:
        unique_year_sets: list[set[int]] = []
        for years in year_sets:
            if not any(years == existing for existing in unique_year_sets):
                unique_year_sets.append(years)
        return unique_year_sets
