from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable

from scrapers.wiki.parsers.sections.normalization import normalize_section_profile_key

if TYPE_CHECKING:
    from bs4 import Tag

SectionTree = dict[str, Any]


@dataclass(slots=True)
class SectionTreeMatch:
    section: SectionTree
    strategy: str
    score: float


@dataclass(slots=True)
class SectionMatch:
    heading: Tag
    strategy: str
    score: float


@dataclass(frozen=True, slots=True)
class SectionMatchPriorities:
    exact_id_score: float = 3.0
    exact_text_score: float = 2.0
    fuzzy_base_score: float = 1.0
    fuzzy_threshold: float = 0.82


@dataclass(frozen=True, slots=True)
class SectionProfile:
    domain: str
    canonical_section_ids: frozenset[str]
    heading_aliases: dict[str, frozenset[str]]
    dynamic_alias_resolver: Callable[[str], set[str]] | None = None
    priorities: SectionMatchPriorities = field(
        default_factory=SectionMatchPriorities,
    )
    required_sections: frozenset[str] = frozenset()
    optional_sections: frozenset[str] = frozenset()

    def aliases_for(self, target: str) -> set[str]:
        normalized_target = normalize_section_profile_key(target)
        aliases = set(self.heading_aliases.get(normalized_target, frozenset()))
        if normalized_target in self.canonical_section_ids:
            aliases.update(self.heading_aliases.get(normalized_target, frozenset()))
        if self.dynamic_alias_resolver is not None:
            aliases.update(self.dynamic_alias_resolver(normalized_target))
        return aliases

    def canonical_for(self, target: str) -> str | None:
        normalized_target = normalize_section_profile_key(target)
        if normalized_target in self.canonical_section_ids:
            return normalized_target

        for canonical, aliases in self.heading_aliases.items():
            if normalized_target in aliases:
                return canonical
        return None


@dataclass(slots=True)
class SectionExtractionContext:
    """Shared context passed through every section parser layer."""

    page_title: str = ""
    page_url: str = ""
    breadcrumbs: tuple[str, ...] = ()
    html_metadata: dict[str, Any] | None = None
    section_id: str | None = None

    def with_section(
        self,
        *,
        section_name: str,
        section_id: str | None = None,
    ) -> SectionExtractionContext:
        return SectionExtractionContext(
            page_title=self.page_title,
            page_url=self.page_url,
            breadcrumbs=(*self.breadcrumbs, section_name),
            html_metadata=self.html_metadata,
            section_id=section_id,
        )
