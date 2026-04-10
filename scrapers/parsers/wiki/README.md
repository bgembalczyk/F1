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

Parsery sekcji działają przez wspólny kontekst `SectionExtractionContext`
(z `section_adapter.py`), który przenosi:
- `page_title`
- `page_url`
- `breadcrumbs`
- `html_metadata`
- `section_id`

## Kontrakt parsera elementów

Każdy sparsowany element w polu `elements` ma ujednolicony kontrakt:

```python
{
  "kind": str,
  "source_section_id": str | None,
  "confidence": float,
  "raw_html_fragment": str,
  "data": dict[str, Any],
  "type": str,  # alias kompatybilności wstecznej
}
```

Dodatkowo parsery elementów mają fallback dla wrapperów `div`/`span`:
jeśli sam wrapper nie pasuje do reguły, parser próbuje dopasować pierwszy
obsługiwany element wśród jego bezpośrednich dzieci.

## Przepływ parsowania
1. Parser sekcji dzieli dzieci kontenera na części nagłówkami (`_split_into_parts`).
2. Każda część dostaje `section_id` (anchor nagłówka + normalizacja sluga).
3. Każda część jest przekazywana do parsera niższego poziomu sekcji z tym samym kontekstem.
4. Najniższy poziom (`SubSubSubSectionParser`) parsuje elementy przez rejestr reguł.
