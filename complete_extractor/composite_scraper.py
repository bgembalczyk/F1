from complete_extractor.base import CompositeDataExtractorChildren
from complete_extractor.base import CompleteExtractorBase as CompositeDataExtractor
from complete_extractor.base import ListScraperProtocol
from complete_extractor.base import SingleScraperProtocol

__all__ = [
    "CompositeDataExtractor",
    "CompositeDataExtractorChildren",
    "ListScraperProtocol",
    "SingleScraperProtocol",
]
    def __init__(
        self,
        *,
        options,
        progress: ProgressAdapter | None = None,
    ) -> None:
        super().__init__(options=options)
        self.options = options
        self.progress = progress or TqdmProgressAdapter()
        children = self.build_children()
        self.list_scraper = children.list_scraper
        self.single_scraper = children.single_scraper
        self.records_adapter = children.records_adapter

    def build_children(self) -> CompositeDataExtractorChildren:
        msg = "CompositeDataExtractor requires build_children()."
        raise NotImplementedError(msg)

    def get_detail_url(self, _record: dict[str, Any]) -> str | None:
        return None

    def assemble_record(
        self,
        record: dict[str, Any],
        details: dict[str, Any] | None,
    ) -> dict[str, Any]:
        full_record = dict(record)
        full_record["details"] = details
        return full_record

    def fetch(self) -> list[dict[str, Any]]:
        records = self.records_adapter.get()
        complete: list[dict[str, Any]] = []

        extractor_name = self.__class__.__name__
        wrapped_records = self._wrap_records_with_progress(
            records,
            desc=extractor_name,
            unit="item",
        )
        for record in wrapped_records:
            if not isinstance(record, dict):
                msg = (
                    "Records adapter musi zwracać dict, "
                    f"otrzymano: {type(record).__name__}"
                )
                raise TypeError(msg)

            detail_url = self.get_detail_url(record)
            details: dict[str, Any] | None = None

            if detail_url:
                try:
                    details_list = self.single_scraper.extract_by_url(detail_url)
                    details = details_list[0] if details_list else None
                except (
                    RequestError,
                    ScraperNetworkError,
                    ScraperParseError,
                    DomainParseError,
                ):
                    self.logger.exception(
                        "Nie udało się pobrać szczegółów rekordu (url=%s).",
                        detail_url,
                    )

            complete.append(self.assemble_record(record, details))

        self._data = complete
        return self._data

    def _wrap_records_with_progress(
        self,
        records,
        *,
        desc: str,
        unit: str,
    ):
        """Wrap records with progress adapter preserving backward compatibility."""

        wrap = self.progress.wrap
        try:
            return wrap(records, desc=desc, unit=unit)
        except TypeError:
            pass

        try:
            return wrap(records, _desc=desc, _unit=unit)
        except TypeError:
            pass

        try:
            return wrap(records, desc, unit)
        except TypeError:
            return wrap(records)
