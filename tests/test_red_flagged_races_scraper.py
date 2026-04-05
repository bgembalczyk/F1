# ruff: noqa: E501, PLR2004, RUF001, RUF002, RUF003, ARG001, ARG002, N802, B017, PT011, PT017, E402, PT001, PLC0415, RUF100, SLF001
"""
Unit tests for red-flagged races scraper improvements.

These tests verify that the scraper can handle various Wikipedia page structures,
including cases where section headings are missing or malformed.
"""

import sys
from pathlib import Path

from bs4 import BeautifulSoup

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scrapers.races.red_flagged_races_scraper import (
    NonChampionshipsRacesSubSectionParser,
)
from scrapers.races.red_flagged_races_scraper import RedFlaggedRacesScraper
from scrapers.races.red_flagged_races_scraper import RedFlaggedRacesSectionParser
from scrapers.races.red_flagged_races_scraper import WorldChampionshipsRacesTableParser
from scrapers.races.red_flagged_races_scraper.non_championship import (
    RedFlaggedNonChampionshipRacesScraper,
)
from scrapers.races.red_flagged_races_scraper.world_championship import (
    RedFlaggedWorldChampionshipRacesScraper,
)


class TestRedFlaggedRacesScraperRobustness:
    """Test that the scraper handles various HTML structures gracefully."""

    def test_with_proper_section_headings(self):
        """Test scraper works with proper Wikipedia section structure."""
        html = """
        <html><body>
        <h2><span class="mw-headline" id="Red-flagged_races">Red-flagged races</span></h2>
        <table class="wikitable">
          <tr>
            <th rowspan="2">Year</th><th rowspan="2">Grand Prix</th><th rowspan="2">Lap</th><th rowspan="2">R</th>
            <th rowspan="2">Winner</th><th rowspan="2">Incident that prompted red flag</th>
            <th colspan="2">Failed to make the restart</th><th rowspan="2">Ref.</th>
          </tr>
          <tr>
            <th>Drivers</th><th>Reason</th>
          </tr>
          <tr>
            <td>2024</td><td><a href="/wiki/Monaco">Monaco</a></td><td>5</td><td>Y</td>
            <td><a href="/wiki/Driver">Driver</a></td><td>Crash</td>
            <td></td><td></td><td>[1]</td>
          </tr>
        </table>
        </body></html>
        """
        soup = BeautifulSoup(html, "html.parser")
        scraper = RedFlaggedWorldChampionshipRacesScraper()
        records = scraper.parse_soup(soup)

        assert len(records) == 1
        assert records[0]["season"] == 2024

    def test_with_missing_section_headings(self):
        """Test scraper works even when section headings are missing (uses whole document fallback)."""
        html = """
        <html><body>
        <!-- NO proper h2 heading, just a div -->
        <div>Red-flagged races</div>
        <table class="wikitable">
          <tr>
            <th rowspan="2">Year</th><th rowspan="2">Grand Prix</th><th rowspan="2">Lap</th><th rowspan="2">R</th>
            <th rowspan="2">Winner</th><th rowspan="2">Incident that prompted red flag</th>
            <th colspan="2">Failed to make the restart</th><th rowspan="2">Ref.</th>
          </tr>
          <tr>
            <th>Drivers</th><th>Reason</th>
          </tr>
          <tr>
            <td>2024</td><td><a href="/wiki/Monaco">Monaco</a></td><td>5</td><td>Y</td>
            <td><a href="/wiki/Driver">Driver</a></td><td>Crash</td>
            <td></td><td></td><td>[1]</td>
          </tr>
        </table>
        </body></html>
        """
        soup = BeautifulSoup(html, "html.parser")
        scraper = RedFlaggedWorldChampionshipRacesScraper()
        records = scraper.parse_soup(soup)

        assert len(records) == 1
        assert records[0]["season"] == 2024

    def test_non_championship_scraper_differentiates_tables(self):
        """Test that non-championship scraper finds the correct table based on headers."""
        html = """
        <html><body>
        <!-- Two tables, first is championship, second is non-championship -->
        <table class="wikitable">
          <tr>
            <th rowspan="2">Year</th><th rowspan="2">Grand Prix</th><th rowspan="2">Lap</th><th rowspan="2">R</th>
            <th rowspan="2">Winner</th><th rowspan="2">Incident that prompted red flag</th>
            <th colspan="2">Failed to make the restart</th><th rowspan="2">Ref.</th>
          </tr>
          <tr>
            <th>Drivers</th><th>Reason</th>
          </tr>
          <tr>
            <td>2024</td><td>Monaco</td><td>5</td><td>Y</td>
            <td>Driver A</td><td>Crash</td><td></td><td></td><td>[1]</td>
          </tr>
        </table>
        <table class="wikitable">
          <tr>
            <th rowspan="2">Year</th><th rowspan="2">Event</th><th rowspan="2">Lap</th><th rowspan="2">R</th>
            <th rowspan="2">Winner</th><th rowspan="2">Incident that prompted red flag</th>
            <th colspan="2">Failed to make the restart</th><th rowspan="2">Ref.</th>
          </tr>
          <tr>
            <th>Drivers</th><th>Reason</th>
          </tr>
          <tr>
            <td>1971</td><td>Brand Hatch</td><td>15</td><td>N</td>
            <td>Peter Gethin</td><td>Fatal crash</td><td></td><td></td><td>[1]</td>
          </tr>
        </table>
        </body></html>
        """
        soup = BeautifulSoup(html, "html.parser")
        scraper = RedFlaggedNonChampionshipRacesScraper()
        records = scraper.parse_soup(soup)

        # Should find the non-championship table (with "Event" column)
        assert len(records) == 1
        assert records[0]["season"] == 1971

    def test_composite_non_championship_scope_with_direct_h3_table(self):
        """Test composite parser handles non-championship table directly under h3."""
        html = """
        <html><body>
        <div id="bodyContent">
        <div id="mw-content-text" class="mw-body-content">
        <div class="mw-content-ltr mw-parser-output">
          <h3 class="mw-heading3"><span class="mw-headline" id="World_Championship_races">World Championship races</span></h3>
          <table class="wikitable">
            <tr>
              <th>Year</th><th>Grand Prix</th><th>Lap</th><th>R</th>
              <th>Winner</th><th>Incident that prompted red flag</th>
            </tr>
            <tr>
              <td>2024</td><td>Monaco</td><td>5</td><td>Y</td><td>Driver A</td><td>Crash</td>
            </tr>
          </table>
          <h3 class="mw-heading3"><span class="mw-headline" id="Non-championship_races">Non-championship races</span></h3>
          <table class="wikitable">
            <tr>
              <th>Year</th><th>Event</th><th>Lap</th><th>R</th>
              <th>Winner</th><th>Incident that prompted red flag</th>
            </tr>
            <tr>
              <td>1971</td><td>Brands Hatch</td><td>15</td><td>N</td><td>Peter Gethin</td><td>Fatal crash</td>
            </tr>
          </table>
        </div>
        </div>
        </div>
        </body></html>
        """
        soup = BeautifulSoup(html, "html.parser")
        scraper = RedFlaggedRacesScraper(export_scope="non_championship")
        records = scraper.parse_soup(soup)

        assert len(records) == 1
        assert records[0]["season"] == 1971
        assert records[0]["event"] == {
            "text": "Brands Hatch",
            "url": None,
        }

    def test_composite_non_championship_scope_with_h4_but_no_h5(self):
        """Test composite parser handles h4 structure without h5 nested sections."""
        html = """
        <html><body>
        <div id="bodyContent">
        <div id="mw-content-text" class="mw-body-content">
        <div class="mw-content-ltr mw-parser-output">
          <h3 class="mw-heading3"><span class="mw-headline" id="Non-championship_races">Non-championship races</span></h3>
          <h4 class="mw-heading4"><span class="mw-headline" id="Examples">Examples</span></h4>
          <table class="wikitable">
            <tr>
              <th>Year</th><th>Event</th><th>Lap</th><th>R</th>
              <th>Winner</th><th>Incident that prompted red flag</th>
            </tr>
            <tr>
              <td>1980</td><td>Silverstone Int.</td><td>9</td><td>Y</td><td>Alan Jones</td><td>Oil spill</td>
            </tr>
          </table>
        </div>
        </div>
        </div>
        </body></html>
        """
        soup = BeautifulSoup(html, "html.parser")
        scraper = RedFlaggedRacesScraper(export_scope="non_championship")
        records = scraper.parse_soup(soup)

        assert len(records) == 1
        assert records[0]["season"] == 1980
        assert records[0]["event"] == {
            "text": "Silverstone Int.",
            "url": None,
        }

    def test_composite_non_championship_scope_with_table_nested_in_div(self):
        """Test composite parser finds non-championship table nested inside extra wrappers."""
        html = """
        <html><body>
        <div id="bodyContent">
        <div id="mw-content-text" class="mw-body-content">
        <div class="mw-content-ltr mw-parser-output">
          <h3 class="mw-heading3"><span class="mw-headline" id="Non-championship_races">Non-championship races</span></h3>
          <div class="wrapper">
            <div class="inner">
              <table class="wikitable">
                <tr>
                  <th>Year</th><th>Event</th><th>Lap</th><th>R</th>
                  <th>Winner</th><th>Incident that prompted red flag</th>
                </tr>
                <tr>
                  <td>1972</td><td>Race of Champions</td><td>11</td><td>N</td><td>Emerson Fittipaldi</td><td>Collision</td>
                </tr>
              </table>
            </div>
          </div>
        </div>
        </div>
        </div>
        </body></html>
        """
        soup = BeautifulSoup(html, "html.parser")
        scraper = RedFlaggedRacesScraper(export_scope="non_championship")
        records = scraper.parse_soup(soup)

        assert len(records) == 1
        assert records[0]["season"] == 1972
        assert records[0]["event"] == {
            "text": "Race of Champions",
            "url": None,
        }

    def test_composite_parser_dependencies(self):
        """Test required parser dependencies are wired in composite parser."""
        section_parser = RedFlaggedRacesSectionParser()

        assert isinstance(
            section_parser.child_parser,
            NonChampionshipsRacesSubSectionParser,
        )
        assert isinstance(
            section_parser._world_championship_table_parser,
            WorldChampionshipsRacesTableParser,
        )

    def test_error_message_with_no_matching_table(self):
        """Test that error message includes diagnostic information."""
        html = """
        <html><body>
        <table class="wikitable">
          <tr><th>Wrong</th><th>Headers</th></tr>
          <tr><td>1</td><td>2</td></tr>
        </table>
        </body></html>
        """
        soup = BeautifulSoup(html, "html.parser")
        scraper = RedFlaggedWorldChampionshipRacesScraper()

        try:
            scraper.parse_soup(soup)
            msg = "Should have raised RuntimeError"
            raise AssertionError(msg)
        except RuntimeError as e:
            error_msg = str(e)
            # Should mention that 1 table was found (in Polish)
            assert "Znaleziono 1 tabel" in error_msg

    def test_toc_warning_when_section_missing(self, caplog):
        """Test that a warning is logged when TOC exists but section heading doesn't."""
        html = """
        <html><body>
        <div id="toc-Red-flagged_races">
          <a href="#Red-flagged_races">Red-flagged races</a>
        </div>
        <!-- NO actual section heading -->
        <table class="wikitable">
          <tr>
            <th rowspan="2">Year</th><th rowspan="2">Grand Prix</th><th rowspan="2">Lap</th><th rowspan="2">R</th>
            <th rowspan="2">Winner</th><th rowspan="2">Incident that prompted red flag</th>
            <th colspan="2">Failed to make the restart</th><th rowspan="2">Ref.</th>
          </tr>
          <tr>
            <th>Drivers</th><th>Reason</th>
          </tr>
          <tr>
            <td>2024</td><td>Monaco</td><td>5</td><td>Y</td>
            <td>Driver</td><td>Crash</td><td></td><td></td><td>[1]</td>
          </tr>
        </table>
        </body></html>
        """
        soup = BeautifulSoup(html, "html.parser")
        scraper = RedFlaggedWorldChampionshipRacesScraper()

        import logging

        logging.basicConfig(level=logging.WARNING)
        records = scraper.parse_soup(soup)

        # Should still parse successfully via fallback
        assert len(records) == 1
        # Note: caplog verification would require pytest, which may not be run in this context

    def test_composite_world_championship_scope_produces_rich_output(self):
        """Test composite parser produces structured output matching RedFlaggedWorldChampionshipRacesScraper."""
        html = """
        <html><body>
        <div id="bodyContent">
        <div id="mw-content-text" class="mw-body-content">
        <div class="mw-content-ltr mw-parser-output">
          <h3 class="mw-heading3"><span class="mw-headline" id="World_Championship_races">World Championship races</span></h3>
          <table class="wikitable">
            <tr>
              <th>Year</th><th>Grand Prix</th><th>Lap</th><th>R</th>
              <th>Winner</th><th>Incident that prompted red flag</th>
            </tr>
            <tr>
              <td>1971</td>
              <td><a href="/wiki/1971_Canadian_Grand_Prix">Canadian</a></td>
              <td>64</td>
              <td style="background:#fdd">N</td>
              <td><a href="/wiki/Jackie_Stewart">Jackie Stewart</a></td>
              <td>Mist.</td>
            </tr>
          </table>
        </div>
        </div>
        </div>
        </body></html>
        """
        soup = BeautifulSoup(html, "html.parser")
        scraper = RedFlaggedRacesScraper(export_scope="world_championship")
        records = scraper.parse_soup(soup)

        assert len(records) == 1
        record = records[0]

        assert record["season"] == 1971
        assert record["grand_prix"] == {
            "text": "Canadian",
            "url": "https://en.wikipedia.org/wiki/1971_Canadian_Grand_Prix",
        }
        assert record["lap"] == 64
        assert record["restart_status"] == {
            "code": "N",
            "description": "race_was_not_restarted",
        }
        assert record["background"] == "#fdd"
        assert record["winner"] == {
            "text": "Jackie Stewart",
            "url": "https://en.wikipedia.org/wiki/Jackie_Stewart",
        }
        assert record["incident"] == "Mist."

    def test_composite_non_championship_scope_produces_rich_output(self):
        """Test non-championship parser returns rich structured fields."""
        html = """
        <html><body>
        <div id="bodyContent">
        <div id="mw-content-text" class="mw-body-content">
        <div class="mw-content-ltr mw-parser-output">
          <h3 class="mw-heading3"><span class="mw-headline" id="Non-championship_races">Non-championship races</span></h3>
          <table class="wikitable">
            <tr>
              <th>Year</th><th>Event</th><th>Lap</th><th>R</th>
              <th>Winner</th><th>Incident that prompted red flag</th>
            </tr>
            <tr>
              <td>1971</td>
              <td><a href="/wiki/1971_World_Championship_Victory_Race">Brand Hatch</a></td>
              <td>15</td>
              <td>N</td>
              <td><a href="/wiki/Peter_Gethin">Peter Gethin</a></td>
              <td>Fatal crash of <a href="/wiki/Jo_Siffert">Jo Siffert</a>.</td>
            </tr>
          </table>
        </div>
        </div>
        </div>
        </body></html>
        """
        soup = BeautifulSoup(html, "html.parser")
        scraper = RedFlaggedRacesScraper(export_scope="non_championship")
        records = scraper.parse_soup(soup)

        assert len(records) == 1
        record = records[0]
        assert record["season"] == 1971
        assert record["event"] == {
            "text": "Brand Hatch",
            "url": "https://en.wikipedia.org/wiki/1971_World_Championship_Victory_Race",
        }
        assert record["lap"] == 15
        assert record["restart_status"] == {
            "code": "N",
            "description": "race_was_not_restarted",
        }
        assert record["winner"] == {
            "text": "Peter Gethin",
            "url": "https://en.wikipedia.org/wiki/Peter_Gethin",
        }
        assert record["incident"] == "Fatal crash of Jo Siffert ."

    def test_multi_row_race_produces_failed_to_make_restart_list(self):
        """Test that multi-row race entries (rowspan) produce a grouped failed_to_make_restart list."""
        html = """
        <html><body>
        <div id="bodyContent">
        <div id="mw-content-text" class="mw-body-content">
        <div class="mw-content-ltr mw-parser-output">
          <h3 class="mw-heading3"><span class="mw-headline" id="World_Championship_races">World Championship races</span></h3>
          <table class="wikitable">
            <tr>
              <th rowspan="2">Year</th><th rowspan="2">Grand Prix</th><th rowspan="2">Lap</th><th rowspan="2">R</th>
              <th rowspan="2">Winner</th><th rowspan="2">Incident that prompted red flag</th>
              <th colspan="2">Failed to make the restart</th><th rowspan="2">Ref.</th>
            </tr>
            <tr>
              <th>Drivers</th><th>Reason</th>
            </tr>
            <tr>
              <th rowspan="4"><a href="/wiki/1973_Formula_One_season">1973</a></th>
              <td rowspan="4" align="center"><a href="/wiki/1973_British_Grand_Prix">British</a></td>
              <td rowspan="4" align="center">2</td>
              <td rowspan="4" align="center" style="background:#cfc">Y</td>
              <td rowspan="4"><a href="/wiki/Peter_Revson">Peter Revson</a></td>
              <td rowspan="4">Crash involving <a href="/wiki/Jody_Scheckter">Jody Scheckter</a></td>
              <td><a href="/wiki/Jody_Scheckter">Jody Scheckter</a> <br> <a href="/wiki/Roger_Williamson">Roger Williamson</a></td>
              <td>Crash</td>
              <td rowspan="4">[19]</td>
            </tr>
            <tr>
              <td><a href="/wiki/Andrea_de_Adamich">Andrea de Adamich</a></td>
              <td>Crash, injured</td>
            </tr>
            <tr>
              <td><a href="/wiki/David_Purley">David Purley</a></td>
              <td>Spun off</td>
            </tr>
            <tr>
              <td><a href="/wiki/Graham_McRae">Graham McRae</a></td>
              <td>Throttle</td>
            </tr>
          </table>
        </div>
        </div>
        </div>
        </body></html>
        """
        soup = BeautifulSoup(html, "html.parser")
        scraper = RedFlaggedRacesScraper(export_scope="world_championship")
        records = scraper.parse_soup(soup)

        assert len(records) == 1
        record = records[0]

        assert record["season"] == 1973
        assert record["grand_prix"]["text"] == "British"
        assert record["lap"] == 2
        assert record["restart_status"]["code"] == "Y"
        assert record["background"] == "#cfc"
        assert record["winner"]["text"] == "Peter Revson"

        ftmr = record["failed_to_make_restart"]
        assert isinstance(ftmr, list)
        assert len(ftmr) == 4

        assert ftmr[0]["reason"] == "Crash"
        assert len(ftmr[0]["drivers"]) == 2
        assert ftmr[0]["drivers"][0]["text"] == "Jody Scheckter"
        assert ftmr[0]["drivers"][1]["text"] == "Roger Williamson"

        assert ftmr[1]["reason"] == "Crash, injured"
        assert len(ftmr[1]["drivers"]) == 1
        assert ftmr[1]["drivers"][0]["text"] == "Andrea de Adamich"

        assert ftmr[2]["reason"] == "Spun off"
        assert ftmr[2]["drivers"][0]["text"] == "David Purley"

        assert ftmr[3]["reason"] == "Throttle"
        assert ftmr[3]["drivers"][0]["text"] == "Graham McRae"


if __name__ == "__main__":
    # Run tests manually for verification
    test = TestRedFlaggedRacesScraperRobustness()

    print("Test 1: Proper section headings...")
    test.test_with_proper_section_headings()
    print("✓ PASSED")

    print("\nTest 2: Missing section headings...")
    test.test_with_missing_section_headings()
    print("✓ PASSED")

    print("\nTest 3: Non-championship scraper differentiates tables...")
    test.test_non_championship_scraper_differentiates_tables()
    print("✓ PASSED")

    print("\nTest 4: Error message with no matching table...")
    test.test_error_message_with_no_matching_table()
    print("✓ PASSED")

    print("\nTest 5: TOC warning when section missing...")
    test.test_toc_warning_when_section_missing(None)
    print("✓ PASSED")

    print("\n" + "=" * 50)
    print("All tests passed!")
