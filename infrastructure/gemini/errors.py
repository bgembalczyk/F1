"""Wyjątki domenowe dla klienta Gemini."""


class GeminiError(Exception):
    """Bazowy wyjątek dla błędów klienta Gemini."""


class GeminiTransportError(GeminiError):
    """Błąd warstwy transportowej (sieć, SSL, URL, połączenie)."""


class GeminiHttpError(GeminiError):
    """Błąd HTTP zwrócony przez Gemini API."""


class GeminiResponseParseError(GeminiError):
    """Błąd parsowania odpowiedzi Gemini API."""


class GeminiRateLimitExhaustedError(GeminiError):
    """Wszystkie modele są chwilowo niedostępne (rate limit / exhaustion)."""

