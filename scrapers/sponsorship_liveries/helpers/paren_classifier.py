"""Klasyfikator nawiasów w kolumnie roku tabel sponsorskich F1.

Gdy w kolumnie ``Year`` wpis zawiera nawiasową adnotację (np.
``1988 (Dallara F188)`` lub ``1990 (with Subaru power)``), ten moduł
pyta Gemini API o to, czego ta adnotacja dotyczy, i zwraca ustrukturyzowaną
odpowiedź JSON z następującymi kategoriami:

* ``driver``            - konkretni kierowcy F1
* ``car_model``         - modele bolidów/samochodów wyścigowych
* ``engine_constructor`` - konstruktorzy silników
* ``grand_prix``        - konkretne wyścigi Grand Prix lub GP
* ``time_period``       - okresy czasowe w sezonie (np. „later races")
* ``other``             - inne informacje (np. „never raced")

Każda kategoria to lista łańcuchów (lub pusta lista, jeśli nie dotyczy).
"""

import logging
from typing import Any

from infrastructure.gemini.client import GeminiClient

logger = logging.getLogger(__name__)

_PROMPT_TEMPLATE = """
Analizujesz tabelę Wikipedii o historycznych malowaniach sponsorów w Formule 1.

Określ, czego dotyczy ta adnotacja.
Odpowiedz wyłącznie w formacie JSON z następującymi kluczami
(każdy zawiera listę elementów lub pustą listę []):
- "driver": lista kierowców F1, których dotyczy adnotacja (imię i nazwisko)
- "car_model": lista modeli bolidów/samochodów wyścigowych
- "engine_constructor": lista konstruktorów/dostawców silników
- "grand_prix": lista konkretnych wyścigów Grand Prix
  (pełna nazwa, np. "Monaco Grand Prix")

Przykład odpowiedzi:
{{
  "driver": [],
  "car_model": ["Dallara F188"],
  "engine_constructor": [],
  "grand_prix": []
}}

Odpowiedz tylko poprawnym JSON, bez dodatkowego tekstu.

Nie uzupełniaj za pomocą własnej wiedzy; odpowiedz tylko na podstawie
poniższych informacji. Jeśli danej informacji nie da się wywnioskować
wyłącznie z tych danych, pozostaw odpowiednią kategorię pustą.
Jeśli treść ewidentnie sugeruje przeczenie, to znaczy,
że nie dotyczy tego o czym wspomina, więc nie należy tego wpisywać do kategorii.

Zespół F1: {team_name}

W kolumnie "Year" (rok) przy wpisie roku {year_text!r}
pojawia się adnotacja w nawiasie: {paren_content!r}
"""


class ParenClassifier:
    """Klasyfikuje treść nawiasowej adnotacji w kolumnie roku tabeli sponsorskiej.

    Korzysta z Gemini API (z cache) do semantycznej klasyfikacji adnotacji.

    Parameters
    ----------
    gemini_client:
        Skonfigurowany klient Gemini API.
    """

    def __init__(self, gemini_client: GeminiClient) -> None:
        self._client = gemini_client

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def classify(
        self,
        *,
        paren_content: str,
        team_name: str,
        year_text: str,
        headers: list[str] | None = None,
    ) -> dict[str, list[str]]:
        """Klasyfikuje adnotację nawiasową i zwraca strukturę kategorii.

        Parameters
        ----------
        paren_content:
            Treść adnotacji w nawiasie (bez samych nawiasów).
        team_name:
            Nazwa zespołu F1 (kontekst).
        year_text:
            Tekst roku z komórki
            (np. "1988" lub "1988-1990").
        headers:
            Lista nagłówków kolumn tabeli (kontekst dla Gemini).

        Returns
        -------
        dict
            Słownik z kluczami: ``driver``, ``car_model``,
            ``engine_constructor``, ``grand_prix``.
            Każda wartość to lista łańcuchów lub pusta lista.
        """
        prompt = self._build_prompt(
            paren_content=paren_content,
            team_name=team_name,
            year_text=year_text,
            headers=headers or [],
        )
        try:
            result = self._client.query(prompt)
            return self._normalize_result(result)
        except Exception:
            logger.exception(
                "Gemini classification failed for paren=%r team=%r",
                paren_content,
                team_name,
            )
            return self._empty_result()

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_prompt(
        *,
        paren_content: str,
        team_name: str,
        year_text: str,
        headers: list[str],
    ) -> str:
        headers_str = ", ".join(headers) if headers else "(brak)"
        return _PROMPT_TEMPLATE.format(
            team_name=team_name,
            headers=headers_str,
            year_text=year_text,
            paren_content=paren_content,
        )

    @staticmethod
    def _empty_result() -> dict[str, list[str]]:
        return {
            "driver": [],
            "car_model": [],
            "engine_constructor": [],
            "grand_prix": [],
        }

    @classmethod
    def _normalize_result(cls, raw: Any) -> dict[str, list[str]]:
        """Upewnia się, że wynik ma właściwy kształt."""
        if not isinstance(raw, dict):
            return cls._empty_result()
        keys = ("driver", "car_model", "engine_constructor", "grand_prix")
        result = {}
        for key in keys:
            value = raw.get(key, [])
            if isinstance(value, list):
                result[key] = [str(item) for item in value if item]
            else:
                result[key] = []
        return result
