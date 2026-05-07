"""
Base Chain Scraper - מחלקת בסיס לכל רשתות השיווק

כל רשת חדשה צריכה לרשת מהמחלקה הזו ולממש:
1. get_store_files() - מחזיר רשימת URLs של קבצי PriceFull לסניפים
2. parse_xml() - אם פורמט ה-XML שונה (רוב הרשתות משתמשות באותו פורמט)

הלוגיקה המשותפת (הורדה, פירוק GZ, חישוב מחיר ליחידה) נמצאת כאן.
"""
import gzip
import io
import logging
from datetime import datetime
from typing import List, Dict, Optional
from xml.etree import ElementTree as ET

import httpx

logger = logging.getLogger(__name__)


class BaseChainScraper:
    """
    מחלקת בסיס לכל סקרייפר של רשת שיווק.
    
    מאפיינים שכל רשת צריכה להגדיר:
    - chain_name: שם הרשת בעברית (לדוגמה: "שופרסל")
    - chain_id: מזהה רשת (8-9 ספרות, לפי החוק)
    """
    
    chain_name: str = ""
    chain_id: str = ""
    
    # ניתן לדרוס headers בכל רשת
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    
    def __init__(self, branch_ids: Optional[List[str]] = None, max_branches: int = 5):
        """
        Args:
            branch_ids: רשימת מזהי סניפים ספציפיים להורדה (None = הכל עד max_branches)
            max_branches: מקסימום סניפים להורדה (לבדיקות, מונע overload)
        """
        self.branch_ids = branch_ids
        self.max_branches = max_branches
    
    # ===== מתודות שכל רשת חייבת לממש =====
    
    def get_store_files(self) -> List[Dict[str, str]]:
        """
        מחזיר רשימת קבצי PriceFull להורדה.
        כל פריט: {"branch_id": "001", "url": "https://...", "store_name": "..."}
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement get_store_files()")
    
    # ===== מתודות משותפות (לא לדרוס בדרך כלל) =====
    
    def download_and_extract(self, url: str) -> Optional[str]:
        """מוריד קובץ GZ ומחזיר את התוכן XML כטקסט."""
        try:
            with httpx.Client(timeout=30.0, follow_redirects=True, headers=self.HEADERS) as client:
                response = client.get(url)
                response.raise_for_status()
                
                # פירוק GZ
                with gzip.open(io.BytesIO(response.content), 'rt', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"שגיאה בהורדת {url}: {e}")
            return None
    
    def parse_xml(self, xml_content: str, branch_id: str, store_name: str) -> List[Dict]:
        """
        פירוק XML של PriceFull.
        רוב הרשתות בישראל משתמשות באותו פורמט (כי החוק מחייב), 
        אבל אם רשת ספציפית שונה - אפשר לדרוס מתודה זו.
        """
        results = []
        
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            logger.error(f"שגיאה בפירוק XML של סניף {branch_id}: {e}")
            return results
        
        # בכל ה-XML של רשתות בישראל, הפריטים נמצאים תחת Items/Item
        items = root.findall(".//Item")
        
        for item in items:
            try:
                product = self._parse_item(item, branch_id, store_name)
                if product:
                    results.append(product)
            except Exception as e:
                logger.debug(f"שגיאה בפירוק פריט: {e}")
                continue
        
        logger.info(f"  ✓ סניף {branch_id} ({store_name}): {len(results)} מוצרים")
        return results
    
    def _parse_item(self, item: ET.Element, branch_id: str, store_name: str) -> Optional[Dict]:
        """פירוק פריט בודד מתוך XML."""
        
        def get_text(tag: str, default: str = "") -> str:
            """מציאת טקסט בטאג. לפעמים יש tags באותיות שונות."""
            for variant in [tag, tag.lower(), tag.upper()]:
                el = item.find(variant)
                if el is not None and el.text:
                    return el.text.strip()
            return default
        
        # שדות חובה
        barcode = get_text("ItemCode")
        name = get_text("ItemName")
        price_str = get_text("ItemPrice")
        
        # אם חסר ברקוד או מחיר - לדלג
        if not barcode or not price_str:
            return None
        
        try:
            price = float(price_str)
            if price <= 0:
                return None  # מחירים אפסיים = מוצרים שאינם רלוונטיים
        except ValueError:
            return None
        
        # שדות נוספים
        brand = get_text("ManufacturerName")
        size_value_str = get_text("Quantity")
        size_unit = get_text("UnitQty") or get_text("UnitOfMeasure")
        unit_price_str = get_text("UnitOfMeasurePrice")
        
        # המרה למספרים
        try:
            size_value = float(size_value_str) if size_value_str else None
        except ValueError:
            size_value = None
        
        try:
            price_per_unit = float(unit_price_str) if unit_price_str else None
        except ValueError:
            price_per_unit = None
        
        # אם אין מחיר ליחידה אבל יש גודל - נחשב
        if not price_per_unit and size_value and size_value > 0:
            price_per_unit = round(price / size_value, 2)
        
        # בניית size טקסטואלי
        size_text = ""
        if size_value and size_unit:
            size_text = f"{size_value} {size_unit}"
        
        return {
            "barcode": barcode,
            "name": name,
            "brand": brand,
            "size": size_text,
            "size_value": size_value,
            "size_unit": size_unit,
            "price": price,
            "price_per_unit": price_per_unit,
            "store_name": store_name,
            "store_chain": self.chain_name,
            "branch_id": branch_id,
            "updated_at": datetime.utcnow().isoformat(),
        }
    
    def scrape(self) -> List[Dict]:
        """
        הפונקציה הראשית - הורדה ופירוק של כל הקבצים.
        מחזירה רשימה של מוצרים+מחירים מוכנים לשמירה בדאטאבייס.
        """
        logger.info(f"🛒 מתחיל סקרייפינג של {self.chain_name}...")
        
        store_files = self.get_store_files()
        
        # הגבלה לפי max_branches (חשוב! לא להוריד 400 קבצים)
        if self.branch_ids:
            # אם המשתמש סיפק רשימה ספציפית - רק אלה
            store_files = [f for f in store_files if f["branch_id"] in self.branch_ids]
        else:
            # אחרת - רק max_branches הראשונים
            store_files = store_files[:self.max_branches]
        
        logger.info(f"📥 מוריד {len(store_files)} קבצים...")
        
        all_products = []
        for i, file_info in enumerate(store_files, 1):
            branch_id = file_info["branch_id"]
            url = file_info["url"]
            store_name = file_info.get("store_name", f"סניף {branch_id}")
            
            logger.info(f"[{i}/{len(store_files)}] מוריד: {store_name}")
            
            xml_content = self.download_and_extract(url)
            if not xml_content:
                continue
            
            products = self.parse_xml(xml_content, branch_id, store_name)
            all_products.extend(products)
        
        logger.info(f"✅ {self.chain_name}: סה\"כ {len(all_products)} רשומות מחיר")
        return all_products
