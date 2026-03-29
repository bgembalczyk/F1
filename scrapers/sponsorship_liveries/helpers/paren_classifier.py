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
import time
from typing import Any
from typing import Literal

from infrastructure.gemini.client import GeminiClient
from infrastructure.gemini.errors import GeminiHttpError
from infrastructure.gemini.errors import GeminiRateLimitExhaustedError
from infrastructure.gemini.errors import GeminiResponseParseError
from infrastructure.gemini.errors import GeminiTransportError
from scrapers.sponsorship_liveries.helpers.constants import PROMPT_TEMPLATE

logger = logging.getLogger(__name__)


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
        self._error_policy: Literal["retry", "fallback", "fail-fast"] = "fallback"
        self._retry_attempts = 2

    def with_error_policy(
        self,
        *,
        policy: Literal["retry", "fallback", "fail-fast"],
        retry_attempts: int = 2,
    ) -> "ParenClassifier":
        self._error_policy = policy
        self._retry_attempts = max(1, retry_attempts)
        return self

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
        return self._classify_with_policy(
            prompt=prompt,
            paren_content=paren_content,
            team_name=team_name,
        )

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
        return PROMPT_TEMPLATE.format(
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

    def _classify_with_policy(
        self,
        *,
        prompt: str,
        paren_content: str,
        team_name: str,
    ) -> dict[str, list[str]]:
        retries_left = self._retry_attempts
        while retries_left > 0:
            try:
                result = self._client.query(prompt)
                return self._normalize_result(result)
            except (GeminiTransportError, GeminiHttpError) as exc:
                retries_left -= 1
                if self._error_policy == "retry" and retries_left > 0:
                    time.sleep(0.05)
                    continue
                return self._handle_error(
                    exc=exc,
                    paren_content=paren_content,
                    team_name=team_name,
                )
            except (GeminiResponseParseError, GeminiRateLimitExhaustedError) as exc:
                return self._handle_error(
                    exc=exc,
                    paren_content=paren_content,
                    team_name=team_name,
                )
            except Exception as exc:
                return self._handle_error(
                    exc=exc,
                    paren_content=paren_content,
                    team_name=team_name,
                )
        return self._empty_result()

    def _handle_error(
        self,
        *,
        exc: Exception,
        paren_content: str,
        team_name: str,
    ) -> dict[str, list[str]]:
        if self._error_policy == "fail-fast":
            raise exc
        logger.exception(
            "Gemini classification failed for paren=%r team=%r",
            paren_content,
            team_name,
        )
        return self._empty_result()
