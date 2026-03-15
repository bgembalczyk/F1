# Wiki parsers – architektura

Ten katalog zawiera parsery odpowiedzialne za ekstrakcję treści z HTML-a Wikipedii.

## Mapa klas

### Warstwa bazowa
- `WikiParser` (`base.py`) – wspólny kontrakt parserów.

### Parsery elementarne (`elements/`)
- `InfoboxParser` – parsowanie tabel infobox (`<table class="infobox">`).
- `ParagraphParser` – parsowanie akapitów (`<p>`).
- `FigureParser` – parsowanie rycin (`<figure>`).
- `ListParser` – parsowanie list (`<ul>`).
- `TableParser` – parsowanie tabel danych (`<table class="wikitable">`).
- `NavBoxParser` – parsowanie bloków nawigacyjnych (`<div role="navigation" class="navbox">`).
- `ReferencesWrapParser` – parsowanie bloków odnośników (`references-wrap`).

### Parsery sekcji (`sections/`)
- `SectionParser` (poziom 2)
- `SubSectionParser` (poziom 3)
- `SubSubSectionParser` (poziom 4)
- `SubSubSubSectionParser` (poziom 5)

Parsery sekcji delegują parsowanie pojedynczych elementów do `WikiElementParserMixin` (zdefiniowanego w `sub_sub_sub_section.py`), który trzyma instancje parserów elementarnych i wybiera parser na podstawie typu elementu HTML.

## Przepływ parsowania
1. Parser sekcji dzieli dzieci kontenera na części nagłówkami (`_split_into_parts`).
2. Każda część jest przekazywana do parsera niższego poziomu sekcji.
3. Najniższy poziom (`SubSubSubSectionParser`) parsuje elementy bezpośrednio przez `WikiElementParserMixin._parse_element`.

## Kontrakt sygnatur
W parserach z `elements/` i `sections/` metody publiczne `parse` mają spójny kontrakt:

```python
def parse(self, element: Tag) -> dict[str, Any]:
    ...
```

Dzięki temu parsery można łatwo podmieniać i testować w jednolity sposób.
