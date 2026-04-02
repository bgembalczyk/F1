from __future__ import annotations

from dataclasses import dataclass

from scrapers.cli.legacy_registry import DOMAIN_COMMANDS
from scrapers.cli.legacy_registry import SCRAPER_MODULE_PATH_PARTS


@dataclass(frozen=True)
class DeprecationPolicy:
    transitional_release_window: tuple[str, ...]
    removal_target: str
    canonical_replacement_template: str

    @property
    def transition_release_count(self) -> int:
        return len(self.transitional_release_window)

    def render_runtime_message(
        self,
        *,
        module_path: str,
        replacement_module: str,
        domain_hint: str = "",
    ) -> str:
        return (
            f"{module_path} is deprecated and scheduled for removal after "
            f"{self.transition_release_count} transitional releases "
            f"(removal target: {self.removal_target}); "
            f"use `{self.canonical_replacement_template.format(replacement_module=replacement_module)}`"
            f"{domain_hint}."
        )

    def render_schedule_markdown(self) -> str:
        r0, r1 = self.transitional_release_window
        return "\n".join(
            (
                f"- **{r0} (aktualna wersja):** legacy moduły działają, ale emitują `DeprecationWarning`.",
                f"- **{r1} (kolejna wersja):** legacy moduły nadal działają, warning pozostaje obowiązkowy.",
                f"- **{self.removal_target} (druga wersja przejściowa):** legacy moduły są usuwane.",
                "",
                "Runtime warning ma teraz jawny komunikat o oknie migracji:",
                (
                    "- `scheduled for removal after "
                    f"{self.transition_release_count} transitional releases "
                    f"(removal target: {self.removal_target})`"
                ),
                "- oraz wskazanie canonical komendy `python -m scrapers.cli run <new_module>`.",
            )
        )


DEPRECATION_POLICY = DeprecationPolicy(
    transitional_release_window=("R0", "R1"),
    removal_target="R2",
    canonical_replacement_template="python -m scrapers.cli run {replacement_module}",
)


def deprecated_runtime_message(
    module_path: str,
    *,
    replacement_module_path: str | None,
) -> str:
    replacement_module = replacement_module_path or module_path
    domain_hint = ""
    parts = replacement_module.split(".")
    if (
        len(parts) >= SCRAPER_MODULE_PATH_PARTS
        and parts[0] == "scrapers"
        and parts[-1] == "entrypoint"
    ):
        domain_name = parts[1]
        if domain_name in DOMAIN_COMMANDS:
            domain_hint = f" or `python -m scrapers.cli domain {domain_name}`"
    return DEPRECATION_POLICY.render_runtime_message(
        module_path=module_path,
        replacement_module=replacement_module,
        domain_hint=domain_hint,
    )


def render_deprecation_schedule_markdown() -> str:
    return DEPRECATION_POLICY.render_schedule_markdown()
