from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from scrapers.base.table.config import ScraperConfig


@dataclass(frozen=True)
class DomainScraperSpec:
    """Reusable domain profile for list table scrapers."""

    domain: str
    base_url: str
    options_profile: str
    default_validator: Any | None = None
    parser_section: str | None = None

    def make_config(
        self,
        *,
        section_id: str | None,
        expected_headers: list[str] | tuple[str, ...] | None,
        schema,
        record_factory,
        model_class: type | None = None,
        table_css_class: str = "wikitable",
    ) -> ScraperConfig:
        return ScraperConfig(
            url=self.base_url,
            section_id=section_id,
            expected_headers=expected_headers,
            schema=schema,
            record_factory=record_factory,
            model_class=model_class,
            table_css_class=table_css_class,
        )
