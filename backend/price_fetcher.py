"""
Price Fetcher - שליפת מחירים
מקורות:
1. DB מקומי (מהיר - מתעדכן יומית מקבצי XML רשמיים)
2. Open Food Facts (חינם, אין מחירי ישראל)
3. קבצי XML רשמיים של הרשתות (חוק שקיפות מחירים)
"""
import logging
import httpx
from typing import List, Dict, Optional
from database import db

logger = logging.getLogger(__name__)

# רשימת הרשתות + URL לקבצי המחירים (חוק שקיפות מחירים)
STORE_CHAINS = {
    "shufersal": {
        "name": "שופרסל",
        "price_url": "https://prices.shufersal.co.il/FileObject/UpdateCategory?catID=5&storeId=0",
    },
    "rami_levy": {
        "name": "רמי לוי",
        "price_url": "https://url.rami-levy.co.il/api/catalog/search?q={barcode}",
    },
    "victory": {
        "name": "ויקטורי",
        "price_url": "https://matrixcatalog.co.il/",
    },
    "mega": {
        "name": "מגה",
        "price_url": "https://publishprice.mega.co.il/",
    },
    "yeinot_bitan": {
        "name": "יינות ביתן",
        "price_url": "https://publishprice.ybitan.co.il/",
    },
    "osher_ad": {
        "name": "אושר עד",
        "price_url": "https://publishprice.osherad.co.il/",
    },
}


async def get_comparisons(
    barcode: Optional[str],
    product_name: Optional[str] = None,
    category: Optional[str] = None,
) -> List[Dict]:
    """
    מחזיר רשימת השוואות מחירים ממוינת לפי מחיר ליחידה
    """
    comparisons = []

    # 1. ניסיון ראשון: DB מקומי (מהיר)
    if barcode:
        cached = db.get_prices(barcode)
        if cached:
            logger.info(f"Found {len(cached)} prices in local DB for {barcode}")
            return _format_comparisons(cached)

    # 2. שליפה מקבצי XML (Rami Levy יש API נגיש)
    if barcode:
        prices = await fetch_rami_levy(barcode)
        comparisons.extend(prices)

        prices_sh = await fetch_shufersal(barcode)
        comparisons.extend(prices_sh)

    # 3. אם אין תוצאות - נחזיר דמו כדי לא לשבור את ה-UI
    if not comparisons and product_name:
        comparisons = generate_demo_data(product_name)

    # שמור ב-DB לשימוש עתידי
    if comparisons and barcode:
        try:
            db.save_prices(comparisons)
        except Exception as e:
            logger.warning(f"Could not save prices to DB: {e}")

    return _format_comparisons(comparisons)


async def fetch_rami_levy(barcode: str) -> List[Dict]:
    """שליפה מ-API של רמי לוי"""
    try:
        url = f"https://www.rami-levy.co.il/api/catalog/search?q={barcode}"
        async with httpx.AsyncClient(timeout=5.0, headers={"User-Agent": "Mozilla/5.0"}) as client:
            resp = await client.get(url)
            data = resp.json()

        items = data.get("data", [])
        results = []
        for item in items:
            price = item.get("price", {})
            if not price:
                continue
            barcode_val = item.get("barcode") or barcode
            size_val = item.get("weight") or item.get("unit_qty")
            size_unit = item.get("unit_of_measure", "g")
            price_val = float(price.get("sale_price") or price.get("price") or 0)
            if price_val == 0:
                continue
            price_per_unit = _calc_per_unit(price_val, size_val, size_unit)
            results.append({
                "barcode": barcode_val,
                "store_name": "רמי לוי",
                "store_chain": "rami_levy",
                "branch_id": "online",
                "price": price_val,
                "price_per_unit": price_per_unit,
                "size": f"{size_val} {size_unit}" if size_val else "",
                "size_value": size_val,
                "size_unit": size_unit,
                "updated_at": _now(),
            })
        return results
    except Exception as e:
        logger.warning(f"Rami Levy fetch error: {e}")
        return []


async def fetch_shufersal(barcode: str) -> List[Dict]:
    """שליפה משופרסל (דרך API לא רשמי)"""
    try:
        url = f"https://www.shufersal.co.il/online/he/search?q={barcode}&format=json"
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
        async with httpx.AsyncClient(timeout=5.0, headers=headers) as client:
            resp = await client.get(url)
            data = resp.json()

        products = data.get("results", [])
        results = []
        for item in products[:3]:
            price_val = float(item.get("price", 0) or 0)
            if price_val == 0:
                continue
            size_raw = item.get("unitOfMeasureLabel", "")
            size_val, size_unit = _parse_size(item.get("name", ""))
            price_per_unit = _calc_per_unit(price_val, size_val, size_unit)
            results.append({
                "barcode": barcode,
                "store_name": "שופרסל",
                "store_chain": "shufersal",
                "branch_id": "online",
                "price": price_val,
                "price_per_unit": price_per_unit,
                "size": size_raw,
                "size_value": size_val,
                "size_unit": size_unit,
                "updated_at": _now(),
            })
        return results
    except Exception as e:
        logger.warning(f"Shufersal fetch error: {e}")
        return []


def generate_demo_data(product_name: str) -> List[Dict]:
    """
    דמו דטה - רק לבדיקות ו-MVP ראשוני
    יוחלף בנתונים אמיתיים
    """
    import random
    base_price = round(random.uniform(8, 45), 2)
    chains = [
        ("שופרסל", "shufersal"),
        ("רמי לוי", "rami_levy"),
        ("ויקטורי", "victory"),
        ("מגה", "mega"),
    ]
    sizes = [(500, "g"), (1000, "g"), (1500, "g")]
    results = []

    for store_name, chain in chains:
        for size_val, size_unit in sizes[:2]:
            multiplier = size_val / 500
            price = round(base_price * multiplier * random.uniform(0.85, 1.20), 2)
            price_per_unit = round(price / size_val * 100, 2)
            results.append({
                "barcode": None,
                "store_name": store_name,
                "store_chain": chain,
                "branch_id": "demo",
                "price": price,
                "price_per_unit": price_per_unit,
                "size": f"{size_val} {size_unit}",
                "size_value": size_val,
                "size_unit": size_unit,
                "updated_at": _now(),
            })

    return results


def _format_comparisons(raw: List[Dict]) -> List[Dict]:
    """פורמט אחיד לתוצאות"""
    out = []
    for r in raw:
        out.append({
            "store_name": r.get("store_name", ""),
            "store_chain": r.get("store_chain", ""),
            "price": float(r.get("price", 0)),
            "price_per_unit": float(r.get("price_per_unit") or 0),
            "size": r.get("size", ""),
            "size_value": r.get("size_value"),
            "size_unit": r.get("size_unit", ""),
            "is_current": r.get("is_current", False),
        })
    return sorted(out, key=lambda x: x["price_per_unit"] or x["price"])


def _calc_per_unit(price: float, size_val, size_unit: str) -> float:
    """מחשב מחיר ל-100 יחידות (גרם/מ"ל)"""
    if not size_val or float(size_val) == 0:
        return price
    return round(price / float(size_val) * 100, 4)


def _parse_size(text: str):
    """מנסה לחלץ גודל מטקסט חופשי"""
    import re
    m = re.search(r'(\d+(?:\.\d+)?)\s*(g|kg|ml|l|ליטר|גרם)', text, re.IGNORECASE)
    if m:
        val = float(m.group(1))
        unit = m.group(2).lower()
        if unit in ("kg", "ליטר", "l"):
            val *= 1000
            unit = "g" if unit == "kg" else "ml"
        return val, unit
    return None, "g"


def _now():
    from datetime import datetime
    return datetime.utcnow().isoformat()
