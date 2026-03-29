from dataclasses import dataclass


@dataclass(frozen=True)
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

    def __post_init__(self) -> None:
        """Waliduje wymagane pola konfiguracji modelu."""
        if not self.model.strip():
            msg = "Pole 'model' nie może być puste."
            raise ValueError(msg)
        if self.requests_per_minute <= 0:
            msg = "Pole 'requests_per_minute' musi być większe od 0."
            raise ValueError(msg)
        if self.requests_per_day <= 0:
            msg = "Pole 'requests_per_day' musi być większe od 0."
            raise ValueError(msg)
