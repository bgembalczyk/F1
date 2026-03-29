from dataclasses import dataclass
from typing import Any

from scrapers.base.data_extractor import BaseDataExtractor
from scrapers.base.progress import ProgressAdapter
from scrapers.base.progress import TqdmProgressAdapter
from scrapers.base.source_adapter import IterableSourceAdapter
from scrapers.base.source_adapter import MultiIterableSourceAdapter


@dataclass(frozen=True)
class CompositeDataExtractorChildren:
    list_scraper: Any
    single_scraper: Any
    records_adapter: (
        IterableSourceAdapter[dict[str, Any]]
        | MultiIterableSourceAdapter[dict[str, Any]]
    )


class CompositeDataExtractor(BaseDataExtractor):
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
        for record in self.progress.wrap(
            records,
            desc=extractor_name,
            unit="item",
        ):
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
                    details_list = self.single_scraper.fetch_by_url(detail_url)
                    details = details_list[0] if details_list else None
                except Exception:
                    self.logger.exception(
                        "Nie udało się pobrać szczegółów rekordu (url=%s).",
                        detail_url,
                    )

            complete.append(self.assemble_record(record, details))

        self._data = complete
        return self._data
