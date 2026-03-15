# Standard parserów Wikipedii i parserów domenowych

## Cel

Ujednolicenie sposobu łączenia parserów niskopoziomowych (`WikiParser.parse(Tag)`) z parserami domenowymi działającymi na całym artykule (`parse_article(BeautifulSoup)`).

## Kontrakty

### 1) `WikiParser`
- Wejście: pojedynczy element `Tag`.
- API: `parse(element: Tag) -> Any`.
- Użycie: parsery struktury HTML Wikipedii (nagłówek, sekcje, elementy).

### 2) `ArticleParser` (parser domenowy)
- Wejście: cały artykuł `BeautifulSoup`.
- API: `parse_article(soup: BeautifulSoup) -> dict | list | None`.
- Użycie: logika domenowa F1 (np. standings, wyniki, infoboksy biznesowe).

### 3) Adaptery
- `WikiParserArticleAdapter`: adaptuje `WikiParser.parse(Tag)` do kontraktu `ArticleParser`.
- `CallableArticleParserAdapter`: adaptuje funkcję `BeautifulSoup -> wynik`.

## Kiedy tworzyć który parser?

## Twórz `WikiParser`, gdy:
- parser dotyczy konkretnego węzła HTML (np. `<table>`, `<div id="bodyContent">`, `<header>`),
- logika jest niezależna od domeny F1,
- parser może być wielokrotnie używany między scraperami.

## Twórz parser domenowy (`ArticleParser`), gdy:
- parser potrzebuje kontekstu całego artykułu,
- łączysz wiele sekcji lub fallbacków,
- wynik ma bezpośrednio odpowiadać rekordowi domenowemu scrapera.

## Jak łączyć parsery

1. W `WikiScraper` zarejestruj etapy parserów domenowych po bazowym etapie Wikipedii.
2. Dla parserów opartych o `Tag` użyj `register_wiki_parser(...)` lub `WikiParserArticleAdapter`.
3. Dla parserów domenowych użyj `register_article_parser(..., target_key=...)`.
4. Dla wielu parserów domenowych (np. sezon) użyj cienkiego pipeline'u (`SeasonParsersPipeline`) i merge do rekordu (`target_key=None`).

## Przykładowy wzorzec

- **Single scraper** tworzy parsery domenowe.
- Rejestruje je przez `register_article_parser`.
- `WikiScraper._parse_soup`:
  - parsuje `header` i `body_content` (jeśli `include_wiki_content=True`),
  - wykonuje etapy domenowe,
  - zwraca jeden rekord z `url` + danymi etapów.

