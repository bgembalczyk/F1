# Dozwolone kierunki zależności

- `models` / `validation` -> brak zależności do `infrastructure` i `scrapers`.
- `scrapers` -> mogą używać `models`, `validation`, `infrastructure` (adaptery IO/HTTP), ale nie powinny importować `layers` poza modułami integracyjnymi CLI/wiki.
- `layers` -> orkiestracja; mogą używać `scrapers` i `models`, ale **nie mogą** importować `infrastructure` poza composition root (`layers/application.py`).
- `infrastructure` -> implementacje zewnętrzne (HTTP/cache/Gemini); nie importują `layers`.

Praktyka graniczna: warstwa wyżej zależy od interfejsu/protokołu, a konkretna implementacja jest podpinana w composition root (adapter/factory).
