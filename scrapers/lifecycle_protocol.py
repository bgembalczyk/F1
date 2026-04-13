from typing import Protocol

from bs4 import BeautifulSoup

from scrapers.protocols.capabilities import ExportCapability
from scrapers.protocols.capabilities import FetchCapability
from scrapers.protocols.capabilities import ValidateCapability
from scrapers.runners.pipeline_runner import RawRecord


class ScraperLifecycleProtocol(
    FetchCapability,
    ValidateCapability,
    ExportCapability,
    Protocol,
):
    def parse(self, soup: BeautifulSoup) -> list[RawRecord]: ...
