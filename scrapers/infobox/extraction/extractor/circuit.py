from scrapers.infobox.extraction.extractor.contracts import InfoboxExtractor


class CircuitInfoboxExtractor(InfoboxExtractor[BeautifulSoup]):
    def find_infoboxes(self, soup: BeautifulSoup) -> Iterable[BeautifulSoup]:
        return [soup]

    def build_parser(self, *, options: ScraperOptions, url: str) -> SoupParser:
        return F1CircuitInfoboxParser(
            options=options,
            url=url,
        )

    def normalize_result(
        self,
        parsed_records: list[dict[str, Any]],
    ) -> InfoboxExtractionResult:
        return InfoboxExtractionResult(
            records=[dict(record) for record in parsed_records],
        )
