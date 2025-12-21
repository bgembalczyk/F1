from __future__ import annotations

import re

# przypisy Wikipedii: [1], [b], [note 3], [citation needed], ...
_REF_RE = re.compile(r"\[\s*[^]]+\s*]")


def clean_wiki_text(text: str) -> str:
    """
    Normalizacja whitespace + usunięcie przypisów Wikipedii.
    """
    t = text.replace("\xa0", " ").replace("&nbsp;", " ")
    t = _REF_RE.sub("", t)
    return t.strip()


def strip_marks(text: str | None) -> str | None:
    if text is None:
        return None
    # typowe znaki w tabelach F1
    return (
        text.replace("*", "")
        .replace("†", "")
        .replace("‡", "")
        .replace("✝", "")
        .replace("✚", "")
        .replace("~", "")
        .replace("^", "")
        .strip()
    )
