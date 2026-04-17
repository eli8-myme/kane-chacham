"""
Price Fetcher - שליפת מחירים מה-DB
המחירים מתעדכנים יומית דרך xml_importer.py
"""
import logging
from typing import List, Dict, Optional
from database import db

logger = logging.getLogger(__name__)


async def get_comparisons(barcode: Optional[str] = None) -> List[Dict]:
    """
    מחזיר רשימת מחירים מה-DB, ממוינת לפי מחיר
    """
    if not barcode:
        return []

    cached = db.get_prices(barcode)
    if cached:
        logger.info(f"Found {len(cached)} prices in DB for {barcode}")
        return _format_and_dedupe(cached)

    logger.info(f"No prices found in DB for {barcode}")
    return []


def _format_and_dedupe(raw: List[Dict]) -> List[Dict]:
    """
    פורמט אחיד + דה-דופליקציה (מחיר אחד לכל רשת - הזול ביותר)
    """
    # קח את המחיר הזול ביותר לכל רשת
    best_per_chain = {}
    for r in raw:
        chain = r.get("store_chain", "")
        price = float(r.get("price", 0))
        if chain not in best_per_chain or price < best_per_chain[chain]["price"]:
            best_per_chain[chain] = {
                "store_name": r.get("store_name", ""),
                "store_chain": chain,
                "price": price,
                "price_per_unit": float(r.get("price_per_unit") or 0),
                "size": r.get("size", ""),
                "size_value": r.get("size_value"),
                "size_unit": r.get("size_unit", ""),
                "is_current": False,
            }

    result = list(best_per_chain.values())
    return sorted(result, key=lambda x: x["price"])
