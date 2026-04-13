# MTG Legacy Meta Scraper

Scrape MTGGoldfish meta decks for Magic: The Gathering Legacy format, extract sideboard statistics, and export to CSV.

## What This Does

- **Scrapes MTGGoldfish meta page** — Gets the latest Legacy format archetype decks
- **Extracts sideboard data** — Aggregated sideboard card stats (avg count, % of decks using)
- **Exports to CSV** — Deckname, format, archetype, author, URL, maindeck, and sideboard cards
- **Headless browser** — Chrome runs in background (no visible windows)

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

### Scrape Limited Decks (Testing)

```bash
. venv/bin/activate && PYTHONPATH=$(PWD) python scripts/scrape_legacy.py --limit 3
```

### With Debug Logging

```bash
. venv/bin/activate && PYTHONPATH=$(PWD) python scripts/scrape_legacy.py --limit 1 --debug
```

Shows:
- Which decks were scraped
- Number of sideboard cards found per deck
- First 3 sideboard cards with stats

## Flags

| Flag | Description |
|------|-------------|
| `--limit N` | Limit to N decks (useful for testing) |
| `--debug` | Enable verbose logging with detailed output |

## Output Format

CSV with columns:
- `date` — Deck date (YYYY-MM-DD)
- `deck_name` — Deck name from MTGGoldfish
- `format` — Always "legacy" for this scraper
- `archetype` — Archetype classification
- `author` — Deck author/source
- `url` — Link to archetype page on MTGGoldfish
- `maindeck_cards` — Full maindeck list (60 cards)
- `sideboard_cards` — JSON array of sideboard cards with stats

### Sideboard Card Format

Each sideboard card in the JSON is:
```json
{
  "card_name": "Force of Negation",
  "avg_count": 2.0,
  "percentage": 100
}
```

- `avg_count` — Average number of copies in decks using this card
- `percentage` — % of meta decks using this card

## Makefile Targets

```bash
make venv           # Create Python 3.12+ virtual environment
make install        # Install dependencies (requires active venv)
make install-dev    # Install + development tools (pytest, black, flake8)
make scrape-legacy  # Run Legacy format scraper (60 decks)
make clean          # Remove venv and cache files
```

## Notes

- Scraping is throttled (0.6-0.8s delays between requests per MTGGoldfish)
- Chrome runs **headless** (no windows visible) — check logs for status
- Sideboard data only includes cards used in 30%+ of meta decks

