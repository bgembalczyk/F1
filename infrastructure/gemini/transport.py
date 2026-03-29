import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from infrastructure.gemini.constants import API_URL_TEMPLATE


class GeminiTransport:
    """Warstwa transportu HTTP do Gemini API."""

    def __init__(self, *, api_key: str, timeout: int, ssl_context: ssl.SSLContext) -> None:
        self._api_key = api_key
        self._timeout = timeout
        self._ssl_context = ssl_context

    def generate(
        self,
        prompt: str,
        *,
        model: str,
        response_mime_type: str,
    ) -> dict[str, Any]:
        url = API_URL_TEMPLATE.format(model=model, api_key=self._api_key)
        parsed_url = urllib.parse.urlparse(url)
        if parsed_url.scheme != "https":
            msg = "Gemini API endpoint musi używać schematu https."
            raise RuntimeError(msg)

        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": response_mime_type},
        }
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(  # noqa: S310
            parsed_url.geturl(),
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        print(f"[GeminiClient] >>> Zapytanie do API (model={model}):")
        print(prompt)

        try:
            req_url = req.full_url
            parsed_req_url = urllib.parse.urlparse(req_url)
            if parsed_req_url.scheme != "https":
                msg = "Żądanie Gemini API musi używać schematu https."
                raise RuntimeError(msg)

            with urllib.request.urlopen(  # noqa: S310
                req,
                timeout=self._timeout,
                context=self._ssl_context,
            ) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            msg = (
                f"Gemini API zwróciło HTTP {exc.code}: {exc.reason}\n"
                f"Response body:\n{error_body}"
            )
            raise RuntimeError(msg) from exc
        except urllib.error.URLError as exc:
            msg = (
                "Nie udało się połączyć z Gemini API. "
                "Sprawdź połączenie sieciowe, SSL/certyfikaty oraz\n"
                "poprawność endpointu.\n"
                f"Szczegóły: {exc}"
            )
            raise RuntimeError(msg) from exc

        print("[GeminiClient] <<< Odpowiedź surowa od API:")
        print(raw)

        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            msg = f"Gemini API zwróciło niepoprawny JSON:\n{raw}"
            raise RuntimeError(msg) from exc
