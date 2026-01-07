# Red-Flagged Races Scraper Fix

## Problem

The red-flagged races scraper was failing with the error:

```
Nie znaleziono pasującej tabeli. Próbowano sekcji: ['Red-flagged_races', 'World_Championship_races', 'Championship_races', 'World_championship_races', 'Red_flagged_races', None]. Dostępne sekcje na stronie: []
```

This indicated that:
1. No `.mw-headline` elements were found on the Wikipedia page
2. The fallback mechanisms weren't working properly
3. Error messages didn't provide enough diagnostic information

## Root Cause

The Wikipedia page structure was either:
- Temporarily malformed (missing proper `<h2><span class="mw-headline">` tags)
- Changed to use a different structure
- Returned incomplete HTML due to network/caching issues

## Solution

### 1. Improved Error Diagnostics

Added detailed error reporting that shows:
- Number of tables found with the expected CSS class
- Headers of available tables (first 5)
- Available section IDs from `.mw-headline` elements

This helps diagnose what's actually on the page when the scraper fails.

### 2. TOC Mismatch Detection

Added detection for cases where the Table of Contents (TOC) has an entry for a section, but the actual section heading is missing. This logs a warning to help identify page structure issues:

```
WARNING: Found TOC entry 'toc-Red-flagged_races' but no matching section heading. Wikipedia page structure may be malformed or incomplete.
```

### 3. Robust Fallback Mechanism

The scraper already had a fallback to search the whole document (`section_id=None`) when specific sections aren't found. This fallback now works correctly and will find tables even when section headings are completely missing.

### 4. Table Differentiation by Headers

The championship and non-championship scrapers correctly differentiate tables based on column headers:
- Championship scraper looks for "Grand Prix" column
- Non-championship scraper looks for "Event" column

This ensures the correct table is selected even when both are present in the document.

## Testing

Created comprehensive tests in `tests/test_red_flagged_races_scraper.py` covering:

1. ✓ Proper section headings (standard Wikipedia structure)
2. ✓ Missing section headings (fallback to whole document)
3. ✓ Multiple tables (correct table selection by headers)
4. ✓ Error messages with diagnostics
5. ✓ TOC mismatch detection

All tests pass successfully.

## Files Changed

- `scrapers/grands_prix/red_flagged_races_scraper/base.py`: Improved error handling and diagnostics
- `tests/test_red_flagged_races_scraper.py`: New comprehensive test suite

## Expected Behavior

With these changes:

1. **Normal case**: Scraper finds section by ID and parses the table
2. **Missing sections**: Scraper falls back to whole document search
3. **Malformed HTML**: Scraper provides detailed diagnostics in error message
4. **Multiple tables**: Scraper selects correct table based on expected headers

The scraper is now much more robust and will work even when Wikipedia page structure is non-standard or incomplete.
