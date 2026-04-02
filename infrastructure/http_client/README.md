# infrastructure/http_client

## Cel modułu
Ujednolicony klient HTTP dla projektu (retry, rate limit, cache, timeout, nagłówki), wykorzystywany przez scrapery niezależnie od konkretnego transportu.

## Główne klasy
- `HttpClientConfig` – wspólna konfiguracja klienta.
- `BaseHttpClient` – bazowa implementacja logiki request/retry/cache.
- `UrllibHttpClient` – domyślny klient oparty o `requests_shim`.
- `DefaultHttpPolicyFactory` – budowa retry/rate-limit/cache z konfiguracji.
- `RequestExecutor` – wykonanie pojedynczego requestu z backoffem.

## Co jest publiczne
- Publiczne entrypointy modułu: klasy klientów z `clients/*`, konfiguracja (`HttpClientConfig`) i interfejsy z `interfaces/*`.
- Publiczny kontrakt praktyczny: `get()`, `get_text()`, `get_json()` na kliencie.

## Gdzie najczęściej debugować
- `infrastructure/http_client/clients/base.py`: `_request_with_retries()`, `get_text()`, `get_json()`.
- `infrastructure/http_client/components/request_executor.py`: decyzje retry i moment `raise_for_status()`.
- `infrastructure/http_client/factories/default_http_policy_factory.py`: czy wstrzyknięte policy nadpisują domyślne.
- `infrastructure/http_client/config.py`: wartości timeout/retries/cache i ich źródło.

## Najczęstsze pułapki
- Cache w `get_text()` jest per URL (headers/timeout nie wpływają na cache key).
- `response.raise_for_status()` jest wołane także po udanym requestcie — błędy HTTP wychodzą dopiero tu.
- Ręczne `headers` nadpisują domyślne i mogą przypadkiem usunąć ważne nagłówki.
- Zbyt agresywny retry/backoff może wydłużyć scrape bardziej niż oczekiwano.
