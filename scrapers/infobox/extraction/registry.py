from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.infobox.extraction.extractor.circuit_extractor import (
    CircuitInfoboxExtractor,
)
from scrapers.orchestration.circuit_orchestrator import CircuitInfoboxOrchestrator
from scrapers.orchestration.constructor_infobox_orchestrator import (
    ConstructorInfoboxOrchestrator,
)
from scrapers.orchestration.driver_infobox_orchestrator import DriverInfoboxOrchestrator
from scrapers.protocols.infobox_extractor import InfoboxExtractorABC

EXTRACTOR_REGISTRY: dict[str, type[InfoboxExtractorABC[BeautifulSoup]]] = {
    "circuit": CircuitInfoboxExtractor,
}

ORCHESTRATOR_REGISTRY: dict[str, type] = {
    "driver": DriverInfoboxOrchestrator,
    "constructor": ConstructorInfoboxOrchestrator,
    "circuit": CircuitInfoboxOrchestrator,
}
