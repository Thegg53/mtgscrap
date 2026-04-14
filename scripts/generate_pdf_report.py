#!/usr/bin/env python3
"""
Generate a printer-friendly PDF from hate cards report.
Reads the latest report from _output/reports/ and creates a single-page PDF.
Automatically scales font sizes to maximize readability while fitting on one page.
"""
import logging
import re
from pathlib import Path
from weasyprint import HTML, CSS

OUTPUT_DIR = Path(__file__).parent.parent / "_output"
REPORTS_DIR = OUTPUT_DIR / "reports"
PAPER_DIR = OUTPUT_DIR / "paper"


def get_latest_report() -> Path:
    """Get the latest text report from reports folder."""
    report_files = sorted(REPORTS_DIR.glob("hate_cards_report_*.txt"))
    if not report_files:
        raise FileNotFoundError("No report files found in _output/reports/")
    return report_files[-1]


def extract_timestamp(report_path: Path) -> str:
    """Extract timestamp from report filename."""
    match = re.search(r'(\d{8}_\d{6})', report_path.name)
    if match:
        return match.group(1)
    return ""


def parse_report(report_path: Path) -> list:
    """
    Parse text report into structured data.
    Returns a list of archetypes (preserving order) with top 3 cards per section.
    """
    archetypes = []
    current_archetype = None
    current_section = None
    archetype_dict = None
    skip_next_line = False
    
    with open(report_path) as f:
        for line in f:
            line = line.rstrip()
            
            # Skip header lines and separators
            if line.startswith("=") or not line.strip():
                skip_next_line = False
                continue
            
            # Skip known header lines
            if "LEGACY HATE CARDS ANALYSIS" in line or line.startswith("Source:"):
                continue
            
            # Skip lines that are just dashes (section separators)
            if line.strip() and all(c == '-' for c in line.strip()):
                skip_next_line = True
                continue
            
            # Detect archetype headers (all caps, doesn't start with space, not preceded by dashes we just skipped)
            if not skip_next_line and line.isupper() and not line.startswith(" "):
                current_archetype = line.strip()
                archetype_dict = {"name": current_archetype, "maindeck": [], "sideboard": []}
                archetypes.append(archetype_dict)
                current_section = None
                skip_next_line = False
                continue
            
            skip_next_line = False
            
            # Detect section headers (MAINDECK: or SIDEBOARD:)
            if "MAINDECK:" in line:
                current_section = "maindeck"
                continue
            if "SIDEBOARD:" in line:
                current_section = "sideboard"
                continue
            
            # Parse card lines (• Card Name ...)
            if archetype_dict and current_section and "•" in line:
                # Extract card data from line like:
                # "    • Card Name                                 avg:  X.Xx  |  YYY% of decks"
                match = re.search(r"•\s+(.+?)\s{2,}avg:\s+([\d.]+)x\s+\|\s+(\d+)%", line)
                if match:
                    card_name = match.group(1).strip()
                    avg_count = float(match.group(2))
                    percentage = int(match.group(3))
                    
                    archetype_dict[current_section].append({
                        "name": card_name,
                        "avg": avg_count,
                        "pct": percentage
                    })
    
    return archetypes


def format_card_list(cards: list, max_cards: int = 3) -> str:
    """
    Format up to max_cards cards as "Name avg/pct Name avg/pct ...".
    Cards are assumed to be sorted by percentage descending.
    """
    if not cards:
        return ""
    
    formatted = []
    for card in cards[:max_cards]:
        card_str = f"{card['name']} {card['avg']:.1f}/{card['pct']}%"
        formatted.append(card_str)
    
    return " | ".join(formatted)


def get_page_count(html_content: str) -> int:
    """Get the number of pages by rendering the HTML without saving."""
    try:
        doc = HTML(string=html_content).render()
        # Count pages from the document
        return len(doc.pages)
    except Exception as e:
        # If rendering fails, assume many pages (conservative)
        return 999


def find_optimal_font_sizes(archetypes: list, report_path: Path, logger) -> dict:
    """
    Iteratively find the maximum font sizes that fit on a single page.
    Starts with base sizes and increases until overflow is detected.
    """
    base_sizes = {
        'body': 7.5,
        'thead': 7.0,
        'cards': 6.5,
        'date': 6.5,
    }
    
    current_scale = 1.0
    increment = 0.02
    last_working_sizes = base_sizes.copy()
    max_iterations = 50
    iteration = 0
    
    logger.info("Optimizing font sizes for single-page fit...")
    
    while iteration < max_iterations:
        iteration += 1
        
        # Calculate sizes for current scale
        sizes = {k: round(v * current_scale, 2) for k, v in base_sizes.items()}
        
        # Generate HTML and check page count
        html_content = generate_html(archetypes, report_path, sizes)
        pages = get_page_count(html_content)
        
        if pages == 1:
            logger.info(f"  Scale {current_scale:.2f}x ({sizes['body']}pt body): ✓ 1 page")
            last_working_sizes = sizes.copy()
            current_scale += increment
        else:
            logger.info(f"  Scale {current_scale:.2f}x ({sizes['body']}pt body): ✗ {pages} pages - stopping")
            break
    
    logger.info(f"\nOptimal sizes found:")
    logger.info(f"  Body: {last_working_sizes['body']}pt")
    logger.info(f"  Headers: {last_working_sizes['thead']}pt")
    logger.info(f"  Cards: {last_working_sizes['cards']}pt")
    
    return last_working_sizes


def generate_html(archetypes: list, report_path: Path, font_sizes: dict = None) -> str:
    """
    Generate compact HTML table for single-page A4 printing.
    One row per archetype with top 3 cards per section.
    Constraint: Must fit on exactly one A4 page.
    
    Args:
        archetypes: List of archetype data
        report_path: Path to the report file
        font_sizes: Dict with keys: 'body', 'thead', 'cards', 'date' (in pt)
    """
    if font_sizes is None:
        font_sizes = {
            'body': 7.5,
            'thead': 7.0,
            'cards': 6.5,
            'date': 6.5,
        }
    
    timestamp = extract_timestamp(report_path)
    date_str = f"20{timestamp[:2]}-{timestamp[2:4]}-{timestamp[4:6]}" if timestamp else "Unknown"
    
    html_parts = [
        f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Legacy Hate Cards Analysis</title>
    <style>
        @page {{
            size: A4;
            margin: 8mm;
            orphans: 1;
            widows: 1;
        }}
        html, body {{
            margin: 0;
            padding: 0;
            width: 100%;
        }}
        body {{
            font-family: Arial, Helvetica, sans-serif;
            font-size: {font_sizes['body']}pt;
            line-height: 1.2;
            color: #000;
        }}
        h1 {{
            font-size: 14pt;
            margin: 0 0 2pt 0;
            text-align: center;
            font-weight: bold;
        }}
        .header {{
            text-align: center;
            margin-bottom: 4pt;
            border-bottom: 1px solid #000;
            padding-bottom: 2pt;
        }}
        .date {{
            font-size: {font_sizes['date']}pt;
            color: #444;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: {font_sizes['body']}pt;
            line-height: 1.1;
        }}
        thead {{
            background-color: #e0e0e0;
            font-weight: bold;
            font-size: {font_sizes['thead']}pt;
        }}
        th {{
            border: 0.5pt solid #000;
            padding: 1pt 2pt;
            text-align: left;
            font-weight: bold;
        }}
        td {{
            border: 0.5pt solid #ccc;
            padding: 1pt 2pt;
            vertical-align: top;
        }}
        .archetype-col {{
            width: 25%;
            font-weight: bold;
            word-wrap: break-word;
        }}
        .cards-col {{
            width: 75%;
            font-size: {font_sizes['cards']}pt;
        }}
        tbody tr:nth-child(odd) {{
            background-color: #ffffff;
        }}
        tbody tr:nth-child(even) {{
            background-color: #d0d0d0;
        }}
        .section-label {{
            font-weight: bold;
            color: #333;
            font-size: {font_sizes['cards']}pt;
        }}
        .cards-text {{
            color: #000;
            font-size: {font_sizes['cards']}pt;
            word-wrap: break-word;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Legacy Hate Cards Analysis</h1>
        <div class="date">Generated: """ + date_str + """</div>
    </div>
    <table>
        <thead>
            <tr>
                <th>Archetype</th>
                <th>Hate Cards (Maindeck | Sideboard)</th>
            </tr>
        </thead>
        <tbody>
"""
    ]
    
    # Process each archetype (preserving order)
    for arch_data in archetypes:
        md_cards = sorted(arch_data["maindeck"], key=lambda c: c["pct"], reverse=True)
        sb_cards = sorted(arch_data["sideboard"], key=lambda c: c["pct"], reverse=True)
        
        md_text = format_card_list(md_cards, max_cards=3)
        sb_text = format_card_list(sb_cards, max_cards=3)
        
        cards_html = ""
        if md_text and sb_text:
            cards_html = f'<span class="section-label">MD:</span> <span class="cards-text">{md_text}</span><br/><span class="section-label">SB:</span> <span class="cards-text">{sb_text}</span>'
        elif md_text:
            cards_html = f'<span class="section-label">MD:</span> <span class="cards-text">{md_text}</span>'
        elif sb_text:
            cards_html = f'<span class="section-label">SB:</span> <span class="cards-text">{sb_text}</span>'
        else:
            cards_html = '<span style="color: #ccc;">No hate cards</span>'
        
        html_parts.append(
            f'            <tr>'
            f'<td class="archetype-col">{arch_data["name"]}</td>'
            f'<td class="cards-col">{cards_html}</td>'
            f'</tr>'
        )
    
    html_parts.append(
        """        </tbody>
    </table>
</body>
</html>"""
    )
    
    return "\n".join(html_parts)


def main():
    """Main entry point."""
    PAPER_DIR.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        report_path = get_latest_report()
        logger.info(f"Reading report: {report_path.name}")
        
        # Parse text report
        archetypes = parse_report(report_path)
        
        if not archetypes:
            logger.warning("No data found in report")
            return
        
        logger.info(f"Found {len(archetypes)} archetypes")
        
        # Find optimal font sizes
        optimal_sizes = find_optimal_font_sizes(archetypes, report_path, logger)
        
        # Generate HTML with optimal sizes
        html_content = generate_html(archetypes, report_path, optimal_sizes)
        
        # Save PDF
        timestamp = extract_timestamp(report_path)
        pdf_filename = f"hate_cards_{timestamp}.pdf" if timestamp else "hate_cards.pdf"
        pdf_path = PAPER_DIR / pdf_filename
        
        HTML(string=html_content).write_pdf(str(pdf_path))
        logger.info(f"PDF saved to: {pdf_path}")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
