# MTG Legacy Meta Scraper

Minimal scraper for MTGGoldfish Legacy format metagame sideboard statistics. Exports archetype decklists with aggregated sideboard card data to CSV.

## What This Does

- **Scrapes MTGGoldfish meta page** — Gets the latest Legacy format archetype decks and sideboard stats
- **Extracts sideboard data** — Aggregated sideboard card statistics (avg count, % of decks using)
- **Exports to CSV** — Date, archetype name, and card-level sideboard data
- **Headless browser** — Chrome runs in background via Selenium (no visible windows)
- **Optional throttling** — Random 1-3 second delays between requests to avoid blocking

## Installation

**Requirements:** macOS, Python 3.12+, Chrome/Chromium browser

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

Creates timestamped CSV in `output/legacy_decklists_YYYYMMDD_HHMMSS.csv`

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
- Number of sideboard cards found per archetype
- First 3 sideboard cards with stats

## Flags

| Flag | Description |
|------|-------------|
| `--limit N` | Limit to N decks (useful for testing) |
| `--throttle` | Add random 1-3 second delays between deck scrapes |
| `--debug` | Enable verbose logging with detailed output |

## Output Format

CSV with columns:
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
make scrape-legacy  # Run Legacy format scraper (60 decks)
make clean          # Remove venv and cache files
```

## Dependencies

**Core dependencies:**
- `beautifulsoup4` — HTML parsing
- `selenium` — Headless Chrome browser automation
- `requests` — HTTP requests with throttling
- `lxml` — XML/HTML processing

**Removed:**
- scryfall.py (not needed for goldfish scraping)
- scrython (Scryfall API)
- Arena format support
- YouTube/video scraping modules

## Notes

- Sideboard data is extracted from the aggregated "Sideboard" section on MTGGoldfish archetype pages
- Each archetype represents a meta snapshot (60 decks total across all archetypes)
- No individual decklists—only aggregated sideboard statistics


- Scraping is throttled (0.6-0.8s delays between requests per MTGGoldfish)
- Chrome runs **headless** (no windows visible) — check logs for status
- Sideboard data only includes cards used in 30%+ of meta decks

