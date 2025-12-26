"""Helpers for normalizing text and filtering language links."""

import re
from typing import Any

# Centralne miejsce do usuwania przypisów wiki - nie duplikuj regexu w scraperach.
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


def clean_infobox_text(text: Any) -> str | None:
    """Czyści tekst z infoboxa i zwraca None dla pustych wartości."""
    if not isinstance(text, str):
        return None
    cleaned = clean_wiki_text(text, strip_lang_suffix=False)
    return cleaned or None


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

    if f"{txt}.wikipedia.org" in url_l:
        return True

    if f"wikipedia.org/{txt}/" in url_l:
        return True

    if ".wikipedia.org/" in url_l or ".wikimedia.org/" in url_l:
        return True

    return False


def normalize_text(obj: Any) -> str:
    """Bezpieczna konwersja obiektu do znormalizowanego tekstu (lowercase, stripped)."""
    if isinstance(obj, dict):
        return (obj.get("text") or "").strip().lower()
    if obj is None:
        return ""
    return str(obj).strip().lower()


def add_unique_name(
    names_set: set[str], name_list: list[str], value: str | None
) -> None:
    """Dodaje nazwę do listy nazw, unikając duplikatów."""
    if not value:
        return
    value = value.strip()
    if value and value not in names_set:
        names_set.add(value)
        name_list.append(value)


# ============================================================================
# Driver & Vehicle Matching
# ============================================================================


def normalize_driver_text(obj: Any) -> str:
    """Normalizuje tekst kierowcy: usuwa dopiski w nawiasach i zbędne spacje."""
    s = normalize_text(obj)
    if not s:
        return ""
    s = re.sub(r"\s*\([^)]*\)\s*", " ", s)
    return " ".join(s.split())


def match_driver_loose(a: Any, b: Any, *, min_len: int = 4) -> bool:
    """Porównuje kierowców z tolerancją na przedrostki i sufiksy."""
    da = normalize_driver_text(a)
    db = normalize_driver_text(b)
    if not da or not db:
        return False
    if len(da) < min_len or len(db) < min_len:
        return False
    return (
        da == db or da.startswith(db) or db.startswith(da) or (da in db) or (db in da)
    )


def normalize_vehicle_text(v: Any) -> str:
    """Normalizuje tekst pojazdu."""
    if isinstance(v, dict):
        v = v.get("text") or ""
    s = str(v or "").strip().lower()
    return " ".join(s.split())


def match_vehicle_prefix(a: Any, b: Any, *, min_len: int = 10) -> bool:
    """Porównuje pojazdy na podstawie prefiksu."""
    va = normalize_vehicle_text(a)
    vb = normalize_vehicle_text(b)
    if not va or not vb:
        return False
    if len(va) < min_len or len(vb) < min_len:
        return False
    return va.startswith(vb) or vb.startswith(va)


# ============================================================================
# Text Parsing
# ============================================================================


def split_delimited_text(
    text: str | None, *, separators: str = r";|,|/", min_parts: int = 1
) -> list[str]:
    """Split text by common delimiters and trim whitespace.

    Returns an empty list for falsy input or when the number of non-empty parts is
    below ``min_parts``.
    """
    if not text:
        return []

    parts = [p.strip() for p in re.split(separators, text) if p.strip()]
    return parts if len(parts) >= min_parts else []
