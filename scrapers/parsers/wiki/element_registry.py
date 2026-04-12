from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Callable

from bs4 import Tag

from models.data.wiki_parser import WikiParserData
from scrapers.parsers.element_parser_abc import ElementType
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.wiki.wiki_normalization import normalize_section_text

WIKI_SELECTOR_FAMILY_MAP: dict[ElementType, str] = {
    "table": "table.wikitable",
    "list": "ul, ol",
    "infobox": "table.infobox",
    "section": "div.mw-heading2|3|4",
    "figure": "figure",
    "paragraph": "p",
    "navbox": "div.navbox",
    "references_wrap": "div.reflist | div[class*='references-wrap']",
}


@dataclass(frozen=True)
class ElementParseInput:
    """Wspólny model wejścia parsera elementu (tag + metadata + section context)."""

    tag: Tag
    metadata: dict[str, object] | None = None
    section_context: SectionExtractionContext = field(default_factory=SectionExtractionContext)

    @property
    def domain(self) -> str | None:
        if not isinstance(self.metadata, dict):
            return None
        raw_domain = self.metadata.get("domain")
        return str(raw_domain).strip().lower() if raw_domain else None

    @property
    def section_id(self) -> str | None:
        section_id = self.section_context.section_id
        return normalize_section_text(section_id) if section_id else None


@dataclass(frozen=True)
class ElementParserRegistration:
    """Registry entry resolving parser by element type + domain + section context."""

    element_type: ElementType
    parser: Callable[[Tag], WikiParserData]
    parser_class: type
    domain: str | None = None
    section_id: str | None = None
    section_profile: str | None = None


@dataclass(frozen=True)
class ElementRegistry:
    registrations: tuple[ElementParserRegistration, ...]
    type_predicates: dict[ElementType, Callable[[Tag], bool]]

    @staticmethod
    def _get_classes(el: Tag) -> list[str]:
        classes = el.get("class") or []
        if isinstance(classes, str):
            return classes.split()
        return list(classes)

    def detect_element_type(self, element: Tag) -> ElementType | None:
        for element_type, predicate in self.type_predicates.items():
            if predicate(element):
                return element_type
        return None

    def resolve_registration(
        self,
        parse_input: ElementParseInput,
    ) -> ElementParserRegistration | None:
        element_type = self.detect_element_type(parse_input.tag)
        if element_type is None:
            return None
        return self._pick_best_registration(
            element_type=element_type,
            domain=parse_input.domain,
            section_id=parse_input.section_id,
        )

    def resolve(
        self,
        parse_input: ElementParseInput,
    ) -> tuple[str, Callable[[Tag], WikiParserData]] | None:
        registration = self.resolve_registration(parse_input)
        if registration is None:
            return None
        return registration.element_type, registration.parser

    def validate_selector_family_coverage(self) -> None:
        missing_predicates = set(WIKI_SELECTOR_FAMILY_MAP) - set(self.type_predicates)
        if missing_predicates:
            missing = ", ".join(sorted(missing_predicates))
            raise ValueError(f"Missing selector predicates for families: {missing}")

        registered_families = {registration.element_type for registration in self.registrations}
        missing_registrations = {
            family
            for family in WIKI_SELECTOR_FAMILY_MAP
            if family != "section" and family not in registered_families
        }
        if missing_registrations:
            missing = ", ".join(sorted(missing_registrations))
            raise ValueError(f"Missing parser registrations for families: {missing}")

    def _pick_best_registration(
        self,
        *,
        element_type: ElementType,
        domain: str | None,
        section_id: str | None,
    ) -> ElementParserRegistration | None:
        normalized_section_id = normalize_section_text(section_id) if section_id else None
        candidates: list[tuple[int, ElementParserRegistration]] = []
        for registration in self.registrations:
            if registration.element_type != element_type:
                continue
            score = self._match_score(
                registration=registration,
                domain=domain,
                section_id=normalized_section_id,
            )
            if score is None:
                continue
            candidates.append((score, registration))
        if not candidates:
            return None
        candidates.sort(key=lambda item: item[0], reverse=True)
        return candidates[0][1]

    @staticmethod
    def _match_score(
        *,
        registration: ElementParserRegistration,
        domain: str | None,
        section_id: str | None,
    ) -> int | None:
        score = 0
        if registration.domain is not None:
            if domain != registration.domain:
                return None
            score += 10
        if registration.section_id is not None:
            if section_id != registration.section_id:
                return None
            score += 4
        if registration.section_profile is not None:
            if section_id != registration.section_profile:
                return None
            score += 2
        return score
