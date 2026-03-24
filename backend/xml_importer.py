"""
xml_importer.py - יבוא יומי של קבצי XML מחירים
הרץ כ-cron job יומי: python xml_importer.py

מקורות (חוק שקיפות מחירים):
- שופרסל: https://prices.shufersal.co.il
- רמי לוי: https://url.rami-levy.co.il
- ויקטורי: https://matrixcatalog.co.il
- מגה: https://publishprice.mega.co.il
"""
import asyncio
import httpx
import gzip
import xml.etree.ElementTree as ET
import logging
import os
from datetime import datetime
from database import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# URLs לקבצי המחירים הרשמיים
PRICE_SOURCES = [
    {
        "chain": "shufersal",
        "name": "שופרסל",
        "index_url": "https://prices.shufersal.co.il/FileObject/UpdateCategory?catID=5&storeId=0",
    },
    {
        "chain": "rami_levy",
        "name": "רמי לוי",
        "index_url": "https://url.rami-levy.co.il/api/catalog/",
    },
]


async def download_and_parse_xml(url: str, chain: str, store_name: str) -> list:
    """מוריד קובץ XML (או gz) ומפרסר מחירים"""
    prices = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, follow_redirects=True)
            content = resp.content

            # אם gz - פתח
            if url.endswith(".gz") or content[:2] == b'\x1f\x8b':
                content = gzip.decompress(content)

            root = ET.fromstring(content)

            # מבנה XML שופרסל/רמי לוי
            for item in root.iter("Item"):
                try:
                    barcode = (
                        item.findtext("ItemCode") or
                        item.findtext("Barcode") or ""
                    ).strip()
                    if not barcode:
                        continue

                    price_str = item.findtext("ItemPrice") or item.findtext("Price") or "0"
                    price = float(price_str.replace(",", "."))
                    if price <= 0:
                        continue

                    name = item.findtext("ItemName") or item.findtext("Name") or ""
                    size_raw = item.findtext("UnitQty") or item.findtext("Quantity") or ""
                    unit = item.findtext("UnitOfMeasure") or "g"
                    branch_id = root.findtext("StoreId") or root.findtext("BranchNumber") or "0"

                    size_val = float(size_raw) if size_raw else None
                    price_per_unit = round(price / size_val * 100, 4) if size_val and size_val > 0 else price

                    prices.append({
                        "barcode": barcode,
                        "store_name": store_name,
                        "store_chain": chain,
                        "branch_id": branch_id,
                        "price": price,
                        "price_per_unit": price_per_unit,
                        "size": f"{size_raw} {unit}".strip() if size_raw else "",
                        "size_value": size_val,
                        "size_unit": unit,
                        "updated_at": datetime.utcnow().isoformat(),
                    })

                    # שמור גם מוצר אם לא קיים
                    if name:
                        try:
                            existing = db.get_product_by_barcode(barcode)
                            if not existing:
                                db.save_product({
                                    "barcode": barcode,
                                    "name": name,
                                    "size": f"{size_raw} {unit}".strip(),
                                })
                        except Exception:
                            pass

                except (ValueError, AttributeError):
                    continue

        except Exception as e:
            logger.error(f"Error processing {url}: {e}")

    return prices


async def run_import():
    """הרץ יבוא מלא"""
    logger.info(f"Starting XML import at {datetime.now()}")
    total = 0

    # כאן יש להוסיף את ה-URLs הספציפיים של הקבצים
    # כל רשת מפרסמת אינדקס - צריך קודם לשלוף ממנו את הקבצים
    # לדוגמה פשוטה - URL ישיר:
    test_urls = [
        # ("https://prices.shufersal.co.il/...", "shufersal", "שופרסל"),
    ]

    for url, chain, name in test_urls:
        prices = await download_and_parse_xml(url, chain, name)
        if prices:
            db.bulk_import_prices(prices)
            total += len(prices)
            logger.info(f"Imported {len(prices)} prices from {name}")

    logger.info(f"Import complete. Total: {total} prices")


if __name__ == "__main__":
    asyncio.run(run_import())
