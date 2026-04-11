from typing import Protocol

from scrapers.infobox.parsers.bundles.driver import DriverInfoboxComponents


class DriverInfoboxProvider(Protocol):
    def build(
        self,
        *,
        include_urls: bool,
        wikipedia_base: str,
        schema: object,
        logger: object,
    ) -> DriverInfoboxComponents: ...
