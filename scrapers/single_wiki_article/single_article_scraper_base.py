from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar

from infrastructure.helpers import init_scraper_options
from scrapers.adapters.section.entry import SectionAdapterEntry
from scrapers.dto import InfoboxPayloadDTO
from scrapers.dto import SectionsPayloadDTO
from scrapers.dto import TablesPayloadDTO
from scrapers.helpers.config_factory import build_scraper_options
from scrapers.parsers.section.helpers import profile_entry_aliases
from scrapers.scraper_wiki import WikiScraper
from scrapers.section.id_resolver import SectionIdResolver
from scrapers.section.parse_results import SectionParseResult
from scrapers.section.selection_strategy import WikipediaSectionByIdSelectionStrategy
from scrapers.section.serializer import coerce_section_parse_result
from scrapers.section.serializer import serialize_section_result
from scrapers.wiring import ScraperRuntimeFactory

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.options import ScraperOptions
    from scrapers.section.selection_strategy.base import SectionSelectionStrategy


class ArticleScraperBase(WikiScraper, ABC):
    """Base class responsible for article fetch, parsing, and record assembly lifecycle.

    Includes section-selection helpers (formerly SectionAwareMixin) and
    section-parsing utilities (formerly SectionAdapter).
    """

    options_domain: str | None = None
    options_profile: str = "article_strict"

    STANDARD_HOOKS: ClassVar[dict[str, str]] = {
        "_build_infobox_payload": "Build normalized infobox payload.",
        "_build_tables_payload": "Build normalized table payload.",
        "_build_sections_payload": "Build normalized section payload.",
        "_assemble_record": "Compose final domain record from payload hooks.",
    }

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        include_urls: bool = True,
        section_selection_strategy: SectionSelectionStrategy | None = None,
    ) -> None:
        resolved_options = init_scraper_options(options, include_urls=include_urls)
        resolved_options = build_scraper_options(
            domain=self.options_domain,
            profile=self.options_profile,
            options=resolved_options,
            scraper_cls=type(self),
        )
        policy = self.get_http_policy(resolved_options)
        runtime = ScraperRuntimeFactory().build(options=resolved_options, policy=policy)
        resolved_options.fetcher = runtime.fetcher
        resolved_options.source_adapter = runtime.source_adapter

        super().__init__(options=resolved_options)
        self.url: str = ""
        self._original_url: str | None = None
        self._section_fragment: str | None = None
        self.section_selection_strategy = section_selection_strategy
        self._options = resolved_options
        self.policy = self.http_policy
        self.debug_dir = resolved_options.debug_dir

    def extract_by_url(self, url: str) -> list[dict[str, Any]]:
        self._original_url = url
        if self.section_selection_strategy is None:
            self.url = url
            self._section_fragment = None
            return super().fetch()

        base_url, fragment = self.section_selection_strategy.split_url_fragment(url)
        self.url = base_url
        self._section_fragment = fragment
        return super().fetch()

    def parse(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        if not self._should_parse_article(soup):
            return []

        working_soup = self._prepare_article_soup(soup)
        if self.parser is not None:
            return self.parser.parse(working_soup)
        return self._parse_soup(working_soup)

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return [self._build_article_record(soup)]

    def _should_parse_article(self, soup: BeautifulSoup) -> bool:
        _ = soup
        return True

    def _prepare_article_soup(self, soup: BeautifulSoup) -> BeautifulSoup:
        if self.section_selection_strategy is None:
            return soup
        return self.section_selection_strategy.select_article_soup(
            soup,
            fragment=self._section_fragment,
        )

    def extract_section_by_id(
        self,
        soup: BeautifulSoup,
        section_id: str,
        *,
        domain: str | None = None,
    ) -> BeautifulSoup | None:
        strategy = getattr(self, "section_selection_strategy", None)
        if strategy is None:
            return None
        return strategy.extract_section_by_id(soup, section_id, domain=domain)

    # ------------------------------------------------------------------
    # Section parsing helpers (formerly SectionAdapter)
    # ------------------------------------------------------------------

    @classmethod
    def _extract_section_from_heading(cls, heading_match) -> BeautifulSoup | None:
        return WikipediaSectionByIdSelectionStrategy.extract_section_by_heading(
            heading_match.heading,
        )

    def parse_sections(
        self,
        *,
        soup: BeautifulSoup,
        domain: str,
        entries: list[SectionAdapterEntry],
    ) -> list[SectionParseResult]:
        parsed: list[SectionParseResult] = []
        resolver = SectionIdResolver(domain=domain)
        for entry in entries:
            canonical_section_id = str(entry.section_id).strip()
            export_section_id = (
                (
                    entry.section_id.to_export()
                    if hasattr(entry.section_id, "to_export")
                    else canonical_section_id
                )
                .strip()
                .lower()
            )
            entry_aliases = profile_entry_aliases(
                domain,
                canonical_section_id,
                *entry.aliases,
            )
            resolution = resolver.resolve_heading(
                soup=soup,
                section_id=canonical_section_id,
                alternative_section_ids=entry_aliases,
                aliases={
                    canonical_section_id: set(entry_aliases),
                },
            )
            if resolution.heading_match is None:
                continue

            section_fragment = self._extract_section_from_heading(
                resolution.heading_match,
            )
            if section_fragment is None:
                continue
            parsed.append(
                coerce_section_parse_result(
                    entry.parser.parse(section_fragment),
                    default_section_id=export_section_id,
                    default_section_label=export_section_id.replace("_", " "),
                    parser=entry.parser.__class__.__name__,
                ),
            )
        return parsed

    def assemble_section_dicts(
        self,
        *,
        soup: BeautifulSoup,
        domain: str,
        entries: list[SectionAdapterEntry],
    ) -> list[dict[str, Any]]:
        return [
            serialize_section_result(result)
            for result in self.parse_sections(soup=soup, domain=domain, entries=entries)
        ]

    # ------------------------------------------------------------------
    # Article record building
    # ------------------------------------------------------------------

    def _build_article_record(self, soup: BeautifulSoup) -> dict[str, Any]:
        return self._run_record_pipeline(soup)

    def _run_record_pipeline(self, soup: BeautifulSoup) -> dict[str, Any]:
        self._before_payload_build(soup)
        record = self._assemble_record(
            soup=soup,
            infobox_payload=self._build_infobox_payload(soup),
            tables_payload=self._build_tables_payload(soup),
            sections_payload=self._build_sections_payload(soup),
        )
        return self._after_record_assembled(record, soup)

    def _before_payload_build(self, soup: BeautifulSoup) -> None:
        _ = soup

    def _after_record_assembled(
        self,
        record: dict[str, Any],
        soup: BeautifulSoup,
    ) -> dict[str, Any]:
        _ = soup
        return record

    def _build_infobox_payload(self, soup: BeautifulSoup) -> InfoboxPayloadDTO:
        _ = soup
        return InfoboxPayloadDTO()

    def _build_tables_payload(self, soup: BeautifulSoup) -> TablesPayloadDTO:
        _ = soup
        return TablesPayloadDTO()

    def _build_sections_payload(self, soup: BeautifulSoup) -> SectionsPayloadDTO:
        _ = soup
        return SectionsPayloadDTO()

    @abstractmethod
    def _assemble_record(
        self,
        *,
        soup: BeautifulSoup,
        infobox_payload: InfoboxPayloadDTO,
        tables_payload: TablesPayloadDTO,
        sections_payload: SectionsPayloadDTO,
    ) -> dict[str, Any]:
        """Compose final domain record from template-method payload hooks."""


__all__ = ["ArticleScraperBase"]
