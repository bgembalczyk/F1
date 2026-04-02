# layers/zero

## Cel modułu
Warstwa 0 uruchamia scrape'y listowe (seed/list jobs), zapisuje surowe artefakty do `layers/0_layer/.../raw`, a na końcu odpala merge wyników.

## Główne klasy
- `LayerZeroExecutor` – główna orkiestracja pętli po `list_job_registry`.
- `LayerZeroMergeService` – cienki adapter nad funkcją łączenia wyników.
- Hooki w `policies.py` (`NullLayerZeroJobHook`, `MirrorConstructorsJobHook`) – logika post-job.
- `LayerZeroPathBuilder` + `layer_zero_raw_paths()` – wyliczanie ścieżek outputu.

## Co jest publiczne
- Publiczny alias: `LayerZeroRunner` (alias do `LayerZeroExecutor`) z `layers.zero.__init__`.
- Publiczny kontrakt uruchomienia: `LayerZeroExecutor.run(run_config, base_wiki_dir)`.

## Gdzie najczęściej debugować
- `layers/zero/executor.py`: `_build_local_run_config()`, `_run_single_job()`, `_finalize_merge()`.
- `layers/zero/run_profile_paths.py`: czy output trafia do oczekiwanej ścieżki.
- `layers/zero/policies.py`: czy hook po jobie uruchamia się tylko dla właściwych seedów.

## Najczęstsze pułapki
- Niezgodność `seed_name` vs mapa factory (`run_config_factory_map_builder`) powoduje fallback na domyślną konfigurację.
- Mylenie `run_config` z `local_run_config` (nadpisania `scraper_kwargs` mogą nie wejść, jeśli są puste).
- Błędny `json_output_path`/`csv_output_path` w rejestrze daje poprawny run, ale z nieoczekiwanym miejscem zapisu.
