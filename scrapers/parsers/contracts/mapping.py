"""Re-exports: mapping contracts — MapperABC and table mapper ABCs.

These ABCs define the canonical mapping contracts for the domain mapping layer.
All *Mapper classes must implement ``map(...)`` as their public entrypoint.
"""

from scrapers.mapper_abc import MapperABC
from scrapers.table_domain_mapper_abc import TableDomainMapperABC
from scrapers.table_mapper_abc import TableMapperABC

__all__ = [
    "MapperABC",
    "TableDomainMapperABC",
    "TableMapperABC",
]
