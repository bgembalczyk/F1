import re
from typing import Any

from models.records.link import LinkRecord
from models.services import prune_empty
from scrapers.base.error_handler import ErrorHandler
from scrapers.base.helpers.parsing import parse_int_from_text
from scrapers.base.helpers.parsing import parse_number_with_unit
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.base.helpers.text_normalization import split_delimited_text
from scrapers.base.helpers.time import parse_date_text
from scrapers.base.helpers.wiki import is_wikipedia_redlink


class InfoboxTextUtils:
    """Ogólne helpery do pracy na dictach z infoboksa."""

    # ------------------------------
    # Tekst
    # ------------------------------

    # ------------------------------
    # Proste listy / liczby / długości
    # ------------------------------

    def _split_simple_list(self, row: dict[str, Any] | None) -> list[str] | None:
        if not row:
            return None
        text = clean_infobox_text(row.get("text")) or ""
        parts = split_delimited_text(text)
        return parts or None

    def parse_int(self, row: dict[str, Any] | None) -> int | None:
        if not row:
            return None
        text = clean_infobox_text(row.get("text")) or ""
        return ErrorHandler.run_domain_parse(
            lambda: parse_int_from_text(text),
            message=f"Nie udało się sparsować liczby całkowitej: {text!r}.",
            parser_name=self.__class__.__name__,
        )

    def parse_length(
        self,
        row: dict[str, Any] | None,
        *,
        unit: str,
    ) -> float | None:
        if not row:
            return None
        text = clean_infobox_text(row.get("text")) or ""
        return ErrorHandler.run_domain_parse(
            lambda: parse_number_with_unit(text, unit=unit),
            message=f"Nie udało się sparsować długości ({unit}): {text!r}.",
            parser_name=self.__class__.__name__,
        )

    def _parse_dates(self, row: dict[str, Any] | None) -> dict[str, Any] | None:
        """Parsyje daty typu YYYY-MM-DD, YYYY-MM, YYYY i zwraca też listę lat."""
        if not row:
            return None
        text = clean_infobox_text(row.get("text")) or ""
        if not text:
            return None
        parsed = ErrorHandler.run_domain_parse(
            lambda: parse_date_text(text),
            message=f"Nie udało się sparsować daty: {text!r}.",
            parser_name=self.__class__.__name__,
        )
        iso = parsed.iso
        if isinstance(iso, list):
            iso_dates = iso or None
        elif isinstance(iso, str):
            iso_dates = [iso]
        else:
            iso_dates = None

        years = (
            re.findall(r"\b(1[89]\d{2}|20\d{2})\b", parsed.raw or "")
            if parsed.raw
            else None
        )

        return {
            "text": parsed.raw,
            "iso_dates": iso_dates,
            "years": years or None,
        }

    # ------------------------------
    # Linki
    # ------------------------------

    @staticmethod
    def _find_link(
        text: str | None,
        links: list[LinkRecord],
    ) -> LinkRecord | None:
        if not text:
            return None
        wanted = text.strip().lower()
        for link in links:
            link_text = link.get("text", "")
            if link_text and link_text.strip().lower() == wanted:
                return link
        return None

    def _with_link(
        self,
        text: str | None,
        links: list[LinkRecord] | None,
    ) -> dict[str, Any] | None:
        if text is None:
            return None
        link = self._find_link(text, links or [])

        url: str | None = None
        if link:
            candidate = link.get("url")
            # ignorujemy redlinki Wikipedii
            if candidate and not is_wikipedia_redlink(candidate):
                url = candidate

        return {"text": text, "url": url}

    # ------------------------------
    # Czyszczenie None / pustych struktur
    # ------------------------------

    def prune_nulls(self, data: Any) -> Any:
        return prune_empty(
            data,
            drop_empty_lists=True,
            drop_none=True,
            drop_empty_dicts=True,
        )
