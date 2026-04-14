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


def clean_archetype_name(archetype: str) -> str:
    """Remove UUID suffix from archetype name."""
    # Remove UUID pattern like: 468d6491 E6a9 46c8 B9fb Da35bfca78fa
    # UUID format: 8-4-4-4-12 hex digits separated by spaces/hyphens
    import re
    # Match and remove UUID at the end (preceded by space)
    cleaned = re.sub(r'\s+[0-9a-fA-F]{8}\s+[0-9a-fA-F]{4}\s+[0-9a-fA-F]{4}\s+[0-9a-fA-F]{4}\s+[0-9a-fA-F]{12}$', '', archetype)
    return cleaned.strip()


def analyze_hate_cards(csv_path: Path) -> dict:
    """Analyze hate cards per archetype from CSV."""
    hate_cards = load_hate_cards()
    archetype_hate_cards = {}  # Use regular dict to preserve order + handle duplicates
    archetype_counts = defaultdict(int)  # Track duplicate archetype names
    
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            archetype = clean_archetype_name(row["archetype"])
            
            # Handle duplicate archetype names
            archetype_counts[archetype] += 1
            if archetype_counts[archetype] > 1:
                # Append counter for duplicates
                archetype_key = f"{archetype} {archetype_counts[archetype]}"
            else:
                archetype_key = archetype
            
            # Initialize if not seen before
            if archetype_key not in archetype_hate_cards:
                archetype_hate_cards[archetype_key] = {"maindeck": [], "sideboard": []}
            
            # Process maindeck cards
            if row.get("maindeck_cards"):
                try:
                    maindeck_data = json.loads(row["maindeck_cards"])
                    for card in maindeck_data:
                        card_name = card["card_name"].lower()
                        if card_name in hate_cards:
                            archetype_hate_cards[archetype_key]["maindeck"].append(card)
                except (json.JSONDecodeError, KeyError):
                    pass
            
            # Process sideboard cards
            if row.get("sideboard_cards"):
                try:
                    sideboard_data = json.loads(row["sideboard_cards"])
                    for card in sideboard_data:
                        card_name = card["card_name"].lower()
                        if card_name in hate_cards:
                            archetype_hate_cards[archetype_key]["sideboard"].append(card)
                except (json.JSONDecodeError, KeyError):
                    pass
    
    return dict(archetype_hate_cards)


def generate_report(hate_cards_data: dict, csv_path: Path) -> str:
    """Generate a formatted text report, with numbered variants grouped consecutively."""
    lines = []
    lines.append("=" * 80)
    lines.append("LEGACY HATE CARDS ANALYSIS")
    lines.append(f"Source: {csv_path.name}")
    lines.append("=" * 80)
    lines.append("")
    
    processed = set()
    
    for archetype in hate_cards_data.keys():
        # Skip if already processed (part of a numbered group)
        if archetype in processed:
            continue
        
        # Check if this archetype has numbered variants (e.g., "JESKAI CONTROL" and "JESKAI CONTROL 2")
        base_name = archetype
        if archetype and archetype[-1].isdigit() and archetype[-2] == ' ':
            # This is a numbered archetype, find the base
            base_name = archetype[:-2]
        
        # Find all variants of this archetype
        variants = [base_name]
        i = 2
        while f"{base_name} {i}" in hate_cards_data:
            variants.append(f"{base_name} {i}")
            i += 1
        
        # Output all variants consecutively
        for variant in variants:
            if variant not in hate_cards_data or variant in processed:
                continue
            
            data = hate_cards_data[variant]
            if not data["maindeck"] and not data["sideboard"]:
                processed.add(variant)
                continue
            
            lines.append(f"\n{variant.upper()}")
            lines.append("-" * 80)
            
            # Maindeck hate cards
            if data["maindeck"]:
                lines.append("\n  MAINDECK:")
                for card in sorted(data["maindeck"], key=lambda c: c["percentage"], reverse=True):
                    lines.append(
                        f"    • {card['card_name']:40s} "
                        f"avg: {card['avg_count']:>4.1f}x  |  {card['percentage']:>3d}% of decks"
                    )
            
            # Sideboard hate cards
            if data["sideboard"]:
                lines.append("\n  SIDEBOARD:")
                for card in sorted(data["sideboard"], key=lambda c: c["percentage"], reverse=True):
                    lines.append(
                        f"    • {card['card_name']:40s} "
                        f"avg: {card['avg_count']:>4.1f}x  |  {card['percentage']:>3d}% of decks"
                    )
            
            lines.append("")
            processed.add(variant)
    
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
