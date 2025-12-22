"""Helpers for normalizing text and filtering language links."""

from __future__ import annotations

import re

_REF_RE = re.compile(r"\[\s*[^]]+\s*]")

_LANG_CODES = {
    "en",
    "es",
    "fr",
    "de",
    "it",
    "pt",
    "pl",
    "ru",
    "cs",
    "sk",
    "hu",
    "ro",
    "bg",
    "sr",
    "hr",
    "sl",
    "nl",
    "sv",
    "no",
    "da",
    "fi",
    "el",
    "tr",
    "ar",
    "he",
    "id",
    "ms",
    "th",
    "vi",
    "ja",
    "ko",
    "zh",
    "uk",
    "ca",
    "eu",
    "gl",
}


def _strip_wiki_refs(text: str) -> str:
    """Usuń przypisy w formacie [1], [note 3], ..."""
    return _REF_RE.sub("", text)


def _normalize_dashes(text: str) -> str:
    """Ujednolić warianty myślników i usuń spacje wokół '-'."""
    t = text.replace("–", "-").replace("—", "-").replace("−", "-")
    return re.sub(r"(?<=\w)\s*-\s*(?=\w)", "-", t)


def _strip_lang_suffix(text: str) -> str:
    """Usuń tokeny językowe na końcu (np. "(es)", " es")."""
    lang_alt = "|".join(sorted(_LANG_CODES, key=len, reverse=True))
    t = text

    while True:
        before = t

        # Usuń tokeny w nawiasach: (es), (fr), etc.
        t = re.sub(rf"\s*\(\s*({lang_alt})\s*\)\s*$", "", t, flags=re.IGNORECASE)
        t = t.strip()

        # Usuń tokeny bez nawiasów: " es", " fr", etc.
        t = re.sub(rf"\s+({lang_alt})\s*$", "", t, flags=re.IGNORECASE)
        t = t.strip()

        if t == before:
            break

    return t


def clean_wiki_text(
    text: str,
    *,
    strip_lang_suffix: bool = True,
    strip_refs: bool = True,
    normalize_dashes: bool = True,
) -> str:
    """Normalizuje whitespace oraz opcjonalnie usuwa przypisy i markery językowe."""
    t = (text or "").replace("\xa0", " ").replace("&nbsp;", " ")
    if strip_refs:
        t = _strip_wiki_refs(t)
    t = re.sub(r"\s+", " ", t).strip()
    if normalize_dashes:
        t = _normalize_dashes(t)
    if strip_lang_suffix:
        t = _strip_lang_suffix(t)
    return t


def is_language_link(text: str | None, url: str | None) -> bool:
    """Zwraca True dla linków językowych typu 'fr' -> fr.wikipedia.org."""
    txt = (text or "").strip().lower()
    url_l = (url or "").strip().lower()
    if not txt or not url_l:
        return False

    if txt not in _LANG_CODES:
        return False

    if f"://{txt}.wikipedia.org/" in url_l:
        return True

    if ".wikipedia.org/" in url_l or ".wikimedia.org/" in url_l:
        return True

    return False
