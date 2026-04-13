from dataclasses import dataclass
from typing import Any

from scrapers.parsers.wiki.domain_mapper import WikiDomainMapper


@dataclass(frozen=True)
class WikiMapperRegistry:
    """Jawny registry mapperów używanych wyłącznie w etapie translacji domenowej."""

    domain_mapper: WikiDomainMapper
    table_mappers: tuple[Any, ...] = ()
