from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")
PayloadT = TypeVar("PayloadT")
RecordT = TypeVar("RecordT", bound=dict[str, Any])


class Extractor(ABC, Generic[InputT, OutputT]):
    """Contract for composing data from one or many source payloads."""

    @abstractmethod
    def extract(self, source: InputT) -> OutputT:
        """Compose raw source inputs into extraction-ready payload."""


class Factory(ABC, Generic[PayloadT, RecordT]):
    """Contract for building the canonical domain model/record."""

    @abstractmethod
    def create(self, payload: PayloadT) -> RecordT:
        """Create domain model/record from parsed payload."""


class Scraper(ABC, Generic[InputT, OutputT]):
    """Contract for end-to-end orchestration across extractor/parser/factory."""

    @abstractmethod
    def run(self, source: InputT) -> OutputT:
        """Run complete orchestration flow for a given source."""


class PipelineService(ABC, Generic[InputT, OutputT]):
    """Contract for domain pipeline services exposing execute/run API."""

    @abstractmethod
    def execute(self, input_dto: InputT) -> OutputT:
        """Execute pipeline on typed input DTO."""

    @abstractmethod
    def run(self, source: InputT) -> OutputT:
        """Compatibility entrypoint for pipeline execution."""
