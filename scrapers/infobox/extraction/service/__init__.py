from scrapers.infobox.extraction.protocol import InfoboxExtractionService
from scrapers.infobox.extraction.service.base_orchestrator import BaseInfoboxOrchestrator
from scrapers.infobox.extraction.service.circuit_orchestrator import CircuitInfoboxOrchestrator
from scrapers.infobox.extraction.service.constructor_orchestrator import (
    ConstructorInfoboxOrchestrator,
)
from scrapers.infobox.extraction.service.driver_orchestrator import DriverInfoboxOrchestrator
from scrapers.infobox.extraction.service.strategy_orchestrator import (
    StrategyBackedInfoboxOrchestrator,
)

BaseInfoboxExtractionService = BaseInfoboxOrchestrator
CircuitInfoboxExtractionService = CircuitInfoboxOrchestrator
ConstructorInfoboxExtractionService = ConstructorInfoboxOrchestrator
DriverInfoboxExtractionService = DriverInfoboxOrchestrator
StrategyBackedInfoboxExtractionService = StrategyBackedInfoboxOrchestrator

__all__ = [
    "BaseInfoboxExtractionService",
    "BaseInfoboxOrchestrator",
    "CircuitInfoboxExtractionService",
    "CircuitInfoboxOrchestrator",
    "ConstructorInfoboxExtractionService",
    "ConstructorInfoboxOrchestrator",
    "DriverInfoboxExtractionService",
    "DriverInfoboxOrchestrator",
    "InfoboxExtractionService",
    "StrategyBackedInfoboxExtractionService",
    "StrategyBackedInfoboxOrchestrator",
]
