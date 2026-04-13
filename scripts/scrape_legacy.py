#!/usr/bin/env python3
"""
Scrape MTGGoldfish meta page for Legacy format decklists and export to CSV.
"""
import argparse
import logging
from datetime import datetime
from pathlib import Path

from mtg.deck.scrapers.goldfish import scrape_meta
from mtg.deck.export import export_decks_to_csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def scrape_legacy_decklists(limit: int | None = None) -> None:
    """Scrape MTGGoldfish Legacy format meta page and export to CSV.
    
    Args:
        limit: optionally, limit the number of decks to scrape (useful for testing)
    """
    
    logger.info("Starting MTGGoldfish Legacy scraper...")
    
    try:
        # Scrape Legacy format decklists from MTGGoldfish meta page
        logger.info(f"Scraping MTGGoldfish meta page for Legacy format{f' (limit: {limit})' if limit else ''}...")
        decks = scrape_meta(fmt="legacy", limit=limit)
        
        if not decks:
            logger.warning("No decks scraped. Check if the page structure has changed.")
            return
        
        logger.info(f"Successfully scraped {len(decks)} Legacy decklists")
        
        # Create output directory if it doesn't exist
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Generate timestamped CSV filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = OUTPUT_DIR / f"legacy_decklists_{timestamp}.csv"
        
        # Export to CSV (format_filter already applied during scraping, but we filter in export too)
        export_decks_to_csv(
            decks,
            csv_filename,
            format_filter="legacy"
        )
        
        logger.info(f"CSV export complete: {csv_filename}")
        logger.info(f"Total decklists in CSV: {len(decks)}")
        
    except Exception as e:
        logger.error(f"Error during scraping: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape MTGGoldfish Legacy decklists to CSV")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of decks to scrape (useful for testing)"
    )
    args = parser.parse_args()
    
    scrape_legacy_decklists(limit=args.limit)
