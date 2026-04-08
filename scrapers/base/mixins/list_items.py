from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

class ExtractListItemsMixin:
    @staticmethod
    def _extract_list_items(section_fragment: "BeautifulSoup") -> list[dict[str, str]]:
        records = [
            {"text": text}
            for li in section_fragment.select("ul li")
            if (text := li.get_text(" ", strip=True))
        ]
        if records:
            return records
        return [
            {"text": text}
            for li in section_fragment.find_all("li")
            if (text := li.get_text(" ", strip=True))
        ]
