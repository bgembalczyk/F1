# Spec ról: Parser / Extractor / Mapper-Factory (Wiki scraping)

## 1) Kontrakty ról

### Parser
- Odpowiada za transformację *raw input* (`raw_html_fragment`) do danych strukturalnych.
- Kontrakt kanoniczny:

```python
parse(raw_html_fragment) -> structured_data
```

- Parser nie wykonuje HTTP/file I/O i nie buduje rekordów domenowych end-to-end.
- Parser jest przypięty do konkretnego elementu HTML (np. tabela wiki, infobox, lista, sekcja).

### Extractor
- Odpowiada za pobieranie i wycinanie fragmentów z większego dokumentu.
- Typowe zadania:
  - lokalizacja sekcji po `id` / nagłówkach,
  - wybór właściwych fragmentów DOM,
  - przygotowanie inputu dla parserów elementowych.
- Extractor nie mapuje bezpośrednio na model domenowy (to rola mappera/fabryki).

### Mapper / Factory
- Odpowiada za mapowanie danych strukturalnych (`structured_data`) do rekordów domenowych.
- Typowe zadania:
  - walidacja i normalizacja pól domenowych,
  - tworzenie rekordów (`dict` domenowy / dataclass / model),
  - enkapsulacja reguł mapowania i fallbacków.

## 2) Reguła zależności (warstwowanie)

**Reguła nadrzędna:** domena nie zależy bezpośrednio od surowego HTML.

Dozwolony przepływ:

```text
Raw HTML -> Extractor -> Element Parser(parse) -> structured_data -> Mapper/Factory -> domain record
```

Niedozwolone:
- logika domenowa oparta o `BeautifulSoup`/`Tag` bezpośrednio,
- mapowanie domenowe wykonywane „w środku” parsera HTML,
- service domenowy, który używa surowych selektorów HTML zamiast parsera elementowego.

## 3) Uzgodnienie nazw klas do roli (zakres: `scrapers/parsers`, `scrapers/services`, `scrapers/adapters`)

Przyjęta reguła:
- klasy parsujące mają sufiks `Parser`,
- klasy wycinające/zbierające mają sufiks `Extractor` lub `ExtractionService` (gdy to orkiestracja extraction use-case),
- klasy mapujące/tworzące rekordy mają sufiks `Mapper` albo `Factory`,
- klasy translacyjne między kontraktami mają sufiks `Adapter`,
- klasy use-case mają sufiks `Service`.
- API publiczne: `Parser` udostępnia `parse(...)`, a `Extractor` udostępnia `extract(...)`.

W ramach bieżącego porządkowania wykonano rename:
- `SeasonTableService` -> `SeasonTableParser` (`scrapers/parsers/seasons/table.py`) — klasa realizuje operacje `parse_*`, więc semantycznie jest parserem.

## 4) Checklista review (gate)

- [ ] Czy `Parser` implementuje `parse(...)`?
- [ ] Czy nazwa klasy odpowiada roli (`Parser` / `Extractor` / `Mapper` / `Factory` / `Adapter` / `Service`)?
- [ ] Czy parser jest przypięty do konkretnego elementu HTML Wikipedii?
- [ ] Czy logika domenowa korzysta z parserów elementowych + mapperów/fabryk zamiast bezpośrednio z raw HTML?
- [ ] Czy extractor tylko wybiera/przygotowuje fragmenty, a nie mapuje rekordów domenowych?
