# Wiki parser architecture (final model)

Docelowy podział parserów wiki:

- `scrapers/parsers/html_elements/*` – **czyste parsery HTML** (`Tag -> dict`).
- `scrapers/parsers/wiki/elements/*` – **wiki-specyficzne implementacje** parserów elementów (`*ElementParser`).
- `scrapers/parsers/wiki/sections/*` – **hierarchia sekcji h2-h5** (`*SectionParser`).
- `scrapers/parsers/wiki/infobox/*` – parsery i kontrakty infoboxu wiki.
- `scrapers/parsers/wiki/tables/*` – parsery HTML tabel wiki.
- `scrapers/mappers/wiki_tables/*` – mappery domenowe tabel (`*Mapper`).

## Granice odpowiedzialności

1. `html_elements`: brak logiki wiki/domenowej.
2. `wiki/elements`: dopasowanie i parse elementów Wikipedii.
3. `wiki/sections`: składanie drzewa sekcji i delegacja do parserów elementów.
4. `wiki/tables`: parsowanie HTML `<table class="wikitable">`.
5. `mappers/wiki_tables`: mapowanie payloadu tabel na pola domenowe (bez parsowania HTML).

## Konwencje nazw

- parsery elementów: `*ElementParser`,
- parsery sekcji: `*SectionParser`,
- mappery: `*Mapper`.

Ten dokument opisuje wyłącznie model docelowy (bez legacy aliasów).
