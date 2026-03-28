from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from models.value_objects import SectionId
from scrapers.base.errors import DomainParseError
from scrapers.base.sections.constants import DOMAIN_SECTION_RESOLVER_CONFIG
from scrapers.wiki.parsers.section_detection import find_section_heading

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


def section_id_to_label(section_id: SectionId | str) -> str:
    resolved = SectionId.from_raw(section_id).to_export()
    return " ".join(
        resolved.replace("_", " ").replace("-", " ").replace("/", " / ").split(),
    )


@dataclass(frozen=True)
class MissingSectionError(RuntimeError):
    domain: str
    section_id: str
    candidates: tuple[str, ...]

    def __post_init__(self) -> None:
        super().__init__(self.message)

    @property
    def message(self) -> str:
        candidates_display = ", ".join(repr(candidate) for candidate in self.candidates)
        return (
            "Missing section "
            f"{self.section_id!r} for domain={self.domain!r}. "
            f"Tried: [{candidates_display}]"
        )

    def as_domain_error(self, *, url: str | None = None) -> DomainParseError:
        return DomainParseError(
            "Brak wymaganej sekcji w artykule.",
            url=url,
            section_id=self.section_id,
            cause=self,
        )


@dataclass(frozen=True)
class SectionResolution:
    section_id: str
    candidates: tuple[str, ...]
    matched_candidate: str | None
    heading_match: object | None


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
        for alias in resolved_alternatives:
            if alias and alias not in candidates:
                candidates.append(alias)

        section_label = section_id_to_label(canonical_section_id)
        if section_label and section_label not in candidates:
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
