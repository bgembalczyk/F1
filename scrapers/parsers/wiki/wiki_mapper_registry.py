from dataclasses import dataclass
from typing import Any

from scrapers.parsers.domain_mapper_abc import DomainMapperABC


@dataclass(frozen=True)
class WikiMapperRegistry:
    """Jawny registry mapperów używanych wyłącznie w etapie translacji domenowej."""

    domain_mapper: DomainMapperABC
    table_mappers: tuple[Any, ...] = ()
