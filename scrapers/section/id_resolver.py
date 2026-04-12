from __future__ import annotations

from typing import TYPE_CHECKING

from models.section_id import SectionId
from scrapers.errors.missing_section import MissingSectionError
from scrapers.parsers.section.detection import find_section_heading
from scrapers.parsers.section.detection import normalize_section_lookup_key
from scrapers.section.constants import DOMAIN_SECTION_RESOLVER_CONFIG
from scrapers.section.helpers import section_id_to_label
from scrapers.section.resolution import SectionResolution

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class SectionIdResolver:
    def __init__(self, *, domain: str) -> None:
        self._domain = domain

    def resolve_candidates(
        self,
        *,
        section_id: SectionId | str,
        alternative_section_ids: tuple[str, ...] = (),
    ) -> tuple[str, ...]:
        normalized_section_id = SectionId.from_raw(section_id).to_export()
        canonical_section_id = (
            section_id if isinstance(section_id, str) else normalized_section_id
        )
        resolved_alternatives = alternative_section_ids
        if not resolved_alternatives:
            domain_config = DOMAIN_SECTION_RESOLVER_CONFIG.get(self._domain, ())
            for candidate in domain_config:  # pragma: no branch
                if (
                    SectionId.from_raw(candidate.section_id).to_export()
                    == normalized_section_id
                ):
                    resolved_alternatives = candidate.alternative_section_ids
                    break

        candidates: list[str] = [canonical_section_id]
        seen_lookup = {normalize_section_lookup_key(canonical_section_id)}
        for alias in resolved_alternatives:
            lookup_key = normalize_section_lookup_key(alias)
            if alias and lookup_key not in seen_lookup:
                candidates.append(alias)
                seen_lookup.add(lookup_key)

        section_label = section_id_to_label(canonical_section_id)
        section_label_lookup = normalize_section_lookup_key(section_label)
        if section_label and section_label_lookup not in seen_lookup:
            candidates.append(section_label)
        return tuple(candidates)

    def resolve_heading(
        self,
        *,
        soup: BeautifulSoup,
        section_id: SectionId | str,
        alternative_section_ids: tuple[str, ...] = (),
        aliases: dict[str, set[str]] | None = None,
    ) -> SectionResolution:
        resolved_section_id = (
            section_id
            if isinstance(section_id, str)
            else SectionId.from_raw(section_id).to_export()
        )
        candidates = self.resolve_candidates(
            section_id=resolved_section_id,
            alternative_section_ids=alternative_section_ids,
        )
        for candidate in candidates:
            heading_match = find_section_heading(
                soup,
                candidate,
                aliases=aliases,
                domain=self._domain,
            )
            if heading_match is not None:
                return SectionResolution(
                    section_id=resolved_section_id,
                    candidates=candidates,
                    matched_candidate=candidate,
                    heading_match=heading_match,
                )
        return SectionResolution(
            section_id=resolved_section_id,
            candidates=candidates,
            matched_candidate=None,
            heading_match=None,
        )

    def build_missing_section_error(
        self,
        *,
        section_id: SectionId | str,
        alternative_section_ids: tuple[str, ...] = (),
    ) -> MissingSectionError:
        resolved_section_id = (
            section_id
            if isinstance(section_id, str)
            else SectionId.from_raw(section_id).to_export()
        )
        return MissingSectionError(
            domain=self._domain,
            section_id=resolved_section_id,
            candidates=self.resolve_candidates(
                section_id=resolved_section_id,
                alternative_section_ids=alternative_section_ids,
            ),
        )
