from __future__ import annotations

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.errors import ErrorCategory
from scrapers.errors import ScraperNotFoundError
from scrapers.helpers.html_utils import find_section_elements


class SectionTraversalMixin:
    """Shared section traversal logic for list/table section extraction."""

    def _find_first_in_section(
        self,
        soup: BeautifulSoup,
        *,
        section_id: str | None,
        tags: list[str],
        class_name: str | None = None,
        missing_with_section_msg: str,
        missing_global_msg: str,
    ) -> Tag:
        kwargs = {"class_": class_name} if class_name else {}
        candidate_elements = find_section_elements(soup, section_id, tags, **kwargs)
        if candidate_elements:
            return candidate_elements[0]

        if section_id:
            raise ScraperNotFoundError(
                missing_with_section_msg,
                category=ErrorCategory.PARSE,
            )
        raise ScraperNotFoundError(missing_global_msg)
