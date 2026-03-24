"""
Gemini Vision - זיהוי מוצר מתמונה
משתמש ב-Google Gemini 1.5 Flash (חינם: 15 req/min)
"""
import os
import json
import base64
import logging
import httpx
from typing import Optional, Dict

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent"
)

SYSTEM_PROMPT = """אתה מומחה לזיהוי מוצרי סופרמרקט.
תקבל תמונה של מוצר וצריך להחזיר JSON עם המידע הבא:
{
  "name": "שם המוצר בעברית",
  "brand": "שם המותג",
  "size": "גודל/משקל (לדוגמה: 1 ליטר, 500 גרם)",
  "size_value": 500,
  "size_unit": "g",
  "barcode": "ברקוד אם נראה בתמונה או null",
  "category": "קטגוריה (מזון/ניקוי/טיפוח וכו')",
  "confidence": 0.95
}
אם אינך יכול לזהות את המוצר החזר {"error": "לא ניתן לזהות"}
החזר JSON בלבד, ללא טקסט נוסף."""


async def identify_product_from_image(image_base64: str) -> Optional[Dict]:
    """
    שולח תמונה ל-Gemini Vision ומקבל מידע על המוצר
    """
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not set!")
        return None

    payload = {
        "contents": [{
            "parts": [
                {"text": SYSTEM_PROMPT},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": image_base64,
                    }
                }
            ]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 512,
        }
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                GEMINI_URL,
                params={"key": GEMINI_API_KEY},
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        text = data["candidates"][0]["content"]["parts"][0]["text"]

        # נקה JSON
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]

        result = json.loads(text)

        if "error" in result:
            logger.warning(f"Gemini could not identify: {result}")
            return None

        logger.info(f"Gemini identified: {result.get('name')}")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"Gemini JSON parse error: {e}")
        return None
    except Exception as e:
        logger.error(f"Gemini Vision error: {e}")
        return None
