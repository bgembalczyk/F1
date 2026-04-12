from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

BundleT_co = TypeVar("BundleT_co", bound="ParsingBundle", covariant=True)


class ParsingBundle(ABC):
    """Kompozycja parserów i komponentów pomocniczych."""


class ParsingBundleProviderABC(ABC, Generic[BundleT_co]):
    @abstractmethod
    def build(self, **kwargs: Any) -> BundleT_co: ...


__all__ = ["BundleT_co", "ParsingBundle", "ParsingBundleProviderABC"]
