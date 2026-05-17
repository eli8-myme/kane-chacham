"""
Chains package - מודולי הורדת XML מרשתות שיווק שונות

כל רשת מקבלת קובץ נפרד שיורש מ-BaseChainScraper.
"""
from .base import BaseChainScraper
from .shufersal import ShufersalScraper
from .published_prices import (
    RamiLevyScraper,
    HaziHinamScraper,
    VictoryScraper,
    YohananofScraper,
    OsherAdScraper,
    TivTaamScraper,
)

# רשימת כל ה-scrapers הזמינים
AVAILABLE_SCRAPERS = [
    ShufersalScraper,
    RamiLevyScraper,
    HaziHinamScraper,
    VictoryScraper,
    YohananofScraper,
    OsherAdScraper,
    TivTaamScraper,
]

__all__ = [
    "BaseChainScraper",
    "ShufersalScraper",
    "RamiLevyScraper",
    "HaziHinamScraper",
    "VictoryScraper",
    "YohananofScraper",
    "OsherAdScraper",
    "TivTaamScraper",
    "AVAILABLE_SCRAPERS",
]
