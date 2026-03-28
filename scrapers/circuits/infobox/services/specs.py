import re
from typing import Any

from scrapers.base.error_handler import ErrorHandler
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.circuits.infobox.services.constants import MATERIAL_PATTERNS
from scrapers.circuits.infobox.services.constants import MIN_CAPACITY_VALUES_FOR_SEATING
from scrapers.circuits.infobox.services.constants import symbol_map
from scrapers.circuits.infobox.services.text_utils import InfoboxTextUtils


class CircuitSpecsParser(InfoboxTextUtils):
    """Parsowanie parametrów technicznych toru (surface, cost, capacity, banking)."""

    @staticmethod
    def _norm_surface_part(surface_part: str) -> list[str]:
        """Normalizuje część powierzchni, identyfikując materiały."""
        surface_lower = surface_part.lower()
        detected_materials = [
            material
            for material, aliases in MATERIAL_PATTERNS.items()
            if any(alias in surface_lower for alias in aliases)
        ]
        if "asphalt" in surface_lower and "Concrete" in detected_materials:
            detected_materials.remove("Concrete")

        if not detected_materials:
            detected_materials = [surface_part.strip().strip(". ")]

        unique_materials: list[str] = []
        for material in detected_materials:
            if material and material not in unique_materials:
                unique_materials.append(material)
        return unique_materials

    @staticmethod
    def parse_surface(row: dict[str, Any] | None) -> dict[str, Any] | None:
        if not row:
            return None

        text = clean_infobox_text(row.get("text")) or ""
        if not text:
            return None

        note = None
        m = re.search(r"\(([^)]*)\)", text)
        if m:
            note = m.group(1).strip()
            base_text = re.sub(r"\([^)]*\)", "", text)
        else:
            base_text = text

        tmp = re.sub(r"\band\b", ",", base_text, flags=re.IGNORECASE)
        tmp = tmp.replace("&", ",").replace("/", ",")
        parts = [p.strip(" .") for p in tmp.split(",") if p.strip(" .")]

        materials: list[str] = []
        for part in parts:
            for material in CircuitSpecsParser._norm_surface_part(part):
                if material not in materials:
                    materials.append(material)

        if not materials:
            return None

        result: dict[str, Any] = {"values": materials, "text": text}
        if note:
            result["note"] = note
        return result

    @staticmethod
    def _parse_capacity(row: dict[str, Any] | None) -> dict[str, int] | None:
        """Capacity: '~125,000 (44,000 seating)' -> total / seating."""
        if not row:
            return None
        text = clean_infobox_text(row.get("text")) or ""
        if not text:
            return None

        text = re.sub(r"\[\d+]", "", text)
        numbers = re.findall(r"[\d,]+", text)
        if not numbers:
            return None

        def _to_int(s: str) -> int:
            return int(s.replace(",", "").replace(" ", ""))

        vals = ErrorHandler.run_domain_parse(
            lambda: [_to_int(n) for n in numbers],
            message=f"Nie udało się sparsować pojemności: {text!r}.",
            parser_name=CircuitSpecsParser.__name__,
        )
        result: dict[str, int] = {"total": vals[0]}
        if len(vals) >= MIN_CAPACITY_VALUES_FOR_SEATING:
            result["seating"] = vals[1]
        return result

    @staticmethod
    def _extract_currency(text_clean: str) -> str | None:
        for symbol, code in symbol_map.items():
            if symbol in text_clean:
                return code
        match_code = re.search(r"\b(EUR|USD|GBP|JPY|AUD|CAD|PLN|CHF)\b", text_clean)
        return match_code.group(1) if match_code else None

    def _parse_construction_cost(
        self,
        row: dict[str, Any] | None,
    ) -> dict[str, Any] | None:
        """Construction cost: amount + currency (+ opcjonalna skala)."""
        if not row:
            return None
        text = clean_infobox_text(row.get("text")) or ""
        if not text:
            return None

        text_clean = re.sub(r"\[\d+]", "", text)
        currency = self._extract_currency(text_clean)

        amount_match = re.search(r"([\d.,]+)", text_clean)
        if not amount_match and not currency:
            return None

        amount: float | None = None
        if amount_match:
            amount = ErrorHandler.run_domain_parse(
                lambda: float(amount_match.group(1).replace(",", "")),
                message=f"Nie udało się sparsować kosztu budowy: {text_clean!r}.",
                parser_name=self.__class__.__name__,
            )

        scale_match = re.search(
            r"\b(million|billion|thousand|mln|bn|k)\b",
            text_clean,
            flags=re.IGNORECASE,
        )
        scale = scale_match.group(1).lower() if scale_match else None

        result: dict[str, Any] = {
            "amount": amount,
            "currency": currency,
            "text": text_clean.strip() or None,
        }
        if scale:
            result["scale"] = scale
        return self.prune_nulls(result)

    @staticmethod
    def parse_banking(row: dict[str, Any] | None) -> dict[str, Any] | None:
        """Banking: liczba + jednostka + opcjonalna notka."""
        if not row:
            return None
        text = clean_infobox_text(row.get("text")) or ""
        if not text:
            return None

        angle_match = re.search(r"([\d.,]+)\s*°", text)
        percent_match = re.search(r"([\d.,]+)\s*%", text)

        unit_match = ("deg", angle_match) if angle_match else ("percent", percent_match)
        unit, selected_match = unit_match
        value: float | None = None

        if selected_match:
            value = ErrorHandler.run_domain_parse(
                lambda: float(selected_match.group(1).replace(",", ".")),
                message=f"Nie udało się sparsować nachylenia toru: {text!r}.",
                parser_name=CircuitSpecsParser.__name__,
            )
        else:
            unit = None

        result: dict[str, Any] = {}
        if value is not None:
            result["value"] = value
        if unit:
            result["unit"] = unit

        cleaned = text
        for match in (angle_match, percent_match):
            if match:
                cleaned = cleaned.replace(match.group(0), "")
        cleaned = cleaned.strip(" ()-;,")
        if cleaned:
            result["note"] = cleaned

        return result or None
