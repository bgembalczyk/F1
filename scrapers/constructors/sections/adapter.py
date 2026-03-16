from __future__ import annotations

from scrapers.base.sections.adapter import SectionAdapterEntry
from scrapers.wiki.parsers.section_profiles import profile_entry_aliases
from scrapers.constructors.sections.championship_results import ConstructorChampionshipResultsSectionParser
from scrapers.constructors.sections.complete_f1_results import ConstructorCompleteF1ResultsSectionParser
from scrapers.constructors.sections.history import ConstructorHistorySectionParser


def constructor_section_entries() -> list[SectionAdapterEntry]:
    return [
        SectionAdapterEntry(
            section_id="history",
            aliases=profile_entry_aliases("constructors", "history", "History"),
            parser=ConstructorHistorySectionParser(),
        ),
        SectionAdapterEntry(
            section_id="championship_results",
            aliases=profile_entry_aliases("constructors", "championship_results", "Championship_results", "Formula_One/World_Championship_results"),
            parser=ConstructorChampionshipResultsSectionParser(),
        ),
        SectionAdapterEntry(
            section_id="complete_formula_one_results",
            aliases=profile_entry_aliases("constructors", "complete_formula_one_results", "Complete_Formula_One_results", "Complete_World_Championship_results"),
            parser=ConstructorCompleteF1ResultsSectionParser(),
        ),
    ]
