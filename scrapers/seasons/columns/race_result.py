from typing import Any

from scrapers.base.helpers.background import extract_background
from scrapers.base.helpers.text import strip_marks
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers.constants import MARKS_RE
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.seasons.columns.helpers.constants import BACKGROUND_TO_RESULT
from scrapers.seasons.columns.helpers.race_result_components import RaceResultBackgroundMapper
from scrapers.seasons.columns.helpers.race_result_components import RaceResultCellParser
from scrapers.seasons.columns.helpers.race_result_components import SuperscriptParseResult
from scrapers.seasons.columns.helpers.race_result_rules import ClassifiedDnfRule
from scrapers.seasons.columns.helpers.race_result_rules import DoublePointsRoundRule
from scrapers.seasons.columns.helpers.race_result_rules import F2EligibilityRule
from scrapers.seasons.columns.helpers.race_result_rules import FatalAccidentRule
from scrapers.seasons.columns.helpers.race_result_rules import HalfPointsRoundRule
from scrapers.seasons.columns.helpers.race_result_rules import MarkBasedEligibilityRule
from scrapers.seasons.columns.helpers.race_result_rules import ResultRule
from scrapers.seasons.columns.helpers.race_result_rules import ResultRuleContext
from scrapers.seasons.columns.helpers.race_result_rules import RoundRule
from scrapers.seasons.columns.helpers.race_result_rules import RoundRuleContext
from scrapers.seasons.columns.helpers.race_result_rules import SharedDriveRule
from scrapers.seasons.columns.helpers.race_result_rules import StarMarkNoteRule


class RaceResultColumn(BaseColumn):
    def __init__(
        self,
        *,
        season_year: int | None = None,
        star_mark_note: str | None = None,
        result_rules: list[ResultRule] | None = None,
        round_rules: list[RoundRule] | None = None,
    ) -> None:
        self._season_year = season_year
        self._cell_parser = RaceResultCellParser()
        self._background_mapper = RaceResultBackgroundMapper(BACKGROUND_TO_RESULT)

        default_result_rules: list[ResultRule] = [
            ClassifiedDnfRule(),
            MarkBasedEligibilityRule(),
            SharedDriveRule(),
            FatalAccidentRule(),
            F2EligibilityRule(),
        ]
        if star_mark_note:
            default_result_rules.append(StarMarkNoteRule(star_mark_note))
        self._result_rules = result_rules or default_result_rules
        self._round_rules = round_rules or [
            DoublePointsRoundRule(),
            HalfPointsRoundRule(),
        ]

    def parse(self, ctx: ColumnContext) -> Any:
        text = self._cell_parser.extract_result_text(ctx)
        if not text:
            return None

        superscript_data = self._cell_parser.parse_superscripts(ctx, self._season_year)
        background = self._background_mapper.map(extract_background(ctx.cell))
        results = self._cell_parser.parse_results(text)

        if self._should_skip_payload(results, background):
            return None

        payload: dict[str, Any] = {}
        self._populate_round(payload, ctx)
        self._populate_results(payload, results, background, superscript_data)
        self._populate_payload_meta(payload, superscript_data)
        self._merge_single_result_with_sprint(payload, superscript_data.sprint_position)
        return payload or None

    @staticmethod
    def _should_skip_payload(
        results: list[dict[str, Any]],
        background: str | None,
    ) -> bool:
        if not results and background is None:
            return True
        return background is None and all(
            result.get("position") is None for result in results
        )

    def _populate_round(self, payload: dict[str, Any], ctx: ColumnContext) -> None:
        if not ctx.header_link:
            return
        if not (ctx.header_link.get("url") or ctx.header_link.get("text")):
            return

        round_link = dict(ctx.header_link)
        if not round_link.get("text"):
            round_link["text"] = ctx.header
        round_note = self._round_note(ctx, round_link)
        if round_note:
            round_link.update(round_note)
        payload["round"] = round_link

    def _populate_results(
        self,
        payload: dict[str, Any],
        results: list[dict[str, Any]],
        background: str | None,
        superscript_data: SuperscriptParseResult,
    ) -> None:
        if not results:
            return

        share_count = len(results)
        for result in results:
            if superscript_data.footnotes:
                result["footnotes"] = superscript_data.footnotes
            self._apply_result_rules(result, background, superscript_data.footnotes)
            if result.get("points_shared") and share_count > 1:
                result["points_share_count"] = share_count
            result.pop("marks", None)
            self._apply_result_flags(
                result,
                background,
                pole_position=superscript_data.pole_position,
                fastest_lap=superscript_data.fastest_lap,
            )

        payload["results"] = results
        if superscript_data.fastest_lap and len(results) > 1:
            payload["fastest_lap_shared"] = True
            payload["fastest_lap_share_count"] = len(results)

    def _apply_result_rules(
        self,
        result: dict[str, Any],
        background: str | None,
        footnotes: list[str],
    ) -> None:
        context = ResultRuleContext(
            season_year=self._season_year,
            background=background,
            footnotes=footnotes,
        )
        for rule in self._result_rules:
            rule.apply(result, context)

    def _apply_result_flags(
        self,
        result: dict[str, Any],
        background: str | None,
        *,
        pole_position: bool,
        fastest_lap: bool,
    ) -> None:
        if background is not None:
            result["background"] = self._resolve_background(result, background)
        if pole_position:
            result["pole_position"] = True
        if fastest_lap:
            result["fastest_lap"] = True

    @staticmethod
    def _resolve_background(result: dict[str, Any], background: str) -> str:
        position = result.get("position")
        if (
            isinstance(position, str)
            and position.upper() == "NC"
            and background == "Other classified position"
        ):
            return "Not classified, finished"
        return background

    @staticmethod
    def _populate_payload_meta(
        payload: dict[str, Any],
        superscript_data: SuperscriptParseResult,
    ) -> None:
        if superscript_data.sprint_position is not None:
            payload["sprint_position"] = superscript_data.sprint_position
        if superscript_data.footnotes:
            payload["footnotes"] = superscript_data.footnotes

    @staticmethod
    def _merge_single_result_with_sprint(
        payload: dict[str, Any],
        sprint_position: int | None,
    ) -> None:
        if sprint_position is None:
            return
        results = payload.get("results")
        if not isinstance(results, list) or len(results) != 1:
            return
        result = results[0]
        result["sprint_position"] = sprint_position
        payload["results"] = result
        payload.pop("sprint_position", None)

    def _round_note(
        self,
        ctx: ColumnContext,
        round_link: dict[str, Any],
    ) -> dict[str, Any] | None:
        marks = MARKS_RE.findall(ctx.header)
        if not marks:
            return None

        context = RoundRuleContext(
            season_year=self._season_year,
            marks=marks,
            header_text=strip_marks(ctx.header).strip(),
            round_url=str(round_link.get("url") or ""),
        )
        for rule in self._round_rules:
            note = rule.apply(context)
            if note:
                return note
        return None
