from __future__ import annotations

from scrapers.parsers.infobox.bundles.driver import DriverInfoboxBundle
from scrapers.parsers.roles import ParsingBundleProviderABC


class DriverInfoboxProviderABC(ParsingBundleProviderABC[DriverInfoboxBundle]):
    def build(
        self,
        *,
        include_urls: bool,
        wikipedia_base: str,
        schema: object,
        logger: object,
    ) -> DriverInfoboxBundle: ...

