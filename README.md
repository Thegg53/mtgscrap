# MTG Legacy Meta Scraper

Minimal scraper for MTGGoldfish Legacy format metagame statistics. Exports archetype decklists with aggregated sideboard and maindeck card data to CSV. Includes hate card analysis with text and PDF report generation.

## What This Does

- **Scrapes MTGGoldfish meta page** — Gets the latest Legacy format archetype decks with maindeck and sideboard stats
- **Extracts card data** — Aggregated maindeck and sideboard card statistics (avg count, % of decks using)
- **Exports to CSV** — Date, archetype name, and card-level maindeck/sideboard data
- **Analyzes hate cards** — Generates text reports of hate card usage per archetype from `_input/hatecards.txt`
- **Generates PDFs** — Converts hate card reports to printer-friendly PDF format
- **Optional throttling** — Random 1-3 second delays between requests to avoid blocking

## Installation

**Requirements:** Python 3.12+, [uv](https://github.com/astral-sh/uv)

```bash
# Clone and enter repo
git clone <repo> && cd <repo>

# Install dependencies (uv handles venv creation)
uv sync
```

This will create a `.venv/` directory with all locked dependencies.

## Usage

### Scrape All 60 Decks

```bash
make scrape-legacy
```

Creates timestamped CSV in `_output/decks/legacy_decklists_YYYYMMDD_HHMMSS.csv`

### Scrape with Limit (Testing)

```bash
make scrape-legacy ARGS="--limit 5"
```

Limits scraping to 5 archetypes.

### Scrape with Debug Output

```bash
make scrape-legacy ARGS="--limit 2 --debug"
```

### Scrape with Throttling

```bash
make scrape-legacy ARGS="--throttle"
```

Adds random 1-3 second delays between requests to avoid blocking MTGGoldfish.

### Analyze Hate Cards

```bash
make analyze-hate
```

Generates a text report of hate card usage per archetype:
- Saved to `_output/reports/hate_cards_report_YYYYMMDD_HHMMSS.txt` (matches the latest scrape)
- Displays maindeck and sideboard usage for each hate card
- Easy-to-read format with archetype sections

### Generate PDF Report

```bash
make generate-pdf
```

Converts the latest hate cards text report to a printable PDF:
- Saved to `_output/paper/hate_cards_YYYYMMDD_HHMMSS.pdf` (matches the report timestamp)
- Organized as formatted HTML tables with archetype grouping
- Optimized for single or multi-page printing
- Includes average count and deck percentage for each hate card

## Output Format

### Deck CSV
Location: `_output/decks/legacy_decklists_YYYYMMDD_HHMMSS.csv`

Columns:
- `date` — Scrape date (YYYY-MM-DD)
- `deck_name` — Archetype name (e.g., "Dimir Tempo")
- `format` — Always "legacy" for this scraper
- `archetype` — Archetype classification
- `author` — Empty (not available for meta decks)
- `url` — Link to archetype page on MTGGoldfish
- `maindeck_cards` — Empty (aggregated meta, not single decklists)
- `sideboard_cards` — JSON array of sideboard cards with usage statistics

### Sideboard Card Format

Each sideboard card in the JSON array is:
```json
{
  "card_name": "Force of Negation",
  "avg_count": 2.0,
  "percentage": 100
}
```

- `card_name` — Card name
- `avg_count` — Average copies in decks using this sideboard card
- `percentage` — % of meta decks that include this card in sideboard

**Example row:**
```
2026-04-13,Dimir Tempo,legacy,Dimir Tempo,,,,"[{"card_name": "Force of Negation", "avg_count": 2.0, "percentage": 100}, {"card_name": "Consign to Memory", "avg_count": 2.6, "percentage": 94}, ...]"
```

## Dependencies

**Core dependencies:**
- `beautifulsoup4` — HTML parsing
- `requests` — HTTP requests with throttling
- `lxml` — XML/HTML processing
- `contexttimer` — Performance timing decorator
- `weasyprint` — HTML to PDF conversion

## Notes

- Sideboard data is extracted from the aggregated "Sideboard" section on MTGGoldfish archetype pages
- Each archetype represents a meta snapshot (60 decks total across all archetypes)
- No individual decklists—only aggregated sideboard statistics


- Scraping is throttled (0.6-0.8s delays between requests per MTGGoldfish)
- Chrome runs **headless** (no windows visible) — check logs for status
- Sideboard data only includes cards used in 30%+ of meta decks

## TODO

- [ ] Change GitHub Actions cron schedule from hourly to Tuesdays at 9:00 AM GMT (`0 9 * * 2`)

