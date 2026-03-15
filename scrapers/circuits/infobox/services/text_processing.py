import re
from typing import Any

from scrapers.base.helpers.text import choose_richer_entity
from scrapers.circuits.infobox.services.text_utils import InfoboxTextUtils


class CircuitTextProcessing(InfoboxTextUtils):
    """Czyszczenie i normalizacja tekstu, konwersja czasów, wybór bogatszych encji."""

    # tylko markery językowe w nawiasie: (es), ( de ), (it)
    _LANG_PAREN_RE = re.compile(r"\(\s*[a-z]{2,3}\s*\)$", flags=re.IGNORECASE)
    _LANG_PAREN_ANYWHERE_RE = re.compile(r"\(\s*[a-z]{2,3}\s*\)", flags=re.IGNORECASE)

    # do czyszczenia uciętych markerów typu "( es" / "( cs"
    _LANG_PAREN_TAIL_RE = re.compile(r"\(\s*[a-z]{2,3}\s*\)?\s*$", flags=re.IGNORECASE)

    @staticmethod
    def _entity_text(val: Any) -> str | None:
        if isinstance(val, dict):
            s = (val.get("text") or "").strip()
            return s or None
        if val is None:
            return None
        s = str(val).strip()
        return s or None

    @staticmethod
    def _entity_url(val: Any) -> str | None:
        if isinstance(val, dict):
            return val.get("url") or None
        return None

    @staticmethod
    def _norm_time(t: Any) -> str | None:
        """
        Normalizuje time do stringa (dla prezentacji).
        Uwaga: do porównań/scalania używamy _time_to_seconds.
        """
        if t is None:
            return None
        if isinstance(t, int | float):
            return f"{float(t):.6f}".rstrip("0").rstrip(".")
        s = str(t).strip()
        return s or None

    @staticmethod
    def _get_vehicle_field(rec: dict[str, Any]) -> Any:
        return rec.get("vehicle") or rec.get("car")

    @staticmethod
    def _get_class_field(rec: dict[str, Any]) -> Any:
        # traktujemy category/class/series jako to samo semantycznie
        return rec.get("series") or rec.get("category") or rec.get("class")

    def _strip_lang_markers(self, s: str) -> str:
        """
        Usuwa tylko śmieciowe markery językowe:
        - '(es)' '( de )' '(it)' itp. (również w środku tekstu, gdy psują parsing)
        Nie dotyka normalnych nawiasów: '(motorcyclist)'.
        """
        s = (s or "").replace("\xa0", " ").strip()
        s = self._LANG_PAREN_ANYWHERE_RE.sub("", s)
        return re.sub(r"\s+", " ", s).strip()

    def _strip_lang_marker_tail_only(self, s: str) -> str:
        """
        Usuwa ucięte markery na końcu:
        - "Juan Martín Trucco ( es" -> "Juan Martín Trucco"
        - "David Vršecký ( cs" -> "David Vršecký"
        """
        s = (s or "").replace("\xa0", " ").strip()
        s = self._LANG_PAREN_TAIL_RE.sub("", s).strip()
        return re.sub(r"\s+", " ", s).strip()

    def _norm_text_for_key(self, x: Any) -> str:
        if isinstance(x, dict):
            x = x.get("text") or ""
        return self._strip_lang_marker_tail_only(str(x or "")).strip().lower()

    @staticmethod
    def _extract_outer_parens(text: str) -> str | None:
        """
        Zwraca zawartość pierwszego zewnętrznego nawiasu (...) z uwzględnieniem
        zagnieżdżeń w środku.
        """
        if not text:
            return None
        start = text.find("(")
        if start < 0:
            return None

        depth = 0
        inner_start: int | None = None

        for i in range(start, len(text)):
            ch = text[i]
            if ch == "(":
                depth += 1
                if depth == 1:
                    inner_start = i + 1
            elif ch == ")":
                if depth == 1 and inner_start is not None:
                    return text[inner_start:i]
                depth = max(depth - 1, 0)

        return None

    @staticmethod
    def _is_en_wiki(url: str | None) -> bool:
        if not url:
            return False
        return url.startswith(("https://en.wikipedia.org/", "http://en.wikipedia.org/"))

    def _choose_richer_entity(self, a: Any, b: Any) -> Any:
        return choose_richer_entity(a, b)
