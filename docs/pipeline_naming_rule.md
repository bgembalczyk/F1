# Reguła nazewnictwa etapów pipeline (`extract` → `parse` → `build` → `assemble`)

## Cel

Ujednolicenie nazewnictwa metod w scraperach i usługach sekcji:

1. `extract` – pobranie surowych danych (HTML, sekcja, wynik po URL).
2. `parse` – strukturyzacja surowych danych.
3. `build` – budowa payloadów/fragmentów pośrednich.
4. `assemble` – złożenie finalnego rekordu / serializowanego wyniku końcowego.

## Audyt (zakres: `scrapers/*/single_scraper.py`, `scrapers/*/sections/*.py`, `scrapers/base/*`)

Poniższe metody oznaczono jako niezgodne z docelową regułą i objęto migracją:

- `SingleWikiArticleScraperBase.fetch_by_url(...)` → docelowo `extract_by_url(...)`.
- `SingleSeasonScraper.fetch_by_url(...)` → docelowo `extract_by_url(...)`.
- `SectionAdapter.parse_section_dicts(...)` (parse + serializacja) → docelowo `assemble_section_dicts(...)`.
- `ABCScraper._finalize_fetch(...)` → docelowo `_assemble_fetch_result(...)`.

## Plan migracji (etapowy, z aliasami deprecacyjnymi)

Etap 1 (ten commit):
- Wprowadzamy nowe nazwy docelowe.
- Zachowujemy stare metody jako aliasy z `DeprecationWarning`.

Etap 2 (kolejny cykl):
- Przepinamy wywołania wewnętrzne i domenowe na nowe API.
- Dodajemy testy kontraktowe pod nowe nazwy.

Etap 3 (cleanup):
- Usuwamy aliasy deprecacyjne po uzgodnionym oknie kompatybilności.

## Przykłady implementacji

```python
# EXTRACT (docelowo)
records = scraper.extract_by_url(url)

# PARSE
section_results = adapter.parse_sections(soup=soup, domain=domain, entries=entries)

# BUILD
payload = scraper._build_sections_payload(soup)

# ASSEMBLE
record = scraper._assemble_record(
    soup=soup,
    infobox_payload=infobox_payload,
    tables_payload=tables_payload,
    sections_payload=sections_payload,
)
```
