"""Shared mixin for section-based table parsing with legacy fallback."""

from collections.abc import Callable
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.mixins.wiki_sections import WikipediaSectionByIdMixin


class SectionTableParseMixin:
    """Parse a configured section or fallback to base table parsing."""

    def _diagnostic_context(
        self,
        *,
        domain: str,
        section_label: str | None,
    ) -> str:
        details = [f"domain={domain!r}"]
        if section_label is not None:
            details.append(f"section_label={section_label!r}")
        return ", ".join(details)

    def parse_section_or_fallback(
        self,
        soup: BeautifulSoup,
        *,
        domain: str,
        parser_factory: Callable[[], Any],
        section_label: str | None = None,
    ) -> list[Any]:
        """Parse records from configured section, then fallback to full soup if needed."""
        section_id = self.config.section_id
        if not section_id:
            return super()._parse_soup(soup)

        section_fragment = WikipediaSectionByIdMixin.extract_section_by_id(
            soup,
            section_id,
            domain=domain,
        )
        if section_fragment is None:
            context = self._diagnostic_context(
                domain=domain,
                section_label=section_label,
            )
            msg = f"Nie znaleziono sekcji o id={section_id!r} ({context})"
            raise RuntimeError(msg)

        parser = parser_factory()
        try:
            return parser.parse(section_fragment).records
        except RuntimeError:
            return super()._parse_soup(soup)
