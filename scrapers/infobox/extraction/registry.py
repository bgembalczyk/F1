from __future__ import annotations

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.circuit_orchestrator import CircuitInfoboxOrchestrator
from scrapers.constructor_infobox_orchestrator import ConstructorInfoboxOrchestrator
from scrapers.driver_infobox_orchestrator import DriverInfoboxOrchestrator
from scrapers.infobox.extraction.extractor.circuit_extractor import CircuitInfoboxExtractor
from scrapers.protocols.infobox_extractor import InfoboxExtractorProtocol

EXTRACTOR_REGISTRY: dict[str, type[InfoboxExtractorProtocol[BeautifulSoup]]] = {
    "circuit": CircuitInfoboxExtractor,
}

ORCHESTRATOR_REGISTRY: dict[str, type] = {
    "driver": DriverInfoboxOrchestrator,
    "constructor": ConstructorInfoboxOrchestrator,
    "circuit": CircuitInfoboxOrchestrator,
}
