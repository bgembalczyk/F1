"""Komponent odpowiedzialny za scalanie nagłówków HTTP."""


class HeaderResolver:
    """Rozwiązuje nagłówki domyślne i per-request."""

    def __init__(self, default_headers: dict[str, str]) -> None:
        self._default_headers = dict(default_headers)

    def resolve(self, headers: dict[str, str] | None = None) -> dict[str, str]:
        merged_headers = dict(self._default_headers)
        if headers:
            merged_headers.update(headers)
        return merged_headers
