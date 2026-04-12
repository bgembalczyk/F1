from abc import ABC
from abc import abstractmethod
from typing import Generic

from bs4 import BeautifulSoup

from scrapers.parsers.html_elements.base_html_element_parser import TOutput


class BaseHtmlSectionParser(ABC, Generic[TOutput]):
    """Base contract for document/section parsers.

    Document/section parsers are the only parsers that can accept BeautifulSoup.
    """

    @abstractmethod
    def parse(self, soup: BeautifulSoup) -> TOutput: ...
