from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Mapping
from typing import Any
from typing import Generic
from typing import TypeVar

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

    def get(self) -> list[T]:
        if callable(self._iterable):
            return list(self._iterable())
        return list(self._iterable)


class MultiIterableSourceAdapter(Generic[T]):
    """Adapter łączący rekordy z wielu iterable/fabryk iterable."""

    def __init__(
        self,
        iterables: Iterable[Iterable[T] | Callable[[], Iterable[T]]],
    ) -> None:
        self._iterables = list(iterables)

    def get(self) -> list[T]:
        records: list[T] = []
        for iterable in self._iterables:
            if callable(iterable):
                records.extend(iterable())
                continue
            records.extend(iterable)
        return records
