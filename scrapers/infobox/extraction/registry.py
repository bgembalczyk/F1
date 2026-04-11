from __future__ import annotations

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.infobox.extraction.extractor.circuit_extractor import CircuitInfoboxExtractor
from scrapers.infobox.extraction.extractor.infobox_extractor import InfoboxExtractorProtocol
from scrapers.infobox.extraction.service.circuit_orchestrator import CircuitInfoboxOrchestrator
from scrapers.infobox.extraction.service.constructor_infobox_orchestrator import (
    ConstructorInfoboxOrchestrator,
)
from scrapers.infobox.extraction.service.driver_infobox_orchestrator import DriverInfoboxOrchestrator

EXTRACTOR_REGISTRY: dict[str, type[InfoboxExtractorProtocol[BeautifulSoup]]] = {
    "circuit": CircuitInfoboxExtractor,
}

ORCHESTRATOR_REGISTRY: dict[str, type] = {
    "driver": DriverInfoboxOrchestrator,
    "constructor": ConstructorInfoboxOrchestrator,
    "circuit": CircuitInfoboxOrchestrator,
}
