import re
from typing import Any

from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class RoundColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        cell = ctx.cell
        if cell is None:
            return None

        tokens = [
            clean_wiki_text(token, strip_lang_suffix=False, strip_refs=False)
            for token in cell.stripped_strings
        ]
        tokens = [t for t in tokens if t]
        if not tokens:
            return None

        round_link = ctx.links[0] if ctx.links else None
        link_tokens = []
        if round_link and round_link.get("text"):
            link_tokens = clean_wiki_text(
                round_link["text"],
                strip_lang_suffix=False,
                strip_refs=False,
            ).split()

        remaining = list(tokens)
        for token in link_tokens:
            for i, existing in enumerate(remaining):
                if existing == token:
                    remaining.pop(i)
                    break

        result_text = " ".join(remaining).strip()
        result: int | str | None
        if not result_text or result_text == "-":
            result = None
        elif result_text.isdigit():
            result = int(result_text)
        else:
            result = result_text

        return {
            "round": round_link,
            "code": self._round_code(round_link, tokens),
            "result": result,
            "background": self._extract_background(cell),
            "pole_position": self._has_tag(cell, ["b", "strong"]),
            "fastest_lap": self._has_tag(cell, ["i", "em"]),
            "superscript": self._superscript_text(cell),
        }

    @staticmethod
    def _round_code(round_link: dict | None, tokens: list[str]) -> str | None:
        if round_link and round_link.get("text"):
            return clean_wiki_text(round_link["text"]).split()[0]
        if tokens:
            return tokens[0]
        return None

    @staticmethod
    def _extract_background(cell) -> str | None:
        style = cell.get("style") or ""
        if style:
            match = re.search(r"background(?:-color)?\s*:\s*([^;]+)", style, re.I)
            if match:
                return match.group(1).strip()

        bgcolor = cell.get("bgcolor")
        if bgcolor:
            return str(bgcolor).strip()

        return None

    @staticmethod
    def _has_tag(cell, names: list[str]) -> bool:
        return cell.find(names) is not None

    @staticmethod
    def _superscript_text(cell) -> str | None:
        sup_texts = [
            clean_wiki_text(sup.get_text(" ", strip=True))
            for sup in cell.find_all("sup")
        ]
        sup_texts = [t for t in sup_texts if t]
        if not sup_texts:
            return None
        return " ".join(sup_texts)
