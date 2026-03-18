import re
from typing import Any

from bs4 import BeautifulSoup
from bs4 import NavigableString
from bs4 import Tag

from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.helpers.url import normalize_url
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.sponsorship_liveries.parsers.grand_prix_scope import GrandPrixScopeParser
from scrapers.sponsorship_liveries.parsers.parts import SponsorPartsParser
from scrapers.sponsorship_liveries.parsers.record_text import SponsorshipRecordText


class SponsorColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        if not ctx.clean_text and not ctx.links:
            return []

        if ctx.cell is not None and ctx.cell.find("br"):
            return self._parse_br_cell(ctx)

        if ctx.cell is not None and ctx.cell.find("p", recursive=False):
            text = clean_wiki_text(self._get_text_with_paragraph_breaks(ctx.cell))
        else:
            text = clean_wiki_text(ctx.clean_text or "")

        links = normalize_links(ctx.links or [])
        return self._parse_text_with_links(text, links)

    def _parse_br_cell(self, ctx: ColumnContext) -> list[Any]:
        """Process a sponsor cell whose entries are separated by <br> elements.

        Each <br>-delimited segment is parsed independently.  A trailing
        grand-prix-scope parenthetical at the end of a segment is propagated
        to every item within that segment so that, e.g.,
        "Alpquell, Elan, Raiffeisen (Austrian GP only)" correctly scopes all
        three sponsors to the Austrian GP.
        """
        results: list[Any] = []
        for seg_nodes in self._split_cell_by_br(ctx.cell):
            results.extend(self._parse_br_segment(seg_nodes, ctx.base_url))
        return results

    def _parse_br_segment(self, seg_nodes: list[Any], base_url: str) -> list[Any]:
        seg_html = "".join(str(node) for node in seg_nodes)
        seg_soup = BeautifulSoup(seg_html, "html.parser")
        seg_text = clean_wiki_text(seg_soup.get_text(" ", strip=True))
        seg_links = normalize_links(
            seg_soup,
            full_url=lambda href: normalize_url(base_url, href),
            drop_empty_text=True,
        )
        return self._propagate_segment_scope(
            self._parse_text_with_links(seg_text, seg_links),
        )

    def _parse_text_with_links(
        self,
        text: str,
        links: list[dict[str, Any]],
    ) -> list[Any]:
        """Core parsing: split *text* into sponsor entries using *links* for URL lookup.

        Slashes that are part of a link text (e.g. "RE/MAX") are protected
        before splitting so they are not treated as list separators.
        """
        text = self._normalize_text(clean_wiki_text(text))
        links = normalize_links(links)

        if not text:
            return links

        text, slash_replacements = self._protect_link_slashes(text, links)
        parts_with_sep = self._split_parts_with_sep(text)
        if not parts_with_sep:
            return links or []

        parts_with_sep = [
            (self._restore_link_slashes(p, slash_replacements), s)
            for p, s in parts_with_sep
        ]

        return self._parse_parts_grouped_by_slash(parts_with_sep, links)

    def _parse_parts_grouped_by_slash(
        self,
        parts_with_sep: list[tuple[str, str]],
        links: list[dict[str, Any]],
    ) -> list[Any]:
        results: list[Any] = []
        slash_group: list[str] = []

        for part, sep in parts_with_sep:
            slash_group.append(part)
            if sep != "/":
                self._flush_slash_group(results, slash_group, links)
        self._flush_slash_group(results, slash_group, links)
        return results

    def _flush_slash_group(
        self,
        results: list[Any],
        slash_group: list[str],
        links: list[dict[str, Any]],
    ) -> None:
        if not slash_group:
            return
        parsed = [self._parse_part(p, links) for p in slash_group]
        if len(slash_group) > 1:
            parsed = self._propagate_slash_group_year_params(parsed)
        results.extend(item for item in parsed if item is not None)
        slash_group.clear()

    @staticmethod
    def _split_cell_by_br(cell: Tag) -> list[list[Any]]:
        """Split the direct children of *cell* at every <br> element.

        Returns a list of segments, where each segment is the list of child
        nodes (Tags and NavigableStrings) between two consecutive <br> tags.
        """
        segments: list[list[Any]] = []
        current: list[Any] = []
        for child in cell.children:
            if isinstance(child, Tag) and child.name == "br":
                if current:
                    segments.append(current)
                current = []
            else:
                current.append(child)
        if current:
            segments.append(current)
        return segments

    @staticmethod
    def _propagate_segment_scope(items: list[Any]) -> list[Any]:
        """Propagate a trailing grand-prix-scope from the last item to all others.

        When a <br> segment contains multiple comma-separated sponsors followed
        by a single shared grand-prix parenthetical (e.g.
        "Alpquell, Elan, Raiffeisen (Austrian GP only)"), only the last item
        gets the scope after regular parsing.  This method copies those scope
        params onto every item that does not yet have any params.
        """
        if not items:
            return items

        last = items[-1]
        trailing_scope_params = None
        if isinstance(last, dict) and last.get("params"):
            if GrandPrixScopeParser.parse_grand_prix_scope(last["params"]):
                trailing_scope_params = last["params"]

        if trailing_scope_params is None:
            return items

        result: list[Any] = []
        for item in items:
            if isinstance(item, dict) and "params" in item:
                result.append(item)
            elif isinstance(item, dict):
                result.append({**item, "params": trailing_scope_params})
            elif isinstance(item, str):
                result.append({"text": item, "params": trailing_scope_params})
            else:
                result.append(item)
        return result

    @staticmethod
    def _protect_link_slashes(
        text: str,
        links: list[dict[str, Any]],
    ) -> tuple[str, list[tuple[str, str]]]:
        """Replace '/' and ',' inside known link texts with a placeholder.

        This prevents ``_split_parts_with_sep`` from treating a slash or comma
        that is part of a linked name (e.g. "RE/MAX", "CA, Inc.") as a list
        separator.

        Returns the modified *text* and the list of ``(placeholder, original)``
        pairs needed to restore the originals afterwards.
        """
        replacements: list[tuple[str, str]] = []
        for link in links:
            link_text = clean_wiki_text(link.get("text") or "")
            if ("/" in link_text or "," in link_text) and link_text in text:
                placeholder = f"\x00{len(replacements)}\x00"
                replacements.append((placeholder, link_text))
                text = text.replace(link_text, placeholder)
        return text, replacements

    @staticmethod
    def _restore_link_slashes(
        text: str,
        replacements: list[tuple[str, str]],
    ) -> str:
        """Undo the placeholder substitutions made by :meth:`_protect_link_slashes`."""
        for placeholder, original in replacements:
            text = text.replace(placeholder, original)
        return text

    @staticmethod
    def _normalize_text(text: str) -> str:
        text = re.sub(r",\s*and\s+", ", ", text, flags=re.IGNORECASE)
        text = re.sub(r"\s+and\s+", ", ", text, flags=re.IGNORECASE)
        return re.sub(r"^\s*and\s+", "", text, flags=re.IGNORECASE)

    @staticmethod
    def _split_parts_with_sep(text: str) -> list[tuple[str, str]]:
        """Split text into (part, separator_after) tuples.

        separator_after is one of ',', ';', '/' or '' for the last part.

        In addition to the explicit separators, an implicit split is emitted
        after a closing ')' at depth 0 when the next non-whitespace character
        starts a new token.
        """
        if not text:
            return []
        parser = SponsorPartsParser(text)
        return parser.parse()

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
                p for p in item_params if SponsorshipRecordText.is_year_param(p)
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
    def _parse_part(
        part: str,
        links: list[dict[str, Any]],
    ) -> Any | None:
        base_text, params = SponsorColumn._extract_params(part)
        base_text = clean_wiki_text(base_text)
        matched_link = SponsorColumn._find_matching_link(base_text, links)
        link_pool = [
            link
            for link in links
            if not matched_link or link.get("url") != matched_link.get("url")
        ]
        parsed_params = SponsorColumn._parse_params(params, link_pool)

        result: Any | None
        if matched_link:
            if matched_link.get("url") is None:
                text = matched_link.get("text") or base_text
                result = (
                    {"text": text, "params": parsed_params} if parsed_params else text
                )
            else:
                result = (
                    {**matched_link, "params": parsed_params}
                    if parsed_params
                    else matched_link
                )
        else:
            if not base_text:
                base_text = clean_wiki_text(part)
            if not base_text:
                result = None
            else:
                result = (
                    {"text": base_text, "params": parsed_params}
                    if parsed_params
                    else base_text
                )
        return result

    @staticmethod
    def _extract_params(text: str) -> tuple[str, list[str]]:
        params = []
        for group in re.findall(r"\(([^)]+)\)", text):
            params.extend(SponsorColumn._split_parts(group))
        base_text = re.sub(r"\s*\([^)]*\)", "", text).strip()
        return base_text, params

    @staticmethod
    def _parse_params(
        params: list[str],
        links: list[dict[str, Any]],
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
        base_text: str,
        links: list[dict[str, Any]],
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
            remainder = target[len(link_lower) :]
            if target.startswith(link_lower) and re.sub(r"[\s\-—]", "", remainder):
                continue
            if target.startswith(link_lower):
                if len(link_text) > best_len:
                    best = link
                    best_len = len(link_text)
        return best

    @staticmethod
    def _get_text_with_paragraph_breaks(cell: Tag) -> str:
        """Extract text from a cell.

        Treat direct <p> children as comma-separated entries.
        """
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
