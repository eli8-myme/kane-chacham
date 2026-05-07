"""
XML Importer - יבוא מחירים מקבצי XML של רשתות השיווק

הקובץ הזה הוא ה-entry point של תהליך הייבוא:
1. מפעיל את כל הסקרייפרים
2. שומר את הנתונים בדאטאבייס
3. ניתן לקריאה מ-main.py (POST /api/import) או מה-Cron Job

איך מוסיפים רשת חדשה:
1. יוצרים קובץ ב-chains/ עם המחלקה החדשה
2. מוסיפים אותה ל-AVAILABLE_SCRAPERS ב-chains/__init__.py
3. זהו - הכל ירוץ אוטומטית!
"""
import logging
import sys
from datetime import datetime
from typing import List, Dict

from database import db
from chains import AVAILABLE_SCRAPERS

# הגדרת logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
)
logger = logging.getLogger(__name__)


def save_products_and_prices(records: List[Dict]) -> Dict[str, int]:
    """
    שומר את המוצרים והמחירים בדאטאבייס.
    
    כל record מהסקרייפר מכיל גם נתוני מוצר וגם נתוני מחיר -
    אנחנו מפצלים אותם ושומרים בנפרד.
    
    Returns: dict עם מונים { "products": N, "prices": M }
    """
    if not records:
        logger.warning("⚠️  אין נתונים לשמירה")
        return {"products": 0, "prices": 0}
    
    # ===== שלב 1: שמירת מוצרים ייחודיים =====
    logger.info(f"💾 שומר מוצרים ייחודיים...")
    
    seen_barcodes = set()
    unique_products = []
    
    for record in records:
        barcode = record.get("barcode")
        if barcode and barcode not in seen_barcodes:
            seen_barcodes.add(barcode)
            unique_products.append({
                "barcode": barcode,
                "name": record.get("name", ""),
                "brand": record.get("brand", ""),
                "size": record.get("size", ""),
                "category": "",  # ה-XML של ישראל לא כולל קטגוריות
                "image_url": "",  # נמלא בהמשך מ-Open Food Facts
            })
    
    products_saved = 0
    for product in unique_products:
        try:
            db.save_product(product)
            products_saved += 1
        except Exception as e:
            logger.debug(f"שגיאה בשמירת מוצר {product.get('barcode')}: {e}")
    
    logger.info(f"✓ נשמרו {products_saved} מוצרים ייחודיים (מתוך {len(unique_products)})")
    
    # ===== שלב 2: שמירת מחירים =====
    logger.info(f"💰 שומר רשומות מחיר...")
    
    # ממירים records למבנה של prices
    prices_to_save = []
    for record in records:
        prices_to_save.append({
            "barcode": record.get("barcode"),
            "store_name": record.get("store_name"),
            "store_chain": record.get("store_chain"),
            "branch_id": record.get("branch_id", ""),
            "price": record.get("price"),
            "price_per_unit": record.get("price_per_unit"),
            "size": record.get("size"),
            "size_value": record.get("size_value"),
            "size_unit": record.get("size_unit"),
            "updated_at": record.get("updated_at", datetime.utcnow().isoformat()),
        })
    
    try:
        db.bulk_import_prices(prices_to_save)
        prices_saved = len(prices_to_save)
        logger.info(f"✓ נשמרו {prices_saved} רשומות מחיר")
    except Exception as e:
        logger.error(f"שגיאה בשמירת מחירים: {e}")
        prices_saved = 0
    
    return {
        "products": products_saved,
        "prices": prices_saved,
    }


def run_full_import(max_branches_per_chain: int = 5) -> int:
    """
    הפונקציה הראשית - מפעילה את כל הסקרייפרים ושומרת נתונים.
    
    Args:
        max_branches_per_chain: כמה סניפים מקסימום להוריד מכל רשת (MVP=5)
    
    Returns:
        סה"כ רשומות מחיר שנשמרו
    """
    start_time = datetime.utcnow()
    logger.info("=" * 60)
    logger.info(f"🚀 מתחיל ייבוא XML | {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    logger.info(f"📊 מספר רשתות פעילות: {len(AVAILABLE_SCRAPERS)}")
    logger.info(f"🏪 מקסימום סניפים לרשת: {max_branches_per_chain}")
    logger.info("=" * 60)
    
    total_prices = 0
    total_products = 0
    chain_results = {}
    
    for ScraperClass in AVAILABLE_SCRAPERS:
        chain_name = ScraperClass.chain_name
        logger.info(f"\n{'─' * 60}")
        logger.info(f"📦 רשת: {chain_name}")
        logger.info(f"{'─' * 60}")
        
        try:
            scraper = ScraperClass(max_branches=max_branches_per_chain)
            records = scraper.scrape()
            
            if not records:
                logger.warning(f"⚠️  לא הוחזרו נתונים מ-{chain_name}")
                chain_results[chain_name] = {"products": 0, "prices": 0, "status": "empty"}
                continue
            
            # שמירה בדאטאבייס
            stats = save_products_and_prices(records)
            total_products += stats["products"]
            total_prices += stats["prices"]
            chain_results[chain_name] = {**stats, "status": "ok"}
            
        except Exception as e:
            logger.error(f"❌ שגיאה ברשת {chain_name}: {e}", exc_info=True)
            chain_results[chain_name] = {"products": 0, "prices": 0, "status": f"error: {e}"}
            continue
    
    # ===== סיכום =====
    duration = (datetime.utcnow() - start_time).total_seconds()
    logger.info("\n" + "=" * 60)
    logger.info("✅ ייבוא הושלם!")
    logger.info(f"⏱️  משך: {duration:.1f} שניות")
    logger.info(f"📊 סה\"כ מוצרים: {total_products}")
    logger.info(f"💰 סה\"כ רשומות מחיר: {total_prices}")
    logger.info("\nפירוט לפי רשת:")
    for chain, stats in chain_results.items():
        logger.info(f"  • {chain}: {stats['prices']} מחירים, {stats['products']} מוצרים [{stats['status']}]")
    logger.info("=" * 60)
    
    return total_prices


# מאפשר הפעלה ידנית מ-command line:
# python xml_importer.py
if __name__ == "__main__":
    # אם רוצים לשנות מספר סניפים: python xml_importer.py 10
    max_branches = 5
    if len(sys.argv) > 1:
        try:
            max_branches = int(sys.argv[1])
        except ValueError:
            pass
    
    total = run_full_import(max_branches_per_chain=max_branches)
    sys.exit(0 if total > 0 else 1)
