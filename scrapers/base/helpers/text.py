"""Helpers for selecting richer text entities."""

from typing import Any


def choose_richer_entity(a: Any, b: Any) -> Any:
    """
    Preferuj encję z url; jeśli oba mają url albo oba nie mają,
    wybierz tę z dłuższym textem.
    Obsługuje dict / str / None.
    """
    if not a:
        return b
    if not b:
        return a

    if isinstance(a, dict) and not isinstance(b, dict):
        return a
    if isinstance(b, dict) and not isinstance(a, dict):
        return b

    a_url = a.get("url") if isinstance(a, dict) else None
    b_url = b.get("url") if isinstance(b, dict) else None
    if a_url and not b_url:
        return a
    if b_url and not a_url:
        return b

    a_txt = (a.get("text") if isinstance(a, dict) else str(a or "")).strip()
    b_txt = (b.get("text") if isinstance(b, dict) else str(b or "")).strip()
    return a if len(a_txt) >= len(b_txt) else b
