from dataclasses import dataclass

from scrapers.errors import DomainParseError


@dataclass(frozen=True)
class MissingSectionError(RuntimeError):
    domain: str
    section_id: str
    candidates: tuple[str, ...]

    def __post_init__(self) -> None:
        super().__init__(self.message)

    @property
    def message(self) -> str:
        candidates_display = ", ".join(repr(candidate) for candidate in self.candidates)
        return (
            "Missing section "
            f"{self.section_id!r} for domain={self.domain!r}. "
            f"Tried: [{candidates_display}]"
        )

    def as_domain_error(self, *, url: str | None = None) -> DomainParseError:
        return DomainParseError(
            "Brak wymaganej sekcji w artykule.",
            url=url,
            section_id=self.section_id,
            cause=self,
        )
