import re
from typing import Optional, Dict, Any, List

from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.circuits.infobox.services.constants import symbol_map
from scrapers.circuits.infobox.services.text_utils import InfoboxTextUtils


class CircuitSpecsParser(InfoboxTextUtils):
    """Parsowanie parametrów technicznych toru (surface, cost, capacity, banking)."""

    @staticmethod
    def _norm_surface_part(surface_part: str) -> List[str]:
        """Normalizuje część powierzchni, identyfikując materiały."""
        surface_lower = surface_part.lower()
        detected_materials: List[str] = []

        if (
            "tarmac" in surface_lower
            or "asphalt" in surface_lower
            or "asphalt concrete" in surface_lower
        ):
            detected_materials.append("Asphalt")
        if "concrete" in surface_lower and "asphalt" not in surface_lower:
            detected_materials.append("Concrete")
        if (
            "cobblestone" in surface_lower
            or "cobbles" in surface_lower
            or "cobbl" in surface_lower
        ):
            detected_materials.append("Cobblestones")
        if "brick" in surface_lower:
            detected_materials.append("Brick")
        if "wood" in surface_lower:
            detected_materials.append("Wood")
        if "dirt" in surface_lower:
            detected_materials.append("Dirt")
        if "steel" in surface_lower:
            detected_materials.append("Steel")
        if "graywacke" in surface_lower:
            detected_materials.append("Graywacke")

        if not detected_materials:
            detected_materials.append(surface_part.strip().strip(". "))

        unique_materials: List[str] = []
        for material in detected_materials:
            if material and material not in unique_materials:
                unique_materials.append(material)
        return unique_materials

    @staticmethod
    def parse_surface(row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
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

        tmp = base_text
        tmp = re.sub(r"\band\b", ",", tmp, flags=re.IGNORECASE)
        tmp = tmp.replace("&", ",").replace("/", ",")
        parts = [p.strip(" .") for p in tmp.split(",") if p.strip(" .")]

        materials: List[str] = []
        for part in parts:
            for m_ in CircuitSpecsParser._norm_surface_part(part):
                if m_ not in materials:
                    materials.append(m_)

        if not materials:
            return None

        result: Dict[str, Any] = {"values": materials, "text": text}
        if note:
            result["note"] = note
        return result

    @staticmethod
    def _parse_capacity(row: Optional[Dict[str, Any]]) -> Optional[Dict[str, int]]:
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

        vals = [_to_int(n) for n in numbers]
        result: Dict[str, int] = {}
        if len(vals) >= 1:
            result["total"] = vals[0]
        if len(vals) >= 2:
            result["seating"] = vals[1]
        return result or None

    def _parse_construction_cost(
        self, row: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Construction cost: amount + currency (+ opcjonalna skala)."""
        if not row:
            return None
        text = clean_infobox_text(row.get("text")) or ""
        if not text:
            return None

        text_clean = re.sub(r"\[\d+]", "", text)

        currency: Optional[str] = None
        for symbol, code in symbol_map.items():
            if symbol in text_clean:
                currency = code
                break

        if currency is None:
            match_code = re.search(r"\b(EUR|USD|GBP|JPY|AUD|CAD|PLN|CHF)\b", text_clean)
            if match_code:
                currency = match_code.group(1)

        amount_match = re.search(r"([\d.,]+)", text_clean)
        if not amount_match and not currency:
            return None

        amount: Optional[float] = None
        if amount_match:
            try:
                amount = float(amount_match.group(1).replace(",", ""))
            except ValueError:
                amount = None

        scale_match = re.search(
            r"\b(million|billion|thousand|mln|bn|k)\b", text_clean, flags=re.IGNORECASE
        )
        scale = scale_match.group(1).lower() if scale_match else None

        result: Dict[str, Any] = {
            "amount": amount,
            "currency": currency,
        }
        if scale:
            result["scale"] = scale
        result["text"] = text_clean.strip() or None
        return self.prune_nulls(result)

    @staticmethod
    def parse_banking(row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Banking: liczba + jednostka + opcjonalna notka."""
        if not row:
            return None
        text = clean_infobox_text(row.get("text")) or ""
        if not text:
            return None

        angle_match = re.search(r"([\d.,]+)\s*°", text)
        percent_match = re.search(r"([\d.,]+)\s*%", text)

        value: Optional[float] = None
        unit: Optional[str] = None

        if angle_match:
            value = float(angle_match.group(1).replace(",", "."))
            unit = "deg"
        elif percent_match:
            value = float(percent_match.group(1).replace(",", "."))
            unit = "percent"

        result: Dict[str, Any] = {}
        if value is not None:
            result["value"] = value
        if unit:
            result["unit"] = unit

        cleaned = text
        for m in (angle_match, percent_match):
            if m:
                cleaned = cleaned.replace(m.group(0), "")
        cleaned = cleaned.strip(" ()-;,")
        if cleaned:
            result["note"] = cleaned

        return result or None
