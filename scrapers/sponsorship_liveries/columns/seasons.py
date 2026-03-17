import re
from typing import TYPE_CHECKING
from typing import Any
from typing import Optional

from models.services.season_service import parse_seasons
from scrapers.base.helpers.links import normalize_links
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.sponsorship_liveries.helpers.constants import YEAR_RE

if TYPE_CHECKING:
    from scrapers.sponsorship_liveries.helpers.paren_classifier import ParenClassifier


class SponsorshipSeasonsColumn(BaseColumn):
    """Season column for sponsorship-livery tables.

    Extends the standard ``SeasonsColumn`` behaviour by also parsing extra
    information that Wikipedia sometimes encodes inside a parenthetical
    directly in the year cell.

    When *team_name* and *classifier* are provided, the parenthetical content
    is sent **exclusively** to the Gemini API for semantic classification.
    The structured result drives the following fields on the record:

    * ``grand_prix_scope`` / ``_season_scoped_gp`` - when Gemini returns
      ``grand_prix`` entries.  The ``_season_scoped_gp`` marker is used by
      :class:`~scrapers.sponsorship_liveries.parsers.section_parser.SponsorshipSectionParser`
      to split any broader overlapping season entry.

    * ``driver`` - when Gemini returns ``driver`` entries.

    * ``car`` - when Gemini returns ``car_model`` entries.

    * ``engine`` - when Gemini returns ``engine_constructor`` entries.

    Classified values are validated against the original cell text before use;
    any value not found in the cell text is treated as a model hallucination and
    discarded.  When no *classifier* is provided, parenthetical content is
    ignored entirely.
    """

    def __init__(
        self,
        *,
        team_name: str | None = None,
        classifier: Optional["ParenClassifier"] = None,
        table_headers: list[str] | None = None,
    ) -> None:
        self._team_name = team_name
        self._classifier = classifier
        self._table_headers = table_headers or []

    def parse(self, ctx: ColumnContext) -> Any:
        return parse_seasons(self._year_only_text(ctx.clean_text or ""))

    def apply(self, ctx: ColumnContext, record: dict[str, Any]) -> None:
        text = ctx.clean_text or ""
        year_text = self._year_only_text(text)
        record[ctx.key] = parse_seasons(year_text)

        paren_match = re.search(r"\(([^)]*)\)", text)
        if not paren_match:
            return
        paren_content = paren_match.group(1).strip()
        if not paren_content:
            return

        # Analizowanie zawartości nawiasów odbywa się wyłącznie przez Gemini API.
        if self._classifier is None:
            return

        links = normalize_links(ctx.links or [])
        non_year_links = [
            lnk for lnk in links if not YEAR_RE.match((lnk.get("text") or "").strip())
        ]

        classification = self._classifier.classify(
            paren_content=paren_content,
            team_name=self._team_name or "",
            year_text=year_text,
            headers=self._table_headers,
        )

        # Filter out hallucinations: only keep values that actually appear in
        # the original cell text.  "GP" is expanded to "Grand Prix" in the
        # normalised text so that a Gemini response of "Chinese Grand Prix"
        # still matches a cell that says "Chinese GP".
        normalised_text = re.sub(
            r"\bGP\b",
            "Grand Prix",
            text,
            flags=re.IGNORECASE,
        ).lower()

        def _filter_present(values: list[str]) -> list[str]:
            return [v for v in values if v.lower() in normalised_text]

        # Categories are applied in priority order and are mutually exclusive:
        # grand_prix_scope > driver > car > engine.
        gp_names: list[str] = _filter_present(classification.get("grand_prix") or [])
        if self._apply_gp_scope(record, gp_names, non_year_links):
            return

        other_links = [lnk for lnk in non_year_links if not self._is_gp_link(lnk)]

        driver_names: list[str] = _filter_present(classification.get("driver") or [])
        if self._apply_classified_field(record, "driver", driver_names, other_links):
            return

        car_names: list[str] = _filter_present(classification.get("car_model") or [])
        if self._apply_classified_field(record, "car", car_names, other_links):
            return

        engine_names: list[str] = _filter_present(
            classification.get("engine_constructor") or [],
        )
        self._apply_classified_field(record, "engine", engine_names, other_links)

    # ------------------------------------------------------------------
    # helpers for apply()
    # ------------------------------------------------------------------

    def _apply_gp_scope(
        self,
        record: dict[str, Any],
        gp_names: list[str],
        non_year_links: list[dict[str, Any]],
    ) -> bool:
        """Apply grand-prix scope to *record* if *gp_names* is non-empty.

        Returns ``True`` when the scope was applied (caller should stop).
        """
        if not gp_names:
            return False
        gp_links = [lnk for lnk in non_year_links if self._is_gp_link(lnk)]
        if gp_links:
            gp_entries = [
                {"text": self._expand_gp_name(lnk), "url": lnk["url"]}
                if lnk.get("url")
                else {"text": self._expand_gp_name(lnk)}
                for lnk in gp_links
            ]
        else:
            gp_entries = [{"text": name} for name in gp_names]
        record["grand_prix_scope"] = {"type": "only", "grand_prix": gp_entries}
        record["_season_scoped_gp"] = True
        return True

    @staticmethod
    def _apply_classified_field(
        record: dict[str, Any],
        field: str,
        names: list[str],
        links: list[dict[str, Any]],
    ) -> bool:
        """Write *field* to *record* from *names* (or *links* when available).

        Returns ``True`` when the field was applied (caller should stop).
        """
        if not names:
            return False
        if links:
            record[field] = [
                {"text": lnk["text"], "url": lnk["url"]}
                if lnk.get("url")
                else {"text": lnk["text"]}
                for lnk in links
            ]
        else:
            record[field] = [{"text": name} for name in names]
        return True

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _year_only_text(text: str) -> str:
        """Strip any trailing parenthetical so only the year part remains."""
        return re.sub(r"\s*\([^)]*\)\s*$", "", text).strip()

    @staticmethod
    def _is_gp_link(link: dict[str, Any]) -> bool:
        text = link.get("text") or ""
        url = link.get("url") or ""
        return bool(re.search(r"grand prix|\bGP\b", text, re.IGNORECASE)) or bool(
            re.search(r"Grand_Prix|grand_prix", url),
        )

    @staticmethod
    def _expand_gp_name(link: dict[str, Any]) -> str:
        """Expand abbreviated GP text: 'Chinese GP' → 'Chinese Grand Prix'."""
        text = link.get("text") or ""
        if re.search(r"\bGP\b", text) and not re.search(
            r"grand prix",
            text,
            re.IGNORECASE,
        ):
            text = re.sub(r"\bGP\b", "Grand Prix", text).strip()
        return text
