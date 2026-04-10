from __future__ import annotations

from scrapers.adapters.section.entry import SectionAdapterEntry
from scrapers.parsers.section.table.constructor.history import ConstructorHistorySectionParser
from scrapers.parsers.section.table.results.constructor.championship import ConstructorChampionshipResultsSectionParser
from scrapers.parsers.section.table.results.constructor.complete_f1 import ConstructorCompleteF1ResultsSectionParser
from scrapers.parsers.section.wiki.helpers import profile_entry_aliases


def constructor_section_entries() -> list[SectionAdapterEntry]:
    return [
        SectionAdapterEntry(
            section_id="history",
            aliases=profile_entry_aliases("constructors", "history", "History"),
            parser=ConstructorHistorySectionParser(),
        ),
        SectionAdapterEntry(
            section_id="championship_results",
            aliases=profile_entry_aliases(
                "constructors",
                "championship_results",
                "Championship_results",
                "Formula_One/World_Championship_results",
            ),
            parser=ConstructorChampionshipResultsSectionParser(),
        ),
        SectionAdapterEntry(
            section_id="complete_formula_one_results",
            aliases=profile_entry_aliases(
                "constructors",
                "complete_formula_one_results",
                "Complete_Formula_One_results",
                "Complete_World_Championship_results",
            ),
            parser=ConstructorCompleteF1ResultsSectionParser(),
        ),
    ]


__all__ = ["constructor_section_entries"]
