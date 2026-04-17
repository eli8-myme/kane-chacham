"""
קנה חכם - Backend API
FastAPI server for product price comparison
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import logging
import httpx

from database import db
from price_fetcher import get_comparisons

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="קנה חכם API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    barcode: Optional[str] = None
    store_name: Optional[str] = None
    store_price: Optional[float] = None


@app.get("/")
def root():
    return {"status": "ok", "app": "קנה חכם", "version": "2.0"}


@app.get("/health")
def health():
    count = db.count_products()
    return {"status": "healthy", "db_products": count}


@app.get("/api/prices/{barcode}")
async def get_prices_by_barcode(barcode: str):
    """
    חיפוש מחירים לפי ברקוד - endpoint פשוט
    מחזיר מידע על המוצר + מחירים מכל הרשתות
    """
    product = db.get_product_by_barcode(barcode)

    if not product:
        product = await fetch_from_open_food_facts(barcode)
        if product:
            db.save_product(product)

    if not product:
        raise HTTPException(status_code=404, detail="המוצר לא נמצא במאגר")

    comparisons = await get_comparisons(barcode=barcode)

    if not comparisons:
        raise HTTPException(status_code=404, detail="לא נמצאו מחירים להשוואה")

    sorted_comps = sorted(comparisons, key=lambda x: x.get("price", 999))
    best = sorted_comps[0] if sorted_comps else None

    return {
        "product": product,
        "current_store": sorted_comps[-1]["store_name"] if sorted_comps else "",
        "current_price": sorted_comps[-1]["price"] if sorted_comps else 0,
        "comparisons": sorted_comps,
    }


@app.post("/api/search")
async def search(req: SearchRequest):
    """
    מקבל ברקוד, מחזיר מוצר + השוואת מחירים
    """
    if not req.barcode:
        raise HTTPException(status_code=400, detail="נדרש ברקוד")

    barcode = req.barcode
    logger.info(f"Searching by barcode: {barcode}")

    product = db.get_product_by_barcode(barcode)
    if not product:
        product = await fetch_from_open_food_facts(barcode)
        if product:
            db.save_product(product)

    if not product:
        raise HTTPException(status_code=404, detail="המוצר לא נמצא במאגר")

    comparisons = await get_comparisons(barcode=barcode)

    if not comparisons:
        raise HTTPException(status_code=404, detail="לא נמצאו מחירים להשוואה")

    current_price = req.store_price
    current_store = req.store_name

    if current_store:
        for c in comparisons:
            if current_store.lower() in c["store_name"].lower():
                c["is_current"] = True
    elif comparisons:
        comparisons[-1]["is_current"] = True

    if not current_price and comparisons:
        current_price = comparisons[-1]["price"]
    if not current_store and comparisons:
        current_store = comparisons[-1]["store_name"]

    return {
        "product": product,
        "current_store": current_store,
        "current_price": current_price,
        "comparisons": comparisons,
    }


async def fetch_from_open_food_facts(barcode: str):
    """שליפה חינמית מ-Open Food Facts"""
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
