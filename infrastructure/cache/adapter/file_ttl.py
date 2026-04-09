from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import TypeVar

T = TypeVar("T")


class FileTtlCacheAdapter(Generic[T], ABC):
    """Abstrakcyjna baza adapterów serializacji wartości cache do/z tekstu."""

    extension: str

    @abstractmethod
    def serialize(self, value: T) -> str:
        """Serializuje wartość do postaci tekstowej."""

    @abstractmethod
    def deserialize(self, raw_text: str) -> T:
        """Deserializuje tekst do docelowego typu."""
