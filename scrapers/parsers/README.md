# Konwencja parserów (final)

Finalny podział pakietów parserów wiki:

- `scrapers/parsers/html_elements/*`
- `scrapers/parsers/wiki/elements/*`
- `scrapers/parsers/wiki/sections/*`
- `scrapers/parsers/wiki/infobox/*`
- `scrapers/parsers/wiki/tables/*`
- `scrapers/mappers/wiki_tables/*`

## Nazewnictwo

- `*ElementParser` – parser elementu HTML,
- `*SectionParser` – parser sekcji/hierarchii sekcji,
- `*Mapper` – mapper domenowy (bez parsowania HTML).

## Zasada

`Parser` oznacza publiczne `parse(...)`; `Mapper` oznacza publiczne `map(...)`.

Dokumentacja opisuje wyłącznie model końcowy, bez warstwy legacy.
