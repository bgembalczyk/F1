"""Tests for EngineParsingHelpers covering the engine-spec extraction cases."""

import pytest
from bs4 import BeautifulSoup

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers.engine_parsing import EngineParsingHelpers
from scrapers.base.table.columns.types.engine import EngineColumn

BASE_URL = "https://en.wikipedia.org"


def _parse_segment(html: str) -> dict:
    """Parse engine data from a <td> HTML string."""
    segment = BeautifulSoup(html, "html.parser").find("td")
    return EngineParsingHelpers.parse_segment(segment, {}, BASE_URL)


def _parse_column(html: str) -> dict:
    """Parse engine data via EngineColumn (includes background-class detection)."""
    cell = BeautifulSoup(html, "html.parser").find("td")
    ctx = ColumnContext(
        header="",
        key="",
        raw_text="",
        clean_text="",
        links=[],
        cell=cell,
        base_url=BASE_URL,
        model_fields=None,
    )
    return EngineColumn().parse(ctx)


def _parse_any(html: str) -> dict:
    """Parse engine data via EngineColumn from any cell tag (<td> or <th>)."""
    cell = BeautifulSoup(html, "html.parser").find()
    ctx = ColumnContext(
        header="",
        key="",
        raw_text="",
        clean_text="",
        links=[],
        cell=cell,
        base_url=BASE_URL,
        model_fields=None,
    )
    return EngineColumn().parse(ctx)


# ---------------------------------------------------------------------------
# is_f2_background
# ---------------------------------------------------------------------------

class TestIsF2Background:
    def test_ffcccc_is_f2(self) -> None:
        assert EngineParsingHelpers.is_f2_background("#ffcccc") is True

    def test_ffcccc_uppercase_is_f2(self) -> None:
        assert EngineParsingHelpers.is_f2_background("#FFCCCC") is True

    def test_efefef_is_f2(self) -> None:
        assert EngineParsingHelpers.is_f2_background("#efefef") is True

    def test_white_is_not_f2(self) -> None:
        assert EngineParsingHelpers.is_f2_background("#ffffff") is False

    def test_empty_string_is_not_f2(self) -> None:
        assert EngineParsingHelpers.is_f2_background("") is False


# ---------------------------------------------------------------------------
# First link is engine-type code (Speluzzi case)
# ---------------------------------------------------------------------------

class TestFirstLinkIsType:
    def test_speluzzi_model_text(self) -> None:
        html = (
            '<td>Speluzzi 1.5 '
            '<a href="/wiki/Inline-four_engine">L4</a> '
            '<a href="/wiki/Supercharger">s</a></td>'
        )
        result = _parse_segment(html)
        assert result["model"]["text"] == "Speluzzi"
        assert result["model"]["url"] is None

    def test_speluzzi_displacement(self) -> None:
        html = (
            '<td>Speluzzi 1.5 '
            '<a href="/wiki/Inline-four_engine">L4</a> '
            '<a href="/wiki/Supercharger">s</a></td>'
        )
        result = _parse_segment(html)
        assert result["displacement_l"] == 1.5

    def test_speluzzi_type(self) -> None:
        html = (
            '<td>Speluzzi 1.5 '
            '<a href="/wiki/Inline-four_engine">L4</a> '
            '<a href="/wiki/Supercharger">s</a></td>'
        )
        result = _parse_segment(html)
        assert result["type"] == "L4"
        assert result["layout"] == "L"
        assert result["cylinders"] == 4

    def test_speluzzi_supercharged(self) -> None:
        html = (
            '<td>Speluzzi 1.5 '
            '<a href="/wiki/Inline-four_engine">L4</a> '
            '<a href="/wiki/Supercharger">s</a></td>'
        )
        result = _parse_segment(html)
        assert result.get("supercharged") is True


# ---------------------------------------------------------------------------
# Engine type embedded in single link text
# ---------------------------------------------------------------------------

class TestEmbeddedTypeInLinkText:
    def test_climax_fpf_model_text(self) -> None:
        html = '<td><a href="/wiki/Coventry_Climax#FPF">Climax FPF 2.0 L4</a></td>'
        result = _parse_segment(html)
        assert result["model"]["text"] == "Climax FPF"
        assert result["model"]["url"] == "https://en.wikipedia.org/wiki/Coventry_Climax#FPF"

    def test_climax_fpf_type(self) -> None:
        html = '<td><a href="/wiki/Coventry_Climax#FPF">Climax FPF 2.0 L4</a></td>'
        result = _parse_segment(html)
        assert result["type"] == "L4"
        assert result["layout"] == "L"
        assert result["cylinders"] == 4

    def test_climax_fwmv_v8(self) -> None:
        html = '<td><a href="/wiki/Coventry_Climax#FWMV">Climax FWMV 1.5 V8</a></td>'
        result = _parse_segment(html)
        assert result["model"]["text"] == "Climax FWMV"
        assert result["type"] == "V8"
        assert result["layout"] == "V"
        assert result["cylinders"] == 8

    def test_renault_rs26_v8(self) -> None:
        html = '<td><a href="/wiki/Renault_RS_engine">Renault RS26 2.4 V8</a></td>'
        result = _parse_segment(html)
        assert result["model"]["text"] == "Renault RS26"
        assert result["displacement_l"] == 2.4
        assert result["type"] == "V8"
        assert result["layout"] == "V"
        assert result["cylinders"] == 8


# ---------------------------------------------------------------------------
# Engine type embedded in a secondary link text
# ---------------------------------------------------------------------------

class TestEmbeddedTypeInSecondaryLink:
    def test_repco_620_v8(self) -> None:
        html = (
            '<td>'
            '<a href="/wiki/Repco-Brabham_V8">Repco</a> '
            '<a href="/wiki/Repco-Brabham_V8#RB620">620 3.0 V8</a>'
            '</td>'
        )
        result = _parse_segment(html)
        assert result["model"]["text"] == "Repco 620"
        assert result["model"]["url"] == "https://en.wikipedia.org/wiki/Repco-Brabham_V8"
        assert result["displacement_l"] == 3.0
        assert result["type"] == "V8"
        assert result["layout"] == "V"
        assert result["cylinders"] == 8


# ---------------------------------------------------------------------------
# Gas turbine detection
# ---------------------------------------------------------------------------

class TestGasTurbine:
    def test_pratt_whitney_gas_turbine(self) -> None:
        html = (
            '<td>'
            '<a href="/wiki/Pratt_%26_Whitney">Pratt &amp; Whitney</a> STN76 '
            '<a href="/wiki/Gas_turbine">tbn</a>'
            '</td>'
        )
        result = _parse_segment(html)
        assert result["model"]["text"] == "Pratt & Whitney STN76"
        assert result.get("gas_turbine") is True
        assert "tbn" not in result["model"]["text"]


# ---------------------------------------------------------------------------
# F2 class from #ffcccc background
# ---------------------------------------------------------------------------

class TestF2Background:
    def test_climax_fpf_f2_class(self) -> None:
        html = '<td style="background:#ffcccc;"><a href="/wiki/Coventry_Climax#FPF">Climax FPF 1.5 L4</a></td>'
        result = _parse_column(html)
        assert result["class"] == "F2"
        assert result["model"]["text"] == "Climax FPF"
        assert result["type"] == "L4"

    def test_porsche_f4_f2_class(self) -> None:
        html = (
            '<td style="background:#ffcccc;" rowspan="2">'
            '<a href="/wiki/Porsche">Porsche</a> 547/3 1.5 '
            '<a href="/wiki/Flat-4">F4</a>'
            '</td>'
        )
        result = _parse_column(html)
        assert result["class"] == "F2"
        assert result["model"]["text"] == "Porsche 547/3"
        assert result["type"] == "F4"
        assert result["layout"] == "F"
        assert result["cylinders"] == 4


# ---------------------------------------------------------------------------
# Regression: previously-working cases still work
# ---------------------------------------------------------------------------

class TestRegression:
    def test_alfa_romeo_l8_supercharged(self) -> None:
        html = (
            '<td>'
            '<a href="/wiki/Alfa_Romeo">Alfa Romeo</a> 158 1.5 '
            '<a href="/wiki/Straight-eight_engine">L8</a> '
            '<a href="/wiki/Supercharger">s</a>'
            '</td>'
        )
        result = _parse_segment(html)
        assert result["model"]["text"] == "Alfa Romeo 158"
        assert result["displacement_l"] == 1.5
        assert result["type"] == "L8"
        assert result["layout"] == "L"
        assert result["cylinders"] == 8
        assert result.get("supercharged") is True

    def test_ford_cosworth_dfv_v8_single_link(self) -> None:
        html = '<td><a href="/wiki/Ford_Cosworth_DFV">Ford Cosworth DFV 3.0 V8</a></td>'
        result = _parse_segment(html)
        assert result["model"]["text"] == "Ford Cosworth DFV"
        assert result["displacement_l"] == 3.0
        assert result["type"] == "V8"


# ---------------------------------------------------------------------------
# CSS shorthand hex colour for F2 detection (#fcc → #ffcccc)
# ---------------------------------------------------------------------------

class TestIsF2BackgroundShorthand:
    def test_fcc_shorthand_is_f2(self) -> None:
        assert EngineParsingHelpers.is_f2_background("#fcc") is True

    def test_fcc_uppercase_is_f2(self) -> None:
        assert EngineParsingHelpers.is_f2_background("#FCC") is True

    def test_fcc_column_class_from_column(self) -> None:
        html = (
            '<td style="background:#fcc;">'
            '<a href="/wiki/Cosworth_FVA">Ford Cosworth FVA</a> 1.6 '
            '<a href="/wiki/Straight-4">L4</a>'
            '</td>'
        )
        result = _parse_column(html)
        assert result["class"] == "F2"
        assert result["type"] == "L4"


# ---------------------------------------------------------------------------
# Type code with modifier suffix (L4t → L4 + turbocharged)
# ---------------------------------------------------------------------------

class TestTypeWithModifierSuffix:
    def test_bmw_l4t_type(self) -> None:
        html = (
            '<td rowspan="2">'
            '<a href="/wiki/BMW_M12">BMW M12</a>/13 1.5 '
            '<a href="/wiki/Inline-four_engine">L4t</a>'
            '</td>'
        )
        result = _parse_segment(html)
        assert result["type"] == "L4"
        assert result["layout"] == "L"
        assert result["cylinders"] == 4

    def test_bmw_l4t_turbocharged(self) -> None:
        html = (
            '<td rowspan="2">'
            '<a href="/wiki/BMW_M12">BMW M12</a>/13 1.5 '
            '<a href="/wiki/Inline-four_engine">L4t</a>'
            '</td>'
        )
        result = _parse_segment(html)
        assert result.get("turbocharged") is True


# ---------------------------------------------------------------------------
# Verbose engine type names as separate link text (Straight-4, Flat-4)
# ---------------------------------------------------------------------------

class TestVerboseEngineTypeNames:
    def test_straight4_link_sets_type(self) -> None:
        html = (
            '<th>'
            '<a href="/wiki/Coventry_Climax">Climax</a> '
            '<a href="/wiki/Straight-4">Straight-4</a>'
            '</th>'
        )
        result = _parse_any(html)
        assert result["type"] == "L4"
        assert result["layout"] == "L"
        assert result["cylinders"] == 4

    def test_straight4_link_removes_from_model(self) -> None:
        html = (
            '<th>'
            '<a href="/wiki/Coventry_Climax">Climax</a> '
            '<a href="/wiki/Straight-4">Straight-4</a>'
            '</th>'
        )
        result = _parse_any(html)
        assert result["model"]["text"] == "Climax"

    def test_flat4_link_sets_type(self) -> None:
        html = (
            '<th>'
            '<a href="/wiki/Porsche_in_motorsport">Porsche</a> '
            '<a href="/wiki/Flat-4">Flat-4</a>'
            '</th>'
        )
        result = _parse_any(html)
        assert result["type"] == "F4"
        assert result["layout"] == "F"
        assert result["cylinders"] == 4

    def test_flat4_link_removes_from_model(self) -> None:
        html = (
            '<th>'
            '<a href="/wiki/Porsche_in_motorsport">Porsche</a> '
            '<a href="/wiki/Flat-4">Flat-4</a>'
            '</th>'
        )
        result = _parse_any(html)
        assert result["model"]["text"] == "Porsche"

    def test_alta_straight4(self) -> None:
        html = (
            '<th>'
            '<a href="/wiki/Alta_Car_and_Engineering_Company">Alta</a> '
            '<a href="/wiki/Straight-4">Straight-4</a>'
            '</th>'
        )
        result = _parse_any(html)
        assert result["model"]["text"] == "Alta"
        assert result["type"] == "L4"

    def test_hart_straight4(self) -> None:
        html = (
            '<th nowrap="">'
            '<a href="/wiki/Brian_Hart_Ltd.">Hart</a> '
            '<a href="/wiki/Straight-4">Straight-4</a>'
            '</th>'
        )
        result = _parse_any(html)
        assert result["model"]["text"] == "Hart"
        assert result["type"] == "L4"


# ---------------------------------------------------------------------------
# Engine type from plain text (V8, V12 after displacement, no separate link)
# ---------------------------------------------------------------------------

class TestEngineTypeFromPlainText:
    def test_jaguar_v12_in_plain_text(self) -> None:
        html = (
            '<th nowrap="">'
            '<a href="/wiki/Jaguar_V12_engine">Jaguar</a> 7.4L V12'
            '</th>'
        )
        result = _parse_any(html)
        assert result["type"] == "V12"
        assert result["layout"] == "V"
        assert result["cylinders"] == 12
        assert result["displacement_l"] == 7.4

    def test_gibson_v8_in_plain_text(self) -> None:
        html = (
            '<th rowspan="2" nowrap="">'
            '<a href="/wiki/Gibson_Technology">Gibson</a> GK428 4.2 L V8'
            '</th>'
        )
        result = _parse_any(html)
        assert result["type"] == "V8"
        assert result["layout"] == "V"
        assert result["cylinders"] == 8

    def test_lotus_judd_v8(self) -> None:
        html = (
            '<th nowrap="">'
            '<a href="/wiki/Lotus_Cars">Lotus</a> '
            '(<a href="/wiki/Judd_(engine)">Judd</a>) 3.6\xa0L V8'
            '</th>'
        )
        result = _parse_any(html)
        assert result["type"] == "V8"
        assert result["layout"] == "V"
        assert result["cylinders"] == 8
        assert result["model"]["text"] == "Lotus ( Judd )"


# ---------------------------------------------------------------------------
# Diesel fuel type detection
# ---------------------------------------------------------------------------

class TestDieselFuelType:
    def test_audi_tdi_diesel_fuel_type(self) -> None:
        html = (
            '<th nowrap="">'
            '<a href="/wiki/Audi">Audi</a> '
            '<a href="/wiki/Turbo_Direct_Injection">TDI</a> '
            '5.5\xa0L Turbo V12 '
            '(<a href="/wiki/Diesel_engine">Diesel</a>)'
            '</th>'
        )
        result = _parse_any(html)
        assert result["fuel_type"] == "diesel"
        assert result.get("turbocharged") is True
        assert result["type"] == "V12"

    def test_audi_br_diesel_is_not_array(self) -> None:
        html = (
            '<th nowrap="">'
            '<a href="/wiki/Audi">Audi</a> 5.5L Turbo V12'
            '<br>'
            '(<a href="/wiki/Diesel_engine">Diesel</a>)'
            '</th>'
        )
        result = _parse_any(html)
        assert not isinstance(result, list), "Should not create array for (Diesel) note"

    def test_audi_br_diesel_fuel_type(self) -> None:
        html = (
            '<th nowrap="">'
            '<a href="/wiki/Audi">Audi</a> 5.5L Turbo V12'
            '<br>'
            '(<a href="/wiki/Diesel_engine">Diesel</a>)'
            '</th>'
        )
        result = _parse_any(html)
        assert result["fuel_type"] == "diesel"
        assert result.get("turbocharged") is True
        assert result["type"] == "V12"
        assert result["model"]["text"] == "Audi"
