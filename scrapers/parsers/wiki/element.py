from __future__ import annotations

from dataclasses import dataclass

from scrapers.adapters.html_elements import HtmlElementParserAdapterSet
from scrapers.adapters.html_elements import HtmlElementParserFactory


@dataclass(frozen=True)
class WikiElementParsers(HtmlElementParserAdapterSet):
    """Backward-compatible alias for element parser bundle used by section parsers."""


def build_default_wiki_element_parsers() -> WikiElementParsers:
    adapters = HtmlElementParserFactory().build()
    return WikiElementParsers(**adapters.__dict__)
