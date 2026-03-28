from dataclasses import dataclass


@dataclass
class ModelConfig:
    """Konfiguracja pojedynczego modelu Gemini z limitami zapytań.

    Parameters
    ----------
    model:
        Nazwa modelu, np. ``"gemini-2.5-flash-lite"``.
    requests_per_minute:
        Maksymalna liczba zapytań na minutę (RPM).
    requests_per_day:
        Maksymalna liczba zapytań na dobę (RPD).
    """

    model: str
    requests_per_minute: int
    requests_per_day: int
