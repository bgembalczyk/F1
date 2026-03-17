from scrapers.sponsorship_liveries.helpers.constants import COLOUR_KEYS
from scrapers.sponsorship_liveries.helpers.constants import SPONSOR_KEYS
from scrapers.sponsorship_liveries.parsers.colour_scope import ColourScopeHandler
from scrapers.sponsorship_liveries.parsers.record_splitter_protocols import SplitRule
from scrapers.sponsorship_liveries.parsers.sponsor_scope import SponsorScopeHandler


class HasPossessiveColoursRule:
    def should_apply(self, record: dict[str, object]) -> bool:
        return any(
            ColourScopeHandler.has_possessive_colour_groups(record.get(key))
            for key in COLOUR_KEYS
        )


class HasMultipleSeasonsRule:
    def should_apply(self, record: dict[str, object]) -> bool:
        seasons = record.get("season")
        return isinstance(seasons, list) and len(seasons) > 1


class HasYearSpecificSponsorsRule:
    def should_apply(self, record: dict[str, object]) -> bool:
        return SponsorScopeHandler.record_has_year_specific_sponsors(
            record,
            SPONSOR_KEYS,
        )


class HasYearSpecificColoursRule:
    def should_apply(self, record: dict[str, object]) -> bool:
        return ColourScopeHandler.record_has_year_specific_colours(record, COLOUR_KEYS)
