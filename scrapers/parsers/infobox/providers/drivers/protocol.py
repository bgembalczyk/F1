from typing import Protocol

from scrapers.parsers.infobox.bundles.driver import DriverInfoboxBundle
from scrapers.parsers.roles import ParsingBundleProvider


class DriverInfoboxProvider(ParsingBundleProvider[DriverInfoboxBundle], Protocol):
    def build(
        self,
        *,
        include_urls: bool,
        wikipedia_base: str,
        schema: object,
        logger: object,
    ) -> DriverInfoboxBundle: ...


# Backward-compatible alias.
DriverInfoboxParserProvider = DriverInfoboxProvider
