"""Public API for orchestration components.

Konwencja: każdy nowy komponent dodajemy do ``__init__.py`` i do ``__all__``.
"""

from scrapers.base.orchestration.components.section_source_adapter import SectionSourceAdapter
from scrapers.base.orchestration.lifecycle import PIPELINE_LIFECYCLE
from scrapers.base.orchestration.lifecycle import PipelineStage
from scrapers.base.orchestration.lifecycle import StageCheckpointDumper
from scrapers.base.orchestration.lifecycle import StageEnvelope

__all__ = [
    "PIPELINE_LIFECYCLE",
    "PipelineStage",
    "SectionSourceAdapter",
    "StageCheckpointDumper",
    "StageEnvelope",
]
