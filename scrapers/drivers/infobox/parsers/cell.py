import re
from typing import Any
from typing import Dict
from typing import List

from bs4 import Tag

from scrapers.base.errors import DomainParseError
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.drivers.infobox.parsers.link_extractor import InfoboxLinkExtractor


class InfoboxCellParser:
    def __init__(self, *, include_urls: bool, link_extractor: InfoboxLinkExtractor) -> None:
        self._include_urls = include_urls
        self._link_extractor = link_extractor

    def parse_cell(self, cell: Tag) -> Dict[str, Any]:
        text = clean_infobox_text(cell.get_text(" ", strip=True))
        payload = {"text": text}
        if self._include_urls:
            payload["links"] = self._link_extractor.extract_links(cell)
        return payload

    def parse_active_years(self, cell: Tag) -> Dict[str, int | None]:
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        return self.parse_year_range(text)

    @staticmethod
    def parse_year_range(text: str) -> Dict[str, int | None]:
        try:
            normalized = clean_infobox_text(text) or ""
            range_match = re.search(r"\b(\d{4})\s*[-–]\s*(\d{2,4})\b", normalized)
            if range_match:
                start = int(range_match.group(1))
                end_text = range_match.group(2)
                if len(end_text) == 2:
                    end = (start // 100) * 100 + int(end_text)
                else:
                    end = int(end_text)
                return {"start": start, "end": end}

            years = [int(value) for value in re.findall(r"\d{4}", normalized)]
            if not years:
                return {"start": None, "end": None}
            start = years[0]
            if "present" in normalized.lower() and len(years) == 1:
                end = None
            elif len(years) > 1:
                end = years[-1]
            else:
                end = start
            return {"start": start, "end": end}
        except (TypeError, ValueError) as exc:
            raise DomainParseError(
                f"Nie udało się sparsować zakresu lat: {text!r}.",
                cause=exc,
            ) from exc

    def parse_teams(self, cell: Tag) -> List[Any]:
        if self._include_urls:
            return self._link_extractor.extract_links(cell)
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        if not text:
            return []
        return [part for part in (p.strip() for p in text.split(",")) if part]

    @staticmethod
    def parse_entries(cell: Tag) -> Dict[str, int | None]:
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        try:
            values = [int(value) for value in re.findall(r"\d+", text)]
        except (TypeError, ValueError) as exc:
            raise DomainParseError(
                f"Nie udało się sparsować wpisów/startów: {text!r}.",
                cause=exc,
            ) from exc
        entries = values[0] if values else None
        starts = values[1] if len(values) > 1 else None
        return {"entries": entries, "starts": starts}

    @staticmethod
    def parse_int_cell(cell: Tag) -> int | None:
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        match = re.search(r"-?\d+", text.replace(",", ""))
        if not match:
            return None
        try:
            return int(match.group(0))
        except (TypeError, ValueError) as exc:
            raise DomainParseError(
                f"Nie udało się sparsować liczby całkowitej: {text!r}.",
                cause=exc,
            ) from exc

    @staticmethod
    def parse_float_cell(cell: Tag) -> float | None:
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        match = re.search(r"-?\d+(?:\.\d+)?", text.replace(",", ""))
        if not match:
            return None
        try:
            return float(match.group(0))
        except (TypeError, ValueError) as exc:
            raise DomainParseError(
                f"Nie udało się sparsować liczby zmiennoprzecinkowej: {text!r}.",
                cause=exc,
            ) from exc

    def parse_car_numbers(self, cell: Tag) -> List[Dict[str, Any]]:
        raw_text = cell.get_text("\n", strip=True) or ""
        if not raw_text:
            return []
        normalized = clean_wiki_text(raw_text, strip_lang_suffix=False)
        normalized = re.sub(r"\band\b", ",", normalized, flags=re.IGNORECASE)
        normalized = normalized.replace("/", ",").replace(";", ",")
        entries: List[Dict[str, Any]] = []
        pattern = re.compile(
            r"(?<!\d)(?P<prefix>No\.?|#|№)?\s*(?P<number>\d+)\s*(?:\((?P<years>[^)]+)\))?",
            re.IGNORECASE,
        )
        for match in pattern.finditer(normalized):
            prefix = match.group("prefix") or ""
            try:
                number = int(match.group("number"))
            except (TypeError, ValueError) as exc:
                raise DomainParseError(
                    f"Nie udało się sparsować numeru samochodu: {raw_text!r}.",
                    cause=exc,
                ) from exc
            if number >= 1900 and not prefix:
                continue
            years_text = match.group("years") or ""
            years = (
                self.parse_year_range(years_text)
                if years_text
                else {"start": None, "end": None}
            )
            entries.append({"number": number, "years": years})
        return entries

    def parse_best_finish(self, cell: Tag) -> Dict[str, Any]:
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        try:
            if " in " in text:
                result_text, season_text = text.split(" in ", 1)
                season = self.parse_year_range(season_text)
            else:
                result_text = text
                season = {"start": None, "end": None}
            return {"result": result_text.strip() or None, "season": season}
        except (TypeError, ValueError) as exc:
            raise DomainParseError(
                f"Nie udało się sparsować najlepszego wyniku: {text!r}.",
                cause=exc,
            ) from exc

    def parse_full_data(self, cell: Tag) -> Dict[str, Any]:
        text = clean_infobox_text(cell.get_text(" ", strip=True))
        payload: Dict[str, Any] = {"text": text}
        if self._include_urls:
            payload["links"] = self._link_extractor.extract_links(cell)

        nested_table = cell.find("table")
        if nested_table:
            payload["table"] = self.parse_nested_table(nested_table)
        return payload

    @staticmethod
    def parse_nested_table(table: Tag) -> Dict[str, Any]:
        rows = table.find_all("tr")
        if not rows:
            return {"headers": [], "rows": []}
        header_cells = rows[0].find_all(["th", "td"])
        headers = [clean_wiki_text(c.get_text(" ", strip=True)) for c in header_cells]
        data_rows: List[List[str]] = []
        for row in rows[1:]:
            cells = [
                clean_wiki_text(c.get_text(" ", strip=True))
                for c in row.find_all(["th", "td"])
            ]
            if cells:
                data_rows.append(cells)
        return {"headers": headers, "rows": data_rows}
