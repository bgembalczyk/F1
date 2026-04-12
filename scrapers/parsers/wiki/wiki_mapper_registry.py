from dataclasses import dataclass

from scrapers.parsers.domain_mapper_abc import DomainMapperABC
from scrapers.parsers.wiki_table_mapper_set import WikiTableMapperSet


@dataclass(frozen=True)
class WikiMapperRegistry:
    """Jawny registry mapperów używanych wyłącznie w etapie translacji domenowej."""

    domain_mapper: DomainMapperABC
    table_mappers: WikiTableMapperSet = WikiTableMapperSet()
