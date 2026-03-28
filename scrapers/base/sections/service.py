from __future__ import annotations

import logging
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any
from typing import Protocol

from models.value_objects import EntityName
from models.value_objects import SectionId
from models.value_objects import WikiUrl
from scrapers.base.options import ScraperOptions
from scrapers.base.sections.interface import SectionParseResult
from scrapers.base.sections.serializer import normalize_section_metadata
from scrapers.base.sections.serializer import serialize_section_result

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.sections.adapter import SectionAdapter
    from scrapers.base.sections.adapter import SectionAdapterEntry


logger = logging.getLogger(__name__)


class SectionExtractionService(Protocol):
    def extract(self, soup: BeautifulSoup) -> list[dict[str, Any]]: ...


class BaseSectionExtractionService(ABC):
    domain: str
    flatten_records = False
    aggregate_records_by_section_id = False

    def __init__(
        self,
        *,
        adapter: SectionAdapter,
        options: ScraperOptions | None = None,
        url: WikiUrl | str | None = None,
    ) -> None:
        self._adapter = adapter
        self._options = options
        self._url = WikiUrl.from_raw(url) if url is not None else None

    def extract(
        self,
        soup: BeautifulSoup,
    ) -> list[dict[str, Any]] | dict[str, list[dict[str, Any]]]:
        sections = self._parse_sections(soup)
        return self._aggregate_sections(sections)

    @abstractmethod
    def build_entries(self) -> list[SectionAdapterEntry]:
        """Build domain-specific section adapter entries."""

    def _parse_sections(self, soup: BeautifulSoup) -> list[SectionParseResult]:
        sections: list[SectionParseResult] = []
        for entry in self.build_entries():
            try:
                sections.extend(
                    self._adapter.parse_sections(
                        soup=soup,
                        domain=self.domain,
                        entries=[entry],
                    ),
                )
            except Exception:  # pragma: no cover - defensive branch
                logger.exception(
                    "Failed to parse section entry",
                    extra={
                        "domain": self.domain,
                        "section_id": SectionId.from_raw(entry.section_id).to_export(),
                        "parser": entry.parser.__class__.__name__,
                    },
                )
        return sections

    def _aggregate_sections(
        self,
        sections: list[SectionParseResult],
    ) -> list[dict[str, Any]] | dict[str, list[dict[str, Any]]]:
        if self.flatten_records:
            return [
                record
                for section in sections
                for record in self._build_section_records(section)
            ]
        if self.aggregate_records_by_section_id:
            return {
                SectionId.from_raw(section.section_id).to_export(): section.records
                for section in sections
            }
        return [self._build_section_payload(section) for section in sections]

    def _build_section_payload(
        self,
        section: SectionParseResult,
    ) -> dict[str, Any]:
        return serialize_section_result(section)

    def _build_section_records(
        self,
        section: SectionParseResult,
    ) -> list[dict[str, Any]]:
        section_metadata = self._build_section_metadata(section)
        return [
            {
                **record,
                **self._build_record_metadata(
                    section=section,
                    section_metadata=section_metadata,
                ),
            }
            for record in section.records
        ]

    def _build_record_metadata(
        self,
        *,
        section: SectionParseResult,
        section_metadata: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "section": EntityName.from_raw(section.section_label).to_export(),
            "section_id": SectionId.from_raw(section.section_id).to_export(),
            "section_metadata": section_metadata,
        }

    def _build_section_metadata(
        self,
        section: SectionParseResult,
    ) -> dict[str, Any]:
        return normalize_section_metadata(section)

    def require_options(self) -> ScraperOptions:
        if self._options is None:
            msg = (
                f"{self.__class__.__name__} requires ScraperOptions to build "
                "section entries."
            )
            raise ValueError(msg)
        return self._options

    def require_url(self) -> WikiUrl:
        if self._url is None:
            msg = f"{self.__class__.__name__} requires a URL to build section entries."
            raise ValueError(msg)
        return self._url
