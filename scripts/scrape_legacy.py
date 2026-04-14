#!/usr/bin/env python3
"""
Scrape MTGGoldfish meta page for Legacy format decklists and export to CSV.
"""
import argparse
import logging
from datetime import datetime
from pathlib import Path

from mtgscrap.deck.goldfish import scrape_meta
from mtgscrap.deck.export import export_decks_to_csv

OUTPUT_DIR = Path(__file__).parent.parent / "_output" / "decks"


def scrape_legacy_decklists(limit: int | None = None, debug: bool = False, throttle: bool = False) -> None:
    """Scrape MTGGoldfish Legacy format meta page and export to CSV.
    
    Args:
        limit: optionally, limit the number of decks to scrape (useful for testing)
        debug: enable debug logging
        throttle: add random 1-3 second delay between deck scrapes to avoid blocking
    """
    # Configure logging
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    if debug:
        logger.debug("Debug mode enabled")
    
    logger.info("Starting MTGGoldfish Legacy scraper...")
    
    try:
        # Scrape Legacy format decklists from MTGGoldfish meta page
        limit_str = f" (limit: {limit})" if limit else ""
        logger.info(f"Scraping MTGGoldfish meta page for Legacy format{limit_str}...")
        decks = scrape_meta(fmt="legacy", limit=limit, throttle=throttle)
        
        if not decks:
            logger.warning("No decks scraped. Check if the page structure has changed.")
            return
        
        logger.info(f"Successfully scraped {len(decks)} Legacy decklists")
        
        if debug:
            for i, deck in enumerate(decks, 1):
                logger.debug(f"Deck {i}: {deck.name} ({deck.archetype}) - {deck.format}")
                sideboard = deck.metadata.get("sideboard", [])
                if sideboard:
                    logger.debug(f"  Sideboard cards: {len(sideboard)}")
                    for card in sideboard[:3]:  # Show first 3
                        logger.debug(f"    - {card['card_name']}: {card['avg_count']} in {card['percentage']}%")
        
        # Create output directory if it doesn't exist
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Generate timestamped CSV filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = OUTPUT_DIR / f"legacy_decklists_{timestamp}.csv"
        
        logger.debug(f"Exporting to: {csv_filename}")
        
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
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging with detailed output"
    )
    parser.add_argument(
        "--throttle",
        action="store_true",
        help="Add random 1-3 second delay between deck scrapes to avoid blocking"
    )
    args = parser.parse_args()
    
    scrape_legacy_decklists(limit=args.limit, debug=args.debug, throttle=args.throttle)
