import re
from typing import Any

from bs4 import NavigableString
from bs4 import Tag

from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.sponsorship_liveries.parsers.record_text import SponsorshipRecordText


class SponsorColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        if not ctx.clean_text and not ctx.links:
            return []

        if ctx.cell is not None and ctx.cell.find("p", recursive=False):
            text = clean_wiki_text(self._get_text_with_paragraph_breaks(ctx.cell))
        else:
            text = clean_wiki_text(ctx.clean_text or "")
        text = self._normalize_text(text)
        links = normalize_links(ctx.links or [])

        if not text:
            return links

        parts = self._split_parts(text)
        if not parts:
            return links or []

        results: list[Any] = []
        for part in parts:
            item = self._parse_part(part, links)
            if item is None:
                continue
            results.append(item)
        return results

    @staticmethod
    def _normalize_text(text: str) -> str:
        text = re.sub(r",\s*and\s+", ", ", text, flags=re.IGNORECASE)
        text = re.sub(r"\s+and\s+", ", ", text, flags=re.IGNORECASE)
        text = re.sub(r"^\s*and\s+", "", text, flags=re.IGNORECASE)
        return text

    @staticmethod
    def _split_on_major_separators(text: str) -> list[str]:
        """Split text on ',' and ';' at depth 0 (not on '/')."""
        if not text:
            return []
        parts: list[str] = []
        current: list[str] = []
        depth = 0
        for char in text:
            if char == "(":
                depth += 1
            elif char == ")":
                depth = max(depth - 1, 0)
            if depth == 0 and char in {",", ";"}:
                part = "".join(current).strip()
                if part:
                    parts.append(part)
                current = []
                continue
            current.append(char)
        part = "".join(current).strip()
        if part:
            parts.append(part)
        return parts

    @staticmethod
    def _split_slash_with_propagation(group: str) -> list[str]:
        """Split a '/' group and propagate trailing year params to all sub-items.

        When Wikipedia lists related entities as "Honda / HRC (2026)", the year
        annotation "(2026)" applies to every item in the '/' group, not only the
        last one.  This method detects that pattern and rewrites the sub-items so
        that each carries the shared year annotation before they are processed
        individually by :meth:`_parse_part`.

        Examples::

            "Honda / HRC (2026)"   →  ["Honda (2026)", "HRC (2026)"]
            "A / B"                →  ["A", "B"]          (no year to propagate)
            "A (2021) / B (2025)"  →  ["A (2021)", "B (2025)"]  (each has own)
        """
        # Split on "/" at depth 0
        sub_parts: list[str] = []
        current: list[str] = []
        depth = 0
        for char in group:
            if char == "(":
                depth += 1
            elif char == ")":
                depth = max(depth - 1, 0)
            if depth == 0 and char == "/":
                part = "".join(current).strip()
                if part:
                    sub_parts.append(part)
                current = []
                continue
            current.append(char)
        part = "".join(current).strip()
        if part:
            sub_parts.append(part)

        if len(sub_parts) <= 1:
            return sub_parts

        # Extract year-only params from the LAST sub-part
        _, last_params = SponsorColumn._extract_params(sub_parts[-1])
        year_params = [p for p in last_params if SponsorshipRecordText.is_year_param(p)]
        if not year_params:
            return sub_parts

        # Build the year annotation suffix, e.g. " (2026)" or " (2022–2025)".
        # _extract_params returns params as plain strings (list[str]), so
        # param_text() is used for forward-compatible string extraction.
        year_suffix = (
            " (" + ", ".join(SponsorshipRecordText.param_text(p) for p in year_params) + ")"
        )

        # Propagate to sub-parts that do not already carry year params
        result: list[str] = []
        for sub in sub_parts:
            _, sub_params = SponsorColumn._extract_params(sub)
            sub_year_params = [
                p for p in sub_params if SponsorshipRecordText.is_year_param(p)
            ]
            if not sub_year_params:
                result.append(sub + year_suffix)
            else:
                result.append(sub)
        return result

    @staticmethod
    def _split_parts(text: str) -> list[str]:
        if not text:
            return []
        major_parts = SponsorColumn._split_on_major_separators(text)
        result: list[str] = []
        for part in major_parts:
            result.extend(SponsorColumn._split_slash_with_propagation(part))
        return result

    @staticmethod
    def _parse_part(part: str, links: list[dict[str, Any]]) -> Any | None:
        base_text, params = SponsorColumn._extract_params(part)
        base_text = clean_wiki_text(base_text)
        matched_link = SponsorColumn._find_matching_link(base_text, links)
        link_pool = [
            link
            for link in links
            if not matched_link or link.get("url") != matched_link.get("url")
        ]
        parsed_params = SponsorColumn._parse_params(params, link_pool)

        if matched_link:
            if matched_link.get("url") is None:
                text = matched_link.get("text") or base_text
                if parsed_params:
                    return {"text": text, "params": parsed_params}
                return text
            if parsed_params:
                return {**matched_link, "params": parsed_params}
            return matched_link

        if not base_text:
            base_text = clean_wiki_text(part)
        if not base_text:
            return None
        if parsed_params:
            return {"text": base_text, "params": parsed_params}
        return base_text

    @staticmethod
    def _extract_params(text: str) -> tuple[str, list[str]]:
        params = []
        for group in re.findall(r"\(([^)]+)\)", text):
            params.extend(SponsorColumn._split_parts(group))
        base_text = re.sub(r"\s*\([^)]*\)", "", text).strip()
        return base_text, params

    @staticmethod
    def _parse_params(
            params: list[str], links: list[dict[str, Any]],
    ) -> list[str | dict[str, Any]]:
        if not params:
            return []
        results: list[str | dict[str, Any]] = []
        for param in params:
            cleaned = clean_wiki_text(param)
            if not cleaned:
                continue
            match_text = SponsorColumn._normalize_param_match_text(cleaned)
            matched_link = SponsorColumn._find_matching_link(match_text, links)
            if matched_link and matched_link.get("url"):
                results.append({"text": cleaned, "url": matched_link["url"]})
            else:
                results.append(cleaned)
        return results

    @staticmethod
    def _normalize_param_match_text(text: str) -> str:
        text = re.sub(r"\b(only|onwards?)\b", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^\s*from\s+", "", text, flags=re.IGNORECASE)
        return text.strip()

    @staticmethod
    def _find_matching_link(
            base_text: str, links: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        if not base_text:
            return None
        target = base_text.lower()
        best: dict[str, Any] | None = None
        best_len = 0
        for link in links:
            link_text = clean_wiki_text(link.get("text") or "")
            if not link_text:
                continue
            link_lower = link_text.lower()
            if target == link_lower:
                if len(link_text) > best_len:
                    best = link
                    best_len = len(link_text)
                continue
            if target.startswith(link_lower) and target[len(link_lower):].strip(
                    " -–—",
            ):
                continue
            if target.startswith(link_lower):
                if len(link_text) > best_len:
                    best = link
                    best_len = len(link_text)
        return best

    @staticmethod
    def _get_text_with_paragraph_breaks(cell: Tag) -> str:
        """Extract text from a cell, treating direct <p> children as comma-separated entries."""
        parts: list[str] = []
        current: list[str] = []
        for child in cell.children:
            if getattr(child, "name", None) == "p":
                pre_text = " ".join(current).strip()
                if pre_text:
                    parts.append(pre_text)
                current = []
                assert isinstance(child, Tag)
                p_text = child.get_text(" ", strip=True)
                if p_text:
                    parts.append(p_text)
            elif isinstance(child, Tag):
                t = child.get_text(" ", strip=True)
                if t:
                    current.append(t)
            elif isinstance(child, NavigableString):
                t = str(child).strip()
                if t:
                    current.append(t)
        remaining = " ".join(current).strip()
        if remaining:
            parts.append(remaining)
        return ", ".join(parts)
