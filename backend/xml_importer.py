"""
xml_importer.py - יבוא יומי של מחירי סופרמרקט מקבצי XML רשמיים
הרץ יומית: python xml_importer.py

משתמש בחבילת il-supermarket-scraper להורדת הקבצים
ומפרסר את ה-XML לתוך SQLite
"""
import os
import sys
import gzip
import xml.etree.ElementTree as ET
import logging
import glob
import shutil
from datetime import datetime
from database import db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# תיקיית הורדות
DUMP_DIR = os.path.join(os.path.dirname(__file__), "dumps")

# הרשתות שנרצה לייבא (שם ב-enum של il-supermarket-scraper)
ENABLED_CHAINS = [
    "SHUFERSAL",
    "RAMI_LEVY",
    "VICTORY",
    "YAYNO_BITAN_AND_CARREFOUR",
    "OSHER_AD",
    "HAZI_HINAM",
    "TIV_TAAM",
]

# מיפוי שמות רשתות לעברית
CHAIN_NAMES = {
    "SHUFERSAL": "שופרסל",
    "RAMI_LEVY": "רמי לוי",
    "VICTORY": "ויקטורי",
    "YAYNO_BITAN_AND_CARREFOUR": "יינות ביתן",
    "OSHER_AD": "אושר עד",
    "HAZI_HINAM": "חצי חינם",
    "TIV_TAAM": "טיב טעם",
}


def download_price_files():
    """הורדת קבצי PriceFull מכל הרשתות"""
    try:
        from il_supermarket_scarper import ScarpingTask
        from il_supermarket_scarper.scrappers_factory import ScraperFactory
        from il_supermarket_scarper.utils.file_types import FileTypesFilters
    except ImportError:
        logger.error("il-supermarket-scraper not installed. Run: pip install il-supermarket-scraper")
        sys.exit(1)

    os.makedirs(DUMP_DIR, exist_ok=True)

    logger.info(f"Downloading PriceFull files for {len(ENABLED_CHAINS)} chains...")

    for chain_name in ENABLED_CHAINS:
        try:
            chain_enum = ScraperFactory[chain_name]
            logger.info(f"Downloading: {chain_name} ({CHAIN_NAMES.get(chain_name, chain_name)})")

            scraper = ScarpingTask(
                enabled_scrapers=[chain_enum],
                files_types=[FileTypesFilters.PRICE_FULL_FILE],
                dump_folder=DUMP_DIR,
                limit=1,  # רק הקובץ האחרון (העדכני ביותר)
            )
            scraper.start()
            logger.info(f"Downloaded: {chain_name}")

        except Exception as e:
            logger.error(f"Error downloading {chain_name}: {e}")
            continue


def parse_xml_file(filepath: str, chain_key: str) -> tuple:
    """פרסור קובץ XML יחיד, מחזיר (products, prices)"""
    products = []
    prices = []
    store_name = CHAIN_NAMES.get(chain_key, chain_key)

    try:
        # פתח קובץ (gz או XML רגיל)
        if filepath.endswith(".gz"):
            with gzip.open(filepath, "rb") as f:
                content = f.read()
        else:
            with open(filepath, "rb") as f:
                content = f.read()

        root = ET.fromstring(content)

        # מצא StoreId/BranchNumber
        branch_id = (
            root.findtext("StoreId")
            or root.findtext("BranchId")
            or root.findtext(".//StoreId")
            or root.findtext(".//BranchId")
            or "0"
        ).strip()

        for item in root.iter("Item"):
            try:
                barcode = (
                    item.findtext("ItemCode")
                    or item.findtext("Barcode")
                    or ""
                ).strip()
                if not barcode or len(barcode) < 7:
                    continue

                price_str = (
                    item.findtext("ItemPrice")
                    or item.findtext("Price")
                    or "0"
                )
                price = float(price_str.replace(",", "."))
                if price <= 0:
                    continue

                name = (
                    item.findtext("ItemName")
                    or item.findtext("Name")
                    or ""
                ).strip()

                size_raw = item.findtext("UnitQty") or item.findtext("Quantity") or ""
                unit = (
                    item.findtext("UnitOfMeasure")
                    or item.findtext("UnitMeasure")
                    or ""
                ).strip()

                size_val = None
                try:
                    size_val = float(size_raw) if size_raw else None
                except ValueError:
                    pass

                # חישוב מחיר ליחידה
                price_per_unit = price
                if size_val and size_val > 0:
                    # נרמול: אם ק"ג -> גרם, אם ליטר -> מ"ל
                    normalized = size_val
                    if unit.lower() in ("kg", "ק\"ג", "קג"):
                        normalized = size_val * 1000
                    elif unit.lower() in ("l", "ליטר", "ל"):
                        normalized = size_val * 1000
                    price_per_unit = round(price / normalized * 100, 4) if normalized > 0 else price

                size_str = f"{size_raw} {unit}".strip() if size_raw else ""

                prices.append({
                    "barcode": barcode,
                    "store_name": store_name,
                    "store_chain": chain_key.lower(),
                    "branch_id": branch_id,
                    "price": price,
                    "price_per_unit": price_per_unit,
                    "size": size_str,
                    "size_value": size_val,
                    "size_unit": unit,
                    "updated_at": datetime.utcnow().isoformat(),
                })

                # שמור גם מוצר
                if name:
                    products.append({
                        "barcode": barcode,
                        "name": name,
                        "brand": item.findtext("ManufacturerName") or "",
                        "size": size_str,
                        "category": "",
                        "image_url": "",
                    })

            except (ValueError, AttributeError):
                continue

    except ET.ParseError as e:
        logger.error(f"XML parse error in {filepath}: {e}")
    except Exception as e:
        logger.error(f"Error processing {filepath}: {e}")

    return products, prices


def import_downloaded_files():
    """מייבא את כל הקבצים שהורדו ל-DB"""
    if not os.path.exists(DUMP_DIR):
        logger.warning("No dump directory found. Run download first.")
        return 0

    total_prices = 0
    total_products = 0

    for chain_key in ENABLED_CHAINS:
        chain_lower = chain_key.lower()
        # חפש קבצי pricefull שהורדו
        pattern = os.path.join(DUMP_DIR, "**", "*")
        all_files = glob.glob(pattern, recursive=True)

        price_files = [
            f for f in all_files
            if os.path.isfile(f)
            and "pricefull" in os.path.basename(f).lower()
            and (f.endswith(".xml") or f.endswith(".gz"))
        ]

        if not price_files:
            # נסה גם בלי "full"
            price_files = [
                f for f in all_files
                if os.path.isfile(f)
                and "price" in os.path.basename(f).lower()
                and "promo" not in os.path.basename(f).lower()
                and (f.endswith(".xml") or f.endswith(".gz"))
            ]

        logger.info(f"{CHAIN_NAMES.get(chain_key, chain_key)}: found {len(price_files)} price files")

        for filepath in price_files:
            products, prices = parse_xml_file(filepath, chain_key)

            if products:
                for prod in products:
                    try:
                        existing = db.get_product_by_barcode(prod["barcode"])
                        if not existing:
                            db.save_product(prod)
                            total_products += 1
                    except Exception:
                        pass

            if prices:
                try:
                    db.bulk_import_prices(prices)
                    total_prices += len(prices)
                    logger.info(f"  Imported {len(prices)} prices from {os.path.basename(filepath)}")
                except Exception as e:
                    logger.error(f"  Error importing prices: {e}")

    return total_prices


def cleanup_dumps():
    """ניקוי קבצים שהורדו"""
    if os.path.exists(DUMP_DIR):
        shutil.rmtree(DUMP_DIR)
        logger.info("Cleaned up dump directory")


def run_full_import():
    """הרצת תהליך מלא: הורדה -> יבוא -> ניקוי"""
    start = datetime.now()
    logger.info(f"=== Starting full import at {start} ===")

    # שלב 1: הורדה
    download_price_files()

    # שלב 2: יבוא
    total = import_downloaded_files()

    # שלב 3: ניקוי
    cleanup_dumps()

    elapsed = (datetime.now() - start).total_seconds()
    logger.info(f"=== Import complete: {total} prices in {elapsed:.0f}s ===")

    return total


if __name__ == "__main__":
    run_full_import()
