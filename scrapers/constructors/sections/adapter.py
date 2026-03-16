from __future__ import annotations

from scrapers.base.sections.adapter import SectionAdapterEntry
from scrapers.constructors.sections.championship_results import ConstructorChampionshipResultsSectionParser
from scrapers.constructors.sections.complete_f1_results import ConstructorCompleteF1ResultsSectionParser
from scrapers.constructors.sections.history import ConstructorHistorySectionParser


def constructor_section_entries() -> list[SectionAdapterEntry]:
    return [
        SectionAdapterEntry(
            section_id="history",
            aliases=("History",),
            parser=ConstructorHistorySectionParser(),
        ),
        SectionAdapterEntry(
            section_id="championship_results",
            aliases=("Championship_results", "Formula_One/World_Championship_results"),
            parser=ConstructorChampionshipResultsSectionParser(),
        ),
        SectionAdapterEntry(
            section_id="complete_formula_one_results",
            aliases=("Complete_Formula_One_results", "Complete_World_Championship_results"),
            parser=ConstructorCompleteF1ResultsSectionParser(),
        ),
    ]
