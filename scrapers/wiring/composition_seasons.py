from __future__ import annotations

from dataclasses import dataclass

from scrapers.domain_parsing_policy import DomainParsingPolicy
from scrapers.options import ScraperOptions
from scrapers.pipeline_seasons import SeasonParsingComponentsBuilder
from scrapers.pipeline_seasons import SeasonSectionPipeline
from scrapers.pipeline_seasons import SeasonYearResolver
from scrapers.services.domain_record.season import SeasonDomainRecordService
from scrapers.services.section.extraction.season_text import (
    SeasonTextSectionExtractionService,
)
from scrapers.services.section.factories.section_service_factory import (
    SectionServiceFactory,
)


@dataclass(frozen=True, slots=True)
class SeasonScraperDependencies:
    season_year_resolver: SeasonYearResolver
    season_pipeline: SeasonSectionPipeline
    domain_record_service: SeasonDomainRecordService


@dataclass(frozen=True, slots=True)
class SeasonScraperCompositionFactory:
    """Factory budująca komplet zależności dla SingleSeasonScraper."""

    test_mode: bool = False
    season_year_resolver: SeasonYearResolver | None = None
    parser_set_builder: SeasonParsingComponentsBuilder | None = None
    season_pipeline: SeasonSectionPipeline | None = None
    parsing_policy: DomainParsingPolicy | None = None
    text_sections_service_factory: (
        SectionServiceFactory[SeasonTextSectionExtractionService] | None
    ) = None
    domain_record_service: SeasonDomainRecordService | None = None

    @classmethod
    def for_tests(
        cls,
        *,
        season_year_resolver: SeasonYearResolver | None = None,
        parser_set_builder: SeasonParsingComponentsBuilder | None = None,
        season_pipeline: SeasonSectionPipeline | None = None,
        parsing_policy: DomainParsingPolicy | None = None,
        text_sections_service_factory: (
            SectionServiceFactory[SeasonTextSectionExtractionService] | None
        ) = None,
        domain_record_service: SeasonDomainRecordService | None = None,
    ) -> SeasonScraperCompositionFactory:
        return cls(
            test_mode=True,
            season_year_resolver=season_year_resolver,
            parser_set_builder=parser_set_builder,
            season_pipeline=season_pipeline,
            parsing_policy=parsing_policy,
            text_sections_service_factory=text_sections_service_factory,
            domain_record_service=domain_record_service,
        )

    def build(
        self,
        *,
        options: ScraperOptions | None = None,
    ) -> SeasonScraperDependencies:
        season_year_resolver = self.season_year_resolver or SeasonYearResolver()

        parser_set_builder = self.parser_set_builder or SeasonParsingComponentsBuilder(
            options=options,
            include_urls=(options.include_urls if options is not None else False),
            policy=self.parsing_policy,
        )

        season_pipeline = self.season_pipeline or SeasonSectionPipeline(
            parser_set_builder=parser_set_builder,
            text_sections_service_factory=self.text_sections_service_factory,
        )

        domain_record_service = (
            self.domain_record_service or SeasonDomainRecordService()
        )

        return SeasonScraperDependencies(
            season_year_resolver=season_year_resolver,
            season_pipeline=season_pipeline,
            domain_record_service=domain_record_service,
        )
