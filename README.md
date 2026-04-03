# F1 Data Pipeline — README

Ten plik jest punktem wejścia do dokumentacji projektu.  
Szczegółowe opisy utrzymujemy centralnie w **indeksie dokumentacji**: [`docs/README.md`](docs/README.md).

## Quick start (PyCharm only)

> Jedyny wspierany sposób uruchomienia projektu to konfiguracja **Run** w **PyCharm**.
> Uruchamianie z terminala (`python -m ...`) jest niewspierane.
> Pełne zasady: [`docs/MODULE_BOUNDARIES.md`](docs/MODULE_BOUNDARIES.md).

## Szybka diagnoza problemów pipeline

Jeśli debugujesz Layer 0/1 lub merge rekordów, zacznij od cookbooka:  
- [`docs/DEBUG_COOKBOOK.md`](docs/DEBUG_COOKBOOK.md)

## 1) Architektura warstw

Architektura opiera się o separację odpowiedzialności między warstwami technicznymi i domenowymi:

- **Fetcher** — pobieranie źródeł danych,
- **Parser** — ekstrakcja struktur z payloadów,
- **Normalizer** — ujednolicanie formatów,
- **Assembler** — reguły domenowe i składanie rekordów,
- **Exporter** — zapis danych wyjściowych.

Pełny opis granic warstw i relacji między komponentami:  
- [`docs/scrapers-layer-architecture.md`](docs/scrapers-layer-architecture.md)  
- [`docs/MODULE_BOUNDARIES.md`](docs/MODULE_BOUNDARIES.md)

## 2) Kluczowe protokoły / interfejsy

Najważniejsze kontrakty i interfejsy projektu:

- kontrakty warstw (`Fetcher`, `Parser`, `Normalizer`, `Assembler`, `Exporter`),
- kontrakt konfiguracji scraperów,
- kontrakt parserów sekcji,
- strategia Dependency Injection (bez zbędnych interfejsów o pojedynczej implementacji),
- konwencje nazewnictwa hooków.

Źródła prawdy (single source of truth):
- ADR: [`docs/adr/README.md`](docs/adr/README.md)
- indeks dokumentacji: [`docs/README.md`](docs/README.md)

## 3) Zasady OOP / DRY dla contributorów

- **SRP**: każda klasa/moduł ma jedną odpowiedzialność.
- **Dependency Inversion**: zależności kierujemy do interfejsów/kontraktów.
- **Open/Closed**: rozszerzamy przez nowe implementacje, nie przez łamanie kontraktów.
- **DRY**: nową logikę najpierw próbujemy osadzić w komponentach bazowych (`scrapers/base/*`), zamiast kopiować implementacje domenowe.
- **Brak duplikacji opisów**: nie powielamy szczegółów architektury w wielu plikach — linkujemy do indeksu i dokumentu źródłowego.

Checklisty review i merge-gate:
- [`docs/CHANGES_CHECKLIST.md`](docs/CHANGES_CHECKLIST.md)
- [`docs/MODULE_BOUNDARIES.md`](docs/MODULE_BOUNDARIES.md)

## 4) Linki do ADR i docs

- **Indeks dokumentacji (canonical):** [`docs/README.md`](docs/README.md)
- **ADR:** [`docs/adr/README.md`](docs/adr/README.md)
- **Granice modułów:** [`docs/MODULE_BOUNDARIES.md`](docs/MODULE_BOUNDARIES.md)
- **Architektura warstw scraperów:** [`docs/scrapers-layer-architecture.md`](docs/scrapers-layer-architecture.md)
- **UML index:** [`docs/INDEX_DOKUMENTACJI_UML.md`](docs/INDEX_DOKUMENTACJI_UML.md)
- **Debug cookbook (objaw → gdzie szukać):** [`docs/DEBUG_COOKBOOK.md`](docs/DEBUG_COOKBOOK.md)

## 5) Checklista: dodawanie nowej domeny / komponentu

Przed merge PR sprawdź:

- [ ] Czy nowy moduł ma jasno określoną odpowiedzialność (SRP)?
- [ ] Czy nie duplikuje istniejącej logiki i używa wspólnych abstrakcji?
- [ ] Czy zachowuje granice warstw/importów opisane w `MODULE_BOUNDARIES.md`?
- [ ] Czy kontrakty typów/interfejsów są zgodne z aktualnymi ADR?
- [ ] Czy dodano/uzupełniono testy (jednostkowe i/lub statyczne) adekwatne do zmiany?
- [ ] Czy zaktualizowano dokumentację domeny (`scrapers/<domain>/README.md`) i wpisano link do indeksu docs?
- [ ] Czy jeśli zmiana ma charakter architektoniczny, dodano/zmieniono ADR i referencję w PR?
- [ ] Czy sekcje PR (`SRP impact`, `DRY impact`, `Contracts changed`, `Backward compatibility`, `DoD`) są uzupełnione?
- [ ] Czy checklista techniczna (`testy kontraktowe`, `brak nowych Any`, `brak nowych magic strings`, `zaktualizowany ADR/docs`) jest odhaczona?
- [ ] Czy w PR dodano dowód review (output testów/checków) wymagany do akceptacji?
- [ ] Czy nowy entrypoint i sposób uruchomienia są zgodne ze standardem PyCharm Run (zgodnie z `docs/MODULE_BOUNDARIES.md`)?
