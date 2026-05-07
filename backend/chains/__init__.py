"""
Chains package - מודולי הורדת XML מרשתות שיווק שונות

כל רשת מקבלת קובץ נפרד שיורש מ-BaseChainScraper.
כשנוסיף רשתות חדשות (publishedprices, mega, וכו') - פשוט נוסיף קובץ פה.
"""
from .base import BaseChainScraper
from .shufersal import ShufersalScraper

# רשימת כל ה-scrapers הזמינים
AVAILABLE_SCRAPERS = [
    ShufersalScraper,
    # בעתיד נוסיף:
    # PublishedPricesScraper,  # רמי לוי, ויקטורי, יוחננוף, חצי חינם...
    # MegaScraper,
    # BitanScraper,
]

__all__ = ["BaseChainScraper", "ShufersalScraper", "AVAILABLE_SCRAPERS"]
