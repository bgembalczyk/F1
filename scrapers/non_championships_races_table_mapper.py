"""Compatibility shim."""

from scrapers.mappers.non_championships_races_table_mapper import (
    NonChampionshipsRacesTableMapper,
)

# legacy typo-compatible alias
NonChampionshipRacesTableMapper = NonChampionshipsRacesTableMapper

__all__ = ["NonChampionshipsRacesTableMapper", "NonChampionshipRacesTableMapper"]
