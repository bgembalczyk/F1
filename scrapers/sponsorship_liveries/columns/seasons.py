import re
from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from scrapers.base.helpers.links import normalize_links
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn
from models.services.season_service import SeasonService

if TYPE_CHECKING:
    from scrapers.sponsorship_liveries.helpers.paren_classifier import ParenClassifier


class SponsorshipSeasonsColumn(BaseColumn):
    """Season column for sponsorship-livery tables.

    Extends the standard ``SeasonsColumn`` behaviour by also parsing extra
    information that Wikipedia sometimes encodes inside a parenthetical
    directly in the year cell:

    * ``(only <GP>)``   → sets ``grand_prix_scope`` on the record and marks
      the record with ``_season_scoped_gp = True`` so that the post-processing
      step in :class:`~scrapers.sponsorship_liveries.parsers.section_parser.SponsorshipSectionParser`
      can split any broader overlapping season entry.

    * ``(<Driver>'s car)`` → sets ``driver`` on the record with the linked
      driver info.  These entries are independent of the GP-scope mechanism.

    When *team_name* and *classifier* are provided, any parenthetical that is
    not fully handled by the heuristic logic above is additionally sent to
    Gemini API for semantic classification.  The structured result is stored
    under ``paren_classification`` in the record so that downstream code can
    use it for more precise scope assignments.
    """

    # Year-only link text – e.g. "2004" or "2005"
    _YEAR_RE = re.compile(r"^\d{4}$")

    def __init__(
            self,
            *,
            team_name: Optional[str] = None,
            classifier: Optional["ParenClassifier"] = None,
            table_headers: Optional[List[str]] = None,
    ) -> None:
        self._team_name = team_name
        self._classifier = classifier
        self._table_headers = table_headers or []

    def parse(self, ctx: ColumnContext) -> Any:
        return SeasonService.parse_seasons(self._year_only_text(ctx.clean_text or ""))

    def apply(self, ctx: ColumnContext, record: Dict[str, Any]) -> None:
        text = ctx.clean_text or ""
        year_text = self._year_only_text(text)
        record[ctx.key] = SeasonService.parse_seasons(year_text)

        paren_match = re.search(r"\(([^)]*)\)", text)
        if not paren_match:
            return
        paren_content = paren_match.group(1).strip()
        if not paren_content:
            return

        links = normalize_links(ctx.links or [])
        non_year_links = [
            lnk for lnk in links
            if not self._YEAR_RE.match((lnk.get("text") or "").strip())
        ]

        has_only = bool(re.search(r"\bonly\b", paren_content, re.IGNORECASE))
        has_gp = bool(
            re.search(r"grand prix|\bGP\b", paren_content, re.IGNORECASE),
        )

        gp_links = [lnk for lnk in non_year_links if self._is_gp_link(lnk)]
        driver_links = [lnk for lnk in non_year_links if not self._is_gp_link(lnk)]

        if (has_only or has_gp) and gp_links:
            gp_entries = [
                {"text": self._expand_gp_name(lnk), "url": lnk["url"]}
                if lnk.get("url")
                else {"text": self._expand_gp_name(lnk)}
                for lnk in gp_links
            ]
            if gp_entries:
                record["grand_prix_scope"] = {"type": "only", "grand_prix": gp_entries}
                record["_season_scoped_gp"] = True
        elif driver_links and not has_only and not has_gp:
            has_car = bool(re.search(r"\bcar\b", paren_content, re.IGNORECASE))
            field = "car" if has_car else "driver"
            record[field] = [
                {"text": lnk["text"], "url": lnk["url"]}
                if lnk.get("url")
                else {"text": lnk["text"]}
                for lnk in driver_links
            ]

        # Gemini-based semantic classification (when classifier is configured).
        if self._classifier is not None:
            classification = self._classifier.classify(
                paren_content=paren_content,
                team_name=self._team_name or "",
                year_text=year_text,
                headers=self._table_headers,
            )
            record["paren_classification"] = classification

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _year_only_text(text: str) -> str:
        """Strip any trailing parenthetical so only the year part remains."""
        return re.sub(r"\s*\([^)]*\)\s*$", "", text).strip()

    @staticmethod
    def _is_gp_link(link: Dict[str, Any]) -> bool:
        text = link.get("text") or ""
        url = link.get("url") or ""
        return bool(re.search(r"grand prix|\bGP\b", text, re.IGNORECASE)) or bool(
            re.search(r"Grand_Prix|grand_prix", url),
        )

    @staticmethod
    def _expand_gp_name(link: Dict[str, Any]) -> str:
        """Expand abbreviated GP text: 'Chinese GP' → 'Chinese Grand Prix'."""
        text = link.get("text") or ""
        if re.search(r"\bGP\b", text) and not re.search(
                r"grand prix", text, re.IGNORECASE,
        ):
            text = re.sub(r"\bGP\b", "Grand Prix", text).strip()
        return text
