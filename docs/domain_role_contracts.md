# Domain role contracts

## 1) Rodzina `Scraper`

| Metody wymagane | Odpowiedzialność | Zależności |
|---|---|---|
| `run(source)` | Pobieranie + orkiestracja pełnego flow extractor/parser/factory. | Mixiny orkiestracyjne, adaptery źródła, serwisy domenowe. |

## 2) Rodzina `Extractor`

| Metody wymagane | Odpowiedzialność | Zależności |
|---|---|---|
| `extract(source)` | Składanie danych wejściowych z wielu źródeł do spójnego payloadu technicznego. | Adaptery źródła, fetchery, agregatory. |

## 3) Rodzina `Parser`

| Metody wymagane | Odpowiedzialność | Zależności |
|---|---|---|
| `parse(raw)` | Transformacja HTML/tekstu do struktury pośredniej. | `BeautifulSoup`, parsery tabel/sekcji, helpery czyszczenia tekstu. |

## 4) Rodzina `Factory`

| Metody wymagane | Odpowiedzialność | Zależności |
|---|---|---|
| `create(payload)` | Tworzenie kanonicznego modelu domenowego/rekordu eksportowego. | DTO payloadu, mapery rekordów, reguły domenowe. |

## Mixiny przekrojowe

| Mixin | Kontrakt | Cel |
|---|---|---|
| `RetryMixin` | `with_retry(fn, retries=...)` | Ujednolicone ponawianie operacji podatnych na błędy przejściowe. |
| `DebugDumpMixin` | `dump_debug_payload(payload, stem)` | Zrzut JSON do katalogu debug dla diagnostyki. |
| `ValidationMixin` | `validate_required(payload, required_fields)` | Walidacja spójności payloadu przed budową rekordu. |
