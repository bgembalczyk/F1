from collections.abc import Callable
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import TypeVar
from uuid import uuid4

from bs4 import BeautifulSoup
from bs4 import Tag

from infrastructure.helpers import init_scraper_options
from infrastructure.http.policies.http import HttpPolicy
from models.data.wiki_parser import WikiParserData
from models.payload import WikiParsedPayload
from scrapers.adapters.result_tabular import ResultTabularAdapter
from scrapers.component_metadata_wiki import validate_metadata_for_component_class
from scrapers.errors.base import ScraperError
from scrapers.errors.network import ScraperNetworkError
from scrapers.errors.parse import ScraperParseError
from scrapers.helpers.url import normalize_url
from scrapers.logging import get_logger
from scrapers.options import ScraperOptions
from scrapers.parsers.rules import ParserRule
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.wiki.body_content_assembler import BodyContentAssembler
from scrapers.parsers.wiki.element import ElementParseInput
from scrapers.parsers.wiki.element import ElementRegistry
from scrapers.parsers.wiki.element import WikiElementSet
from scrapers.parsers.wiki.element import build_wikipedia_element_registry
from scrapers.parsers.wiki.element_dispatcher import ElementDispatcher
from scrapers.parsers.wiki.element_factory import build_default_wiki_element_parsers
from scrapers.parsers.wiki.element_payload_factory import ElementParseResult
from scrapers.parsers.wiki.header import HeaderParser
from scrapers.post_processors import apply_post_processors
from scrapers.results import ScrapeResult
from scrapers.runners.pipeline_runner import NormalizedRecord
from scrapers.runners.pipeline_runner import RawRecord
from scrapers.scraper_components import ErrorPolicy
from scrapers.scraper_components import PipelineOrchestrator
from scrapers.scraper_components import QualityReportService
from scrapers.scraper_components import RuntimeInitializer
from scrapers.services.capability_services import ExportCapabilityService
from scrapers.services.capability_services import ReportingCapabilityService
from scrapers.services.capability_services import ValidationCapabilityService
from scrapers.services.result_export import ResultExportService
from scrapers.transformers.helpers import apply_transformers
from validation.validator_base import ExportRecord

if TYPE_CHECKING:
    from scrapers.parsers.wiki.recursive import RecursiveSectionParser

T = TypeVar("T")


class WikiScraper:
    """Bazowy scraper artykułów Wikipedii z pełnym pipeline'em pobierania i parsowania.

    Łączy w sobie lifecycle scrapera (fetch/parse/build_result), inicjalizację
    stanu (opcje, logger, walidacja), logikę orkiestracji pipeline'u oraz
    specyficzne dla Wikipedii parsery stron:

    - HeaderParser - przetwarza nagłówek strony
      (<header class="mw-body-header vector-page-titlebar no-font-mode-scale">)
    - BodyContentAssembler - przetwarza główną treść strony
      (<div id="bodyContent">)

    Pobieranie HTML odbywa się za pośrednictwem source_adapter (HtmlFetcher),
    który po swojej stronie decyduje, czy dane są pobierane bezpośrednio z sieci,
    czy zwracane z cache.

    ListScrapery i SingleScrapery dziedziczą po WikiScraperze i nadpisują
    metodę _parse_soup, korzystając ze swoich wyspecjalizowanych parserów.

    Użycie jako samodzielny scraper artykułu Wikipedii:
        scraper = WikiScraper()
        result = scraper.scrape("https://en.wikipedia.org/wiki/Lewis_Hamilton")
    """

    #: URL artykułu Wikipedii (ustawiany dynamicznie lub przez podklasy)
    url: str = ""
    scraper_kind: str = "single"

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        header_parser: HeaderParser | None = None,
        body_content_parser: BodyContentAssembler | None = None,
        element_parsers: WikiElementSet | None = None,
    ) -> None:
        """Inicjalizuje WikiScraper.

        Args:
            options: Opcje scrapera (HTTP, cache, eksport itp.).
                Domyślnie tworzy nowe ScraperOptions.
            header_parser: Parser nagłówka strony. Domyślnie tworzy nowy HeaderParser.
            body_content_parser: Parser treści strony. Domyślnie tworzy nowy
                BodyContentAssembler.
            element_parsers: Zestaw parserów elementów Wiki. Domyślnie tworzy
                standardowe parsery.
        """
        validate_metadata_for_component_class(type(self))
        options = init_scraper_options(options)

        # Core state (previously BaseScraperCore)
        self.include_urls = options.include_urls
        self.normalize_empty_values = options.normalize_empty_values
        self.logger = get_logger(self.__class__.__name__)
        self._run_id: str | None = options.run_id
        self.debug_dir = Path(options.debug_dir) if options.debug_dir else None
        self._validation_mode = "soft"
        self._data: list[ExportRecord] | None = None

        # Pipeline wiring (previously ABCScraper)
        self._quality_report_enabled = options.quality_report
        self._debug_diff_domains = options.debug_diff_domains
        self._debug_diff_record_ids = options.debug_diff_record_ids
        self._initialize_runtime(options)
        self._initialize_quality_reporting()
        self._initialize_validation_capability()
        self._initialize_export_capability()
        self._validation_service.assert_mode_supported()
        self._initialize_pipeline_orchestrator()

        # Wiki element parsers
        resolved_element_parsers = (
            element_parsers or build_default_wiki_element_parsers()
        )
        self.infobox_parser = resolved_element_parsers.infobox_parser
        self.list_parser = resolved_element_parsers.list_parser
        self.table_parser = resolved_element_parsers.table_parser
        self.navbox_parser = resolved_element_parsers.navbox_parser
        self.references_parser = resolved_element_parsers.references_parser
        self._paragraph_parser = resolved_element_parsers.paragraph_parser
        self._figure_parser = resolved_element_parsers.figure_parser
        resolved_registry = build_wikipedia_element_registry(
            parsers=resolved_element_parsers,
        )
        self.element_registry: ElementRegistry = resolved_registry
        self.dispatcher = ElementDispatcher(registry=resolved_registry)
        self._parser_rules: list[ParserRule] = []

        # Wiki-specific parsers
        self.header_parser = header_parser or HeaderParser()
        self.body_content_parser = body_content_parser or BodyContentAssembler(
            element_parsers=resolved_element_parsers,
        )
        self.section_parser: RecursiveSectionParser = (
            self.body_content_parser.content_text_parser.section_parser
        )

    # ---------- Runtime initialization (previously FetchOrchestrationMixin) ----------

    def _initialize_runtime(self, options: ScraperOptions) -> None:
        runtime = RuntimeInitializer(
            resolve_http_policy=self.get_http_policy,
        ).initialize(
            options=options,
            logger=self.logger,
            normalize_empty_values=self.normalize_empty_values,
            default_validator=getattr(self, "default_validator", None),
        )
        self.http_policy = runtime.http_policy
        self.source_adapter = runtime.source_adapter
        self.fetcher = runtime.fetcher
        self.parser = runtime.parser
        self.exporter = runtime.exporter
        self._record_normalizer = runtime.record_normalizer
        self.transformers = runtime.transformers
        self.post_processors = runtime.post_processors
        self.validator = runtime.validator
        self._validation_mode = runtime.validation_mode
        self._error_policy = self._create_error_policy(runtime=runtime, options=options)

    def _create_error_policy(
        self,
        *,
        runtime,
        options: ScraperOptions,
    ) -> ErrorPolicy:
        return ErrorPolicy(
            error_handler=runtime.error_handler,
            logger=self.logger,
            get_url=lambda: getattr(self, "url", None),
            policy=options.error_policy,
            retry_attempts=options.error_retry_attempts,
        )

    def _initialize_pipeline_orchestrator(self) -> None:
        self._pipeline_orchestrator = self._create_pipeline_orchestrator()

    def _create_pipeline_orchestrator(self) -> PipelineOrchestrator:
        return PipelineOrchestrator(
            logger=self.logger,
            quality_report_service=self._quality_report_service,
            error_policy=self._error_policy,
            parse_records=self.parse_soup,
            normalize_records=self._normalize_pipeline_records,
            transform_records=self._apply_transformers,
            validate_records=self.validate_records,
            post_process_records=self.post_process_records,
        )

    def fetch(self) -> list[ExportRecord]:
        self._validate_fetch_url()
        run_id = self._start_run()
        data = self._pipeline_orchestrator.run_fetch(
            run_id=run_id,
            download_html=self._download,
        )
        if data is None:
            self._data = []
            return self._data

        self._data = data
        self.logger.debug("Scrape run %s finished", run_id)
        return self._data

    def _validate_fetch_url(self) -> None:
        if getattr(self, "url", None):
            return
        msg = "Scraper.url musi być ustawiony przed fetch()."
        raise ValueError(msg)

    def _start_run(self) -> str:
        run_id = self._run_id or uuid4().hex
        self._run_id = run_id
        self._error_policy.set_run_id(run_id)
        self._reporting_service.set_run_context(run_id)
        self._reporting_service.log_start(self.url)
        return run_id

    def _normalize_pipeline_records(
        self,
        records: list[RawRecord],
    ) -> list[NormalizedRecord]:
        return self._record_normalizer.normalize(records)

    # ---------- validation_mode property (previously BaseScraperCore) ----------

    @property
    def validation_mode(self) -> str:
        return self._validation_mode

    @validation_mode.setter
    def validation_mode(self, value: str) -> None:
        self._validation_mode = value

    # ---------- Quality reporting (previously ABCScraper) ----------

    def _initialize_quality_reporting(self) -> None:
        self._quality_report_service = self._create_quality_report_service()
        self._reporting_service = ReportingCapabilityService(
            quality_report_service=self._quality_report_service,
            logger=self.logger,
            run_id_provider=lambda: self._run_id,
        )

    def _initialize_validation_capability(self) -> None:
        self._validation_service = ValidationCapabilityService(
            validation_mode=self.validation_mode,
            validator=self.validator,
            logger=self.logger,
            url_provider=lambda: getattr(self, "url", None),
            write_quality_report=self._write_quality_report,
            validation_runner_factory=PipelineOrchestrator.build_validation_runner,
        )

    def _initialize_export_capability(self) -> None:
        self.result_export_service = ResultExportService()
        self.result_tabular_adapter = ResultTabularAdapter()
        self._export_service = ExportCapabilityService(
            result_export_service=self.result_export_service,
            result_tabular_adapter=self.result_tabular_adapter,
            fetch_data=self.get_data,
            source_url_provider=lambda: getattr(self, "url", None),
            exporter_provider=lambda: self.exporter,
        )

    # ---------- High-level API (previously ABCScraper) ----------

    def get_data(self) -> list[ExportRecord]:
        if self._data is None:
            return self.fetch()
        return self._data

    def validate_records(self, records: list[ExportRecord]) -> list[ExportRecord]:
        self._validation_service.validation_mode = self.validation_mode
        self._validation_service.validator = self.validator
        return self._validation_service.validate_records(records)

    def build_result(self, data: list[ExportRecord] | None = None) -> ScrapeResult:
        return self._export_service.build_result(data)

    def to_json(
        self,
        path: str | Path,
        *,
        indent: int = 2,
        include_metadata: bool = False,
    ) -> None:
        self._export_service.to_json(
            path,
            indent=indent,
            include_metadata=include_metadata,
        )

    def to_csv(
        self,
        path: str | Path,
        *,
        fieldnames: Sequence[str] | None = None,
        fieldnames_strategy: str = "union",
        include_metadata: bool = False,
    ) -> None:
        self._export_service.to_csv(
            path,
            fieldnames=fieldnames,
            fieldnames_strategy=fieldnames_strategy,
            include_metadata=include_metadata,
        )

    def to_dataframe(self):
        return self._export_service.to_dataframe()

    def _download(self) -> str:
        return self.fetch_html(self.url)

    def fetch_html(self, url: str) -> str:
        return self.source_adapter.get(url)

    def parse_records(self, _soup: BeautifulSoup) -> list[RawRecord]:
        msg = (
            f"{self.__class__.__name__} must implement parse_records() "
            "or override parse()."
        )
        raise NotImplementedError(msg)

    def parse(self, soup: BeautifulSoup) -> list[RawRecord]:
        if self.parser is not None:
            return self.parser.parse(soup)

        parse_impl = type(self).parse_records
        if parse_impl is not WikiScraper.parse_records:
            return self.parse_records(soup)

        self.logger.debug(
            "No parser/parse_records implementation for %s; returning empty list.",
            self.__class__.__name__,
        )
        return []

    def parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return self._parse_soup(soup)

    @staticmethod
    def to_export_records(records: list[NormalizedRecord]) -> list[ExportRecord]:
        return records

    def post_process_records(self, records: list[ExportRecord]) -> list[ExportRecord]:
        processed = apply_post_processors(
            self.post_processors,
            records,
            logger=self.logger,
        )
        self.logger.debug(
            "Post-process records: %d -> %d",
            len(records),
            len(processed),
        )
        return processed

    def _create_quality_report_service(self) -> QualityReportService:
        return QualityReportService(
            enabled=self._quality_report_enabled,
            debug_dir=self.debug_dir,
            run_id=self._run_id,
            source_metadata_provider=self._source_metadata,
            logger=self.logger,
            validator_provider=lambda: self.validator,
            debug_diff_domains=self._debug_diff_domains,
            debug_diff_record_ids=self._debug_diff_record_ids,
        )

    def _write_step_quality_report(
        self,
        *,
        step_name: str,
        records: list[dict[str, object]],
    ) -> None:
        self._reporting_service.write_step_quality_report(
            step_name=step_name,
            records=records,
        )

    def _write_quality_report(self) -> None:
        self._reporting_service.write_quality_report()

    def _source_metadata(self) -> dict[str, object]:
        return {
            "domain": self.__module__.split(".")[1]
            if "." in self.__module__
            else self.__module__,
            "scraper": self.__class__.__name__,
            "scraper_kind": getattr(self, "scraper_kind", "single"),
            "url": getattr(self, "url", ""),
        }

    def _apply_transformers(self, records: list[ExportRecord]) -> list[ExportRecord]:
        return apply_transformers(self.transformers, records, logger=self.logger)

    def _full_url(self, href: str) -> str | None:
        return normalize_url(self.url, href)

    def get_http_policy(self, options: ScraperOptions) -> HttpPolicy:
        return options.resolve_http_policy()

    def _wrap_network_error(self, exc: Exception) -> ScraperNetworkError:
        return self._error_policy.wrap_network(exc)

    def _wrap_parse_error(self, exc: Exception) -> ScraperParseError:
        return self._error_policy.wrap_parse(exc)

    def _handle_scraper_error(self, error: ScraperError) -> bool:
        return self._error_policy.handle(error)

    # ---------- Wiki-specific methods ----------

    def scrape(self, url: str) -> dict[str, Any]:
        """Pobiera i parsuje artykuł Wikipedii pod podanym adresem URL.

        Args:
            url: Adres URL artykułu Wikipedii.

        Returns:
            Słownik z:
            - 'url': podany adres URL
            - 'header': wyniki parsowania nagłówka strony
            - 'body_content': wyniki parsowania treści strony
            Lub pusty słownik, gdy nie udało się pobrać/sparsować.
        """
        self.url = url
        records = self.fetch()
        return records[0] if records else {}

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        """Domyślne parsowanie strony Wikipedii.

        Korzysta z HeaderParser i BodyContentAssembler.
        Podklasy (ListScrapery, SingleScrapery) nadpisują tę metodę.

        Args:
            soup: Sparsowany HTML jako obiekt BeautifulSoup.

        Returns:
            Lista z jednym słownikiem zawierającym dane ze strony.
        """
        result: dict[str, Any] = {
            "url": self.url,
            "header": None,
            "body_content": None,
        }

        header_el = HeaderParser.find_header(soup)
        if header_el is not None:
            result["header"] = self.header_parser.parse(header_el)

        body_content_el = BodyContentAssembler.find_body_content(soup)
        if body_content_el is not None:
            result["body_content"] = self.body_content_parser.parse(body_content_el)

        return [result]

    # ---------- Element parsing (previously WikiElementParsingMixin) ----------

    @staticmethod
    def _get_classes(el: Tag) -> list[str]:
        classes = el.get("class") or []
        if isinstance(classes, str):
            return classes.split()
        return list(classes)

    def register_parser_rule(
        self,
        *,
        predicate: Callable[[Tag], bool],
        parser: Callable[[Tag], WikiParserData],
        result_type: str,
        priority: int | None = None,
    ) -> None:
        rule = ParserRule(predicate=predicate, parser=parser, result_type=result_type)
        if priority is None:
            self._parser_rules.append(rule)
            return
        index = max(0, min(priority, len(self._parser_rules)))
        self._parser_rules.insert(index, rule)

    @staticmethod
    def _has_infobox_class(classes: object) -> bool:
        if not classes:
            return False
        if isinstance(classes, str):
            classes = classes.split()
        try:
            return "infobox" in list(classes)
        except TypeError:
            return False

    def parse_elements(
        self,
        elements: list[Tag],
        *,
        section_context: SectionExtractionContext,
    ) -> list[WikiParsedPayload]:
        result: list[WikiParsedPayload] = []
        for el in elements:
            result.extend(
                self._parse_element_list(el, section_context=section_context),
            )
        return result

    def _parse_element_list(
        self,
        el: Tag,
        *,
        section_context: SectionExtractionContext,
    ) -> list[WikiParsedPayload]:
        parsed = self._parse_element(el, section_context=section_context)
        if parsed is not None:
            classes = self._get_classes(el)
            if (
                parsed.get("kind") == "paragraph"
                and isinstance(parsed.get("data"), dict)
                and (
                    not str(parsed["data"].get("text", "")).strip()
                    or "mw-empty-elt" in classes
                )
            ):
                nested_results = self._parse_nested_elements(
                    el,
                    section_context=section_context,
                )
                if nested_results:
                    return nested_results
            return [parsed]

        return self._parse_nested_elements(el, section_context=section_context)

    def _parse_nested_elements(
        self,
        el: Tag,
        *,
        section_context: SectionExtractionContext,
    ) -> list[WikiParsedPayload]:
        nested_results: list[WikiParsedPayload] = []
        for nested_el in self._iter_direct_child_tags(el):
            nested_results.extend(
                self._parse_element_list(
                    nested_el,
                    section_context=section_context,
                ),
            )
        return nested_results

    def _parse_element(
        self,
        el: Tag,
        *,
        section_context: SectionExtractionContext,
    ) -> WikiParsedPayload | None:
        for rule in self._parser_rules:
            if rule.predicate(el):
                return self._build_parsed_payload(
                    el=el,
                    rule=rule,
                    section_context=section_context,
                )

        parse_input = ElementParseInput(
            tag=el,
            metadata=section_context.html_metadata,
            section_context=section_context,
        )
        return self.dispatcher.dispatch(
            parse_input=parse_input,
            section_context=section_context,
        )

    @staticmethod
    def _iter_direct_child_tags(element: Tag) -> list[Tag]:
        return [
            child
            for child in element.find_all(recursive=False)
            if isinstance(child, Tag)
        ]

    def _build_parsed_payload(
        self,
        *,
        el: Tag,
        rule: ParserRule,
        section_context: SectionExtractionContext,
    ) -> WikiParsedPayload:
        parse_result = ElementParseResult(
            element_type=rule.result_type,
            payload=rule.parser(el),
            raw_html_fragment=str(el),
            section_id=section_context.section_id,
            confidence=1.0,
        )
        payload = self.dispatcher.payload_factory.create(parse_result)
        if payload is None:
            return {
                "kind": rule.result_type,
                "source_section_id": section_context.section_id,
                "confidence": 1.0,
                "raw_html_fragment": str(el),
                "data": rule.parser(el),
                "type": rule.result_type,
            }
        return payload
