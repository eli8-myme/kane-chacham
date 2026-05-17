"""
Shufersal Scraper - הורדת מחירים משופרסל

האתר הציבורי של שופרסל: https://prices.shufersal.co.il
- אין צורך ב-login (חוק שקיפות מחירים מ-2014)
- עדכונים יומיומיים ב-2:00 בלילה
- כל סניף מקבל קובץ XML.GZ נפרד

הערה חשובה: שופרסל קוראים לקבצי PriceFull בשם Price (בלי Full).
"""
import logging
import re
from typing import List, Dict

import httpx

from .base import BaseChainScraper

logger = logging.getLogger(__name__)


class ShufersalScraper(BaseChainScraper):
    """סקרייפר עבור רשת שופרסל."""

    chain_name = "שופרסל"
    chain_id = "7290027600007"
    base_url = "https://prices.shufersal.co.il"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "he,en;q=0.9",
    }

    def __init__(self, branch_ids=None, max_branches=20):
        super().__init__(branch_ids=branch_ids, max_branches=max_branches)

    def get_store_files(self) -> List[Dict[str, str]]:
        files = []

        try:
            with httpx.Client(timeout=30.0, follow_redirects=True, headers=self.HEADERS) as client:
                page = 1
                max_pages = 10

                while page <= max_pages:
                    url = f"{self.base_url}/?cat=2&page={page}"
                    logger.info(f"  סורק עמוד {page}...")

                    response = client.get(url)
                    response.raise_for_status()
                    html = response.text

                    page_files = self._parse_html_for_files(html)

                    if not page_files:
                        break

                    files.extend(page_files)

                    if self.branch_ids:
                        found_ids = {f["branch_id"] for f in files}
                        if all(bid in found_ids for bid in self.branch_ids):
                            logger.info(f"  נמצאו כל הסניפים שביקשנו")
                            break

                    page += 1

                logger.info(f"  נמצאו סהכ {len(files)} קבצים")

        except Exception as e:
            logger.error(f"שגיאה בקבלת רשימת הקבצים משופרסל: {e}")
            return []

        return files

    def _parse_html_for_files(self, html: str) -> List[Dict[str, str]]:
        files = []

        link_pattern = r'href="(https://pricesprodpublic\.blob\.core\.windows\.net/price/Price[^"]+\.gz[^"]*)"'

        rows = re.split(r'<tr[^>]*>', html)

        for row in rows:
            link_match = re.search(link_pattern, row)
            if not link_match:
                continue

            url = link_match.group(1)
            url = url.replace("&amp;", "&")

            branch_id = self._extract_branch_id(url)
            if not branch_id:
                continue

            store_name = self._extract_store_name(row)

            files.append({
                "branch_id": branch_id,
                "url": url,
                "store_name": store_name or f"סניף {branch_id}",
            })

        return files

    def _extract_branch_id(self, url: str) -> str:
        match = re.search(r'/Price(?:Full)?(\d+)-(\d+)(?:-(\d+))?', url)
        if not match:
            return ""

        first = match.group(2)
        second = match.group(3)

        if second and len(second) <= 4:
            return second.zfill(3)

        return first.zfill(3)

    def _extract_store_name(self, html_row: str) -> str:
        td_pattern = r'<td[^>]*>([^<]*?\d+[^<]*?-[^<]+)</td>'
        match = re.search(td_pattern, html_row)
        if match:
            text = match.group(1).strip()
            parts = text.split(" - ", 1)
            if len(parts) == 2:
                return parts[1].strip()
            return text
        return ""
