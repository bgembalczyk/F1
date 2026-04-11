# Wiki parsers – architektura warstw

Ten katalog utrzymuje parsery odpowiedzialne za ekstrakcję treści z HTML-a Wikipedii.

## Ustalona hierarchia

1. **Element Parser**
   - odpowiedzialność: parsuje pojedynczy `Tag`,
   - katalog rodziny: `scrapers/parsers/wiki/`.

2. **Structure Parser**
   - odpowiedzialność: kompozycja sekcji/podsekcji i nawigacja po nagłówkach,
   - katalog rodziny: `scrapers/parsers/section/`.

3. **Domain Mapper**
   - odpowiedzialność: mapowanie danych parserów wiki (szczególnie tabel) na rekordy domenowe,
   - katalog rodziny: `scrapers/parsers/table/wiki/`.

Pełna decyzja architektoniczna: `ADR-0006`.

## Section-first orchestration

Dla użytkownika końcowego parser sekcji jest bardziej intuicyjnym entrypointem.
Dlatego parsery w `scrapers/parsers/section/` dobierają zestaw parserów elementarnych
(`SectionParserToolbox`) i delegują parsing HTML do parserów elementów.


## Rodzina parserów elementarnych (`scrapers/parsers/wiki/`)

- `header.py` – nagłówek.
- `paragraph.py` – paragraf.
- `list.py` – lista.
- `../table/wiki/table.py` – tabela wiki.
- `infobox.py` – infobox.
- `navbox.py` – navbox.
- `references_wrap.py` – refs/references-wrap.

## Granice odpowiedzialności

- Parsery elementarne nie mapują bezpośrednio na rekordy domenowe.
- Parsery sekcji składają strukturę i przekazują dane niżej/wyżej, bez logiki domenowej.
- Mappery domenowe tabel wiki realizują mapowanie kolumn i normalizację rekordów.
- Moduły domenowe korzystają z kontraktów parserów (`Protocol`), nie z odwrotnych zależności parser → domena.
