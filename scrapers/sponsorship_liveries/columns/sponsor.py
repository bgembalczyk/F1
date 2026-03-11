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

        parts_with_sep = self._split_parts_with_sep(text)
        if not parts_with_sep:
            return links or []

        results: list[Any] = []
        slash_group: list[str] = []

        def flush_slash_group() -> None:
            if not slash_group:
                return
            parsed = [self._parse_part(p, links) for p in slash_group]
            if len(slash_group) > 1:
                parsed = self._propagate_slash_group_year_params(parsed)
            for item in parsed:
                if item is not None:
                    results.append(item)
            slash_group.clear()

        for part, sep in parts_with_sep:
            slash_group.append(part)
            if sep != "/":
                flush_slash_group()
        flush_slash_group()

        return results

    @staticmethod
    def _normalize_text(text: str) -> str:
        text = re.sub(r",\s*and\s+", ", ", text, flags=re.IGNORECASE)
        text = re.sub(r"\s+and\s+", ", ", text, flags=re.IGNORECASE)
        text = re.sub(r"^\s*and\s+", "", text, flags=re.IGNORECASE)
        return text

    @staticmethod
    def _split_parts_with_sep(text: str) -> list[tuple[str, str]]:
        """Split text into (part, separator_after) tuples.

        separator_after is one of ',', ';', '/' or '' for the last part.
        """
        if not text:
            return []
        parts: list[tuple[str, str]] = []
        current: list[str] = []
        depth = 0
        for char in text:
            if char == "(":
                depth += 1
            elif char == ")":
                depth = max(depth - 1, 0)
            if depth == 0 and char in {",", ";", "/"}:
                part = "".join(current).strip()
                if part:
                    parts.append((part, char))
                current = []
                continue
            current.append(char)
        part = "".join(current).strip()
        if part:
            parts.append((part, ""))
        return parts

    @staticmethod
    def _propagate_slash_group_year_params(
            parsed: list[Any],
    ) -> list[Any]:
        """For items split by '/', propagate year params to items that lack them."""
        year_params: list[Any] = []
        for item in parsed:
            if not isinstance(item, dict):
                continue
            item_params = item.get("params") or []
            item_year_params = [
                p for p in item_params
                if SponsorshipRecordText.is_year_param(p)
            ]
            # Only propagate when all params on this item are year params,
            # to avoid accidentally propagating Grand Prix scope params.
            if item_year_params and len(item_year_params) == len(item_params):
                year_params = item_year_params
                break
        if not year_params:
            return parsed
        result: list[Any] = []
        for item in parsed:
            if item is None:
                result.append(item)
            elif isinstance(item, dict) and "params" not in item:
                result.append({**item, "params": year_params})
            elif isinstance(item, str):
                result.append({"text": item, "params": year_params})
            else:
                result.append(item)
        return result

    @staticmethod
    def _split_parts(text: str) -> list[str]:
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
            if depth == 0 and char in {",", ";", "/"}:
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
