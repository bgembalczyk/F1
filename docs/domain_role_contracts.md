# Domain role contracts

## 1) Rodzina `Extractor`

| Metody wymagane | Odpowiedzialność | Zależności |
|---|---|---|
| `extract(source)` | Pobranie i wstępne ustrukturyzowanie danych wejściowych. | Adaptery źródła, pipeline tabel (`TablePipeline`). |

## 2) Rodzina `Parser`

| Metody wymagane | Odpowiedzialność | Zależności |
|---|---|---|
| `parse(raw)` | Normalizacja surowego HTML/tekstu do modelu pośredniego. | `BeautifulSoup`, parsery tabel/sekcji, helpery czyszczenia tekstu. |

## 3) Rodzina `Assembler`

| Metody wymagane | Odpowiedzialność | Zależności |
|---|---|---|
| `assemble(payload)` | Złożenie finalnego rekordu eksportowego domeny. | DTO payloadu, mappery rekordów (`InfoboxRecordMapper`, `TableRecordMapper`, `SectionRecordMapper`). |

## 4) Rodzina `PipelineService`

| Metody wymagane | Odpowiedzialność | Zależności |
|---|---|---|
| `run(source)` | Orkiestracja end-to-end extractor/parser/assembler z walidacją i obsługą retry/debug. | `RetryMixin`, `DebugDumpMixin`, `ValidationMixin`, konkretne assemblery domenowe. |

## Mixiny przekrojowe

| Mixin | Kontrakt | Cel |
|---|---|---|
| `RetryMixin` | `with_retry(fn, retries=...)` | Ujednolicone ponawianie operacji podatnych na błędy przejściowe. |
| `DebugDumpMixin` | `dump_debug_payload(payload, stem)` | Zrzut JSON do katalogu debug dla diagnostyki. |
| `ValidationMixin` | `validate_required(payload, required_fields)` | Walidacja spójności payloadu przed składaniem rekordu. |
