from __future__ import annotations

from scrapers.parsers.section.table.constructor.base import (
    ConstructorTablesSectionParser,
)


class ConstructorCompleteF1ResultsSectionParser(ConstructorTablesSectionParser):
    def __init__(self) -> None:
        super().__init__(
            section_id="complete_formula_one_results",
            section_label="Complete F1 results",
        )


__all__ = ["ConstructorCompleteF1ResultsSectionParser"]
