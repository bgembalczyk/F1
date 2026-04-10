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
    """Abstrakcyjny kontrakt komponentów wyciągających dane źródłowe."""

    @abstractmethod
    def extract(self, source: InputT) -> OutputT:
        """Wyciąga dane z wejściowego źródła."""


class Parser(ABC, Generic[InputT, OutputT]):
    """Abstrakcyjny kontrakt parserów normalizujących surowe dane."""

    @abstractmethod
    def parse(self, raw: InputT) -> OutputT:
        """Konwertuje surowy format do reprezentacji domenowej."""


class Assembler(ABC, Generic[PayloadT, RecordT]):
    """Abstrakcyjny kontrakt składania końcowego rekordu eksportowego."""

    @abstractmethod
    def assemble(self, payload: PayloadT) -> RecordT:
        """Buduje rekord końcowy na podstawie payloadu."""


class PipelineService(ABC, Generic[InputT, OutputT]):
    """Abstrakcyjny kontrakt orkiestracji pełnego przebiegu pipeline."""

    @abstractmethod
    def run(self, source: InputT) -> OutputT:
        """Uruchamia sekwencję extractor/parser/assembler dla wejścia."""
