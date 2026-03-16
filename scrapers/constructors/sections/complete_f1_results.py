from __future__ import annotations

from scrapers.constructors.sections.common import ConstructorTablesSectionParser


class ConstructorCompleteF1ResultsSectionParser(ConstructorTablesSectionParser):
    def __init__(self) -> None:
        super().__init__(
            section_id="Complete_Formula_One_results",
            section_label="Complete F1 results",
        )
