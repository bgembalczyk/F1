# Mapa migracji nazw ról klas

Stan roboczy: 2026-04-10.

Format: `stara_klasa -> nowa_klasa -> docelowy_moduł`.

## Layer zero

- `extract` (moduł fazy C) -> `LayerZeroPhaseCExtractor` -> `layers/zero/phase_c_extract.py`
- `d_merge` (moduł fazy D) -> `LayerZeroPhaseDMerger` -> `layers/zero/phase_d_merge.py`
- `DomainPipelineConfig` (w `merge.py`) -> `LayerZeroMergePipelineConfig` -> `layers/zero/pipeline_config.py`
- `constructor_domain_handler` -> `ConstructorRecordNormalizer` -> `layers/zero/domain_normalizers/constructor.py`
- `drivers_domain_handler` -> `DriverRecordNormalizer` -> `layers/zero/domain_normalizers/driver.py`

## Layer seed

- `BaseRegistryEntry` -> `SeedRegistryBaseEntry` -> `layers/seed/registry/entries/base.py`
- `SeedRegistryEntry` -> `SeedDefinitionEntry` -> `layers/seed/registry/entries/seed_definition.py`
- `ListJobRegistryEntry` -> `SeedListJobEntry` -> `layers/seed/registry/entries/list_job.py`

## Layer orchestration

- `build_layer_one_runner_map` -> `build_layer_one_orchestrator_registry` -> `layers/orchestration/runner_registry.py`
- `build_layer_zero_run_config_factory_map` -> `build_layer_zero_orchestrator_config_registry` -> `layers/orchestration/runner_registry.py`
- `run_engine_manufacturers` -> `run_engine_manufacturers_orchestration` -> `layers/orchestration/runner_executor.py`

## Infrastructure HTTP

- `BaseHttpClient` -> `HttpFetcherBase` -> `infrastructure/http/fetchers/base.py`
- `UrllibHttpClient` -> `UrllibHttpFetcher` -> `infrastructure/http/fetchers/urllib_fetcher.py`
- `RequestExecutor` -> `HttpRequestOrchestrator` -> `infrastructure/http/orchestration/request_orchestrator.py`
- `HTTPError` -> `HttpError` -> `infrastructure/http/errors/shim/http.py`
- `HTTPTimeoutError` -> `HttpTimeoutError` -> `infrastructure/http/errors/shim/timeout.py`
- `HttpPolicy` -> `HttpRequestPolicy` -> `infrastructure/http/policies/http.py`

## Parser naming rule (binding)

- Każda przyszła klasa `*Parser` musi:
  1. implementować parser contract (`parse(raw) -> object`),
  2. być wolna od I/O (HTTP/file/socket),
  3. delegować pobieranie danych do `Fetcher`/`HttpFetcher*`.
