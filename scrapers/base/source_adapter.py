from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Iterable, List, Optional, TypeVar

T = TypeVar("T")


class SourceAdapter(ABC, Generic[T]):
    """Interfejs dostarczania danych wejściowych dla scraperów."""

    @abstractmethod
    def get(self, source: Optional[str] = None, **kwargs: Any) -> T:
        """Zwróć dane wejściowe na podstawie źródła."""
        raise NotImplementedError


class IterableSourceAdapter(SourceAdapter[List[T]]):
    """Adapter zwracający listę na podstawie przekazanego iterable/fabryki."""

    def __init__(self, iterable: Iterable[T] | Callable[[], Iterable[T]]) -> None:
        self._iterable = iterable

    def get(self, source: Optional[str] = None, **kwargs: Any) -> List[T]:
        if callable(self._iterable):
            return list(self._iterable())
        return list(self._iterable)
