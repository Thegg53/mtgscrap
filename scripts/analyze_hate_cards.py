#!/usr/bin/env python3
"""
Analyze hate card usage across Legacy archetypes.
Parses the latest scrape CSV and filters for hate cards from _input/hatecards.txt.
"""
import csv
import json
import logging
import re
from pathlib import Path
from collections import defaultdict

OUTPUT_DIR = Path(__file__).parent.parent / "_output"
DECKS_DIR = OUTPUT_DIR / "decks"
REPORTS_DIR = OUTPUT_DIR / "reports"
INPUT_DIR = Path(__file__).parent.parent / "_input"


def load_hate_cards() -> set[str]:
    """Load hate cards from _input/hatecards.txt, ignoring comments."""
    hate_file = INPUT_DIR / "hatecards.txt"
    hate_cards = set()
    
    with open(hate_file) as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            hate_cards.add(line.lower())
    
    return hate_cards


def get_latest_csv() -> Path:
    """Get the latest CSV file from decks output folder."""
    # Check both old location (output/) and new location (output/decks/)
    csv_files = sorted(OUTPUT_DIR.glob("legacy_decklists_*.csv"))
    csv_files.extend(sorted(DECKS_DIR.glob("legacy_decklists_*.csv")))
    csv_files = sorted(set(csv_files))
    
    if not csv_files:
        raise FileNotFoundError("No CSV files found in _output/ or _output/decks/")
    return csv_files[-1]


def extract_timestamp(csv_path: Path) -> str:
    """Extract timestamp from CSV filename (YYYYMMDD_HHMMSS format)."""
    match = re.search(r'(\d{8}_\d{6})', csv_path.name)
    if match:
        return match.group(1)
    return ""


def analyze_hate_cards(csv_path: Path) -> dict:
    """Analyze hate cards per archetype from CSV."""
    hate_cards = load_hate_cards()
    archetype_hate_cards = defaultdict(lambda: {"maindeck": [], "sideboard": []})
    
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            archetype = row["archetype"]
            
            # Process maindeck cards
            if row.get("maindeck_cards"):
                try:
                    maindeck_data = json.loads(row["maindeck_cards"])
                    for card in maindeck_data:
                        card_name = card["card_name"].lower()
                        if card_name in hate_cards:
                            archetype_hate_cards[archetype]["maindeck"].append(card)
                except (json.JSONDecodeError, KeyError):
                    pass
            
            # Process sideboard cards
            if row.get("sideboard_cards"):
                try:
                    sideboard_data = json.loads(row["sideboard_cards"])
                    for card in sideboard_data:
                        card_name = card["card_name"].lower()
                        if card_name in hate_cards:
                            archetype_hate_cards[archetype]["sideboard"].append(card)
                except (json.JSONDecodeError, KeyError):
                    pass
    
    return dict(archetype_hate_cards)


def generate_report(hate_cards_data: dict, csv_path: Path) -> str:
    """Generate a formatted text report."""
    lines = []
    lines.append("=" * 80)
    lines.append("LEGACY HATE CARDS ANALYSIS")
    lines.append(f"Source: {csv_path.name}")
    lines.append("=" * 80)
    lines.append("")
    
    for archetype in sorted(hate_cards_data.keys()):
        data = hate_cards_data[archetype]
        maindeck = data["maindeck"]
        sideboard = data["sideboard"]
        
        if not maindeck and not sideboard:
            continue
        
        lines.append(f"\n{archetype.upper()}")
        lines.append("-" * 80)
        
        # Maindeck hate cards
        if maindeck:
            lines.append("\n  MAINDECK:")
            for card in sorted(maindeck, key=lambda c: c["percentage"], reverse=True):
                lines.append(
                    f"    • {card['card_name']:40s} "
                    f"avg: {card['avg_count']:>4.1f}x  |  {card['percentage']:>3d}% of decks"
                )
        
        # Sideboard hate cards
        if sideboard:
            lines.append("\n  SIDEBOARD:")
            for card in sorted(sideboard, key=lambda c: c["percentage"], reverse=True):
                lines.append(
                    f"    • {card['card_name']:40s} "
                    f"avg: {card['avg_count']:>4.1f}x  |  {card['percentage']:>3d}% of decks"
                )
        
        lines.append("")
    
    lines.append("=" * 80)
    return "\n".join(lines)


def main():
    """Main entry point."""
    # Create output directories if they don't exist
    DECKS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        csv_path = get_latest_csv()
        logger.info(f"Analyzing hate cards from: {csv_path.name}")
        
        hate_cards_data = analyze_hate_cards(csv_path)
        
        # Generate report
        report = generate_report(hate_cards_data, csv_path)
        
        # Extract timestamp from CSV and use it in report filename
        timestamp = extract_timestamp(csv_path)
        report_filename = f"hate_cards_report_{timestamp}.txt" if timestamp else "hate_cards_report.txt"
        output_file = REPORTS_DIR / report_filename
        
        with open(output_file, "w") as f:
            f.write(report)
        
        logger.info(f"Report saved to: {output_file}")
        
        # Print to console
        print(report)
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
