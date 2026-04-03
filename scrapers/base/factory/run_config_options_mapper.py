from dataclasses import dataclass

from scrapers.base.options import ScraperOptions
from scrapers.base.run_config import RunConfig


@dataclass(frozen=True)
class RunConfigOptionsMapper:
    """Jawne mapowanie RunConfig -> ScraperOptions."""

    def apply(
        self,
        *,
        run_config: RunConfig,
        options: ScraperOptions,
        run_id: str,
    ) -> None:
        self._apply_if_present(options, "debug_dir", run_config.debug_dir)
        self._apply_if_present(options.cache, "cache_dir", run_config.cache_dir)
        self._apply_if_present(options.cache, "cache_ttl", run_config.cache_ttl)
        self._apply_if_present(options.cache, "cache_adapter", run_config.cache_adapter)
        self._apply_if_present(options.http, "timeout", run_config.http_timeout)
        self._apply_if_present(options.http, "retries", run_config.http_retries)
        self._apply_if_present(
            options.http,
            "backoff_seconds",
            run_config.http_backoff_seconds,
        )

        options.run_id = run_id
        options.quality_report = run_config.quality_report
        options.error_report = run_config.error_report

    @staticmethod
    def _apply_if_present(target: object, name: str, value: object) -> None:
        if value is not None:
            setattr(target, name, value)
