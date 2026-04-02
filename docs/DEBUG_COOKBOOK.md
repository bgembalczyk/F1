# DEBUG COOKBOOK (Layer 0/1)

Szybki przewodnik „**objaw → gdzie szukać**” dla pipeline’u danych.

## 1) Objaw → gdzie szukać

### Objaw: brak rekordu w wyniku końcowym
- **Layer 0 execution:** sprawdź, czy job w ogóle został uruchomiony i czy wygenerował plik `raw` (`[list] running/finished`). Kod ścieżek wyjściowych i uruchomienia jobów: `layers/zero/executor.py`.
- **Layer 0 merge:** zweryfikuj, czy rekord nie został odfiltrowany albo nadpisany podczas merge/post-process (`_load_domain_records`, `_post_process_domain_records`, `_write_merged_domain_records`). Kod: `layers/zero/merge.py`.
- **Layer 1:** upewnij się, że seed jest obsługiwany przez runner i nie został pominięty jako `unsupported seed`. Kod: `layers/one/executor.py`.

### Objaw: duplikaty rekordów
- **Merge kluczy i aliasów:** najczęściej problem wynika z klucza deduplikacji lub map aliasów podczas merge (`_merge_*`, logika indeksowania rekordów). Kod: `layers/zero/merge.py`.
- **Źródła raw:** sprawdź, czy duplikaty nie przychodzą już z kilku plików `raw` dla tej samej domeny (`layers/0_layer/<domain>/raw/*.json`).

### Objaw: błędne mapowanie źródła (zły transformer)
- **Dobór transformera po `domain` + `source_name`:** sprawdź `TRANSFORM_PIPELINES` i `_resolve_record_transform_handlers(...)`.
- **Efekt uboczny:** rekord ma złą strukturę (`racing_series`, pola F1, statusy), mimo że `raw` wygląda poprawnie.
- Kod: `layers/zero/merge.py`.

### Objaw: brak outputu po uruchomieniu CLI
- **CLI entrypoint:** sprawdź, czy uruchamiasz właściwy moduł/komendę i profil; punkty wejścia są mapowane dynamicznie. Kod: `scrapers/cli.py`.
- **Layer 1 seed:** jeśli w logu pojawia się `skipping unsupported seed`, to seed nie ma runnera w mapie (`runner_map`). Kod: `layers/one/executor.py`.
- **Layer 0 output path:** sprawdź, czy `output_dir`/`base_wiki_dir` wskazuje właściwy katalog i czy pliki trafiają do `layers/0_layer/.../raw`. Kod: `layers/zero/executor.py`.

## 2) Minimalne scenariusze debugowe

### A. Brak rekordu
1. Uruchom pipeline dla pojedynczej domeny (lub minimalnego zestawu seedów).
2. Sprawdź, czy rekord istnieje w `raw` (`layers/0_layer/<domain>/raw/*.json`).
3. Jeśli jest w `raw`, ale nie ma go w `layers/0_layer/<domain>/<domain>.json`, problem jest w `layers/zero/merge.py`.
4. Jeśli jest po merge, ale nie ma go w complete output, problem jest w runnerze Layer 1 (`layers/one/executor.py`).

### B. Duplikaty
1. Porównaj duplikujące się rekordy w `raw` i w pliku merged.
2. Zweryfikuj klucz merge i aliasy (czy dwa warianty nazwy nie trafiają do różnych kluczy).
3. Sprawdź, czy post-processing domenowy nie dokłada rekordu drugi raz.

### C. Błędne mapowanie źródła
1. Zidentyfikuj `domain` i nazwę pliku źródłowego (`source_name`).
2. Sprawdź, jaki pipeline zostanie wybrany (`TRANSFORM_PIPELINES`, fallback `*` i `DEFAULT_SOURCE_PIPELINE`).
3. Potwierdź wynik transformacji na pojedynczym rekordzie przed/po handlerze.

### D. Brak outputu
1. Zweryfikuj komendę uruchomienia i argumenty w CLI (`scrapers/cli.py`).
2. Sprawdź logi `[list]` (Layer 0) i `[complete]` (Layer 1).
3. Potwierdź, że seed istnieje w rejestrze i ma runner (`layers/one/executor.py`).
4. Potwierdź, że output directory wskazuje katalog roboczy, którego oczekujesz.

## 3) Najważniejsze punkty kontrolne (3–5)

1. **Pliki `raw` istnieją i zawierają dane**
   - `layers/0_layer/<domain>/raw/*.json`
   - jeśli brak, problem jest przed merge (scraper/job/path).

2. **Plik merged domeny powstaje i ma poprawną strukturę**
   - `layers/0_layer/<domain>/<domain>.json`
   - jeśli struktura jest zła, zacznij od transformera w `layers/zero/merge.py`.

3. **Nazwy seedów są spójne między rejestrem i runner_map**
   - objaw niespójności: `skipping unsupported seed`.
   - miejsce weryfikacji: `layers/one/executor.py`.

4. **Transformer jest dobrany zgodnie z `domain` + `source_name`**
   - miejsce weryfikacji: `TRANSFORM_PIPELINES` + `_resolve_record_transform_handlers(...)` w `layers/zero/merge.py`.

5. **CLI uruchamia właściwy entrypoint/profil**
   - miejsce weryfikacji: `scrapers/cli.py`.

## 4) Powiązane pliki

- `layers/zero/executor.py`
- `layers/zero/merge.py`
- `layers/one/executor.py`
- `scrapers/cli.py`
