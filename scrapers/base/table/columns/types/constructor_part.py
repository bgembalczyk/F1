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

    if links:
        if "-" in clean_text and len(links) >= 2:
            return links[index] if index < len(links) else None
        if len(links) >= 2:
            return links[index] if index < len(links) else None
        return links[0]

    if not clean_text:
        return None

    if "-" in clean_text:
        parts = [part.strip() for part in clean_text.split("-", 1)]
        if len(parts) == 2:
            return {"text": parts[index] if index < len(parts) else parts[0], "url": None}

    return {"text": clean_text, "url": None}


