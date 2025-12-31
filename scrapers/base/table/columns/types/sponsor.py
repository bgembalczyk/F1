import re
from typing import Any

from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.text_normalization import clean_wiki_text, split_delimited_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class SponsorColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        if not ctx.clean_text and not ctx.links:
            return []

        text = clean_wiki_text(ctx.clean_text or "")
        text = self._normalize_text(text)
        links = normalize_links(ctx.links or [])

        if not text:
            return links

        parts = split_delimited_text(text)
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
    def _parse_part(part: str, links: list[dict[str, Any]]) -> Any | None:
        base_text, params = SponsorColumn._extract_params(part)
        base_text = clean_wiki_text(base_text)
        matched_link = SponsorColumn._find_matching_link(base_text, links)

        if matched_link:
            if matched_link.get("url") is None:
                text = matched_link.get("text") or base_text
                if params:
                    return {"text": text, "params": params}
                return text
            if params:
                return {**matched_link, "params": params}
            return matched_link

        if not base_text:
            base_text = clean_wiki_text(part)
        if not base_text:
            return None
        if params:
            return {"text": base_text, "params": params}
        return base_text

    @staticmethod
    def _extract_params(text: str) -> tuple[str, list[str]]:
        params = []
        for group in re.findall(r"\(([^)]+)\)", text):
            params.extend(split_delimited_text(group))
        base_text = re.sub(r"\s*\([^)]*\)", "", text).strip()
        return base_text, params

    @staticmethod
    def _find_matching_link(
        base_text: str, links: list[dict[str, Any]]
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
            if target.startswith(link_lower) and target[len(link_lower) :].strip(" -–—"):
                continue
            if target.startswith(link_lower):
                if len(link_text) > best_len:
                    best = link
                    best_len = len(link_text)
        return best
