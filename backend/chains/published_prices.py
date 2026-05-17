"""
Published Prices Scraper - הורדת מחירים מ-publishedprices.co.il

מערכת Cerberus (NCR) מארחת קבצי מחירים עבור מספר רשתות.
הגישה היא דרך FTP עם שמות משתמש ציבוריים (בלי סיסמה).

רשתות נתמכות:
- רמי לוי (RamiLevi)
- חצי חינם (HaziHinam)
- ויקטורי (Victory)
- יוחננוף (yohananof)
- אושר עד (osherad)
- טיב טעם (TivTaam)
"""
import ftplib
import gzip
import io
import logging
import re
from typing import List, Dict, Optional

from .base import BaseChainScraper

logger = logging.getLogger(__name__)

FTP_HOST = "url.retail.publishedprices.co.il"


class PublishedPricesScraper(BaseChainScraper):
    """
    סקרייפר גנרי עבור כל הרשתות שמארחות ב-publishedprices.co.il
    כל רשת שמשתמשת במערכת Cerberus יורשת ממחלקה זו.
    """

    chain_name: str = ""
    ftp_username: str = ""
    ftp_password: str = ""  # בדרך כלל ריק

    def __init__(self, max_branches: int = 5, **kwargs):
        super().__init__(max_branches=max_branches, **kwargs)

    def get_store_files(self) -> List[Dict[str, str]]:
        """מתחבר ב-FTP ומחזיר רשימת קבצי PriceFull."""
        files = []

        try:
            logger.info(f"  FTP connecting: {FTP_HOST} (user: {self.ftp_username})")
            ftp = ftplib.FTP(FTP_HOST, timeout=30)
            ftp.login(user=self.ftp_username, passwd=self.ftp_password)

            # קבל רשימת קבצים
            file_list = []
            ftp.retrlines("LIST", file_list.append)

            # סנן רק קבצי PriceFull
            for entry in file_list:
                filename = entry.split()[-1] if entry.split() else ""
                if not filename:
                    continue

                # חפש קבצי pricefull (בכל שילוב אותיות)
                if "pricefull" not in filename.lower():
                    continue

                # חלץ branch_id מהשם (PriceFull7290058140886-001-...)
                branch_id = self._extract_branch_from_filename(filename)

                files.append({
                    "branch_id": branch_id or "000",
                    "url": filename,  # נשמר כשם קובץ, הורדה בנפרד
                    "store_name": f"{self.chain_name} סניף {branch_id}" if branch_id else self.chain_name,
                })

            ftp.quit()
            logger.info(f"  Found {len(files)} PriceFull files for {self.chain_name}")

        except ftplib.all_errors as e:
            logger.error(f"FTP error for {self.chain_name}: {e}")
        except Exception as e:
            logger.error(f"Error listing files for {self.chain_name}: {e}")

        return files

    def _extract_branch_from_filename(self, filename: str) -> str:
        """חילוץ מזהה סניף משם קובץ."""
        # Pattern: PriceFull7290058140886-001-202401010000.xml.gz
        match = re.search(r'PriceFull\d+-(\d+)-', filename, re.IGNORECASE)
        if match:
            return match.group(1).zfill(3)
        return ""

    def download_and_extract(self, url: str) -> Optional[str]:
        """מוריד קובץ FTP ומחזיר תוכן XML."""
        try:
            ftp = ftplib.FTP(FTP_HOST, timeout=30)
            ftp.login(user=self.ftp_username, passwd=self.ftp_password)

            # הורד לזיכרון
            buffer = io.BytesIO()
            ftp.retrbinary(f"RETR {url}", buffer.write)
            ftp.quit()

            content = buffer.getvalue()
            if not content:
                return None

            # פרוק GZ אם צריך
            if url.endswith(".gz") or content[:2] == b'\x1f\x8b':
                content = gzip.decompress(content)

            return content.decode("utf-8", errors="ignore")

        except ftplib.all_errors as e:
            logger.error(f"FTP download error ({self.chain_name}, {url}): {e}")
            return None
        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            return None


# ===== רשתות ספציפיות =====

class RamiLevyScraper(PublishedPricesScraper):
    chain_name = "רמי לוי"
    chain_id = "7290058140886"
    ftp_username = "RamiLevi"


class HaziHinamScraper(PublishedPricesScraper):
    chain_name = "חצי חינם"
    chain_id = "7290700100008"
    ftp_username = "HaziHinam"


class VictoryScraper(PublishedPricesScraper):
    chain_name = "ויקטורי"
    chain_id = "7290696200003"
    ftp_username = "Victory"


class YohananofScraper(PublishedPricesScraper):
    chain_name = "יוחננוף"
    chain_id = "7290803800003"
    ftp_username = "yohananof"


class OsherAdScraper(PublishedPricesScraper):
    chain_name = "אושר עד"
    chain_id = "7290633800006"
    ftp_username = "osherad"


class TivTaamScraper(PublishedPricesScraper):
    chain_name = "טיב טעם"
    chain_id = "7290873255550"
    ftp_username = "TivTaam"
