from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from scrapers.base_domain_roles import PipelineService
from scrapers.mixins.pipeline_mixins import DebugDumpMixin
from scrapers.mixins.pipeline_mixins import RetryMixin
from scrapers.mixins.pipeline_mixins import ValidationMixin

PayloadT = TypeVar("PayloadT")


class BaseAssemblerPipelineService(
    PipelineService[dict[str, Any], dict[str, Any]],
    RetryMixin,
    DebugDumpMixin,
    ValidationMixin,
    ABC,
    Generic[PayloadT],
):
    required_fields: tuple[str, ...] = ()

    @abstractmethod
    def _build_payload(self, source: dict[str, Any]) -> PayloadT:
        """Mapuje słownik wejściowy na DTO assemblera."""

    @abstractmethod
    def _assemble(self, payload: PayloadT) -> dict[str, Any]:
        """Deleguje składanie do konkretnego assemblera domenowego."""

    def run(self, source: dict[str, Any]) -> dict[str, Any]:
        self.validate_required(source, self.required_fields)
        payload = self._build_payload(source)
        assembled = self.with_retry(lambda: self._assemble(payload))
        self.dump_debug_payload(payload=assembled, stem=self.__class__.__name__.lower())
        return assembled
