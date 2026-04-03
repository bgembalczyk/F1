# infrastructure/http_client

## Odpowiedzialność
Moduł zapewnia ujednolicony klient HTTP dla projektu: timeouty, retry, rate limit, cache, nagłówki i wspólne polityki requestów, niezależnie od warstwy wywołującej.

## Punkt wejścia
- Konfiguracja: `HttpClientConfig`.
- Bazowy kontrakt klienta: `BaseHttpClient`.
- Domyślna implementacja: `UrllibHttpClient`.
- Praktyczny interfejs użycia: `get()`, `get_text()`, `get_json()`.

## Najczęstszy punkt debug
Najczęściej debug zaczyna się w `infrastructure/http_client/clients/base.py` (`_request_with_retries()`, `get_text()`, `get_json()`) oraz w `infrastructure/http_client/components/request_executor.py` (decyzje retry/backoff i `raise_for_status()`).

Dla problemów konfiguracyjnych warto sprawdzić `infrastructure/http_client/factories/default_http_policy_factory.py` i `infrastructure/http_client/config.py`.

## Czego tu nie robić
- Nie umieszczać tu logiki parsowania HTML/JSON specyficznej dla domeny (to odpowiedzialność scraperów).
- Nie kodować tu wyjątków pod konkretne endpointy biznesowe.
- Nie obchodzić policy factory przez „twarde” retry/backoff w kodzie wywołującym.
- Nie traktować cache HTTP jako substytutu warstwy trwałego storage danych.
