from __future__ import annotations

from scrapers.parsers.infobox.bundles.driver_infobox_bundle import DriverInfoboxBundle
from scrapers.parsers.contracts.parsing_bundle_provider_abc import ParsingBundleProviderABC


class DriverInfoboxProviderABC(ParsingBundleProviderABC[DriverInfoboxBundle]):
    def build(
        self,
        *,
        include_urls: bool,
        wikipedia_base: str,
        schema: object,
        logger: object,
    ) -> DriverInfoboxBundle: ...

