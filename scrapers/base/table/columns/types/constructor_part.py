import re

from models.records.link import LinkRecord
from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.base.table.columns.types.func import FuncColumn


class ConstructorPartColumn(FuncColumn):
    def __init__(self, index: int) -> None:
        super().__init__(lambda ctx: _extract_constructor_part(ctx, index))


def _extract_constructor_part(ctx, index: int) -> LinkRecord | None:
    links = normalize_links(ctx.links, strip_marks=True, drop_empty=True)
    clean_text = clean_wiki_text(ctx.clean_text or "")

    split_parts = _split_on_external_hyphen(ctx)
    if split_parts:
        left_part, right_part = split_parts
        if links:
            if index == 0:
                left_normalized = clean_wiki_text(left_part)
                for link in links:
                    if clean_wiki_text(link.get("text", "")) == left_normalized:
                        return link
                return {"text": left_part, "url": None}
            right_normalized = clean_wiki_text(right_part)
            for link in links:
                if clean_wiki_text(link.get("text", "")) == right_normalized:
                    return link
            return {"text": right_part, "url": None}
        return {"text": left_part if index == 0 else right_part, "url": None}

    if links:
        if len(links) >= 2:
            return links[index] if index < len(links) else None
        return links[0]

    if not clean_text:
        return None

    return {"text": clean_text, "url": None}


def _split_on_external_hyphen(ctx) -> tuple[str, str] | None:
    raw_text = clean_wiki_text(ctx.raw_text or "", normalize_dashes=False)
    match = re.search(r"\s[-–—−]\s", raw_text)
    if not match:
        return None
    left_part = raw_text[: match.start()].strip()
    right_part = raw_text[match.end() :].strip()
    if not left_part or not right_part:
        return None
    return left_part, right_part
