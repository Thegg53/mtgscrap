# MTG Legacy Meta Scraper

Minimal scraper for MTGGoldfish Legacy format metagame statistics. Exports archetype decklists with aggregated sideboard and maindeck card data to CSV. Includes hate card analysis with text and PDF report generation.

## What This Does

- **Scrapes MTGGoldfish meta page** — Gets the latest Legacy format archetype decks with maindeck and sideboard stats
- **Extracts card data** — Aggregated maindeck and sideboard card statistics (avg count, % of decks using)
- **Exports to CSV** — Date, archetype name, and card-level maindeck/sideboard data
- **Analyzes hate cards** — Generates text reports of hate card usage per archetype from `input/hatecards.txt`
- **Generates PDFs** — Converts hate card reports to printer-friendly PDF format
- **Optional throttling** — Random 1-3 second delays between requests to avoid blocking

## Installation

**Requirements:** macOS, Python 3.12+

```bash
# Clone and enter repo
git clone <repo> && cd <repo>

# Create virtual environment
make venv

# Install dependencies
make install
```

This will create a `venv/` directory with all required packages.

## Usage

### Scrape All 60 Decks

```bash
make scrape-legacy
```

Creates timestamped CSV in `output/decks/legacy_decklists_YYYYMMDD_HHMMSS.csv`

### Analyze Hate Cards

```bash
make analyze-hate
```

Generates a text report of hate card usage per archetype:
- Saved to `output/reports/hate_cards_report_YYYYMMDD_HHMMSS.txt` (matches the latest scrape)
- Displays maindeck and sideboard usage for each hate card
- Easy-to-read format with archetype sections

### Generate PDF Report

```bash
make generate-pdf
```

Converts the latest hate cards text report to a printable PDF:
- Saved to `output/paper/hate_cards_YYYYMMDD_HHMMSS.pdf` (matches the report timestamp)
- Organized as formatted HTML tables with archetype grouping
- Optimized for single or multi-page printing
- Includes average count and deck percentage for each hate card

### Scrape with Throttling

Adds random 1-3 second delays between deck scrapes to avoid being blocked:

```bash
. venv/bin/activate && PYTHONPATH=$(PWD) python scripts/scrape_legacy.py --throttle
```

### Scrape Limited Decks (Testing)

```bash
. venv/bin/activate && PYTHONPATH=$(PWD) python scripts/scrape_legacy.py --limit 3
```

### With Debug Logging

```bash
. venv/bin/activate && PYTHONPATH=$(PWD) python scripts/scrape_legacy.py --limit 1 --debug
```

Shows:
- Which archetype decks are being scraped
- Number of maindeck and sideboard cards found per archetype
- First 3 cards with stats

## Flags

| Flag | Description |
|------|-------------|
| `--limit N` | Limit to N decks (useful for testing) |
| `--throttle` | Add random 1-3 second delays between deck scrapes |
| `--debug` | Enable verbose logging with detailed output |

## Makefile Targets

```bash
make venv           # Create Python 3.12+ virtual environment
make install        # Install dependencies (requires active venv)
make scrape-legacy  # Run Legacy format scraper and export to CSV
make analyze-hate   # Analyze hate cards from latest scrape
make clean          # Remove venv and cache files
```

## Output Format

### Deck CSV
Location: `output/decks/legacy_decklists_YYYYMMDD_HHMMSS.csv`

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

## Makefile Targets

```bash
make venv           # Create Python 3.12+ virtual environment
make install        # Install dependencies (requires active venv)
make scrape-legacy  # Run Legacy format scraper and export to CSV
make analyze-hate   # Analyze hate cards from latest scrape
make generate-pdf   # Generate printable PDF from latest hate cards report
make clean          # Remove venv and cache files
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

