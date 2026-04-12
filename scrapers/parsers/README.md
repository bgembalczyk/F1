# Konwencja nazewnicza parserów

Krótka konwencja dla nowych nazw klas:

- `*ABC` – kontrakty abstrakcyjne (np. `SectionParserABC`).
- `*Mixin` – współdzielone zachowania wielokrotnego dziedziczenia.
- `*Base` – klasy bazowe/abstrakcyjne.
- `*Service` – komponenty usługowe orkiestrujące logikę.
- `*Parser` – parsery wejścia/HTML/sekcji/tabel.

## Rodzina bazowych kontraktów parserów

- `ParserABC` – kontrakt bazowy `parse(input) -> output`.
- `HtmlTagParserABC` – parser wejścia `bs4.Tag`.
- `HtmlSoupParserABC` – parser wejścia `BeautifulSoup`.
- `SectionParserABC` – parser sekcji.
- `ElementParserABC` – parser elementów HTML (list/table/infobox/navbox/references).
