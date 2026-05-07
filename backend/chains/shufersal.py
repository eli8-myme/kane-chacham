"""
Shufersal Scraper - הורדת מחירים משופרסל

האתר הציבורי של שופרסל: https://prices.shufersal.co.il
- אין צורך ב-login (חוק שקיפות מחירים מ-2014)
- עדכונים יומיומיים ב-2:00 בלילה
- כל סניף מקבל קובץ XML.GZ נפרד
"""
import logging
import re
from typing import List, Dict
from urllib.parse import urljoin

import httpx

from .base import BaseChainScraper

logger = logging.getLogger(__name__)


class ShufersalScraper(BaseChainScraper):
    """סקרייפר עבור רשת שופרסל."""
    
    chain_name = "שופרסל"
    chain_id = "7290027600007"
    base_url = "https://prices.shufersal.co.il"
    
    # User-Agent של דפדפן רגיל - חובה כדי שלא נחסם
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "he,en;q=0.9",
    }
    
    # סניפי MVP - סניפי דגל מסביב לארץ + Online
    DEFAULT_BRANCH_IDS = [
        "001",   # שלי ת"א - בן יהודה
        "002",   # שלי ירושלים - אגרון
        "004",   # שלי חיפה - כרמל
        "035",   # יוניברס באר שבע - וולפסון
        "413",   # שופרסל ONLINE
    ]
    
    def __init__(self, branch_ids=None, max_branches=5):
        # אם המשתמש לא סיפק רשימה - נשתמש ב-defaults של MVP
        if branch_ids is None:
            branch_ids = self.DEFAULT_BRANCH_IDS
        super().__init__(branch_ids=branch_ids, max_branches=max_branches)
    
    def get_store_files(self) -> List[Dict[str, str]]:
        """
        מחזיר רשימת קבצי PriceFull לסניפים.
        
        ה-URL של שופרסל מסונן לפי קטגוריה ב-`?cat=`:
        - cat=2 = PricesFull (הקובץ המלא של מחירים)
        - cat=0 = Prices (רק עדכונים)
        """
        files = []
        
        try:
            with httpx.Client(timeout=30.0, follow_redirects=True, headers=self.HEADERS) as client:
                page = 1
                max_pages = 10  # הגנה - אם משהו השתבש לא נסרוק לנצח
                
                while page <= max_pages:
                    url = f"{self.base_url}/?cat=2&page={page}"
                    logger.info(f"  📄 סורק עמוד {page} של PricesFull...")
                    
                    response = client.get(url)
                    response.raise_for_status()
                    html = response.text
                    
                    # חיפוש קישורים והסניפים שלהם
                    page_files = self._parse_html_for_files(html)
                    
                    if not page_files:
                        # אין יותר קבצים בעמוד הזה - סיימנו
                        break
                    
                    files.extend(page_files)
                    
                    # אם ה-branch_ids כולם נמצאו - אפשר להפסיק
                    if self.branch_ids:
                        found_ids = {f["branch_id"] for f in files}
                        if all(bid in found_ids for bid in self.branch_ids):
                            logger.info(f"  ✓ נמצאו כל הסניפים שביקשנו, מפסיק לסרוק")
                            break
                    
                    page += 1
                
                logger.info(f"  📋 נמצאו סה\"כ {len(files)} קבצי PricesFull")
                
        except Exception as e:
            logger.error(f"שגיאה בקבלת רשימת הקבצים משופרסל: {e}")
            return []
        
        return files
    
    def _parse_html_for_files(self, html: str) -> List[Dict[str, str]]:
        """
        חילוץ קישורי PriceFull מתוך HTML של עמוד שופרסל.
        """
        files = []
        
        # Regex למציאת שורות table - כל שורה מכילה url של PriceFull + שם סניף
        link_pattern = r'href="(https://[^"]*PriceFull[^"]+\.gz[^"]*)"'
        
        # פיצול ל-rows של table
        rows = re.split(r'<tr[^>]*>', html)
        
        for row in rows:
            # האם יש בשורה הזו קישור PriceFull?
            link_match = re.search(link_pattern, row)
            if not link_match:
                continue
            
            url = link_match.group(1)
            
            # חילוץ branch_id מה-URL
            branch_id = self._extract_branch_id(url)
            if not branch_id:
                continue
            
            # חילוץ שם הסניף מהשורה
            store_name = self._extract_store_name(row)
            
            files.append({
                "branch_id": branch_id,
                "url": url,
                "store_name": store_name or f"סניף {branch_id}",
            })
        
        return files
    
    def _extract_branch_id(self, url: str) -> str:
        """
        חילוץ branch_id מה-URL.
        
        דוגמאות:
        - PriceFull7290027600007-001-202605070200.gz → "001"
        - PriceFull7290027600007-001-357-20260507-024000.gz → "357"
        - PriceFull7290027600007-002-413-20260507-024000.gz → "413"
        """
        match = re.search(r'PriceFull\d+-(\d+)(?:-(\d+))?', url)
        if not match:
            return ""
        
        first = match.group(1)
        second = match.group(2)
        
        # אם יש שני מספרים והשני אינו תאריך - השני הוא branch_id
        if second and len(second) <= 4:
            return second.zfill(3)
        
        return first.zfill(3)
    
    def _extract_store_name(self, html_row: str) -> str:
        """חילוץ שם הסניף מתא ב-table."""
        td_pattern = r'<td[^>]*>([^<]*?\d+[^<]*?-[^<]+)</td>'
        match = re.search(td_pattern, html_row)
        if match:
            text = match.group(1).strip()
            parts = text.split(" - ", 1)
            if len(parts) == 2:
                return parts[1].strip()
            return text
        return ""
