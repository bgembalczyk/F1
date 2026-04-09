from abc import ABC
from abc import abstractmethod
from typing import Any


class RecordAssemblyStrategy(ABC):
    """Jawnie typowana strategia składania rekordu listy i szczegółów."""

    @abstractmethod
    def assemble(
        self,
        record: dict[str, Any],
        details: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Zwróć rekord wynikowy zbudowany z danych listy i szczegółów."""
