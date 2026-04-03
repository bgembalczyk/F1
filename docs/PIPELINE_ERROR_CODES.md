# Katalog kodów błędów i warningów pipeline

Poniższa tabela jest mapowana bezpośrednio z `scrapers/base/error_codes.py` i obejmuje typowe klasy problemów.

| Kod | Kod symboliczny | Krótki opis | Typowy kontekst | Rekomendowana akcja naprawcza |
|---|---|---|---|---|
| `D001` | `source.domain_parse_error` | Błąd parsowania danych domenowych | Sekcja/rekord domenowy ma inny format niż oczekiwany przez parser. | Zweryfikuj strukturę sekcji i dopasuj parser domenowy. |
| `D002` | `source.not_found` | Brak oczekiwanego elementu źródła | Nie znaleziono wymaganej tabeli/listy/sekcji. | Sprawdź selektory i aliasy sekcji dla domeny. |
| `M001` | `pipeline.error` | Niezmapowany błąd pipeline | Wyjątek nie został sklasyfikowany do dedykowanego typu. | Dodaj mapowanie wyjątku w `normalize_pipeline_error`. |
| `M002` | `transport.error` | Błąd transportu/sieci | Błąd requestu, timeout lub chwilowa niedostępność źródła. | Sprawdź URL, politykę retry i timeout HTTP. |
| `P001` | `source.parse_error` | Błąd parsowania źródła | HTML nie daje się poprawnie zamienić na rekordy pośrednie. | Dodaj obsługę nowego wariantu HTML lub fallback parsera. |
| `V003` | `validation.error` | Błąd walidacji rekordu | Rekord nie przechodzi walidatora kontraktu danych. | Dostosuj mapowanie pól albo reguły walidacji. |
| `V004` | `validation.soft_reject` | Odrzucony rekord w trybie soft | Walidacja ostrzegła i rekord został pominięty bez przerwania runa. | Przeanalizuj warningi i popraw jakość danych wejściowych. |

## Agregacja błędów w raporcie końcowym runa

- Każdy wpis w `errors.jsonl` zawiera:
  - `code` (symboliczny),
  - `code_id` (np. `D001`),
  - `code_description`,
  - kontekst (`url`, `section_id`, `parser_name`, `run_id`).
- Dodatkowo pipeline zapisuje `errors_summary_by_code.json` z agregacją:
  - `total_errors`,
  - `error_counts_by_code`.
