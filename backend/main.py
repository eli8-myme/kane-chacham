"""
קנה חכם - Backend API
FastAPI server for product price comparison
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import base64
import logging

from database import db
from gemini_vision import identify_product_from_image
from price_fetcher import get_comparisons

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="קנה חכם API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    barcode: Optional[str] = None
    image_base64: Optional[str] = None
    store_name: Optional[str] = None   # הסופר שהלקוח נמצא בו (אופציונלי)
    store_price: Optional[float] = None  # המחיר שהלקוח ראה (אופציונלי)


@app.get("/")
def root():
    return {"status": "ok", "app": "קנה חכם"}


@app.get("/health")
def health():
    return {"status": "healthy", "db_products": db.count_products()}


@app.post("/api/search")
async def search(req: SearchRequest):
    """
    מקבל ברקוד או תמונה, מחזיר מוצר + השוואת מחירים
    """
    barcode = req.barcode
    product_name = None

    # --- שלב 1: זיהוי מוצר ---
    if barcode:
        logger.info(f"Searching by barcode: {barcode}")
        product = db.get_product_by_barcode(barcode)

        if not product:
            # ניסיון Open Food Facts (חינם)
            product = await fetch_from_open_food_facts(barcode)
            if product:
                db.save_product(product)

    elif req.image_base64:
        logger.info("Searching by image (Gemini Vision)")
        result = await identify_product_from_image(req.image_base64)

        if not result:
            raise HTTPException(status_code=404, detail="לא הצלחנו לזהות את המוצר מהתמונה")

        barcode = result.get("barcode")
        product_name = result.get("name")
        product = db.get_product_by_barcode(barcode) if barcode else None

        if not product and product_name:
            product = db.search_product_by_name(product_name)

    else:
        raise HTTPException(status_code=400, detail="נדרש ברקוד או תמונה")

    if not product:
        raise HTTPException(status_code=404, detail="המוצר לא נמצא במאגר")

    # --- שלב 2: השוואת מחירים ---
    comparisons = await get_comparisons(
        barcode=product.get("barcode"),
        product_name=product.get("name"),
        category=product.get("category"),
    )

    if not comparisons:
        raise HTTPException(status_code=404, detail="לא נמצאו מחירים להשוואה")

    # --- שלב 3: סימון 'המחיר הנוכחי' ---
    current_price = req.store_price
    current_store = req.store_name

    # אם לא נשלח מחיר, נשתמש בממוצע כברירת מחדל
    if not current_price and comparisons:
        avg = sum(c["price"] for c in comparisons) / len(comparisons)
        current_price = avg

    # סמן את הרשומה הכי קרובה כ"נוכחית"
    if current_store:
        for c in comparisons:
            if current_store.lower() in c["store_name"].lower():
                c["is_current"] = True
    elif comparisons:
        # ברירת מחדל: הרשומה הראשונה
        comparisons[0]["is_current"] = True

    return {
        "product": product,
        "current_store": current_store or comparisons[0]["store_name"],
        "current_price": current_price or comparisons[0]["price"],
        "comparisons": comparisons,
    }


async def fetch_from_open_food_facts(barcode: str):
    """שליפה חינמית מ-Open Food Facts"""
    import httpx
    try:
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            data = resp.json()

        if data.get("status") != 1:
            return None

        p = data["product"]
        return {
            "barcode": barcode,
            "name": p.get("product_name_he") or p.get("product_name") or "לא ידוע",
            "brand": p.get("brands", ""),
            "size": p.get("quantity", ""),
            "category": p.get("categories_tags", [""])[0].replace("en:", ""),
            "image_url": p.get("image_front_url", ""),
        }
    except Exception as e:
        logger.warning(f"Open Food Facts error: {e}")
        return None


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
