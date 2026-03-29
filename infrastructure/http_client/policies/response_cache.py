from typing import Protocol


class TextCacheProtocol(Protocol):
    """Wspólny kontrakt cache dla wartości tekstowych (get/set)."""

    def get(self, url: str) -> str | None:
        """Zwraca tekst z cache lub None."""

    def set(self, url: str, text: str) -> None:
        """Zapisuje tekst do cache."""


# Alias zachowujący kompatybilność w kodzie HTTP.
ResponseCache = TextCacheProtocol
