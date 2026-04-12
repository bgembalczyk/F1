from dataclasses import dataclass
from dataclasses import field

from scrapers.parsers.section.match.priorities import SectionMatchPriorities
from scrapers.parsers.section.normalization import normalize_section_text


@dataclass(frozen=True, slots=True)
class SectionProfile:
    domain: str
    canonical_section_ids: frozenset[str]
    heading_aliases: dict[str, frozenset[str]]
    priorities: SectionMatchPriorities = field(
        default_factory=SectionMatchPriorities,
    )
    required_sections: frozenset[str] = frozenset()
    optional_sections: frozenset[str] = frozenset()

    def aliases_for(self, target: str) -> set[str]:
        normalized_target = normalize_section_text(target)
        aliases = set(self.heading_aliases.get(normalized_target, frozenset()))
        if normalized_target in self.canonical_section_ids:
            aliases.update(self.heading_aliases.get(normalized_target, frozenset()))
        return aliases

    def canonical_for(self, target: str) -> str | None:
        normalized_target = normalize_section_text(target)
        if normalized_target in self.canonical_section_ids:
            return normalized_target

        for canonical, aliases in self.heading_aliases.items():
            if normalized_target in aliases:
                return canonical
        return None
