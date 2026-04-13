from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SectionMatchPriorities:
    exact_id_score: float = 3.0
    exact_text_score: float = 2.0
    fuzzy_base_score: float = 1.0
    fuzzy_threshold: float = 0.82

    def get_score(
        self,
        *,
        exact_id: bool = False,
        exact_text: bool = False,
    ) -> float:
        if exact_id:
            return self.exact_id_score
        if exact_text:
            return self.exact_text_score
        return self.fuzzy_base_score


from scrapers.parsers.section.extraction_context import SectionExtractionContext

__all__ = ["SectionExtractionContext", "SectionMatchPriorities"]
