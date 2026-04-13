from __future__ import annotations

from scrapers.parsers.infobox.driver_cell import InfoboxCellValueExtractor
from scrapers.parsers.registry import discover_registered_parser_classes
from scrapers.parsers.registry import is_parser_class_registered
from scrapers.parsers.section.standings.f1_table import F1StandingsTableParser


def test_parser_registry_discovery_tracks_concrete_parsers_only() -> None:
    discovered = discover_registered_parser_classes()

    assert F1StandingsTableParser in discovered
    assert is_parser_class_registered(F1StandingsTableParser)

    # Helper/extractor classes should not be treated as parser contract classes.
    assert not is_parser_class_registered(InfoboxCellValueExtractor)
