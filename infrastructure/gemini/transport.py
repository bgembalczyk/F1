import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from infrastructure.gemini.constants import API_URL_TEMPLATE
from scrapers.base.logging import build_execution_context
from scrapers.base.logging import get_logger
from scrapers.base.errors import TransportError


class GeminiTransport:
    """Warstwa transportu HTTP do Gemini API."""

    def __init__(self, *, api_key: str, timeout: int, ssl_context: ssl.SSLContext) -> None:
        self._api_key = api_key
        self._timeout = timeout
        self._ssl_context = ssl_context
        self._logger = get_logger(self.__class__.__name__)

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
            raise TransportError(
                message="Gemini API endpoint musi używać schematu https.",
                source_name=model,
            )

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

        context = build_execution_context(
            domain="gemini",
            source_name=model,
        )
        self._logger.debug("Gemini request payload prompt=%s", prompt, extra=context)

        try:
            req_url = req.full_url
            parsed_req_url = urllib.parse.urlparse(req_url)
            if parsed_req_url.scheme != "https":
                raise TransportError(
                    message="Żądanie Gemini API musi używać schematu https.",
                    source_name=model,
                )

            with urllib.request.urlopen(  # noqa: S310
                req,
                timeout=self._timeout,
                context=self._ssl_context,
            ) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise TransportError(
                message=f"Gemini API zwróciło HTTP {exc.code}.",
                source_name=model,
                cause=exc,
            ) from exc
        except urllib.error.URLError as exc:
            raise TransportError(
                message="Gemini API connection error.",
                source_name=model,
                cause=exc,
            ) from exc

        self._logger.debug("Gemini response raw=%s", raw, extra=context)

        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise TransportError(
                message="Gemini API zwróciło niepoprawny JSON.",
                source_name=model,
                cause=exc,
            ) from exc
