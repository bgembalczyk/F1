# CLI / RunConfig — katalog flag i polityka YAGNI

## 1) Aktualny katalog flag CLI

Wspólny parser (`scrapers.base.cli_entrypoint.build_standard_parser`) udostępnia tylko:

- `--quality-report` / `--no-quality-report`
- `--error-report` / `--no-error-report`
- `--verbose`
- `--trace`

Legacy wrappery **nie przyjmują już** `--profile` — profil runtime jest domyślny i jednolity.

## 2) Aktualne opcje `RunConfig`

Profile runtime są scentralizowane w `scrapers.base.run_profiles`:

- `default` (domyślny)
- `debug` (opcjonalny profil diagnostyczny)

To zastępuje wcześniejsze rozdrobnienie (`strict` / `minimal` / `deprecated`) mapowane teraz do jednego zachowania domyślnego.

## 3) Polityka redukcji opcji

- Usuwamy opcje rzadko używane i duplikujące się semantycznie.
- Jeśli dwie flagi robią to samo, zostaje jedna canonical flaga.
- Każdy nowy profil musi uzasadniać różnicę względem `default`; w przeciwnym razie nie powstaje.

## 4) Wymuszenie YAGNI dla nowych flag

Nowe flagi muszą być deklarowane w katalogu `CliFlagSpec` i zawierać:

- `justification` (po co ta flaga istnieje),
- `review_by` (termin przeglądu, czy flaga nadal jest potrzebna).

Parser uruchamia walidację katalogu flag; brak któregokolwiek pola traktowany jest jako błąd konfiguracji.
