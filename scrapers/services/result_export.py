from collections import defaultdict
from collections.abc import Callable
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from exporters.data import DataExporter
from exporters.helpers import fieldnames_from_first_row
from exporters.helpers import fieldnames_from_union
from scrapers.formatters.helpers import extract_data
from scrapers.normalization_utils import NormalizationRule
from scrapers.normalizers.result import ScrapeResultNormalizer
from scrapers.results import ScrapeResult


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

    @staticmethod
    def _resolve_exporter(exporter: DataExporter | None) -> DataExporter:
        return exporter or DataExporter()

    def export_grouped_json(
        self,
        scraper: Any,
        data: list[dict[str, Any]],
        output_dir: Path,
        key_fn: Callable[[dict[str, Any]], str],
    ) -> None:
        scraper.logger.info("Pobrano rekordów: %s", len(data))
        output_dir.mkdir(parents=True, exist_ok=True)
        exporter = getattr(scraper, "exporter", None)

        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for record in data:
            key = key_fn(record).strip()
            grouped[key if key else "other"].append(record)

        for key, records in grouped.items():
            result = ScrapeResult(
                data=records,
                source_url=getattr(scraper, "url", None),
            )
            self.to_json(result, output_dir / f"{key}.json", exporter=exporter)
