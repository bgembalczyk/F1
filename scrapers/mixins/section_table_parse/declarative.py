"""Shared mixin for section-based table parsing with legacy fallback."""

from typing import Any

from bs4 import BeautifulSoup

from scrapers.mixins.section_table_parse.base import SectionTableParseMixin


class DeclarativeSectionTableParseMixin(SectionTableParseMixin):
    """Declarative section parsing based on domain/label/parser class attributes."""

    domain: str | None = None
    section_label: str | None = None
    section_parser_class: type[Any] | None = None

    def _build_section_parser(self) -> Any:
        if self.section_parser_class is None:
            msg = f"{self.__class__.__name__} must define section_parser_class"
            raise RuntimeError(msg)

        return self.section_parser_class(
            config=self.config,
            section_label=self.section_label,
            include_urls=self.include_urls,
            normalize_empty_values=self.normalize_empty_values,
        )

    def _parse_soup(self, soup: BeautifulSoup) -> list[Any]:
        if self.domain is None:
            msg = f"{self.__class__.__name__} must define domain"
            raise RuntimeError(msg)

        return self.parse_section_or_fallback(
            soup,
            domain=self.domain,
            section_label=self.section_label,
            parser_factory=self._build_section_parser,
        )
