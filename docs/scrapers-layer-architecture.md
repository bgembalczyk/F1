# Architektura warstw scraperów

Ten dokument porządkuje odpowiedzialności między warstwami i opisuje, co **wolno** implementować w każdej z nich.

## Interfejsy warstw (`scrapers/base/layers/interfaces.py`)

- `Fetcher` — pobiera surowe źródło danych (HTTP/cache/plik).  
  **Wolno:** requesty, retry, timeouty, cache-key.  
  **Nie wolno:** interpretować reguł domenowych.
- `Parser` — zamienia surowy payload na strukturę techniczną (np. wiersze tabel HTML).  
  **Wolno:** selektory HTML, parsowanie komórek, obsługa formatów.  
  **Nie wolno:** podejmować decyzji biznesowych.
- `Normalizer` — normalizuje wartości do formatu kanonicznego (np. puste wartości, link/text).  
  **Wolno:** trim, standaryzacja struktur, usuwanie artefaktów parsera.  
  **Nie wolno:** mapować na pojęcia domenowe zależne od kontekstu biznesowego.
- `Assembler` — składa rekord domenowy i nakłada reguły domenowe.  
  **Wolno:** decyzje „rekord odrzucić/zachować”, mapowania domenowe, agregacja pól.  
  **Nie wolno:** bezpośrednio czytać HTML/selectory.
- `Exporter` — serializuje i zapisuje rekordy wyjściowe.  
  **Wolno:** JSON/CSV/NDJSON, metadane exportu, zapis do storage.  
  **Nie wolno:** modyfikować logiki domenowej.

## Przykład: `grands_prix` po refaktorze

- Adapter techniczny `HtmlRowBackgroundColorAdapter` (`scrapers/base/adapters/row_background.py`) odpowiada za ekstrakcję koloru z HTML.
- Usługa domenowa `GrandPrixChampionshipResolver` (`scrapers/grands_prix/services/championship.py`) mapuje kolor na wartość `championship`.
- Assembler domenowy `GrandPrixByYearRecordAssembler` (`scrapers/grands_prix/assemblers/by_year.py`) decyduje o odrzuceniu rekordów „Not held” i składa finalny rekord.
- Parser sekcji `GrandPrixByYearSectionParser` (`scrapers/grands_prix/sections/by_year.py`) pozostał cienki: parsuje tabelę i deleguje reguły do assemblera.

## Szybka checklista „co gdzie trafić”

1. Dotykasz HTML/CSS/selectora? → `Parser` albo adapter techniczny.
2. Ujednolicasz strukturę i puste wartości? → `Normalizer`.
3. Rozstrzygasz regułę domenową? → `Assembler`/usługa domenowa.
4. Zapisujesz dane? → `Exporter`.
5. Koordynujesz przepływ? → single scraper / pipeline (bez logiki domenowej i bez szczegółów technicznych).
