#!/usr/bin/env python3
"""
Generate a printer-friendly PDF from hate cards report.
Reads the latest report from output/reports/ and creates a single-page PDF.
"""
import logging
import re
from pathlib import Path
from weasyprint import HTML, CSS

OUTPUT_DIR = Path(__file__).parent.parent / "output"
REPORTS_DIR = OUTPUT_DIR / "reports"
PAPER_DIR = OUTPUT_DIR / "paper"


def get_latest_report() -> Path:
    """Get the latest text report from reports folder."""
    report_files = sorted(REPORTS_DIR.glob("hate_cards_report_*.txt"))
    if not report_files:
        raise FileNotFoundError("No report files found in output/reports/")
    return report_files[-1]


def extract_timestamp(report_path: Path) -> str:
    """Extract timestamp from report filename."""
    match = re.search(r'(\d{8}_\d{6})', report_path.name)
    if match:
        return match.group(1)
    return ""


def parse_report(report_path: Path) -> dict:
    """Parse text report into structured data."""
    archetypes = {}
    current_archetype = None
    current_section = None
    
    with open(report_path) as f:
        for line in f:
            line = line.rstrip()
            
            # Skip headers and separators
            if line.startswith("=") or not line.strip():
                continue
            
            # Detect archetype headers (all caps, followed by dashes)
            if line.isupper() and not line.startswith(" "):
                current_archetype = line.strip()
                archetypes[current_archetype] = {"maindeck": [], "sideboard": []}
                current_section = None
                continue
            
            # Detect section headers (MAINDECK: or SIDEBOARD:)
            if "MAINDECK:" in line:
                current_section = "maindeck"
                continue
            if "SIDEBOARD:" in line:
                current_section = "sideboard"
                continue
            
            # Parse card lines (• Card Name ...)
            if current_archetype and current_section and "•" in line:
                # Extract card data from line like:
                # "    • Card Name                                 avg:  X.Xx  |  YYY% of decks"
                match = re.search(r"•\s+(.+?)\s{2,}avg:\s+([\d.]+)x\s+\|\s+(\d+)%", line)
                if match:
                    card_name = match.group(1).strip()
                    avg_count = float(match.group(2))
                    percentage = int(match.group(3))
                    
                    archetypes[current_archetype][current_section].append({
                        "name": card_name,
                        "avg": avg_count,
                        "pct": percentage
                    })
    
    return archetypes


def generate_html(archetypes: dict, report_path: Path) -> str:
    """Generate HTML table for printing."""
    timestamp = extract_timestamp(report_path)
    date_str = f"20{timestamp[:2]}-{timestamp[2:4]}-{timestamp[4:6]}" if timestamp else "Unknown"
    
    html_parts = [
        """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 10mm;
            font-size: 9pt;
            line-height: 1.3;
        }
        h1 {
            font-size: 16pt;
            margin: 0 0 5pt 0;
            text-align: center;
        }
        .date {
            text-align: center;
            font-size: 8pt;
            margin-bottom: 10pt;
            color: #666;
        }
        .archetype-section {
            margin-bottom: 12pt;
            page-break-inside: avoid;
        }
        .archetype-name {
            font-weight: bold;
            font-size: 10pt;
            background-color: #f0f0f0;
            padding: 2pt 4pt;
            margin-bottom: 3pt;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 8pt;
            margin-bottom: 3pt;
        }
        th {
            background-color: #ddd;
            font-weight: bold;
            text-align: left;
            padding: 2pt 4pt;
            border-bottom: 1px solid #999;
        }
        td {
            padding: 2pt 4pt;
            border-bottom: 1px solid #e0e0e0;
        }
        .maindeck-label {
            font-weight: bold;
            color: #333;
            font-size: 8pt;
            margin-top: 2pt;
            margin-bottom: 1pt;
        }
        .sideboard-label {
            font-weight: bold;
            color: #333;
            font-size: 8pt;
            margin-top: 2pt;
            margin-bottom: 1pt;
        }
        .avg-col { width: 15%; text-align: center; }
        .pct-col { width: 15%; text-align: center; }
    </style>
</head>
<body>
    <h1>Legacy Hate Cards Analysis</h1>
    <div class="date">Generated: """ + date_str + """</div>
"""
    ]
    
    for archetype in sorted(archetypes.keys()):
        data = archetypes[archetype]
        
        html_parts.append(f'    <div class="archetype-section">')
        html_parts.append(f'        <div class="archetype-name">{archetype}</div>')
        
        # Maindeck table
        if data["maindeck"]:
            html_parts.append('        <div class="maindeck-label">Maindeck</div>')
            html_parts.append('        <table>')
            html_parts.append('            <tr><th>Card</th><th class="avg-col">Avg</th><th class="pct-col">% Decks</th></tr>')
            for card in sorted(data["maindeck"], key=lambda c: c["pct"], reverse=True):
                html_parts.append(
                    f'            <tr><td>{card["name"]}</td>'
                    f'<td class="avg-col">{card["avg"]:.1f}x</td>'
                    f'<td class="pct-col">{card["pct"]}%</td></tr>'
                )
            html_parts.append('        </table>')
        
        # Sideboard table
        if data["sideboard"]:
            html_parts.append('        <div class="sideboard-label">Sideboard</div>')
            html_parts.append('        <table>')
            html_parts.append('            <tr><th>Card</th><th class="avg-col">Avg</th><th class="pct-col">% Decks</th></tr>')
            for card in sorted(data["sideboard"], key=lambda c: c["pct"], reverse=True):
                html_parts.append(
                    f'            <tr><td>{card["name"]}</td>'
                    f'<td class="avg-col">{card["avg"]:.1f}x</td>'
                    f'<td class="pct-col">{card["pct"]}%</td></tr>'
                )
            html_parts.append('        </table>')
        
        html_parts.append('    </div>')
    
    html_parts.append('</body>\n</html>')
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
        
        # Generate HTML
        html_content = generate_html(archetypes, report_path)
        
        # Save PDF
        timestamp = extract_timestamp(report_path)
        pdf_filename = f"hate_cards_{timestamp}.pdf" if timestamp else "hate_cards.pdf"
        pdf_path = PAPER_DIR / pdf_filename
        
        HTML(string=html_content).write_pdf(pdf_path)
        logger.info(f"PDF saved to: {pdf_path}")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
