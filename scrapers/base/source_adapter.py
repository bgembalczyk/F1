from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Iterable, List, Mapping, TypeVar

T = TypeVar("T")


class SourceAdapter(ABC):
    """Interfejs dostarczania HTML z jasnym kontraktem."""

    @property
    @abstractmethod
    def metadata(self) -> Mapping[str, Any]:
        """Metadane adaptera (np. polityka HTTP, cache)."""
        raise NotImplementedError

    @abstractmethod
    def get(self, url: str) -> str:
        """Zwróć HTML dla wskazanego URL-a."""
        raise NotImplementedError


class IterableSourceAdapter(Generic[T]):
    """Adapter zwracający listę na podstawie przekazanego iterable/fabryki."""

    def __init__(self, iterable: Iterable[T] | Callable[[], Iterable[T]]) -> None:
        self._iterable = iterable

    def get(self) -> List[T]:
        if callable(self._iterable):
            return list(self._iterable())
        return list(self._iterable)
