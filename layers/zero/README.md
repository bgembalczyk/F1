# layers/zero

## Odpowiedzialność
Warstwa 0 odpowiada za uruchamianie scrape'ów listowych (seed/list jobs), zapis surowych artefaktów do `layers/0_layer/.../A_scrape` oraz finalny merge wyników do `layers/0_layer/.../B_merge` po przejściu całego rejestru jobów.

## Punkt wejścia
- Publiczny alias: `LayerZeroRunner` (`layers.zero.__init__`).
- Główny kontrakt uruchomienia: `LayerZeroExecutor.run(run_config, base_wiki_dir)`.

## Najczęstszy punkt debug
Najczęściej debug zaczyna się w `layers/zero/executor.py`, zwłaszcza w:
- `_build_local_run_config()` (nadpisania per seed),
- `_run_single_job()` (realne odpalenie joba),
- `_finalize_merge()` (spięcie artefaktów po pętli).

Pomocniczo warto sprawdzić `layers/zero/run_profile_paths.py` (czy ścieżki outputu są poprawne) i `layers/zero/policies.py` (hooki post-job).

## Czego tu nie robić
- Nie przenosić tu logiki domenowej parsowania/normalizacji rekordów (to rola scraperów i warstw domenowych).
- Nie dodawać tu ad-hoc transformacji „pod pojedynczy seed” — takie reguły powinny żyć bliżej runnera/scrapera.
- Nie traktować warstwy 0 jako miejsca do ręcznego „naprawiania” wyników po merge; poprawki powinny iść do źródła danych lub pipeline.
- Nie mieszać kontraktów globalnego `run_config` i lokalnego `local_run_config` bez jasnej intencji.
