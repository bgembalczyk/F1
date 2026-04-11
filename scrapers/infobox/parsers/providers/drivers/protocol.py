from typing import Protocol

from scrapers.infobox.parsers.bundles.driver import DriverInfoboxParserBundle
from scrapers.parsers.roles import ParserProvider


class DriverInfoboxParserProvider(ParserProvider[DriverInfoboxParserBundle], Protocol):
    def build(
        self,
        *,
        include_urls: bool,
        wikipedia_base: str,
        schema: object,
        logger: object,
    ) -> DriverInfoboxParserBundle: ...
