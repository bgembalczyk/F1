from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

from scrapers.base.export.export_helpers import fieldnames_from_first_row
from scrapers.base.export.export_helpers import fieldnames_from_union
from scrapers.base.export.exporters import DataExporter
from scrapers.base.format.formatter_helpers import extract_data
from scrapers.base.normalization import NormalizationRule
from scrapers.base.results import ScrapeResult
from scrapers.base.services.result_normalizer import ScrapeResultNormalizer

if TYPE_CHECKING:
    from scrapers.base.abc import ABCScraper


class ResultExportService:
    def __init__(
        self,
        *,
        normalizer: ScrapeResultNormalizer | None = None,
    ) -> None:
        self._normalizer = normalizer or ScrapeResultNormalizer()

    def to_json(
        self,
        result: ScrapeResult,
        path: str | Path,
        *,
        exporter: DataExporter | None = None,
        indent: int = 2,
        normalize_keys: bool = False,
        normalization_rules: Sequence[NormalizationRule] | None = None,
        include_metadata: bool = False,
    ) -> None:
        normalized = self._normalizer.normalize(
            result,
            normalize_keys=normalize_keys,
            normalization_rules=normalization_rules,
        )
        self._resolve_exporter(exporter).to_json(
            normalized,
            path,
            indent=indent,
            include_metadata=include_metadata,
        )

    def to_csv(
        self,
        result: ScrapeResult,
        path: str | Path,
        *,
        exporter: DataExporter | None = None,
        fieldnames: Sequence[str] | None = None,
        fieldnames_strategy: str = "union",
        normalize_keys: bool = False,
        normalization_rules: Sequence[NormalizationRule] | None = None,
        include_metadata: bool = False,
    ) -> None:
        normalized = self._normalizer.normalize(
            result,
            normalize_keys=normalize_keys,
            normalization_rules=normalization_rules,
        )

        resolved_fieldnames = fieldnames
        if resolved_fieldnames is None:
            data = extract_data(normalized)
            if data:
                if fieldnames_strategy == "union":
                    resolved_fieldnames = fieldnames_from_union(data)
                elif fieldnames_strategy == "first_row":
                    resolved_fieldnames = fieldnames_from_first_row(data)
                else:
                    msg = (
                        "Nieznana strategia fieldnames: "
                        f"{fieldnames_strategy!r}. Dostępne: 'union', 'first_row'."
                    )
                    raise ValueError(msg)

        self._resolve_exporter(exporter).to_csv(
            normalized,
            path,
            fieldnames=resolved_fieldnames,
            include_metadata=include_metadata,
        )

    def export_scraper_result_to_json(
        self,
        scraper: "ABCScraper",
        result: ScrapeResult,
        path: str | Path,
        *,
        indent: int = 2,
        include_metadata: bool = False,
    ) -> None:
        self.to_json(
            result,
            path,
            exporter=scraper.exporter,
            indent=indent,
            include_metadata=include_metadata,
        )

    @staticmethod
    def _resolve_exporter(exporter: DataExporter | None) -> DataExporter:
        return exporter or DataExporter()
