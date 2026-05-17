"""
סקריפט מקומי ליבוא מחירים מרשתות ישראליות

הרץ מהמחשב שלך (בישראל!) כי publishedprices.co.il חוסם גישה מחו"ל.
הסקריפט מתחבר ב-FTP, מוריד קבצי מחירים, ומעלה אותם ל-Render.

שימוש:
  pip install httpx
  python local_import.py

הסקריפט לא דורש התקנות מיוחדות - רק Python 3.8+ ו-httpx.
"""
import ftplib
import gzip
import io
import json
import sys
import time
from datetime import datetime
from xml.etree import ElementTree as ET

# נסה httpx, אם אין - נשתמש ב-urllib
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    import urllib.request
    import urllib.error
    HAS_HTTPX = False

# ===== CONFIG =====
RENDER_URL = "https://kane-chacham.onrender.com"
UPLOAD_SECRET = "kane-chacham-2024"
FTP_HOST = "url.retail.publishedprices.co.il"
MAX_BRANCHES = 3  # מספר סניפים לכל רשת (הגדל ל-10+ לנתונים מלאים)
BATCH_SIZE = 2000  # כמה רשומות לשלוח בכל בקשה

# רשתות לייבוא
CHAINS = [
    {"name": "רמי לוי", "ftp_user": "RamiLevi"},
    {"name": "חצי חינם", "ftp_user": "HaziHinam"},
    {"name": "ויקטורי", "ftp_user": "Victory"},
    {"name": "יוחננוף", "ftp_user": "yohananof"},
    {"name": "אושר עד", "ftp_user": "osherad"},
    {"name": "טיב טעם", "ftp_user": "TivTaam"},
]


def upload_to_render(products, prices):
    """מעלה נתונים לשרת Render"""
    url = f"{RENDER_URL}/api/upload-prices"
    payload = json.dumps({"products": products, "prices": prices}).encode("utf-8")

    if HAS_HTTPX:
        resp = httpx.post(
            url,
            content=payload,
            headers={
                "Content-Type": "application/json",
                "X-Secret": UPLOAD_SECRET,
            },
            timeout=60.0,
        )
        return resp.json()
    else:
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "X-Secret": UPLOAD_SECRET,
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))


def parse_xml(xml_content, chain_name, branch_id, store_name):
    """פרסור XML של PriceFull"""
    records = []
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        print(f"    XML parse error: {e}")
        return records

    for item in root.findall(".//Item"):
        try:
            barcode = _get(item, "ItemCode")
            price_str = _get(item, "ItemPrice")
            if not barcode or not price_str:
                continue

            price = float(price_str)
            if price <= 0:
                continue

            name = _get(item, "ItemName")
            brand = _get(item, "ManufacturerName")
            qty = _get(item, "Quantity")
            unit = _get(item, "UnitQty") or _get(item, "UnitOfMeasure")
            unit_price_str = _get(item, "UnitOfMeasurePrice")

            size_val = None
            try:
                size_val = float(qty) if qty else None
            except ValueError:
                pass

            price_per_unit = None
            try:
                price_per_unit = float(unit_price_str) if unit_price_str else None
            except ValueError:
                pass

            if not price_per_unit and size_val and size_val > 0:
                price_per_unit = round(price / size_val, 2)

            size_text = f"{qty} {unit}".strip() if qty else ""

            records.append({
                "barcode": barcode,
                "name": name or "",
                "brand": brand or "",
                "size": size_text,
                "size_value": size_val,
                "size_unit": unit or "",
                "price": price,
                "price_per_unit": price_per_unit,
                "store_name": store_name,
                "store_chain": chain_name,
                "branch_id": branch_id,
                "updated_at": datetime.utcnow().isoformat(),
            })
        except (ValueError, AttributeError):
            continue

    return records


def _get(item, tag):
    """מציאת טקסט בטאג XML"""
    for variant in [tag, tag.lower(), tag.upper()]:
        el = item.find(variant)
        if el is not None and el.text:
            return el.text.strip()
    return ""


def import_chain(chain):
    """ייבוא רשת אחת"""
    name = chain["name"]
    user = chain["ftp_user"]
    print(f"\n{'='*50}")
    print(f"  {name} (FTP: {user})")
    print(f"{'='*50}")

    try:
        ftp = ftplib.FTP(FTP_HOST, timeout=30)
        ftp.login(user=user, passwd="")
        print(f"  Connected to FTP")
    except Exception as e:
        print(f"  FTP connection failed: {e}")
        return 0

    # רשימת קבצים
    file_list = []
    try:
        ftp.retrlines("LIST", file_list.append)
    except Exception as e:
        print(f"  LIST failed: {e}")
        ftp.quit()
        return 0

    # סנן PriceFull
    price_files = []
    for entry in file_list:
        parts = entry.split()
        if not parts:
            continue
        filename = parts[-1]
        if "pricefull" in filename.lower() and (filename.endswith(".gz") or filename.endswith(".xml")):
            price_files.append(filename)

    print(f"  Found {len(price_files)} PriceFull files")

    if not price_files:
        # נסה גם בלי "full"
        for entry in file_list:
            parts = entry.split()
            if not parts:
                continue
            filename = parts[-1]
            if "price" in filename.lower() and "promo" not in filename.lower() and (filename.endswith(".gz") or filename.endswith(".xml")):
                price_files.append(filename)
        print(f"  Found {len(price_files)} Price files (without 'full')")

    # הגבל מספר סניפים
    price_files = price_files[:MAX_BRANCHES]

    total_uploaded = 0
    for i, filename in enumerate(price_files, 1):
        print(f"  [{i}/{len(price_files)}] Downloading: {filename}")

        try:
            buffer = io.BytesIO()
            ftp.retrbinary(f"RETR {filename}", buffer.write)
            content = buffer.getvalue()

            if not content:
                print(f"    Empty file, skipping")
                continue

            # פרוק GZ
            if filename.endswith(".gz") or content[:2] == b'\x1f\x8b':
                content = gzip.decompress(content)

            xml_text = content.decode("utf-8", errors="ignore")

            # חלץ branch_id
            import re
            match = re.search(r'PriceFull\d+-(\d+)-', filename, re.IGNORECASE)
            branch_id = match.group(1) if match else str(i)

            store_name = f"{name} סניף {branch_id}"

            records = parse_xml(xml_text, name, branch_id, store_name)
            print(f"    Parsed {len(records)} products")

            if records:
                # שלח בקבוצות
                for start in range(0, len(records), BATCH_SIZE):
                    batch = records[start:start + BATCH_SIZE]

                    products = []
                    seen = set()
                    for r in batch:
                        if r["barcode"] not in seen:
                            seen.add(r["barcode"])
                            products.append({
                                "barcode": r["barcode"],
                                "name": r["name"],
                                "brand": r["brand"],
                                "size": r["size"],
                                "category": "",
                                "image_url": "",
                            })

                    prices = [{
                        "barcode": r["barcode"],
                        "store_name": r["store_name"],
                        "store_chain": r["store_chain"],
                        "branch_id": r["branch_id"],
                        "price": r["price"],
                        "price_per_unit": r["price_per_unit"],
                        "size": r["size"],
                        "size_value": r["size_value"],
                        "size_unit": r["size_unit"],
                        "updated_at": r["updated_at"],
                    } for r in batch]

                    try:
                        result = upload_to_render(products, prices)
                        uploaded = result.get("prices_saved", 0)
                        total_uploaded += uploaded
                        print(f"    Uploaded batch: {uploaded} prices")
                    except Exception as e:
                        print(f"    Upload error: {e}")

        except Exception as e:
            print(f"    Error: {e}")
            continue

    try:
        ftp.quit()
    except Exception:
        pass

    print(f"  Total uploaded for {name}: {total_uploaded}")
    return total_uploaded


def main():
    print("="*60)
    print("  קנה חכם - יבוא מחירים מקומי")
    print(f"  רשתות: {len(CHAINS)}")
    print(f"  סניפים לרשת: {MAX_BRANCHES}")
    print(f"  שרת: {RENDER_URL}")
    print("="*60)

    # בדוק חיבור לשרת
    print("\nChecking server connection...")
    try:
        if HAS_HTTPX:
            resp = httpx.get(f"{RENDER_URL}/health", timeout=30.0)
            health = resp.json()
        else:
            with urllib.request.urlopen(f"{RENDER_URL}/health", timeout=30) as resp:
                health = json.loads(resp.read().decode("utf-8"))
        print(f"Server OK: {health}")
    except Exception as e:
        print(f"Server connection failed: {e}")
        print("Make sure the Render server is running!")
        sys.exit(1)

    total = 0
    start = time.time()

    for chain in CHAINS:
        try:
            count = import_chain(chain)
            total += count
        except Exception as e:
            print(f"Error with {chain['name']}: {e}")

    elapsed = time.time() - start
    print(f"\n{'='*60}")
    print(f"  Done! Total prices uploaded: {total}")
    print(f"  Time: {elapsed:.0f} seconds")
    print(f"{'='*60}")

    # בדוק סטטיסטיקות
    try:
        if HAS_HTTPX:
            resp = httpx.get(f"{RENDER_URL}/api/stats", timeout=30.0)
            stats = resp.json()
        else:
            with urllib.request.urlopen(f"{RENDER_URL}/api/stats", timeout=30) as resp:
                stats = json.loads(resp.read().decode("utf-8"))
        print(f"\nServer stats: {json.dumps(stats, ensure_ascii=False, indent=2)}")
    except Exception:
        pass


if __name__ == "__main__":
    main()
