"""
xml_importer.py - יבוא מחירי סופרמרקט מ-Kaggle dataset

מקור הנתונים: https://www.kaggle.com/datasets/erlichsefi/israeli-supermarkets-2024
הנתונים מתעדכנים כל 4 שעות ע"י OpenIsraeliSupermarkets

דרישות:
  - KAGGLE_USERNAME + KAGGLE_KEY (env vars) - חינם מ-kaggle.com
  - pip install kaggle

הרצה: python xml_importer.py
"""
import os
import sys
import csv
import io
import logging
import zipfile
import shutil
from datetime import datetime
from database import db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DUMP_DIR = os.path.join(os.path.dirname(__file__), "dumps")
KAGGLE_DATASET = "erlichsefi/israeli-supermarkets-2024"

# קבצי PriceFull שנרצה לייבא + שם הרשת בעברית
CHAIN_FILES = {
    "price_full_file_shufersal": "שופרסל",
    "price_full_file_rami_levy": "רמי לוי",
    "price_full_file_victory": "ויקטורי",
    "price_full_file_yayno_bitan": "יינות ביתן",
    "price_full_file_osher_ad": "אושר עד",
    "price_full_file_hazi_hinam": "חצי חינם",
    "price_full_file_tiv_taam": "טיב טעם",
    "price_full_file_mega": "מגה",
}

# עמודות שונות שיכולות להופיע ב-CSV (שמות שונים לפי רשת)
BARCODE_COLS = ["itemcode", "item_code", "barcode", "ItemCode"]
PRICE_COLS = ["itemprice", "item_price", "price", "ItemPrice"]
NAME_COLS = ["itemname", "item_name", "name", "ItemName"]
BRAND_COLS = ["manufacturername", "manufacturer_name", "ManufacturerName", "brand"]
SIZE_COLS = ["unitqty", "unit_qty", "quantity", "UnitQty", "Quantity"]
UNIT_COLS = ["unitofmeasure", "unit_of_measure", "UnitOfMeasure"]
STORE_COLS = ["storeid", "store_id", "StoreId", "subchainid"]


def find_col(row: dict, candidates: list) -> str:
    """מוצא את שם העמודה הנכון מתוך רשימת אפשרויות"""
    row_lower = {k.lower(): k for k in row.keys()}
    for c in candidates:
        if c.lower() in row_lower:
            return row_lower[c.lower()]
    return ""


def download_from_kaggle():
    """הורדת הנתונים מ-Kaggle"""
    username = os.environ.get("KAGGLE_USERNAME", "")
    key = os.environ.get("KAGGLE_KEY", "")

    if not username or not key:
        logger.error("Missing KAGGLE_USERNAME or KAGGLE_KEY environment variables!")
        logger.error("Get your free API token from: https://www.kaggle.com/settings -> API -> Create New Token")
        return False

    # הגדר kaggle credentials
    os.environ["KAGGLE_USERNAME"] = username
    os.environ["KAGGLE_KEY"] = key

    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()

        os.makedirs(DUMP_DIR, exist_ok=True)
        logger.info(f"Downloading dataset from Kaggle: {KAGGLE_DATASET}")
        api.dataset_download_files(KAGGLE_DATASET, path=DUMP_DIR, unzip=True)
        logger.info("Download complete!")
        return True

    except ImportError:
        logger.error("kaggle package not installed. Run: pip install kaggle")
        return False
    except Exception as e:
        logger.error(f"Kaggle download error: {e}")
        return False


def import_csv_file(filepath: str, chain_name: str) -> int:
    """מייבא קובץ CSV יחיד ל-DB"""
    imported = 0
    products_added = 0

    try:
        # זהה encoding
        with open(filepath, "rb") as f:
            raw = f.read(1000)
        encoding = "utf-8"
        if b"\xff\xfe" in raw[:4] or b"\xfe\xff" in raw[:4]:
            encoding = "utf-16"

        with open(filepath, "r", encoding=encoding, errors="ignore") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                logger.warning(f"Empty CSV: {filepath}")
                return 0

            # מצא את שמות העמודות הנכונים
            sample_row = {k: "" for k in reader.fieldnames}
            barcode_col = find_col(sample_row, BARCODE_COLS)
            price_col = find_col(sample_row, PRICE_COLS)
            name_col = find_col(sample_row, NAME_COLS)
            brand_col = find_col(sample_row, BRAND_COLS)
            size_col = find_col(sample_row, SIZE_COLS)
            unit_col = find_col(sample_row, UNIT_COLS)
            store_col = find_col(sample_row, STORE_COLS)

            if not barcode_col or not price_col:
                logger.warning(f"Missing barcode/price columns in {filepath}. Columns: {reader.fieldnames}")
                return 0

            logger.info(f"  Columns found: barcode={barcode_col}, price={price_col}, name={name_col}")

            prices_batch = []
            chain_key = chain_name.lower().replace(" ", "_")

            for row in reader:
                try:
                    barcode = (row.get(barcode_col) or "").strip()
                    if not barcode or len(barcode) < 7:
                        continue

                    price_str = (row.get(price_col) or "0").strip()
                    price = float(price_str.replace(",", "."))
                    if price <= 0 or price > 10000:
                        continue

                    name = (row.get(name_col) or "").strip() if name_col else ""
                    brand = (row.get(brand_col) or "").strip() if brand_col else ""
                    size_raw = (row.get(size_col) or "").strip() if size_col else ""
                    unit = (row.get(unit_col) or "").strip() if unit_col else ""
                    branch_id = (row.get(store_col) or "0").strip() if store_col else "0"

                    size_val = None
                    try:
                        size_val = float(size_raw) if size_raw else None
                    except ValueError:
                        pass

                    # חישוב מחיר ליחידה
                    price_per_unit = price
                    if size_val and size_val > 0:
                        normalized = size_val
                        unit_lower = unit.lower()
                        if unit_lower in ("kg", 'ק"ג', "קג", "קילו"):
                            normalized = size_val * 1000
                        elif unit_lower in ("l", "ליטר", "ל", "liter"):
                            normalized = size_val * 1000
                        if normalized > 0:
                            price_per_unit = round(price / normalized * 100, 4)

                    size_str = f"{size_raw} {unit}".strip() if size_raw else ""

                    prices_batch.append({
                        "barcode": barcode,
                        "store_name": chain_name,
                        "store_chain": chain_key,
                        "branch_id": branch_id,
                        "price": price,
                        "price_per_unit": price_per_unit,
                        "size": size_str,
                        "size_value": size_val,
                        "size_unit": unit,
                        "updated_at": datetime.utcnow().isoformat(),
                    })

                    # שמור מוצר (רק אם יש שם)
                    if name and not db.get_product_by_barcode(barcode):
                        db.save_product({
                            "barcode": barcode,
                            "name": name,
                            "brand": brand,
                            "size": size_str,
                            "category": "",
                            "image_url": "",
                        })
                        products_added += 1

                    # ייבוא בקבוצות של 5000
                    if len(prices_batch) >= 5000:
                        db.bulk_import_prices(prices_batch)
                        imported += len(prices_batch)
                        prices_batch = []

                except (ValueError, AttributeError):
                    continue

            # ייבוא השארית
            if prices_batch:
                db.bulk_import_prices(prices_batch)
                imported += len(prices_batch)

    except Exception as e:
        logger.error(f"Error importing {filepath}: {e}")

    logger.info(f"  {chain_name}: {imported} prices, {products_added} new products")
    return imported


def import_downloaded_files() -> int:
    """מייבא את כל הקבצים שהורדו"""
    if not os.path.exists(DUMP_DIR):
        logger.warning("No dump directory found")
        return 0

    total = 0

    # חפש קבצי CSV שתואמים לרשתות
    for file_prefix, chain_name in CHAIN_FILES.items():
        # חפש את הקובץ
        found = None
        for root, dirs, files in os.walk(DUMP_DIR):
            for f in files:
                if f.lower().startswith(file_prefix.lower()) and f.endswith(".csv"):
                    found = os.path.join(root, f)
                    break
            if found:
                break

        if not found:
            # נסה חיפוש גמיש יותר
            chain_short = file_prefix.replace("price_full_file_", "")
            for root, dirs, files in os.walk(DUMP_DIR):
                for f in files:
                    if chain_short in f.lower() and "price" in f.lower() and f.endswith(".csv"):
                        found = os.path.join(root, f)
                        break
                if found:
                    break

        if found:
            logger.info(f"Found: {os.path.basename(found)} -> {chain_name}")
            count = import_csv_file(found, chain_name)
            total += count
        else:
            logger.warning(f"File not found for {chain_name} ({file_prefix})")

    return total


def cleanup_dumps():
    """ניקוי קבצים שהורדו"""
    if os.path.exists(DUMP_DIR):
        shutil.rmtree(DUMP_DIR)
        logger.info("Cleaned up dump directory")


def run_full_import():
    """הרצת תהליך מלא: הורדה מ-Kaggle -> יבוא -> ניקוי"""
    start = datetime.now()
    logger.info(f"=== Starting Kaggle import at {start} ===")

    # שלב 1: הורדה
    success = download_from_kaggle()
    if not success:
        logger.error("Download failed. Aborting.")
        return 0

    # שלב 2: יבוא
    total = import_downloaded_files()

    # שלב 3: ניקוי
    cleanup_dumps()

    elapsed = (datetime.now() - start).total_seconds()
    logger.info(f"=== Import complete: {total} prices in {elapsed:.0f}s ===")

    return total


if __name__ == "__main__":
    run_full_import()
