from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from scrapers.domain_roles import PipelineService
from scrapers.mixins.pipeline_mixins import DebugDumpMixin
from scrapers.mixins.pipeline_mixins import RetryMixin
from scrapers.mixins.pipeline_mixins import ValidationMixin

InputDTO = TypeVar("InputDTO")
PayloadDTO = TypeVar("PayloadDTO")
OutputRecord = TypeVar("OutputRecord", bound=dict[str, Any])


class DomainPipelineService(
    PipelineService[InputDTO, OutputRecord],
    RetryMixin,
    DebugDumpMixin,
    ValidationMixin,
    ABC,
    Generic[InputDTO, PayloadDTO, OutputRecord],
):
    """Wspólny kontrakt pipeline'u domenowego.

    Publiczny kontrakt: ``execute(input_dto)``.
    Warstwa kompatybilności: ``assemble_record(...)`` i ``run(source: dict)``.
    """

    @abstractmethod
    def build_payload(self, input_dto: InputDTO) -> PayloadDTO:
        """Mapuje DTO wejściowe domeny na DTO assemblera."""

    @abstractmethod
    def assemble(self, payload: PayloadDTO) -> OutputRecord:
        """Składa finalny rekord z payloadu assemblera."""

    @abstractmethod
    def _compat_input_from_source(self, source: dict[str, Any]) -> InputDTO:
        """Adapter kompatybilności dla legacy ``run(source: dict)``."""

    def _validate_input(self, input_dto: InputDTO) -> None:
        """Hook walidacyjny dla konkretnych domen."""

    def execute(self, input_dto: InputDTO) -> OutputRecord:
        self._validate_input(input_dto)
        payload = self.build_payload(input_dto)
        assembled = self.with_retry(lambda: self.assemble(payload))
        self.dump_debug_payload(payload=assembled, stem=self.__class__.__name__.lower())
        return assembled

    def assemble_record(self, payload: InputDTO) -> OutputRecord:
        return self.execute(payload)

    def run(self, source: dict[str, Any]) -> OutputRecord:
        return self.execute(self._compat_input_from_source(source))
