# Typing guardrails (rollout etapowy)

## Scope
Aktualny scope bramki typowania (`mypy.ini`):
- `scrapers/base/pipeline_runner.py`
- `scrapers/base/options.py`
- `scrapers/base/table/pipeline.py`
- `scrapers/base/sections/interface.py`
- `layers/`
- `validation/`
- `infrastructure/http_client/`

## Zasady
1. **`Any` poza granicami I/O**
   - dozwolone tylko na styku z niekontrolowanym wejściem/wyjściem (np. surowe JSON/HTTP, serializacja).
   - wewnątrz pipeline i interfejsów domenowych używamy `object`, aliasów domenowych lub `Protocol`.
2. **Brak adnotacji typów zwrotnych w publicznych metodach**
   - publiczna metoda/funkcja (`def name(...)`) musi mieć jawny return type.
3. **Niejawne opcjonalności**
   - `None` musi być jawnie zapisane (`X | None`), bez implicit optional.
4. **Niekompletne adnotacje definicji**
   - wszystkie parametry i return type muszą być typowane.
5. **Nowe moduły: brak `Any` bez uzasadnienia**
   - nowy plik w `layers/`, `validation/`, `infrastructure/http_client/` nie może używać `Any`,
     chyba że obok znajduje się komentarz uzasadniający `ANY-JUSTIFIED:`.
6. **Registry seedów: jedno źródło prawdy**
   - kanoniczne API seed registry to `layers.seed.registry`.
   - `scrapers.wiki.seed_registry` jest wyłącznie fasadą kompatybilności wstecznej
     (re-export tych samych symboli), nie miejscem na nową logikę.

## Roadmapa rolloutu strict typing (per pakiet)
> Każdy etap ma **akceptowalny budżet błędów = 0** i jest zamykany dopiero, gdy
> usuniemy odpowiadające mu wyjątki `ignore_errors = True` z `mypy.ini`.

| Etap | Pakiet / obszar | Moduły objęte etapem (źródło prawdy: `mypy.ini`) | Budżet błędów |
|---|---|---|---|
| 1 | `scrapers/base/*` | `scrapers.base.pipeline_runner`, `scrapers.base.options`, `scrapers.base.table.pipeline`, `scrapers.base.sections.interface` | 0 |
| 2 | `layers/` (orchestration) | `layers.application`, `layers.one.executor`, `layers.orchestration.runners.function_export`, `layers.orchestration.runners.grand_prix` | 0 |
| 3 | `layers/` (seed + zero) | `layers.seed.data_classes`, `layers.seed.helpers`, `layers.seed.registry.constants`, `layers.seed.registry.entries`, `layers.seed.registry.helpers`, `layers.zero.executor`, `layers.zero.merge` | 0 |
| 4 | `validation/` | `validation.composite_validator`, `validation.record_factory_validator`, `validation.rules`, `validation.schema_engine`, `validation.schema_rules`, `validation.schemas`, `validation.validator_base` | 0 |
| 5 | `infrastructure/http_client/` | `infrastructure.http_client.clients.base`, `infrastructure.http_client.clients.urllib_http`, `infrastructure.http_client.components.request_executor`, `infrastructure.http_client.interfaces.http_client_protocol`, `infrastructure.http_client.policies.default_retry`, `infrastructure.http_client.policies.retry`, `infrastructure.http_client.requests_shim.http_error`, `infrastructure.http_client.requests_shim.session` | 0 |

### Definicja „etapu zakończonego”
Etap uznajemy za ukończony, gdy:
1. wszystkie moduły etapu przechodzą `mypy` bez błędów,
2. usunięte są wpisy `ignore_errors = True` dla modułów etapu w `mypy.ini`,
3. zaktualizowane są sekcje **Roadmapa rolloutu** i **Lista wyjątków** w tym dokumencie.

## Lista wyjątków (tymczasowa)
Poniższe moduły mają tymczasowe `ignore_errors = True` w `mypy.ini`:
- `layers.application`
- `layers.one.executor`
- `layers.orchestration.runners.function_export`
- `layers.orchestration.runners.grand_prix`
- `layers.seed.data_classes`
- `layers.seed.helpers`
- `layers.seed.registry.constants`
- `layers.seed.registry.entries`
- `layers.seed.registry.helpers`
- `layers.zero.executor`
- `layers.zero.merge`
- `validation.composite_validator`
- `validation.record_factory_validator`
- `validation.rules`
- `validation.schema_engine`
- `validation.schema_rules`
- `validation.schemas`
- `validation.validator_base`
- `infrastructure.http_client.clients.base`
- `infrastructure.http_client.clients.urllib_http`
- `infrastructure.http_client.components.request_executor`
- `infrastructure.http_client.interfaces.http_client_protocol`
- `infrastructure.http_client.policies.default_retry`
- `infrastructure.http_client.policies.retry`
- `infrastructure.http_client.requests_shim.http_error`
- `infrastructure.http_client.requests_shim.session`

## Bramka regresji CI
CI ma teraz dwie bramki:
1. `enforce_new_module_any_policy.py` — blokuje nowe moduły z `Any` bez `ANY-JUSTIFIED:`.
2. `mypy_regression_gate.py` — porównuje liczbę błędów mypy między `base SHA` i `head SHA`
   i blokuje PR, jeśli liczba błędów wzrośnie.
3. `mypy_regression_gate.py --error-budget 0` — blokuje PR, jeśli aktualna liczba błędów
   przekroczy akceptowalny budżet.

## Aktualizacja dokumentu po każdym etapie (anti-stale)
Po domknięciu etapu z roadmapy:
1. usuń z `mypy.ini` odpowiednie wpisy `ignore_errors = True`,
2. zaktualizuj tabelę etapów (status/zakres) i listę wyjątków w tym pliku,
3. dodaj krótki wpis do opisu PR: który etap został domknięty i jaki jest nowy stan długu typowania.
