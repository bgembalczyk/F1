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
