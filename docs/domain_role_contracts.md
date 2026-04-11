# Domain role contracts

## Cel dokumentu

Ten dokument definiuje kontrakty 5 rodzin ról technicznych:
- `Fetcher`
- `Parser`
- `Extractor`
- `Normalizer`
- `Orchestrator`

Kontrakty są źródłem prawdy dla nazewnictwa, odpowiedzialności i granic modułów.

---

## 1) Rodzina `Fetcher`

### Wspólny interfejs / protocol (wymagane metody)

```python
class FetcherProtocol(Protocol):
    def fetch(self, source: str, *, timeout: int | None = None) -> str: ...
```

Dopuszczalne warianty rozszerzone:
- `fetch_bytes(...) -> bytes`
- `fetch_with_metadata(...) -> tuple[str, dict[str, object]]`

### Dozwolone mixiny
- `RetryMixin` (ponawianie i backoff)
- `RateLimitMixin` (throttling)
- `CacheReadMixin` / `CacheWriteMixin` (cache HTTP/tekst)
- `HeaderResolverMixin`

### Niedozwolone odpowiedzialności
- Parsowanie HTML/DOM i mapowanie na rekordy domenowe.
- Normalizacja pól biznesowych.
- Orkiestracja przepływu wieloetapowego poza retry/request loop.

---

## 2) Rodzina `Parser`

### Wspólny interfejs / protocol (wymagane metody)

```python
class ParserProtocol(Protocol):
    def parse(self, raw: object) -> object: ...
```

Dopuszczalne metody pomocnicze:
- `can_parse(raw) -> bool`
- `parse_many(raw_items) -> list[object]`

### Dozwolone mixiny
- `SafeParserMixin` (ochrona przed niestabilnym inputem)
- `TextCleaningMixin`
- `TableNormalizationMixin` (wyłącznie normalizacja struktury parser output)

### Niedozwolone odpowiedzialności
- Jakiekolwiek I/O (HTTP, pliki, sockety, zapis artefaktów).
- Zarządzanie retry/backoff.
- Sterowanie przebiegiem pipeline (decyzje orkiestracyjne).

### Reguła twarda nazewnicza

**Jeśli nazwa klasy kończy się na `Parser`, klasa musi udostępniać publiczne `parse(...)` (bezpośrednio lub przez dziedziczenie) i nie może zawierać logiki I/O/HTTP.**

Przykład:
- ✅ `SectionParser.parse(...)` + helpery pure.
- ❌ `SectionParser.parse(...)` wykonujący `session.get(...)`.

---

## 3) Rodzina `Extractor`

### Wspólny interfejs / protocol (wymagane metody)

```python
class ExtractorProtocol(Protocol):
    def extract(self, source: object) -> object: ...
```

Dopuszczalne warianty:
- `extract_all(sources: list[object]) -> list[object]`
- `extract_sections(source) -> dict[str, object]`

### Dozwolone mixiny
- `SectionDiscoveryMixin`
- `PayloadAssemblerMixin`
- `ExtractionDiagnosticsMixin`

### Niedozwolone odpowiedzialności
- Retry/backoff i niskopoziomowa polityka HTTP.
- Finalna normalizacja semantyczna domeny (rola `Normalizer`).
- Operacje eksportu/serializacji końcowej.

---

## 4) Rodzina `Normalizer`

### Wspólny interfejs / protocol (wymagane metody)

```python
class NormalizerProtocol(Protocol):
    def normalize(self, payload: object) -> object: ...
```

Dopuszczalne warianty:
- `normalize_field(name: str, value: object) -> object`
- `normalize_many(payloads: list[object]) -> list[object]`

### Dozwolone mixiny
- `EmptyValuePolicyMixin`
- `AliasMappingMixin`
- `CanonicalTextMixin`

### Niedozwolone odpowiedzialności
- Pobieranie danych i I/O.
- Parsowanie struktury HTML.
- Wybór kolejnych kroków pipeline i dispatch runnerów.

---

## 5) Rodzina `Orchestrator`

### Wspólny interfejs / protocol (wymagane metody)

```python
class OrchestratorProtocol(Protocol):
    def run(self, *, run_config: object) -> object: ...
```

Dopuszczalne metody pomocnicze:
- `build_plan(...) -> object`
- `run_step(...) -> object`
- `finalize(...) -> object`

### Dozwolone mixiny
- `StepLifecycleMixin`
- `CheckpointMixin`
- `MetricsMixin`

### Niedozwolone odpowiedzialności
- Szczegółowe parsowanie domenowe.
- Niskopoziomowe requesty HTTP bezpośrednio w orchestratorze.
- Twarde, domenowe reguły normalizacji pól.

---

## Przegląd niespójności nazw i odpowiedzialności (zakres: `layers/zero/*`, `layers/seed/*`, `layers/orchestration/*`, `infrastructure/http/*`)

### A) `layers/zero/*`

1. `extract.py` i `d_merge.py` operują stricte na fazach pipeline (`Phase C`, `Phase D`), ale nazwy modułów są niesymetryczne względem nomenklatury faz (`extract` vs `d_merge`).
   - Rekomendacja: przejście na jeden schemat fazowy (`phase_c_extract.py`, `phase_d_merge.py`).
2. `merge.py` zawiera zarówno konfigurację pipeline (`DomainPipelineConfig`), jak i transformacje domenowe (`*_domain_handler`).
   - Rekomendacja: rozdzielić odpowiedzialność na `pipeline_config` i `domain_transformers`.

### B) `layers/seed/*`

1. `SeedRegistryEntry` i `ListJobRegistryEntry` dziedziczą po `BaseRegistryEntry`, ale pola wyjściowe mają mieszane nazewnictwo (`default_output_path`, `json_output_path`, `legacy_json_output_path`).
   - Rekomendacja: ujednolicić na kontrakt typu `primary_output_path` / `legacy_output_path` + opcjonalne formaty.

### C) `layers/orchestration/*`

1. `runner_registry.py` zawiera i budowę map runnerów, i uruchomienie konkretnego eksportu (`run_engine_manufacturers`).
   - Rekomendacja: pozostawić w module tylko rejestr/fabryki, a wykonania przenieść do dedykowanego `runner_executor`.

### D) `infrastructure/http/*`

1. README opisuje ścieżki `infrastructure/http_client/*`, podczas gdy kod żyje w `infrastructure/http/*`.
   - Rekomendacja: synchronizacja dokumentacji z realną strukturą modułów.
2. Występuje mieszanie stylu nazewnictwa klas błędów (`HttpShimError` vs `HTTPError` / `HTTPTimeoutError`).
   - Rekomendacja: jeden standard akronimów (np. `HttpError`, `HttpTimeoutError`).
3. `UrllibHttpClient` importuje elementy z przestrzeni `infrastructure.http.requests_shim.*`, co semantycznie sugeruje inną warstwę niż aktualna struktura `infrastructure/http/*`.
   - Rekomendacja: domknąć spójny namespace i aliasy migracyjne jawnie opisać.

---

## Checklist egzekucji kontraktów (do CI/linterów)

- [ ] Każda klasa `*Parser` ma publiczne `parse(...)` (lokalnie albo odziedziczone).
- [ ] Każda klasa `*Parser` nie wykonuje HTTP/file I/O.
- [ ] Każdy `Fetcher` nie wykonuje normalizacji domenowej.
- [ ] Każdy `Orchestrator` nie implementuje parserów domenowych inline.
- [ ] Każdy `Normalizer` jest pure (brak I/O i side-effectów sieciowych).
