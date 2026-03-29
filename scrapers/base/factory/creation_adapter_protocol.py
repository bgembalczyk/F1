from typing import Protocol

from scrapers.base.abc import ABCScraper
from scrapers.base.factory.constructor_introspection import ConstructorIntrospection
from scrapers.base.factory.creation_context import ScraperCreationContext


class ScraperCreationAdapterProtocol(Protocol):
    def supports(self, ctor: ConstructorIntrospection) -> bool: ...

    def create(
        self,
        *,
        context: ScraperCreationContext,
        ctor: ConstructorIntrospection,
    ) -> ABCScraper: ...
