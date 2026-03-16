# Granice modułów parserów wiki (stabilizacja architektury)

## 1. Mapa odpowiedzialności warstw

- `list/` — seed scrape, pozyskanie list encji i linków do stron szczegółowych.
- `sections/` — parsowanie `bodyContent` po sekcjach i podsekcjach; wyłącznie logika sekcyjna.
- `infobox/` — strukturalny rdzeń encji (`table.infobox`) i mapowanie pól high-signal.
- `postprocess/` — normalizacja domenowa i domknięcie kontraktu wynikowego.

### Reguła architektoniczna

Moduły `sections/` **nie importują** `single_scraper.py`.
Komunikacja między warstwami odbywa się wyłącznie przez:
- serwisy parserów,
- adaptery (`section_adapter`),
- wspólny kontrakt (`SectionParseResult`).

## 2. Wspólny kontrakt sekcyjny

Każdy parser sekcji zwraca `SectionParseResult`:
- `section_id`
- `section_label`
- `records`
- `metadata`

Dzięki temu adapter i orkiestrator 0/1 mogą traktować parsery domenowe jednolicie.

## 3. Przepływ danych per domena

## `drivers`
1. `drivers/list/` — seed kierowców i URL-e.
2. `drivers/sections/` — parsery sekcji (np. `Career_results`) przez adapter sekcji.
3. `drivers/infobox/` — pola personalne i statystyczne.
4. `drivers/postprocess/` — aliasy nazw, normalizacja dat/kraju.

## `constructors`
1. `constructors/list/` — seed konstruktorów.
2. `constructors/sections/` — parsery sekcyjne wyników/championship context.
3. `constructors/infobox/` — pola strukturalne zespołu.
4. `constructors/postprocess/` — normalizacja identyfikatorów i nazw historycznych.

## `circuits`
1. `circuits/list/` — seed torów.
2. `circuits/sections/` — parsery sekcyjne (np. lap records).
3. `circuits/infobox/` — lokalizacja, layout, długość.
4. `circuits/postprocess/` — normalizacja geo i wariantów nazw.

## `seasons`
1. `seasons/list/` — seed sezonów.
2. `seasons/sections/` — kalendarz, wyniki, klasyfikacje.
3. `seasons/infobox/` — strukturalne pola sezonu.
4. `seasons/postprocess/` — normalizacja round ordering i nazewnictwa klasyfikacji.

## `grands_prix`
1. `grands_prix/list/` — seed GP.
2. `grands_prix/sections/` — by year / sekcje krytyczne przez fallback aliasów.
3. `grands_prix/infobox/` — rdzeń metadanych wyścigu.
4. `grands_prix/postprocess/` — normalizacja statusu mistrzostw, mapowanie domenowe.

## 4. Definition of Done (DoD) dla nowego parsera sekcji

Nowy parser sekcji jest gotowy do merge, jeżeli:
- [ ] ma test snapshotowy HTML (sekcja i edge-cases),
- [ ] ma mapowanie aliasów sekcji (`DOMAIN_CRITICAL_SECTIONS` + fallback),
- [ ] waliduje kontrakt (`SectionParseResult`) i pola `records`,
- [ ] ma wpis w README domeny (`list/sections/infobox/postprocess` + source/fallback).

## 5. Wspólne helpery czyszczenia treści wiki

Helpery czyszczenia tekstu parserów elementów zostały skonsolidowane w:
- `scrapers/wiki/parsers/elements/text_cleaning.py`

Celem jest eliminacja duplikacji i spójna normalizacja tekstu we wszystkich parserach elementarnych.
