from dataclasses import dataclass
from typing import Any
from typing import Protocol
from typing import runtime_checkable

from scrapers.base.data_extractor import BaseDataExtractor
from scrapers.base.progress import ProgressAdapter
from scrapers.base.progress import TqdmProgressAdapter
from tqdm import tqdm

from infrastructure.http_client.requests_shim.request_error import RequestError
from scrapers.base.data_extractor import BaseDataExtractor
from scrapers.base.errors import DomainParseError
from scrapers.base.errors import ScraperNetworkError
from scrapers.base.errors import ScraperParseError
from scrapers.base.composite_dto import CompositeJSONBoundaryAdapter
from scrapers.base.composite_dto import CompositeRecordDTO
from scrapers.base.composite_dto import DetailRecordDTO
from scrapers.base.composite_dto import ListRecordDTO
from scrapers.base.source_adapter import IterableSourceAdapter
from scrapers.base.source_adapter import MultiIterableSourceAdapter


@runtime_checkable
class ListScraperProtocol(Protocol):
    def fetch(self) -> list[dict[str, Any]]: ...


@runtime_checkable
class SingleScraperProtocol(Protocol):
    def fetch_by_url(self, url: str) -> list[dict[str, Any]]: ...


@dataclass(frozen=True)
class CompositeDataExtractorChildren:
    list_scraper: ListScraperProtocol | list[ListScraperProtocol]
    single_scraper: SingleScraperProtocol
    records_adapter: (
        IterableSourceAdapter[ListRecordDTO]
        | MultiIterableSourceAdapter[ListRecordDTO]
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
        self.json_boundary = CompositeJSONBoundaryAdapter()
        children = self.build_children()
        self.list_scraper = children.list_scraper
        self.single_scraper = children.single_scraper
        self.records_adapter = children.records_adapter

    def build_children(self) -> CompositeDataExtractorChildren:
        msg = "CompositeDataExtractor requires build_children()."
        raise NotImplementedError(msg)

    def get_detail_url(self, _record: ListRecordDTO) -> str | None:
        return None

    def assemble_record(
        self,
        record: ListRecordDTO,
        details: DetailRecordDTO | None,
    ) -> CompositeRecordDTO:
        full_record = record.to_dict()
        full_record["details"] = details.to_dict() if details is not None else None
        return CompositeRecordDTO(data=full_record)

    def fetch(self) -> list[dict[str, Any]]:
        records = self.records_adapter.get()
        complete: list[CompositeRecordDTO] = []

        extractor_name = self.__class__.__name__
        for record in self.progress.wrap(
            records,
            desc=extractor_name,
            unit="item",
        ):
            if not isinstance(record, ListRecordDTO):
                msg = (
                    "Records adapter musi zwracać ListRecordDTO, "
                    f"otrzymano: {type(record).__name__}"
                )
                raise TypeError(msg)

            detail_url = self.get_detail_url(record)
            details: DetailRecordDTO | None = None

            if detail_url:
                try:
                    details_list = self.single_scraper.fetch_by_url(detail_url)
                    details = (
                        self.json_boundary.detail_from_json(details_list[0])
                        if details_list
                        else None
                    )
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

        self._data = [self.json_boundary.output_to_json(record) for record in complete]
        return self._data
