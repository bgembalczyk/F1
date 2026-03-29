from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.grands_prix.mappers.by_year_record import GrandPrixByYearRecordMapper
from scrapers.grands_prix.services.championship import GrandPrixChampionshipResolver

if TYPE_CHECKING:
    from bs4 import Tag


class GrandPrixByYearRecordAssembler:
    """Domain assembler for final by-year grand prix records."""

    def __init__(
        self,
        *,
        championship_resolver: GrandPrixChampionshipResolver | None = None,
        record_mapper: GrandPrixByYearRecordMapper | None = None,
    ) -> None:
        self._championship_resolver = (
            championship_resolver or GrandPrixChampionshipResolver()
        )
        self._record_mapper = record_mapper or GrandPrixByYearRecordMapper()

    def assemble(self, *, record: dict[str, Any], row: Tag) -> dict[str, Any] | None:
        assembled = self._record_mapper.map(record)
        if assembled is None:
            return None
        assembled["championship"] = self._championship_resolver.resolve(row)
        return assembled
