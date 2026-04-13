"""

    mtg.deck.scrapers.goldfish
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    Scrape MTGGoldfish Legacy meta decklists and sideboard data.

    @author: mazz3rr

"""
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime

from mtg import Json
from mtg.utils import extract_int, timed
from mtg.utils.scrape import ScrapingError, http_requests_counted, fetch_throttled_soup

_log = logging.getLogger(__name__)


@dataclass
class MinimalDeck:
    """Minimal deck object for sideboard scraping."""
    name: str
    format: str = "legacy"
    archetype: str = ""
    source: str = ""
    decklist: str = ""
    metadata: dict = field(default_factory=dict)
    
    def update_metadata(self, **kwargs) -> None:
        """Update metadata dict."""
        for key, value in kwargs.items():
            if key == "meta":
                self.metadata.update(value)
            elif key == "sideboard":
                self.metadata["sideboard"] = value
            else:
                self.metadata[key] = value


HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9"
}
URL_PREFIX = "https://www.mtggoldfish.com"


def scrape_archetype_sideboard(archetype_url: str) -> list[dict]:
    """Extract sideboard cards from MTGGoldfish archetype page.
    
    Returns: List of dicts with card_name, avg_count, percentage
    """
    soup = fetch_throttled_soup(archetype_url, headers=HEADERS)
    if not soup:
        _log.warning(f"Failed to fetch sideboard data from {archetype_url}")
        return []
    
    sideboard_cards = []
    sideboard_headings = soup.find_all("h3", string=lambda s: s and "Sideboard" in s)
    
    if not sideboard_headings:
        return []
    
    sideboard_heading = sideboard_headings[-1]
    container = sideboard_heading.find_parent("div", class_="spoiler-card-container")
    if not container:
        return []
    
    card_divs = container.find_all("div", class_="spoiler-card", recursive=False)
    
    for card_div in card_divs:
        img = card_div.find("img", class_="price-card-image-image")
        if not img:
            continue
        
        card_alt = img.get("alt", "")
        card_name = card_alt.split(" <")[0] if "<" in card_alt else card_alt.split(" [")[0]
        
        stats_p = card_div.find("p", class_=lambda c: c and "text" in c)
        if stats_p:
            text = stats_p.text.strip()
            try:
                parts = text.split(" in ")
                avg_count = float(parts[0])
                percentage_str = parts[1].split("%")[0] if len(parts) > 1 else "0"
                percentage = int(percentage_str)
                
                sideboard_cards.append({
                    "card_name": card_name,
                    "avg_count": avg_count,
                    "percentage": percentage
                })
            except (ValueError, IndexError):
                pass
    
    return sideboard_cards


@http_requests_counted("scraping meta decks")
@timed("scraping meta decks", precision=1)
def scrape_meta(fmt="standard", limit: int | None = None, throttle: bool = False) -> list[MinimalDeck]:
    """Scrape MTGGoldfish meta page for a given format.
    
    Args:
        fmt: MTG format (e.g., "legacy", "modern")
        limit: optionally, limit the number of decks to scrape
        throttle: add random 1-3 second delays between deck scrapes
    
    Returns:
        List of MinimalDeck objects with sideboard data
    """
    fmt = fmt.lower()
    url = f"https://www.mtggoldfish.com/metagame/{fmt}/full"
    soup = fetch_throttled_soup(url, headers=HEADERS)
    if not soup:
        raise ScrapingError(f"Failed to fetch {url}")
    
    tiles = soup.find_all("div", class_="archetype-tile")
    if not tiles:
        raise ScrapingError("No archetype tiles found")
    
    if limit:
        tiles = tiles[:limit]
    
    decks, metas = [], []
    for i, tile in enumerate(tiles, start=1):
        link = tile.find("a")
        if not link or "href" not in link.attrs:
            continue
        
        archetype_url = f"https://www.mtggoldfish.com{link.attrs['href']}"
        
        # Extract archetype name from URL
        archetype_slug = link.attrs['href'].split("/")[-1]
        if "-" in archetype_slug:
            archetype_slug = "-".join(archetype_slug.split("-")[1:])
        archetype_name = " ".join(word.capitalize() for word in archetype_slug.split("-"))
        
        deck = MinimalDeck(name=archetype_name, format=fmt, archetype=archetype_name)
        
        count = tile.find("span", class_="archetype-tile-statistic-value-extra-data").text.strip()
        count = extract_int(count)
        metas.append({"place": i, "count": count})
        decks.append((deck, archetype_url))
    
    total = sum(m["count"] for m in metas)
    for idx, ((deck, archetype_url), meta) in enumerate(zip(decks, metas)):
        meta["share"] = meta["count"] * 100 / total
        meta["date"] = datetime.now().strftime("%Y-%m-%d")
        deck.update_metadata(meta=meta)
        
        sideboard_data = scrape_archetype_sideboard(archetype_url)
        if sideboard_data:
            deck.update_metadata(sideboard=sideboard_data)
        
        if throttle and idx < len(decks) - 1:
            delay = random.uniform(1, 3)
            _log.debug(f"Throttling: waiting {delay:.2f}s before next deck")
            time.sleep(delay)
    
    return [deck for deck, _ in decks]
